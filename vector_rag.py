"""
Lightweight, zero-dependency Vector DB + RAG Engine for LeafGuard AI.

1. LeafVectorDB (data/leaf_vector_db.npz):
   - Stores L2-normalized 576-dim MobileNetV3 embeddings for real PlantVillage leaves,
     field/camera-cropped leaves, and user-uploaded "Teach AI" reference leaves.
   - Enables instant k-NN cosine retrieval and zero-retraining incremental learning
     when farmers upload new leaf photos via /api/references.

2. AgronomyRAG:
   - Indexes PLANTVILLAGE_MASTER_DB + custom references into normalized TF-IDF
     character/word n-gram vectors for fast semantic/keyword retrieval.
   - Grounds local LLM (Ollama) responses or builds structured retrieved answers
     for farmer questions and notes.
"""

import os
import re
import json
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

from leaf_crop import crop_to_leaf
from plantvillage_engine import PLANTVILLAGE_MASTER_DB

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "data", "leaf_vector_db.npz")


class LeafVectorDB:
    """Persistent cosine-similarity Image Vector Database."""

    def __init__(self, db_path: str = VECTOR_DB_PATH):
        self.db_path = db_path
        self.vectors: np.ndarray = np.zeros((0, 576), dtype=np.float32)
        self.class_ids: List[str] = []
        self.crops: List[str] = []
        self.diseases: List[str] = []
        self.sources: List[str] = []
        self.load()

    def load(self):
        if os.path.exists(self.db_path):
            try:
                d = np.load(self.db_path, allow_pickle=True)
                self.vectors = d["vectors"].astype(np.float32)
                self.class_ids = [str(x) for x in d["class_ids"]]
                self.crops = [str(x) for x in d["crops"]]
                self.diseases = [str(x) for x in d["diseases"]]
                self.sources = [str(x) for x in d["sources"]]
            except Exception as e:
                print("LeafVectorDB load warning:", e)

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            np.savez_compressed(
                self.db_path,
                vectors=self.vectors.astype(np.float32),
                class_ids=np.array(self.class_ids),
                crops=np.array(self.crops),
                diseases=np.array(self.diseases),
                sources=np.array(self.sources),
            )
        except OSError as e:
            print("LeafVectorDB save skipped (read-only fs):", e)

    def add_vectors(
        self,
        vecs: np.ndarray,
        class_ids: List[str],
        crops: List[str],
        diseases: List[str],
        sources: List[str],
        persist: bool = True,
    ):
        if len(vecs) == 0:
            return
        vecs = vecs.astype(np.float32)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-8
        vecs = vecs / norms
        if len(self.vectors) == 0:
            self.vectors = vecs
        else:
            self.vectors = np.concatenate([self.vectors, vecs], axis=0)
        self.class_ids.extend(class_ids)
        self.crops.extend(crops)
        self.diseases.extend(diseases)
        self.sources.extend(sources)
        if persist:
            self.save()

    def search(
        self,
        query_vec: np.ndarray,
        top_k: int = 5,
        crop_hint: str = "",
    ) -> List[Dict[str, Any]]:
        if len(self.vectors) == 0:
            return []
        q = query_vec.astype(np.float32).reshape(-1)
        q = q / (np.linalg.norm(q) + 1e-8)

        sims = (self.vectors.astype(np.float64) @ q.astype(np.float64))
        hint = (crop_hint or "").strip().lower()
        if hint:
            mask = np.array([
                hint in c.lower() or hint in cid.lower().replace("_", " ")
                for c, cid in zip(self.crops, self.class_ids)
            ])
            if mask.any():
                sims = np.where(mask, sims, -2.0)

        order = np.argsort(-sims)[:top_k]
        results = []
        for idx in order:
            s = float(sims[idx])
            if s <= -1.0:
                continue
            results.append({
                "class_id": self.class_ids[idx],
                "crop": self.crops[idx],
                "disease": self.diseases[idx],
                "source": self.sources[idx],
                "similarity": round(s, 4),
            })
        return results

    def stats(self) -> Dict[str, Any]:
        return {
            "total_vectors": int(len(self.vectors)),
            "unique_classes": len(set(self.class_ids)),
            "user_taught_vectors": sum(1 for s in self.sources if s.startswith("teach_ai:")),
        }


class AgronomyRAG:
    """Pure-NumPy TF-IDF Vector Store + RAG retriever over agronomy knowledge."""

    def __init__(self):
        self.docs: List[Dict[str, Any]] = []
        self.vocab: Dict[str, int] = {}
        self.idf: np.ndarray = np.zeros(0, dtype=np.float32)
        self.doc_matrix: np.ndarray = np.zeros((0, 0), dtype=np.float32)
        self.rebuild_index()

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        words = re.findall(r"[a-z0-9\u0900-\u097f]+", (text or "").lower())
        bigrams = [f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1)]
        return words + bigrams

    def rebuild_index(self, extra_refs: Optional[List[Dict[str, Any]]] = None):
        docs = []
        for cid, info in PLANTVILLAGE_MASTER_DB.items():
            organic = "; ".join(info.get("organic_treatment", []))
            chem = "; ".join(info.get("chemical_treatment", []))
            text = (
                f"Crop: {info.get('crop', '')}. Disease: {info.get('disease', '')}. "
                f"Pathogen: {info.get('pathogen_type', '')}. "
                f"Morphology: {info.get('leaf_morphology', '')}. "
                f"Color: {info.get('color_signature', '')}. "
                f"Lesions: {info.get('lesion_pattern', '')}. "
                f"Organic treatment: {organic}. Chemical treatment: {chem}. "
                f"Outbreak risk: {info.get('outbreak_risk', '')}. "
                f"Hindi: {info.get('hindi_summary', '')}"
            )
            docs.append({
                "id": cid,
                "crop": info.get("crop", ""),
                "disease": info.get("disease", ""),
                "text": text,
                "organic_treatment": info.get("organic_treatment", []),
                "chemical_treatment": info.get("chemical_treatment", []),
                "hindi_summary": info.get("hindi_summary", ""),
            })

        if extra_refs:
            for r in extra_refs:
                if str(r.get("id", "")).startswith("ref_") and len(str(r.get("id", ""))) > 14:
                    # Skip auto-synced copies of PLANTVILLAGE_MASTER_DB
                    continue
                text = (
                    f"Crop: {r.get('crop', '')}. Disease: {r.get('disease', '')}. "
                    f"Symptoms: {r.get('visual_symptoms', '')}. "
                    f"Treatment: {r.get('treatment', '')}."
                )
                docs.append({
                    "id": r.get("id", "custom"),
                    "crop": r.get("crop", ""),
                    "disease": r.get("disease", ""),
                    "text": text,
                    "organic_treatment": [r.get("treatment", "")] if r.get("treatment") else [],
                    "chemical_treatment": [],
                    "hindi_summary": "",
                })

        self.docs = docs
        tokenized = [self._tokenize(d["text"]) for d in docs]
        vocab: Dict[str, int] = {}
        df: Dict[str, int] = {}
        for toks in tokenized:
            for t in set(toks):
                if t not in vocab:
                    vocab[t] = len(vocab)
                df[t] = df.get(t, 0) + 1

        self.vocab = vocab
        n_docs = len(docs)
        n_vocab = len(vocab)
        idf = np.zeros(n_vocab, dtype=np.float32)
        for t, idx in vocab.items():
            idf[idx] = float(np.log((n_docs + 1.0) / (df[t] + 1.0)) + 1.0)
        self.idf = idf

        mat = np.zeros((n_docs, n_vocab), dtype=np.float32)
        for i, toks in enumerate(tokenized):
            for t in toks:
                mat[i, vocab[t]] += 1.0
            mat[i] *= idf
            norm = np.linalg.norm(mat[i]) + 1e-8
            mat[i] /= norm
        self.doc_matrix = mat

    def retrieve(self, query: str, crop: str = "", top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.docs or len(self.vocab) == 0:
            return []
        q_text = f"{crop} {query}".strip()
        toks = self._tokenize(q_text)
        q_vec = np.zeros(len(self.vocab), dtype=np.float32)
        for t in toks:
            if t in self.vocab:
                q_vec[self.vocab[t]] += 1.0
        q_vec *= self.idf
        q_vec /= (np.linalg.norm(q_vec) + 1e-8)

        sims = self.doc_matrix @ q_vec
        if crop:
            c_low = crop.lower()
            boost = np.array([0.18 if c_low in d["crop"].lower() else 0.0 for d in self.docs], dtype=np.float32)
            sims = sims + boost

        order = np.argsort(-sims)[:top_k]
        return [
            {
                "id": self.docs[i]["id"],
                "crop": self.docs[i]["crop"],
                "disease": self.docs[i]["disease"],
                "score": round(float(sims[i]), 4),
                "text": self.docs[i]["text"],
                "organic_treatment": self.docs[i]["organic_treatment"],
                "chemical_treatment": self.docs[i]["chemical_treatment"],
                "hindi_summary": self.docs[i]["hindi_summary"],
            }
            for i in order
        ]


_vdb_singleton: Optional[LeafVectorDB] = None
_rag_singleton: Optional[AgronomyRAG] = None


def get_vector_db() -> LeafVectorDB:
    global _vdb_singleton
    if _vdb_singleton is None:
        _vdb_singleton = LeafVectorDB()
    return _vdb_singleton


def get_rag() -> AgronomyRAG:
    global _rag_singleton
    if _rag_singleton is None:
        _rag_singleton = AgronomyRAG()
    return _rag_singleton
