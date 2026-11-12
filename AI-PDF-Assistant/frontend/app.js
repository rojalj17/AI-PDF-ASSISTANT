// ---------------------------------------------------------------------------
// Backend URL config — stored in localStorage so a deployed frontend can be
// pointed at whichever machine is running server.py (localhost, LAN IP, or
// a tunnel URL).
// ---------------------------------------------------------------------------
const STORAGE_KEY = "readingdesk.backendUrl";

function getBackendUrl() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored) return stored.replace(/\/$/, "");
  // Default: same origin the page was served from (works when server.py
  // serves this frontend itself).
  return window.location.origin;
}

function setBackendUrl(url) {
  localStorage.setItem(STORAGE_KEY, url.replace(/\/$/, ""));
}

// ---------------------------------------------------------------------------
// Elements
// ---------------------------------------------------------------------------
const statusStamp = document.getElementById("statusStamp");
const statusDot = document.getElementById("statusDot");
const statusLabel = document.getElementById("statusLabel");
const settingsDrawer = document.getElementById("settingsDrawer");
const backendUrlInput = document.getElementById("backendUrlInput");
const saveBackendUrlBtn = document.getElementById("saveBackendUrl");
const settingsStatus = document.getElementById("settingsStatus");

const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const uploadStatus = document.getElementById("uploadStatus");
const cardDrawer = document.getElementById("cardDrawer");
const emptyNote = document.getElementById("emptyNote");
const clearBtn = document.getElementById("clearBtn");

const ledger = document.getElementById("ledger");
const composer = document.getElementById("composer");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");

// ---------------------------------------------------------------------------
// Settings drawer
// ---------------------------------------------------------------------------
statusStamp.addEventListener("click", () => {
  backendUrlInput.value = getBackendUrl();
  settingsDrawer.classList.toggle("open");
});

saveBackendUrlBtn.addEventListener("click", async () => {
  const url = backendUrlInput.value.trim();
  if (!url) return;
  setBackendUrl(url);
  settingsStatus.textContent = "Checking connection…";
  const ok = await checkHealth();
  settingsStatus.textContent = ok
    ? "Connected. Settings saved."
    : "Saved, but couldn't reach that address.";
  refreshSources();
});

async function checkHealth() {
  try {
    const res = await fetch(`${getBackendUrl()}/api/health`);
    if (!res.ok) throw new Error();
    setStatus(true);
    return true;
  } catch {
    setStatus(false);
    return false;
  }
}

function setStatus(online) {
  statusDot.className = "stamp-dot " + (online ? "online" : "offline");
  statusLabel.textContent = online ? "LOCAL ACCESS" : "DISCONNECTED";
}

// ---------------------------------------------------------------------------
// Catalog (upload + indexed document list)
// ---------------------------------------------------------------------------
dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.classList.add("dragover");
});
dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dragover");
  if (e.dataTransfer.files.length) uploadFiles(e.dataTransfer.files);
});

fileInput.addEventListener("change", () => {
  if (fileInput.files.length) uploadFiles(fileInput.files);
  fileInput.value = "";
});

async function uploadFiles(fileList) {
  const formData = new FormData();
  for (const file of fileList) formData.append("files", file);

  uploadStatus.innerHTML = `Indexing ${fileList.length} file(s)…`;

  try {
    const res = await fetch(`${getBackendUrl()}/api/upload`, {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setStatus(true);

    uploadStatus.innerHTML = data.results
      .map((r) =>
        r.ok
          ? `<div class="ok">✓ ${r.filename} — ${r.chunks} chunks</div>`
          : `<div class="err">✕ ${r.filename} — ${r.error}</div>`
      )
      .join("");

    renderSources(data.sources);
  } catch (err) {
    setStatus(false);
    uploadStatus.innerHTML = `<div class="err">Couldn't reach the backend. Check the connection settings (top right).</div>`;
  }
}

async function refreshSources() {
  try {
    const res = await fetch(`${getBackendUrl()}/api/sources`);
    const data = await res.json();
    setStatus(true);
    renderSources(data.sources);
  } catch {
    setStatus(false);
  }
}

function renderSources(sources) {
  cardDrawer.innerHTML = "";
  if (!sources || sources.length === 0) {
    cardDrawer.appendChild(emptyNote);
    return;
  }
  sources.forEach((name) => {
    const card = document.createElement("div");
    card.className = "index-card";
    card.innerHTML = `
      <div class="index-card-title">${escapeHtml(name)}</div>
      <div class="index-card-meta">
        <span class="index-card-badge">INDEXED</span>
      </div>
    `;
    cardDrawer.appendChild(card);
  });
}

clearBtn.addEventListener("click", async () => {
  if (!confirm("Clear every indexed document? This can't be undone.")) return;
  try {
    const res = await fetch(`${getBackendUrl()}/api/sources`, { method: "DELETE" });
    const data = await res.json();
    renderSources(data.sources);
    uploadStatus.innerHTML = "";
  } catch {
    setStatus(false);
  }
});

// ---------------------------------------------------------------------------
// Chat
// ---------------------------------------------------------------------------
composer.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = messageInput.value.trim();
  if (!message) return;

  messageInput.value = "";
  addBubble("user", message);
  const assistantBubble = addBubble("assistant", "", true);

  sendBtn.disabled = true;
  try {
    const res = await fetch(`${getBackendUrl()}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!res.ok || !res.body) throw new Error("Request failed");
    setStatus(true);

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let full = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      full += decoder.decode(value, { stream: true });
      setBubbleText(assistantBubble, full, true);
    }
    setBubbleText(assistantBubble, full, false);
  } catch (err) {
    setStatus(false);
    setBubbleText(
      assistantBubble,
      "Couldn't reach the backend. Check the connection settings (top right) and try again.",
      false
    );
  } finally {
    sendBtn.disabled = false;
    messageInput.focus();
  }
});

function addBubble(role, text, streaming = false) {
  const row = document.createElement("div");
  row.className = `msg-row ${role}`;
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  row.appendChild(bubble);
  ledger.appendChild(row);
  ledger.scrollTop = ledger.scrollHeight;
  setBubbleText(bubble, text, streaming);
  return bubble;
}

function setBubbleText(bubble, text, streaming) {
  bubble.textContent = text;
  if (streaming) {
    const cursor = document.createElement("span");
    cursor.className = "cursor";
    bubble.appendChild(cursor);
  }
  ledger.scrollTop = ledger.scrollHeight;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
checkHealth().then(refreshSources);

const clearChatBtn = document.getElementById("clearChatBtn");

clearChatBtn?.addEventListener("click", () => {
    chatMessages.innerHTML = "";
    messageInput.value = "";

    addMessage(
        "assistant",
        "Hi! Upload a PDF and ask me anything."
    );
});

