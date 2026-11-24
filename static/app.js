// VoiceKeep Ag / LeafGuard AI - Client Logic

let currentStream = null;
let currentFacingMode = "environment"; // default to back camera for plants
let capturedBase64 = null;
let currentDiagnosis = null;
let isHindi = false;

// DOM Elements
const webcam = document.getElementById("webcam");
const canvas = document.getElementById("photo-canvas");
const previewContainer = document.getElementById("captured-preview");
const previewImg = document.getElementById("preview-img");
const captureBtn = document.getElementById("capture-btn");
const startCamBtn = document.getElementById("start-cam-btn");
const flipCamBtn = document.getElementById("flip-cam-btn");
const cameraStateBadge = document.getElementById("camera-state");
const scanLaser = document.getElementById("scan-laser");
const reticle = document.getElementById("reticle");

function selectCropPill(btn, cropName) {
  document.querySelectorAll(".crop-pill").forEach(p => p.classList.remove("active"));
  btn.classList.add("active");
  document.getElementById("crop-hint").value = cropName;
}

// Initial Setup
window.addEventListener("DOMContentLoaded", () => {
  checkBackendHealth();
  loadReferences();
  loadOutbreaks();
  loadHistory();
});

// Tab Switching
function switchTab(tabId) {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.tab === tabId);
  });
  document.querySelectorAll(".tab-pane").forEach(pane => {
    pane.classList.toggle("active", pane.id === `tab-${tabId}`);
  });

  if (tabId === "outbreak") {
    loadOutbreaks();
  } else if (tabId === "training") {
    loadReferences();
  } else if (tabId === "history") {
    loadHistory();
  }
}

// Toast Notifications
function showToast(message, isError = false) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.style.borderColor = isError ? "#ef4444" : "#10b981";
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3500);
}

// System Health Check
async function checkBackendHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    const statusElem = document.getElementById("system-status");
    if (data.ollama_available) {
      statusElem.innerHTML = `<span class="status-dot"></span><span>Local AI Online: ${data.vision_model} + ${data.llm_model}</span>`;
    } else {
      statusElem.innerHTML = `<span class="status-dot" style="background:#f59e0b;box-shadow:0 0 8px #f59e0b;"></span><span>Pixel Vision Engine Active</span>`;
    }
  } catch (e) {
    console.warn("Health check error:", e);
  }
}

// Camera Management
async function startCamera() {
  if (currentStream) {
    currentStream.getTracks().forEach(t => t.stop());
  }

  try {
    const constraints = {
      video: {
        facingMode: currentFacingMode,
        width: { ideal: 1280 },
        height: { ideal: 960 }
      },
      audio: false
    };

    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    currentStream = stream;
    webcam.srcObject = stream;
    webcam.style.display = "block";
    previewContainer.style.display = "none";
    
    captureBtn.disabled = false;
    startCamBtn.innerHTML = `<span class="btn-icon">🛑</span><span>${isHindi ? "कैमरा बंद करें" : "Stop Camera"}</span>`;
    startCamBtn.onclick = stopCamera;
    flipCamBtn.style.display = "inline-flex";
    cameraStateBadge.textContent = "Live Stream";
    cameraStateBadge.style.color = "#34d399";
    reticle.style.display = "block";
  } catch (err) {
    console.error("Camera access error:", err);
    showToast(isHindi ? "कैमरा शुरू नहीं हो पाया। कृपया अनुमति दें।" : "Unable to open camera. Check permissions.", true);
  }
}

function stopCamera() {
  if (currentStream) {
    currentStream.getTracks().forEach(t => t.stop());
    currentStream = null;
  }
  webcam.srcObject = null;
  captureBtn.disabled = true;
  startCamBtn.innerHTML = `<span class="btn-icon">📹</span><span>${isHindi ? "कैमरा शुरू करें" : "Open Camera"}</span>`;
  startCamBtn.onclick = startCamera;
  cameraStateBadge.textContent = "Standby";
  cameraStateBadge.style.color = "var(--text-muted)";
}

function flipCamera() {
  currentFacingMode = currentFacingMode === "environment" ? "user" : "environment";
  startCamera();
}

// File Upload Handler
function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    capturedBase64 = e.target.result;
    previewImg.src = capturedBase64;
    previewContainer.style.display = "block";
    webcam.style.display = "none";
    stopCamera();
    cameraStateBadge.textContent = "Image Loaded";
    reticle.style.display = "none";

    // Auto-diagnose on upload
    diagnoseCurrentLeaf();
  };
  reader.readAsDataURL(file);
}

// Capture from Live Video
function captureAndDiagnose() {
  if (!currentStream) return;

  canvas.width = webcam.videoWidth || 640;
  canvas.height = webcam.videoHeight || 480;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(webcam, 0, 0, canvas.width, canvas.height);

  capturedBase64 = canvas.toDataURL("image/jpeg", 0.9);
  previewImg.src = capturedBase64;
  previewContainer.style.display = "block";
  webcam.style.display = "none";
  reticle.style.display = "none";

  diagnoseCurrentLeaf();
}

// Diagnosis API Execution
async function diagnoseCurrentLeaf() {
  if (!capturedBase64) {
    showToast(isHindi ? "कृपया पहले पत्ती की फोटो लें!" : "Please take or upload a leaf photo first!", true);
    return;
  }

  // UI state
  document.getElementById("result-empty").style.display = "none";
  document.getElementById("result-content").style.display = "none";
  document.getElementById("result-loading").style.display = "block";
  document.getElementById("speak-btn").style.display = "none";
  scanLaser.style.display = "block";

  const cropHint = document.getElementById("crop-hint").value.trim();
  const farmerNotes = document.getElementById("farmer-notes").value.trim();

  // Progress messages sequence
  const titleElem = document.getElementById("loading-step-title");
  const descElem = document.getElementById("loading-step-desc");

  const progressInterval = setInterval(() => {
    if (titleElem.textContent.includes("Analyzing Leaf")) {
      titleElem.textContent = isHindi ? "रंग, धब्बे व सूखेपन का विश्लेषण..." : "Inspecting Discoloration & Necrotic Spots...";
      descElem.textContent = isHindi ? "लोकल विज़न AI पत्ती के लक्षणों का अध्ययन कर रहा है..." : "Vision model scanning for chlorosis, lesions, and curling...";
    } else {
      titleElem.textContent = isHindi ? "कृषि निदान व उपचार रिपोर्ट तैयार हो रही है..." : "Generating Hyper-Local Agronomy Protocol...";
      descElem.textContent = isHindi ? "LLaMA-3 एवं किसान रेफरेंस डाटा से मिलान हो रहा है..." : "Evaluating smallholder treatment solutions and neighborhood alerts...";
    }
  }, 2200);

  try {
    const res = await fetch("/api/diagnose", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image_base64: capturedBase64,
        crop_hint: cropHint,
        farmer_notes: farmerNotes
      })
    });

    clearInterval(progressInterval);
    scanLaser.style.display = "none";

    if (!res.ok) {
      throw new Error(`Diagnosis server error (${res.status})`);
    }

    const data = await res.json();
    currentDiagnosis = data;
    renderDiagnosis(data);
    showToast(isHindi ? "जांच पूरी हुई!" : "Diagnosis Complete!");
    loadHistory(); // refresh history table
  } catch (err) {
    clearInterval(progressInterval);
    scanLaser.style.display = "none";
    console.error("Diagnosis error:", err);
    document.getElementById("result-loading").style.display = "none";
    document.getElementById("result-empty").style.display = "block";
    showToast(isHindi ? "जांच में त्रुटि हुई, पुनः प्रयास करें।" : "Diagnosis failed. Please try again.", true);
  }
}

// Render Diagnosis Results to UI
function renderDiagnosis(data) {
  document.getElementById("result-loading").style.display = "none";
  document.getElementById("result-content").style.display = "block";
  document.getElementById("speak-btn").style.display = "flex";

  // Condition & Crop
  document.getElementById("diag-condition").textContent = data.condition || "Leaf Condition";
  document.getElementById("diag-crop").textContent = `${isHindi ? "फसल" : "Crop"}: ${data.crop || "Identified Plant"}`;
  document.getElementById("diag-confidence").textContent = data.confidence || "90%";

  // Severity Pill
  const severityPill = document.getElementById("diag-severity");
  const sev = (data.severity || "Moderate").toLowerCase();
  severityPill.textContent = data.severity || "Moderate";
  severityPill.className = `severity-pill ${sev}`;

  // Outbreak Risk Pill
  const riskPill = document.getElementById("diag-outbreak-risk");
  const risk = data.outbreak_risk || "Moderate";
  riskPill.textContent = `${risk} Risk Outbreak`;

  // Hindi Box
  const hindiBox = document.getElementById("hindi-summary-text");
  hindiBox.textContent = data.hindi_summary || "पत्ती की जांच पूरी हो गई है। नीचे दिए गए जैविक व रासायनिक उपायों को देखें।";

  // Visual summary
  document.getElementById("diag-visual-summary").textContent = data.visual_summary || "Detailed leaf visual breakdown.";

  // Metric Bars
  const metrics = data.pixel_metrics || { healthy_green_pct: 65, pale_yellow_pct: 20, brown_dried_pct: 15 };
  document.getElementById("bar-green").style.width = `${metrics.healthy_green_pct}%`;
  document.getElementById("val-green").textContent = `${metrics.healthy_green_pct}%`;
  document.getElementById("bar-yellow").style.width = `${metrics.pale_yellow_pct}%`;
  document.getElementById("val-yellow").textContent = `${metrics.pale_yellow_pct}%`;
  document.getElementById("bar-brown").style.width = `${metrics.brown_dried_pct}%`;
  document.getElementById("val-brown").textContent = `${metrics.brown_dried_pct}%`;

  // Symptoms List
  const symptomsList = document.getElementById("diag-symptoms");
  symptomsList.innerHTML = "";
  (data.symptoms || []).forEach(sym => {
    const li = document.createElement("li");
    li.textContent = sym;
    symptomsList.appendChild(li);
  });

  // Organic Treatment
  const organicList = document.getElementById("diag-organic-list");
  organicList.innerHTML = "";
  (data.organic_treatment || []).forEach(item => {
    const li = document.createElement("li");
    li.textContent = typeof item === "string" ? item : `${item.Method || ""}: ${item.Reason || ""}`;
    organicList.appendChild(li);
  });

  // Chemical Treatment
  const chemList = document.getElementById("diag-chemical-list");
  chemList.innerHTML = "";
  (data.chemical_treatment || []).forEach(item => {
    const li = document.createElement("li");
    li.textContent = typeof item === "string" ? item : `${item.Product || ""}: ${item.Reason || ""}`;
    chemList.appendChild(li);
  });

  // Outbreak Warning Text
  document.getElementById("diag-neighbor-alert").textContent = data.neighbor_alert || "Monitor surrounding fields for similar leaf symptoms.";
}

// Audio Speech Readout (TTS)
function speakDiagnosis() {
  if (!currentDiagnosis) return;
  if (!("speechSynthesis" in window)) {
    showToast("Speech synthesis not supported in this browser.", true);
    return;
  }

  window.speechSynthesis.cancel(); // stop any current speech

  let textToSpeak = "";
  let lang = "en-IN";

  if (isHindi && currentDiagnosis.hindi_summary) {
    textToSpeak = currentDiagnosis.hindi_summary;
    lang = "hi-IN";
  } else {
    textToSpeak = `Diagnosis: ${currentDiagnosis.condition} on ${currentDiagnosis.crop}. Severity is ${currentDiagnosis.severity}. ${currentDiagnosis.visual_summary}. Immediate action: ${currentDiagnosis.organic_treatment ? currentDiagnosis.organic_treatment[0] : ''}.`;
    lang = "en-US";
  }

  const utterance = new SpeechSynthesisUtterance(textToSpeak);
  utterance.lang = lang;
  utterance.rate = 0.95;
  window.speechSynthesis.speak(utterance);
}

// Broadcast Current Diagnosis to Radar
async function broadcastCurrentScan() {
  if (!currentDiagnosis) return;

  try {
    const res = await fetch("/api/outbreaks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        crop: currentDiagnosis.crop || "Unknown Crop",
        disease: currentDiagnosis.condition || "Leaf Outbreak",
        distance: "Your Field (<2 ha)",
        plot_size: "1.0 ha",
        risk_level: currentDiagnosis.outbreak_risk || "High",
        advisory: currentDiagnosis.neighbor_alert || "Infection reported in nearby plot."
      })
    });
    const data = await res.json();
    showToast(isHindi ? "पड़ोसी किसानों को चेतावनी प्रसारित कर दी गई!" : "Outbreak broadcasted to neighborhood radar!");
    switchTab("outbreak");
  } catch (e) {
    showToast("Failed to broadcast alert.", true);
  }
}

// TAB 2: Outbreak Radar Logic
async function loadOutbreaks() {
  try {
    const res = await fetch("/api/outbreaks");
    const alerts = await res.json();
    renderOutbreakRadar(alerts);
    renderOutbreakFeed(alerts);
  } catch (e) {
    console.error("Failed to load outbreaks:", e);
  }
}

function renderOutbreakRadar(alerts) {
  const container = document.getElementById("radar-pins");
  container.innerHTML = "";

  // Map alerts onto the radar circular coords (center is 190px, 190px)
  const centerX = 190;
  const centerY = 190;

  alerts.forEach((alt, idx) => {
    const blip = document.createElement("div");
    blip.className = "radar-blip";

    // distribute visually on radar concentric rings
    const angle = (idx * 115 + 45) * (Math.PI / 180);
    const radius = 60 + (idx * 45) % 110;

    const x = centerX + Math.cos(angle) * radius;
    const y = centerY + Math.sin(angle) * radius;

    blip.style.left = `${x}px`;
    blip.style.top = `${y}px`;

    const colorClass = alt.risk_level === "Critical" ? "red" : (alt.risk_level === "High" ? "orange" : "yellow");

    blip.innerHTML = `
      <div class="blip-dot ${colorClass}"></div>
      <div class="blip-name">${alt.crop}: ${alt.disease.split(" ")[0]} (${alt.distance.split(" ")[0]})</div>
    `;
    blip.onclick = () => showToast(`🚨 ${alt.crop} - ${alt.disease} (${alt.distance}): ${alt.advisory}`);
    container.appendChild(blip);
  });
}

function renderOutbreakFeed(alerts) {
  const feed = document.getElementById("alerts-feed");
  feed.innerHTML = "";

  alerts.forEach(alt => {
    const item = document.createElement("div");
    item.className = `alert-item ${alt.risk_level}`;
    item.innerHTML = `
      <div class="alert-top">
        <span class="alert-crop-name">${alt.crop} • ${alt.disease}</span>
        <span class="alert-time">${alt.timestamp}</span>
      </div>
      <div class="alert-meta">📍 ${alt.distance} &nbsp;|&nbsp; Plot: ${alt.plot_size} &nbsp;|&nbsp; Risk: <strong>${alt.risk_level}</strong></div>
      <p class="alert-desc">${alt.advisory}</p>
    `;
    feed.appendChild(item);
  });
}

async function submitCustomAlert() {
  const crop = document.getElementById("alert-crop").value.trim();
  const disease = document.getElementById("alert-disease").value.trim();
  const distance = document.getElementById("alert-distance").value.trim() || "Within 1km";
  const risk = document.getElementById("alert-risk").value;
  const advisory = document.getElementById("alert-advisory").value.trim();

  if (!crop || !disease || !advisory) {
    showToast(isHindi ? "कृपया सभी विवरण भरें" : "Please fill in all alert fields", true);
    return;
  }

  try {
    await fetch("/api/outbreaks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        crop, disease, distance, plot_size: "1.5 ha", risk_level: risk, advisory
      })
    });
    document.getElementById("alert-crop").value = "";
    document.getElementById("alert-disease").value = "";
    document.getElementById("alert-advisory").value = "";
    showToast(isHindi ? "अलर्ट सफलतापूर्वक प्रसारित किया गया!" : "Alert broadcasted to neighborhood!");
    loadOutbreaks();
  } catch (e) {
    showToast("Error posting alert", true);
  }
}

// TAB 3: Reference Training Knowledge Base
let refImageBase64 = null;

function handleRefImageSelect(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    refImageBase64 = e.target.result;
    document.getElementById("ref-preview-elem").src = refImageBase64;
    document.getElementById("ref-img-preview").style.display = "block";
  };
  reader.readAsDataURL(file);
}

async function handleReferenceSubmit(event) {
  event.preventDefault();
  const crop = document.getElementById("ref-crop").value.trim();
  const disease = document.getElementById("ref-disease").value.trim();
  const symptoms = document.getElementById("ref-symptoms").value.trim();
  const treatment = document.getElementById("ref-treatment").value.trim();
  const risk = document.getElementById("ref-risk").value;

  const btn = document.getElementById("save-ref-btn");
  btn.disabled = true;
  btn.textContent = isHindi ? "सहेजा जा रहा है..." : "Saving Reference...";

  try {
    const res = await fetch("/api/references", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        crop,
        disease,
        visual_symptoms: symptoms,
        treatment,
        risk_level: risk,
        image_base64: refImageBase64
      })
    });

    if (!res.ok) throw new Error("Save reference error");

    document.getElementById("ref-form").reset();
    document.getElementById("ref-img-preview").style.display = "none";
    refImageBase64 = null;

    showToast(isHindi ? "रेफरेंस AI मॉडल में जोड़ दिया गया!" : "New Reference added to Local AI Model!");
    loadReferences();
  } catch (e) {
    showToast("Error saving reference", true);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span class="btn-icon">💾</span><span>${isHindi ? "AI नॉलेज बेस में सेव करें" : "Save Reference to AI Knowledge Base"}</span>`;
  }
}

async function loadReferences() {
  try {
    const res = await fetch("/api/references");
    const refs = await res.json();
    renderReferences(refs);
    document.getElementById("ref-count-badge").textContent = refs.length;
  } catch (e) {
    console.error("Error loading references:", e);
  }
}

function renderReferences(refs) {
  const container = document.getElementById("ref-items-container");
  container.innerHTML = "";

  if (refs.length === 0) {
    container.innerHTML = `<p style="color:var(--text-dim);text-align:center;padding:30px;">No custom references trained yet.</p>`;
    return;
  }

  refs.forEach(r => {
    const card = document.createElement("div");
    card.className = "ref-card-item";
    card.innerHTML = `
      <div class="ref-card-header">
        <div>
          <span class="ref-crop-badge">${r.crop}</span>
          <h4 class="ref-title">${r.disease}</h4>
        </div>
        <button class="ref-del-btn" onclick="deleteReference('${r.id}')" title="Delete reference">🗑️</button>
      </div>
      <p class="ref-symptoms-text"><strong>${isHindi ? "दृश्य लक्षण:" : "Visual Clues:"}</strong> ${r.visual_symptoms}</p>
      <div class="ref-treatment-box">
        <strong>${isHindi ? "उपचार:" : "Treatment:"}</strong> ${r.treatment}
      </div>
    `;
    container.appendChild(card);
  });
}

async function deleteReference(refId) {
  if (!confirm(isHindi ? "क्या आप इस रेफरेंस को हटाना चाहते हैं?" : "Delete this reference sample?")) return;
  try {
    await fetch(`/api/references/${refId}`, { method: "DELETE" });
    showToast(isHindi ? "रेफरेंस हटा दिया गया" : "Reference deleted");
    loadReferences();
  } catch (e) {
    showToast("Error deleting reference", true);
  }
}

// TAB 4: History Table
async function loadHistory() {
  try {
    const res = await fetch("/api/history");
    const history = await res.json();
    renderHistory(history);
  } catch (e) {
    console.error("Error loading history:", e);
  }
}

function renderHistory(history) {
  const tbody = document.getElementById("history-table-body");
  tbody.innerHTML = "";

  if (!history || history.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="table-empty">No scan records found yet.</td></tr>`;
    return;
  }

  history.forEach(item => {
    const tr = document.createElement("tr");
    const timeFormatted = new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const sevClass = (item.severity || "Moderate").toLowerCase();

    tr.innerHTML = `
      <td style="font-family:var(--font-mono);">${timeFormatted}</td>
      <td><strong>${item.crop}</strong></td>
      <td>${item.condition}</td>
      <td><span class="severity-pill ${sevClass}">${item.severity}</span></td>
      <td>${item.outbreak_risk}</td>
      <td style="max-width:280px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${item.visual_summary}</td>
      <td style="font-family:var(--font-mono);color:var(--primary-text);">${item.processing_seconds}s</td>
    `;
    tbody.appendChild(tr);
  });
}

// Multilingual Hindi Toggle
function toggleLanguage() {
  isHindi = !isHindi;
  document.getElementById("lang-label").textContent = isHindi ? "View in English" : "हिंदी में देखें";

  document.querySelectorAll("[data-en]").forEach(el => {
    el.textContent = isHindi ? el.dataset.hi : el.dataset.en;
  });

  showToast(isHindi ? "भाषा हिंदी में बदली गई" : "Language switched to English");
}
