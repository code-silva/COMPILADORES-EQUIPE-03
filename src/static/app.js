"use strict";

const $ = (selector) => document.querySelector(selector);

const MAX_BYTES = 1024 * 1024;
const STAGES = ["upload", "lexer", "parser", "semantic", "codegen"];

const STAGE_ICONS = {
  pending:
    '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true"><circle cx="12" cy="12" r="3"></circle></svg>',
  running:
    '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>',
  done:
    '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>',
  error:
    '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="12" y1="8" x2="12" y2="12"></line><circle cx="12" cy="16" r="1" fill="currentColor"></circle></svg>',
};

const MESSAGE_ICONS = {
  "": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>',
  success:
    '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
  error:
    '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>',
};

const input = $("#file-input");
const button = $("#compile");
const zone = $("#drop-zone");
const editor = $("#source-editor");
const tabUpload = $("#tab-upload");
const tabEditor = $("#tab-editor");
const panelUpload = $("#panel-upload");
const panelEditor = $("#panel-editor");

let mode = "upload";
let selectedFile = null;
let editorFilename = "entrada.py";
let lastJavaCode = "";
let downloadUrl = null;
let busy = false;
let completedStages = 0;

function initTheme() {
  const saved = localStorage.getItem("pytojava-theme");
  const prefersDark =
    window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = saved || (prefersDark ? "dark" : "light");
  applyTheme(theme);
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const toggle = $("#theme-toggle");
  if (toggle) toggle.setAttribute("aria-pressed", String(theme === "dark"));
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function highlightJava(code) {
  const tokenRegex =
    /(\/\/[^\n]*|"(?:\\.|[^"\\])*"|\b(?:public|private|protected|class|static|void|if|else|while|for|return|new|true|false|null)\b|\b(?:int|double|boolean|String|Object)\b|\b\d+(?:\.\d+)?\b)/g;

  let html = "";
  let lastIndex = 0;
  for (const match of code.matchAll(tokenRegex)) {
    const token = match[0];
    const index = match.index;
    html += escapeHtml(code.slice(lastIndex, index));

    let cls = "tok-number";
    if (token.startsWith("//")) cls = "tok-comment";
    else if (token.startsWith('"')) cls = "tok-string";
    else if (/^(int|double|boolean|String|Object)$/.test(token)) cls = "tok-type";
    else if (/^[a-z]/.test(token)) cls = "tok-keyword";

    html += `<span class="${cls}">${escapeHtml(token)}</span>`;
    lastIndex = index + token.length;
  }
  html += escapeHtml(code.slice(lastIndex));
  return html;
}

function renderJavaOutput(javaCode, elapsedMs) {
  lastJavaCode = javaCode;
  const lines = javaCode.split("\n");
  const lineCount = javaCode.endsWith("\n") ? lines.length - 1 : lines.length;

  $("#line-numbers").textContent = Array.from(
    { length: Math.max(1, lineCount) },
    (_, i) => String(i + 1)
  ).join("\n");
  $("#java-code").innerHTML = highlightJava(javaCode);

  const timeText = elapsedMs != null ? ` · compilado em ${Math.round(elapsedMs)} ms` : "";
  $("#result-meta").textContent = `${lineCount} linha${lineCount === 1 ? "" : "s"} geradas${timeText}`;

  if (downloadUrl) URL.revokeObjectURL(downloadUrl);
  downloadUrl = URL.createObjectURL(
    new Blob([javaCode], { type: "text/plain;charset=utf-8" })
  );
  $("#download").href = downloadUrl;
  $("#result").hidden = false;
}

function setMessage(text, state = "") {
  const box = $("#message-box");
  box.className = state ? `message-box ${state}` : "message-box";
  $("#message-icon").innerHTML = MESSAGE_ICONS[state] || MESSAGE_ICONS[""];
  $("#message").textContent = text;
}

function updateProgress(hasError = false) {
  const pct = Math.round((completedStages / STAGES.length) * 100);
  const fill = $("#progress-fill");
  fill.style.width = `${pct}%`;
  fill.classList.toggle("error", hasError);
  $("#stage-counter").textContent = `${completedStages} / ${STAGES.length}`;
}

function clearResult() {
  $("#result").hidden = true;
  $("#java-code").textContent = "";
  $("#line-numbers").textContent = "";
  $("#download").removeAttribute("href");
  $("#elapsed-time").hidden = true;
  $("#elapsed-time").textContent = "";
  lastJavaCode = "";
  if (downloadUrl) URL.revokeObjectURL(downloadUrl);
  downloadUrl = null;
  completedStages = 0;
  updateProgress(false);

  document.querySelectorAll("[data-stage]").forEach((row) => {
    row.className = "";
    row.querySelector(".stage-icon").innerHTML = STAGE_ICONS.pending;
    row.querySelector(".stage-status").textContent = "Pendente";
  });
}

function updateCompileButtonState() {
  if (busy) {
    button.disabled = true;
    return;
  }
  if (mode === "upload") {
    button.disabled = !selectedFile;
  } else {
    button.disabled = false;
  }
}

function setMode(nextMode) {
  if (busy || mode === nextMode) return;
  mode = nextMode;
  const isUpload = mode === "upload";
  tabUpload.classList.toggle("active", isUpload);
  tabUpload.setAttribute("aria-selected", String(isUpload));
  tabEditor.classList.toggle("active", !isUpload);
  tabEditor.setAttribute("aria-selected", String(!isUpload));
  panelUpload.hidden = !isUpload;
  panelEditor.hidden = isUpload;
  updateCompileButtonState();
}

function clearActiveExampleChip() {
  document.querySelectorAll(".example-chip.active").forEach((chip) => {
    chip.classList.remove("active");
  });
}

function selectFile(file, { keepExampleChip = false } = {}) {
  if (busy) return;
  clearResult();
  if (!keepExampleChip) clearActiveExampleChip();
  selectedFile = null;
  $("#selected-file").hidden = true;
  input.value = "";

  if (!file) {
    updateCompileButtonState();
    setMessage("Selecione um arquivo .py ou escolha um exemplo para começar.");
    return;
  }
  if (!file.name.toLowerCase().endsWith(".py")) {
    updateCompileButtonState();
    setMessage("Selecione um arquivo com extensão .py.", "error");
    return;
  }
  if (file.size > MAX_BYTES) {
    updateCompileButtonState();
    setMessage("O arquivo deve ter no máximo 1 MB.", "error");
    return;
  }

  selectedFile = file;
  editorFilename = file.name;
  $("#editor-filename").textContent = file.name;
  $("#file-name").textContent = file.name;
  $("#file-size").textContent = formatBytes(file.size);
  $("#selected-file").hidden = false;
  updateCompileButtonState();
  setMessage(`Arquivo "${file.name}" pronto. Clique em Converter para Java.`);
}

function setStage(name, status) {
  const row = document.querySelector(`[data-stage="${name}"]`);
  if (!row) return;
  const wasDone = row.classList.contains("done");
  row.className = status;
  row.querySelector(".stage-icon").innerHTML = STAGE_ICONS[status] || STAGE_ICONS.pending;
  row.querySelector(".stage-status").textContent =
    { running: "Processando", done: "Concluída", error: "Erro" }[status] || "Pendente";

  if (status === "done" && !wasDone) {
    completedStages += 1;
    updateProgress(false);
  } else if (status === "error") {
    updateProgress(true);
  }
}

async function getInputPayload() {
  if (mode === "upload") {
    if (!selectedFile) throw new Error("Selecione um arquivo .py para continuar.");
    const source = new TextDecoder("utf-8", { fatal: true }).decode(
      await selectedFile.arrayBuffer()
    );
    return { filename: selectedFile.name, source };
  }

  const source = editor.value;
  const byteSize = new TextEncoder().encode(source).length;
  if (byteSize > MAX_BYTES) {
    throw new Error("O código deve ter no máximo 1 MB.");
  }
  const filename = editorFilename.toLowerCase().endsWith(".py")
    ? editorFilename
    : `${editorFilename}.py`;
  return { filename, source };
}

async function runCompilation() {
  if (busy) return;
  if (mode === "upload" && !selectedFile) return;

  busy = true;
  button.disabled = true;
  button.classList.add("loading");
  button.querySelector(".btn-label").textContent = "Convertendo…";
  input.disabled = true;
  editor.disabled = true;
  $("#remove-file").disabled = true;
  $("#inspect-file").disabled = true;

  clearResult();
  setMessage("Compilação em andamento…");
  const startedAt = performance.now();
  let finished = false;

  try {
    setStage("upload", "running");
    const payload = await getInputPayload();
    const response = await fetch("/api/compile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.error || `O servidor recusou o arquivo (HTTP ${response.status}).`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    function handleLine(line) {
      if (!line.trim()) return;
      const event = JSON.parse(line);
      if (event.stage) setStage(event.stage, event.status);
      if (event.status === "error") {
        finished = true;
        setMessage(event.message, "error");
      }
      if (event.status === "complete") {
        finished = true;
        const elapsed = performance.now() - startedAt;
        $("#elapsed-time").textContent = `${Math.round(elapsed)} ms`;
        $("#elapsed-time").hidden = false;
        renderJavaOutput(event.java, elapsed);
        setMessage("Conversão concluída. Seu Main.java está disponível para cópia ou download.", "success");
      }
    }

    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      const lines = buffer.split("\n");
      buffer = lines.pop();
      lines.forEach(handleLine);
      if (done) {
        handleLine(buffer);
        break;
      }
    }

    if (!finished) {
      throw new Error("A conexão foi interrompida. Tente converter novamente.");
    }
  } catch (error) {
    document.querySelectorAll(".checklist .running").forEach((row) => {
      setStage(row.dataset.stage, "error");
    });
    setMessage(
      error instanceof TypeError
        ? "Não foi possível ler o arquivo em UTF-8 ou conectar ao servidor. Confira o arquivo e se o servidor está ativo."
        : error.message,
      "error"
    );
  } finally {
    busy = false;
    button.classList.remove("loading");
    button.querySelector(".btn-label").textContent = "Converter para Java";
    input.disabled = false;
    editor.disabled = false;
    $("#remove-file").disabled = false;
    $("#inspect-file").disabled = false;
    updateCompileButtonState();
  }
}

async function loadExamples() {
  try {
    const response = await fetch("/api/examples");
    if (!response.ok) return;
    const data = await response.json();
    const examples = Array.isArray(data.examples) ? data.examples : [];
    if (!examples.length) return;

    const container = $("#examples-list");
    examples.forEach((example) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "example-chip";
      chip.textContent = example.name;
      chip.addEventListener("click", () => {
        if (busy) return;
        clearActiveExampleChip();
        chip.classList.add("active");
        const file = new File([example.source], example.name, { type: "text/x-python" });
        editor.value = example.source;
        selectFile(file, { keepExampleChip: true });
        if (mode === "editor") {
          setMessage(`Exemplo "${example.name}" carregado no editor. Pressione Ctrl+Enter ou clique em Converter.`);
        }
      });
      container.appendChild(chip);
    });
    $("#examples-bar").hidden = false;
  } catch {
    // Silencioso: exemplos são um recurso complementar.
  }
}

async function copyJavaCode() {
  if (!lastJavaCode) return;
  const label = $("#copy-label");
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(lastJavaCode);
    } else {
      const temp = document.createElement("textarea");
      temp.value = lastJavaCode;
      temp.setAttribute("readonly", "");
      temp.style.position = "absolute";
      temp.style.left = "-9999px";
      document.body.appendChild(temp);
      temp.select();
      document.execCommand("copy");
      document.body.removeChild(temp);
    }
    label.textContent = "Copiado!";
    setTimeout(() => {
      label.textContent = "Copiar código";
    }, 1800);
  } catch {
    setMessage("Não foi possível copiar automaticamente. Selecione o código manualmente.", "error");
  }
}

// Event listeners
$("#theme-toggle").addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  const next = current === "dark" ? "light" : "dark";
  localStorage.setItem("pytojava-theme", next);
  applyTheme(next);
});

tabUpload.addEventListener("click", () => setMode("upload"));
tabEditor.addEventListener("click", async () => {
  if (selectedFile && !editor.value) {
    try {
      editor.value = new TextDecoder("utf-8", { fatal: true }).decode(
        await selectedFile.arrayBuffer()
      );
    } catch {
      // Mantém editor vazio se arquivo não for UTF-8 válido.
    }
  }
  setMode("editor");
  editor.focus();
});

$("#inspect-file").addEventListener("click", async () => {
  if (!selectedFile || busy) return;
  try {
    editor.value = new TextDecoder("utf-8", { fatal: true }).decode(
      await selectedFile.arrayBuffer()
    );
    editorFilename = selectedFile.name;
    $("#editor-filename").textContent = selectedFile.name;
    setMode("editor");
    editor.focus();
  } catch {
    setMessage("Não foi possível decodificar o arquivo selecionado em UTF-8.", "error");
  }
});

input.addEventListener("change", () => selectFile(input.files[0]));
$("#remove-file").addEventListener("click", () => selectFile(null));

zone.addEventListener("dragover", (event) => {
  event.preventDefault();
  if (!busy) zone.classList.add("dragging");
});
zone.addEventListener("dragleave", () => zone.classList.remove("dragging"));
zone.addEventListener("drop", (event) => {
  event.preventDefault();
  zone.classList.remove("dragging");
  if (event.dataTransfer.files.length !== 1) {
    if (!busy) {
      selectFile(null);
      setMessage("Envie um arquivo .py por vez.", "error");
    }
    return;
  }
  selectFile(event.dataTransfer.files[0]);
});

editor.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    event.preventDefault();
    runCompilation();
  }
});

button.addEventListener("click", runCompilation);
$("#copy-code").addEventListener("click", copyJavaCode);

// Bootstrap inicial
initTheme();
clearResult();
setMessage("Selecione um arquivo .py ou escolha um exemplo para começar.");
loadExamples();
