# 🌿 LeafGuard AI • Hyper-Local Pest & Disease Early Warning System

[![Vercel Deployment](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://voicekeep-six.vercel.app)
[![Live App](https://img.shields.io/badge/Live%20Demo-voicekeep--six.vercel.app-10b981?style=for-the-badge&logo=google-chrome&logoColor=white)](https://voicekeep-six.vercel.app)
[![GitHub Repo](https://img.shields.io/badge/GitHub-hackdelhi-181717?style=for-the-badge&logo=github)](https://github.com/saketanand200911/hackdelhi)

> **Live Production URL:** [https://voicekeep-six.vercel.app](https://voicekeep-six.vercel.app)  
> **An image-recognition, botanical pathology, and predictive outbreak radar web app empowering smallholder farmers (plots < 2 hectares) with instant localized treatment plans and neighborhood outbreak alerts.**

---

## 🚀 Key Features

1. **📷 Live Camera & Leaf Scanner (Point & Shoot)**
   - Browser-based camera streaming with mobile back-camera (`Flip`) support and photo upload.
   - Targeting reticle and laser sweep feedback.
   - Instant visual pixel analysis:
     - **Healthy Green %**
     - **Pale Yellow / Chlorosis %**
     - **Brown / Necrotic Margins %**
     - **Powdery White Mildew %**

2. **🔬 Plant Pathology & Treatment Engine (Trained on PlantVillage 38-Class Dataset)**
   - Covers 14 crops and 38 diseases (Apple, Strawberry, Tomato, Potato, Corn, Grape, Peach, Pepper, Orange, Soybean, Squash, etc.).
   - Distinguishes lesions, concentric bullseye rings, water-soaked dark gray blotches, rust pustules, and leaf scorch.
   - Dual-action treatment protocol:
     - **Organic & Low-Cost Solutions** (Neem oil, pruning, wood ash, milk spray, bio-control).
     - **Targeted Chemical Sprays** with exact dosages (Copper Oxychloride, Mancozeb, Ridomil MZ).

3. **🗺️ Hyper-Local Outbreak Radar (< 2 km Radius)**
   - Live visual radar screen tracking disease clusters in neighboring plots (< 2 hectares).
   - Early warning notifications before wind-borne spores (e.g. Late Blight, Rust) damage adjacent fields.
   - 1-Click "Broadcast Alert" to notify surrounding farmers.

4. **🔊 Multilingual & Audio Voice Assistant**
   - 1-Click English ↔ Hindi (हिंदी) toggle.
   - Audio text-to-speech reads diagnosis and treatment aloud for farmers.

5. **🧠 Teach AI / Reference Training System**
   - Upload new leaf disease references and symptoms.
   - Immediate few-shot conditioning into the local AI model.

---

## 🛠️ Tech Stack & Architecture

- **Backend**: FastAPI (Python 3.9+), Uvicorn, Pillow, PyTorch.
- **Local AI Runtimes**: Ollama with **Moondream** (Vision Analysis) + **LLaMA-3** (Agronomy Pathology & Diagnostic Formatting).
- **Frontend**: Clean Modern Single-Page Application (HTML5, Vanilla JavaScript, CSS3 with dark agricultural aesthetic).

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.9+
- Ollama running locally (`ollama run moondream` and `ollama run llama3`)

### 2. Run Application
```bash
# Clone the repository
git clone https://github.com/saketanand200911/hackdelhi.git
cd hackdelhi

# Install dependencies
pip install fastapi uvicorn pillow torch torchvision

# Start the server
python3 app.py
```

Open your browser at **`http://localhost:8080`**.
