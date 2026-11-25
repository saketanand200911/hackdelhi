// VoiceKeep Ag / LeafGuard AI - Client Logic

let currentStream = null;
let currentFacingMode = "environment"; // default to back camera for plants
let capturedBase64 = null;
let currentDiagnosis = null;
let isHindi = false;
let currentLang = "en";
let farmerCoords = null; // { lat, lon, location_name }
let farmerSenderId = sessionStorage.getItem("leafguard_sender_id");
if (!farmerSenderId) {
  farmerSenderId = "farmer_" + Math.random().toString(36).slice(2, 10);
  sessionStorage.setItem("leafguard_sender_id", farmerSenderId);
}
let lastSeenOutbreakTs = 0;
let latestOutbreaks = [];
let googleMap = null;
let googleMapCircle = null;
let googleMapMarkers = [];
let mapsScriptLoading = false;
let mapsApiKey = "";
let currentOutbreakView = "radar";

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
  const badge = document.getElementById("active-crop-badge");
  if (badge) {
    badge.innerText = cropName ? `Locked: ${cropName}` : "🌱 Auto-Detect";
    badge.style.borderColor = cropName ? "var(--color-primary)" : "var(--color-border)";
    badge.style.color = cropName ? "var(--color-primary-light)" : "var(--color-text-muted)";
  }
}

// Initial Setup
window.addEventListener("DOMContentLoaded", () => {
  checkBackendHealth();
  loadAppConfig();
  loadReferences();
  loadOutbreaks();
  loadHistory();
  startOutbreakPolling();
  detectLocationAndWeather(true);
  if ("speechSynthesis" in window) {
    window.speechSynthesis.getVoices();
    window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
  }
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
    if (currentOutbreakView === "gmap" && !googleMap && mapsApiKey) {
      initGoogleMap();
    }
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

// Capture from Live Video (center-cropped to reticle for clean leaf focus)
function captureAndDiagnose() {
  if (!currentStream) return;

  const vw = webcam.videoWidth || 640;
  const vh = webcam.videoHeight || 480;
  const cropSize = Math.round(Math.min(vw, vh) * 0.78);
  const sx = Math.round((vw - cropSize) / 2);
  const sy = Math.round((vh - cropSize) / 2);

  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(webcam, sx, sy, cropSize, cropSize, 0, 0, 512, 512);

  capturedBase64 = canvas.toDataURL("image/jpeg", 0.92);
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
  const cropStr = data.crop && data.crop !== "—"
    ? `${isHindi ? "फसल" : "Crop"}: ${data.crop}`
    : "";
  const modelStr = data.neural_similarity ? ` • 🧠 Trained Model: ${data.neural_similarity}%` : "";
  document.getElementById("diag-crop").textContent = cropStr + modelStr;
  document.getElementById("diag-confidence").textContent = data.confidence || "—";

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

  // Symptoms List — for a detected leaf this is the agronomic breakdown, and it
  // always ends with the real top-5 probabilities from the model.
  const symptomsList = document.getElementById("diag-symptoms");
  symptomsList.innerHTML = "";
  (data.symptoms || []).forEach(sym => {
    if (!sym) return;
    const li = document.createElement("li");
    li.textContent = sym;
    symptomsList.appendChild(li);
  });
  if (data.top_k && data.top_k.length > 1) {
    const li = document.createElement("li");
    const label = data.detected
      ? (isHindi ? "अन्य संभावनाएँ:" : "Other possibilities:")
      : (isHindi ? "सबसे नज़दीकी मेल (सीमा से नीचे):" : "Closest known matches (all below threshold):");
    // Probabilities saturate once a leaf is clearly one class, so alternatives
    // are shown by visual similarity to that disease's reference photos.
    li.innerHTML = `<strong>${label}</strong> ` + data.top_k.slice(1)
      .map(k => `${k.crop} ${k.condition} <em>${Math.round(k.cosine * 100)}% match</em>`)
      .join(" · ");
    symptomsList.appendChild(li);
  }

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

// Audio Speech Readout (TTS) - macOS/Chrome reliable implementation (supports 22 Indian languages)
window._activeUtterance = null;
async function speakDiagnosis() {
  if (!currentDiagnosis) {
    showToast(isHindi ? "पहले पत्ती की जांच करें!" : "Please scan a leaf first!", true);
    return;
  }
  if (!("speechSynthesis" in window)) {
    showToast("Speech synthesis not supported in this browser.", true);
    return;
  }

  const speakBtn = document.getElementById("speak-btn");
  if (window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
    window._activeUtterance = null;
    if (speakBtn) speakBtn.innerHTML = `<span class="btn-icon">🔊</span> <span>${isHindi ? "सुनें" : "Listen"}</span>`;
    return;
  }

  window.speechSynthesis.cancel();

  const firstOrganic = currentDiagnosis.organic_treatment && currentDiagnosis.organic_treatment[0] ? currentDiagnosis.organic_treatment[0] : "";
  const enSummary = `Diagnosis: ${currentDiagnosis.condition} on ${currentDiagnosis.crop}. Severity is ${currentDiagnosis.severity}. ${currentDiagnosis.visual_summary}. ${firstOrganic ? "Recommended action: " + firstOrganic : ""}`;

  let textToSpeak = enSummary;
  let targetLang = currentLang === "en" ? "en-IN" : `${currentLang}-IN`;

  if (currentLang === "hi" && currentDiagnosis.hindi_summary) {
    textToSpeak = currentDiagnosis.hindi_summary;
    targetLang = "hi-IN";
  } else if (currentLang !== "en") {
    const translated = await translateTextsBatch([enSummary], currentLang);
    if (translated && translated[0]) {
      textToSpeak = translated[0];
    }
  }

  // Delay slightly after cancel() so Chrome/macOS does not drop the new utterance
  setTimeout(() => {
    try {
      const utterance = new SpeechSynthesisUtterance(textToSpeak);
      utterance.lang = targetLang;
      utterance.rate = 0.95;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      const voices = window.speechSynthesis.getVoices() || [];
      const langPrefix = targetLang.split("-")[0].toLowerCase();
      const matchedVoice =
        voices.find(v => v.lang && v.lang.toLowerCase() === targetLang.toLowerCase()) ||
        voices.find(v => v.lang && v.lang.toLowerCase().startsWith(langPrefix)) ||
        voices.find(v => v.default);
      if (matchedVoice) {
        utterance.voice = matchedVoice;
      }

      if (speakBtn) speakBtn.innerHTML = `<span class="btn-icon">⏹️</span> <span>${isHindi ? "रुकें" : "Stop"}</span>`;
      utterance.onend = () => {
        window._activeUtterance = null;
        if (speakBtn) speakBtn.innerHTML = `<span class="btn-icon">🔊</span> <span>${isHindi ? "सुनें" : "Listen"}</span>`;
      };
      utterance.onerror = () => {
        window._activeUtterance = null;
        if (speakBtn) speakBtn.innerHTML = `<span class="btn-icon">🔊</span> <span>${isHindi ? "सुनें" : "Listen"}</span>`;
      };

      window._activeUtterance = utterance;
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
      }
      window.speechSynthesis.speak(utterance);
      showToast(isHindi ? "रिपोर्ट पढ़ी जा रही है..." : "Reading diagnosis aloud...");
    } catch (err) {
      console.error("TTS error:", err);
      showToast("Audio playback failed on this browser.", true);
    }
  }, 70);
}

// Broadcast Current Diagnosis to Radar & Other Farmers
async function broadcastCurrentScan() {
  if (!currentDiagnosis) return;

  try {
    const res = await fetch("/api/outbreaks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        crop: currentDiagnosis.crop || "Unknown Crop",
        disease: currentDiagnosis.condition || "Leaf Outbreak",
        distance: farmerCoords && farmerCoords.location_name ? farmerCoords.location_name : "Your Field (<2 ha)",
        plot_size: "1.0 ha",
        risk_level: currentDiagnosis.outbreak_risk || "High",
        advisory: currentDiagnosis.neighbor_alert || "Infection reported in nearby plot.",
        lat: farmerCoords ? farmerCoords.lat : null,
        lon: farmerCoords ? farmerCoords.lon : null,
        location_name: farmerCoords ? farmerCoords.location_name : "",
        sender_id: farmerSenderId
      })
    });
    const data = await res.json();
    if (data && data.alert && data.alert.created_ts) {
      lastSeenOutbreakTs = Math.max(lastSeenOutbreakTs, data.alert.created_ts);
    }
    showToast(isHindi ? "पड़ोसी किसानों को चेतावनी प्रसारित कर दी गई!" : "Outbreak broadcasted to all nearby farmers!");
    switchTab("outbreak");
    if (data && data.alert) {
      showLiveAlertModal(data.alert);
    }
  } catch (e) {
    showToast("Failed to broadcast alert.", true);
  }
}

// TAB 2: Outbreak Radar Logic
async function loadOutbreaks() {
  try {
    const res = await fetch("/api/outbreaks");
    const alerts = await res.json();
    latestOutbreaks = alerts || [];
    latestOutbreaks.forEach(a => {
      if (a.created_ts && a.created_ts > lastSeenOutbreakTs) {
        lastSeenOutbreakTs = a.created_ts;
      }
    });
    renderOutbreakRadar(latestOutbreaks);
    renderOutbreakFeed(latestOutbreaks);
    updateGoogleMapMarkers(latestOutbreaks);
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

async function renderOutbreakFeed(alerts) {
  const feed = document.getElementById("alerts-feed");
  feed.innerHTML = "";

  const targetLang = currentLang;
  let translatedItems = null;
  if (targetLang !== "en" && alerts.length > 0) {
    const flat = [];
    alerts.forEach(a => {
      flat.push(a.crop || "", a.disease || "", a.location_name || a.distance || "", a.risk_level || "", a.advisory || "");
    });
    const res = await translateTextsBatch(flat, targetLang);
    if (res && res.length === flat.length) {
      translatedItems = res;
    }
  }

  alerts.forEach((alt, idx) => {
    const item = document.createElement("div");
    item.className = `alert-item ${alt.risk_level}`;
    const base = idx * 5;
    const cropTxt = translatedItems ? translatedItems[base] : alt.crop;
    const disTxt = translatedItems ? translatedItems[base + 1] : alt.disease;
    const locTxt = translatedItems ? translatedItems[base + 2] : (alt.location_name || alt.distance);
    const riskTxt = translatedItems ? translatedItems[base + 3] : alt.risk_level;
    const advTxt = translatedItems ? translatedItems[base + 4] : alt.advisory;
    const btnLabel = targetLang === "hi" ? "🌐 अनुवाद करें" : "🌐 Translate";

    item.innerHTML = `
      <div class="alert-top">
        <span class="alert-crop-name" id="alert-title-${idx}">${cropTxt} • ${disTxt}</span>
        <span class="alert-time">${alt.timestamp}</span>
      </div>
      <div class="alert-meta" id="alert-meta-${idx}">📍 ${locTxt} &nbsp;|&nbsp; Plot: ${alt.plot_size} &nbsp;|&nbsp; Risk: <strong>${riskTxt}</strong></div>
      <p class="alert-desc" id="alert-desc-${idx}">${advTxt}</p>
      <div class="alert-translate-row">
        <button type="button" class="btn-alert-translate" onclick="translateSingleAlert(${idx}, this)">${btnLabel}</button>
      </div>
    `;
    feed.appendChild(item);
  });
}

async function translateSingleAlert(idx, btn) {
  const alt = latestOutbreaks[idx];
  if (!alt) return;
  const targetLang = currentLang === "en" ? "hi" : currentLang;
  if (btn) btn.disabled = true;
  const translated = await translateTextsBatch(
    [alt.crop || "", alt.disease || "", alt.location_name || alt.distance || "", alt.risk_level || "", alt.advisory || ""],
    targetLang
  );
  if (translated && translated.length === 5) {
    const tEl = document.getElementById(`alert-title-${idx}`);
    const mEl = document.getElementById(`alert-meta-${idx}`);
    const dEl = document.getElementById(`alert-desc-${idx}`);
    if (tEl) tEl.textContent = `${translated[0]} • ${translated[1]}`;
    if (mEl) mEl.innerHTML = `📍 ${translated[2]} &nbsp;|&nbsp; Plot: ${alt.plot_size} &nbsp;|&nbsp; Risk: <strong>${translated[3]}</strong>`;
    if (dEl) dEl.textContent = translated[4];
  }
  if (btn) btn.disabled = false;
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
    const res = await fetch("/api/outbreaks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        crop,
        disease,
        distance,
        plot_size: "1.5 ha",
        risk_level: risk,
        advisory,
        lat: farmerCoords ? farmerCoords.lat : null,
        lon: farmerCoords ? farmerCoords.lon : null,
        location_name: farmerCoords ? farmerCoords.location_name : "",
        sender_id: farmerSenderId
      })
    });
    const data = await res.json();
    if (data && data.alert && data.alert.created_ts) {
      lastSeenOutbreakTs = Math.max(lastSeenOutbreakTs, data.alert.created_ts);
    }
    document.getElementById("alert-crop").value = "";
    document.getElementById("alert-disease").value = "";
    document.getElementById("alert-advisory").value = "";
    showToast(isHindi ? "अलर्ट सफलतापूर्वक प्रसारित किया गया!" : "Alert broadcasted to all farmers!");
    loadOutbreaks();
    if (data && data.alert) {
      showLiveAlertModal(data.alert);
    }
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

// Multilingual Support (English + All 22 Official Languages of India)
async function translateTextsBatch(texts, targetLang) {
  if (!texts || texts.length === 0 || targetLang === "en") return texts;
  try {
    const res = await fetch("/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texts, target_lang: targetLang })
    });
    const data = await res.json();
    return data.translations || texts;
  } catch (e) {
    console.warn("Translation error:", e);
    return texts;
  }
}

async function changeLanguage(lang) {
  currentLang = lang || "en";
  isHindi = currentLang === "hi";
  const selectEl = document.getElementById("lang-select");
  if (selectEl && selectEl.value !== currentLang) selectEl.value = currentLang;

  const elements = Array.from(document.querySelectorAll("[data-en]"));
  if (currentLang === "en") {
    elements.forEach(el => {
      el.textContent = el.dataset.en;
    });
    showToast("Language switched to English");
    return;
  }

  if (currentLang === "hi") {
    const missingIdx = [];
    const missingTexts = [];
    elements.forEach((el, idx) => {
      if (el.dataset.hi) {
        el.textContent = el.dataset.hi;
      } else {
        missingIdx.push(idx);
        missingTexts.push(el.dataset.en);
      }
    });
    if (missingTexts.length > 0) {
      const translated = await translateTextsBatch(missingTexts, "hi");
      missingIdx.forEach((elIdx, i) => {
        elements[elIdx].textContent = translated[i] || elements[elIdx].dataset.en;
      });
    }
    await translateDynamicContent("hi");
    showToast("भाषा हिन्दी में बदली गई");
    return;
  }

  showToast("Translating interface...");
  const sourceTexts = elements.map(el => el.dataset.en);
  // Chunk in batches of 40 so translation stays fast
  for (let i = 0; i < sourceTexts.length; i += 40) {
    const chunk = sourceTexts.slice(i, i + 40);
    const translated = await translateTextsBatch(chunk, currentLang);
    translated.forEach((t, j) => {
      if (elements[i + j]) elements[i + j].textContent = t || elements[i + j].dataset.en;
    });
  }
  await translateDynamicContent(currentLang);
  const selectedLabel = selectEl ? selectEl.options[selectEl.selectedIndex].text : currentLang;
  showToast(`Language: ${selectedLabel}`);
}

async function translateDynamicContent(lang) {
  if (latestOutbreaks && latestOutbreaks.length > 0) {
    await renderOutbreakFeed(latestOutbreaks);
  }
  if (currentDiagnosis && lang !== "en") {
    const condEl = document.getElementById("diag-condition");
    const visEl = document.getElementById("diag-visual-summary");
    const nEl = document.getElementById("diag-neighbor-alert");
    const batch = [
      currentDiagnosis.condition || "",
      currentDiagnosis.visual_summary || "",
      currentDiagnosis.neighbor_alert || ""
    ];
    const tr = await translateTextsBatch(batch, lang);
    if (tr && tr.length === 3) {
      if (condEl) condEl.textContent = tr[0];
      if (visEl) visEl.textContent = tr[1];
      if (nEl) nEl.textContent = tr[2];
    }
  }
  const riskChips = Array.from(document.querySelectorAll("#weather-risk-list .risk-chip"));
  if (riskChips.length > 0 && lang !== "en") {
    const texts = riskChips.map(c => c.innerText);
    const tr = await translateTextsBatch(texts, lang);
    riskChips.forEach((c, i) => {
      if (tr[i]) c.querySelector(".risk-chip-meta").textContent = tr[i];
    });
  }
}

// App Config (Google Maps API key)
async function loadAppConfig() {
  try {
    const res = await fetch("/api/config");
    const cfg = await res.json();
    mapsApiKey = cfg.maps_api_key || "";
  } catch (e) {
    console.warn("Failed to load config:", e);
  }
}

// GPS Location + Live Weather & Disease Risk Dashboard (auto-runs on load)
function detectLocationAndWeather(silent = false) {
  const btn = document.getElementById("btn-detect-weather");
  const locEl = document.getElementById("weather-loc-name");
  const sumEl = document.getElementById("weather-summary");

  if (!("geolocation" in navigator)) {
    if (!silent) showToast("Geolocation is not supported by your browser.", true);
    return;
  }

  if (btn) btn.disabled = true;
  if (sumEl) sumEl.textContent = "Fetching GPS coordinates & live weather...";

  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      const lat = pos.coords.latitude;
      const lon = pos.coords.longitude;
      try {
        const res = await fetch(`/api/weather-risk?lat=${lat}&lon=${lon}`);
        const data = await res.json();
        farmerCoords = {
          lat,
          lon,
          location_name: data.location_name || `${lat.toFixed(3)}, ${lon.toFixed(3)}`
        };

        if (locEl) locEl.textContent = farmerCoords.location_name;
        const w = data.weather || {};
        if (sumEl) {
          sumEl.textContent = `${w.condition || "Live Weather"} • Lat ${lat.toFixed(3)}, Lon ${lon.toFixed(3)} (${data.source || "Weather API"})`;
        }

        const tEl = document.getElementById("w-temp");
        const hEl = document.getElementById("w-humidity");
        const wEl = document.getElementById("w-wind");
        const pEl = document.getElementById("w-precip");
        if (tEl) tEl.textContent = `${w.temp_c ?? "--"}°C`;
        if (hEl) hEl.textContent = `${w.humidity ?? "--"}%`;
        if (wEl) wEl.textContent = `${w.wind_kmh ?? "--"} km/h`;
        if (pEl) pEl.textContent = `${w.precip_prob ?? 0}%`;

        const riskList = document.getElementById("weather-risk-list");
        const risks = data.disease_risks || [];
        if (riskList) {
          riskList.innerHTML = "";
          risks.forEach(r => {
            const chip = document.createElement("div");
            chip.className = `risk-chip ${r.risk}`;
            chip.innerHTML = `
              <div class="risk-chip-title">${r.risk === "Critical" || r.risk === "High" ? "⚠️" : "🌱"} ${r.disease} (${r.risk})</div>
              <div class="risk-chip-meta"><strong>Crops:</strong> ${(r.crops || []).join(", ")}<br/>${r.reason}</div>
            `;
            riskList.appendChild(chip);
          });
        }

        const riskBadge = document.getElementById("weather-risk-badge");
        if (riskBadge) {
          const highCount = risks.filter(r => r.risk === "High" || r.risk === "Critical").length;
          if (highCount > 0) {
            riskBadge.textContent = `${highCount} High`;
            riskBadge.style.display = "inline-block";
          } else {
            riskBadge.style.display = "none";
          }
        }

        if (googleMap) {
          googleMap.setCenter({ lat, lng: lon });
          if (googleMapCircle) googleMapCircle.setCenter({ lat, lng: lon });
          updateGoogleMapMarkers(latestOutbreaks);
        }
        if (!silent) {
          showToast(`Weather & disease risk updated for ${farmerCoords.location_name}`);
        }
      } catch (err) {
        console.error("Weather risk error:", err);
        if (!silent) showToast("Failed to fetch weather risk data.", true);
      } finally {
        if (btn) btn.disabled = false;
      }
    },
    (err) => {
      if (btn) btn.disabled = false;
      if (locEl) locEl.textContent = "Location Permission Needed";
      if (sumEl) sumEl.textContent = "Allow browser GPS permission and click Refresh Weather & Location.";
      if (!silent) showToast("GPS permission denied: " + err.message, true);
    },
    { enableHighAccuracy: true, timeout: 10000 }
  );
}

// Google Maps Integration in Outbreak Tab
function switchOutbreakView(mode) {
  currentOutbreakView = mode;
  const radarEl = document.getElementById("radar-container");
  const gmapEl = document.getElementById("outbreak-gmap");
  const btnRadar = document.getElementById("btn-view-radar");
  const btnGmap = document.getElementById("btn-view-gmap");

  if (btnRadar) btnRadar.classList.toggle("active", mode === "radar");
  if (btnGmap) btnGmap.classList.toggle("active", mode === "gmap");

  if (mode === "gmap") {
    if (radarEl) radarEl.style.display = "none";
    if (gmapEl) gmapEl.style.display = "block";
    if (!googleMap) {
      initGoogleMap();
    } else if (window.google && window.google.maps) {
      setTimeout(() => {
        window.google.maps.event.trigger(googleMap, "resize");
        const c = farmerCoords ? { lat: farmerCoords.lat, lng: farmerCoords.lon } : { lat: 28.6139, lng: 77.2090 };
        googleMap.setCenter(c);
        updateGoogleMapMarkers(latestOutbreaks);
      }, 120);
    }
  } else {
    if (radarEl) radarEl.style.display = "flex";
    if (gmapEl) gmapEl.style.display = "none";
  }
}

function initGoogleMap() {
  if (!mapsApiKey) {
    showToast("Google Maps API key not configured.", true);
    return;
  }
  if (window.google && window.google.maps) {
    renderGoogleMapInstance();
    return;
  }
  if (mapsScriptLoading) return;
  mapsScriptLoading = true;
  window.__onLeafGuardMapsReady = () => {
    mapsScriptLoading = false;
    renderGoogleMapInstance();
  };
  const script = document.createElement("script");
  script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(mapsApiKey)}&callback=__onLeafGuardMapsReady`;
  script.async = true;
  script.defer = true;
  script.onerror = () => {
    mapsScriptLoading = false;
    showToast("Failed to load Google Maps script.", true);
  };
  document.head.appendChild(script);
}

function renderGoogleMapInstance() {
  const mapEl = document.getElementById("outbreak-gmap");
  if (!mapEl || !window.google || !window.google.maps) return;
  const center = farmerCoords ? { lat: farmerCoords.lat, lng: farmerCoords.lon } : { lat: 28.6139, lng: 77.2090 };
  googleMap = new google.maps.Map(mapEl, {
    center,
    zoom: 13,
    mapTypeId: "hybrid"
  });

  googleMapCircle = new google.maps.Circle({
    strokeColor: "#10b981",
    strokeOpacity: 0.85,
    strokeWeight: 2,
    fillColor: "#10b981",
    fillOpacity: 0.14,
    map: googleMap,
    center,
    radius: 2500
  });

  updateGoogleMapMarkers(latestOutbreaks);
}

function updateGoogleMapMarkers(alerts) {
  if (!googleMap || !window.google || !window.google.maps) return;
  googleMapMarkers.forEach(m => m.setMap(null));
  googleMapMarkers = [];

  const baseLat = farmerCoords ? farmerCoords.lat : 28.6139;
  const baseLon = farmerCoords ? farmerCoords.lon : 77.2090;
  const infoWindow = new google.maps.InfoWindow();

  (alerts || []).forEach(alt => {
    const lat = typeof alt.lat === "number" ? alt.lat : baseLat + (alt.lat_offset || 0);
    const lng = typeof alt.lon === "number" ? alt.lon : baseLon + (alt.lon_offset || 0);
    const marker = new google.maps.Marker({
      position: { lat, lng },
      map: googleMap,
      title: `${alt.crop}: ${alt.disease}`
    });
    marker.addListener("click", () => {
      infoWindow.setContent(
        `<div style="color:#111;max-width:240px;">
          <strong>${alt.crop} • ${alt.disease}</strong><br/>
          <span>Risk: ${alt.risk_level} | ${alt.location_name || alt.distance}</span><br/>
          <small>${alt.advisory}</small>
        </div>`
      );
      infoWindow.open(googleMap, marker);
    });
    googleMapMarkers.push(marker);
  });
}

// Live Outbreak Broadcast Polling & Popup Modal for Other Farmers
function startOutbreakPolling() {
  setInterval(async () => {
    try {
      const res = await fetch(`/api/outbreaks?since=${lastSeenOutbreakTs}`);
      const newAlerts = await res.json();
      if (!Array.isArray(newAlerts) || newAlerts.length === 0) return;

      let newestExternal = null;
      newAlerts.forEach(a => {
        if (a.created_ts && a.created_ts > lastSeenOutbreakTs) {
          lastSeenOutbreakTs = a.created_ts;
        }
        if (a.sender_id !== farmerSenderId) {
          newestExternal = a;
        }
      });

      await loadOutbreaks();
      if (newestExternal) {
        showLiveAlertModal(newestExternal);
      }
    } catch (e) {
      // silent poll error
    }
  }, 5000);
}

async function showLiveAlertModal(alt) {
  window._activeLiveAlert = alt;
  const modal = document.getElementById("live-alert-modal");
  if (!modal) return;
  const mainLangSel = document.getElementById("lang-select");
  const modalLangSel = document.getElementById("live-alert-lang");
  if (mainLangSel && modalLangSel) {
    if (modalLangSel.options.length === 0) {
      modalLangSel.innerHTML = mainLangSel.innerHTML;
    }
    modalLangSel.value = currentLang;
  }
  document.getElementById("live-alert-title").textContent = `${alt.crop} — ${alt.disease}`;
  document.getElementById("live-alert-meta").textContent = `📍 ${alt.location_name || alt.distance} • Risk: ${alt.risk_level} • ${alt.timestamp}`;
  document.getElementById("live-alert-advisory").textContent = alt.advisory;
  modal.style.display = "flex";
  showToast(`🚨 New Outbreak Broadcast: ${alt.crop} - ${alt.disease}`, true);

  if (currentLang !== "en") {
    translateLiveAlertModal(currentLang);
  }

  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(880, ctx.currentTime);
    gain.gain.setValueAtTime(0.08, ctx.currentTime);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.18);
  } catch (e) {}
}

async function translateLiveAlertModal(forcedLang = null) {
  const alt = window._activeLiveAlert;
  if (!alt) return;
  const modalLangSel = document.getElementById("live-alert-lang");
  const targetLang = forcedLang || (modalLangSel ? modalLangSel.value : null) || (currentLang === "en" ? "hi" : currentLang);
  if (modalLangSel && modalLangSel.value !== targetLang) {
    modalLangSel.value = targetLang;
  }
  if (targetLang === "en") {
    document.getElementById("live-alert-title").textContent = `${alt.crop} — ${alt.disease}`;
    document.getElementById("live-alert-meta").textContent = `📍 ${alt.location_name || alt.distance} • Risk: ${alt.risk_level} • ${alt.timestamp}`;
    document.getElementById("live-alert-advisory").textContent = alt.advisory;
    return;
  }
  const tr = await translateTextsBatch(
    [alt.crop || "", alt.disease || "", alt.location_name || alt.distance || "", alt.risk_level || "", alt.advisory || ""],
    targetLang
  );
  if (tr && tr.length === 5) {
    document.getElementById("live-alert-title").textContent = `${tr[0]} — ${tr[1]}`;
    document.getElementById("live-alert-meta").textContent = `📍 ${tr[2]} • Risk: ${tr[3]} • ${alt.timestamp}`;
    document.getElementById("live-alert-advisory").textContent = tr[4];
  }
}

function closeLiveAlertModal() {
  const modal = document.getElementById("live-alert-modal");
  if (modal) modal.style.display = "none";
}

function viewOutbreakOnRadar() {
  closeLiveAlertModal();
  switchTab("outbreak");
}
