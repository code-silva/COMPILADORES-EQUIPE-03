"use strict";
const $ = (selector) => document.querySelector(selector);
const input = $("#file-input"), button = $("#compile"), zone = $("#drop-zone");
let selectedFile = null, downloadUrl = null, busy = false;

function message(text, state = "") {
  $("#message").textContent = text;
  $("#message").className = `message ${state}`;
}

function clearResult() {
  $("#result").hidden = true;
  $("#java-code").textContent = "";
  $("#download").removeAttribute("href");
  if (downloadUrl) URL.revokeObjectURL(downloadUrl);
  downloadUrl = null;
  document.querySelectorAll("[data-stage]").forEach((row) => {
    row.className = "";
    row.querySelector(".stage-icon").textContent = "·";
    row.querySelector(".stage-status").textContent = "Pendente";
  });
}

function selectFile(file) {
  if (busy) return;
  clearResult();
  selectedFile = null;
  button.disabled = true;
  $("#selected-file").hidden = true;
  input.value = "";
  if (!file) { message("Selecione um arquivo .py para começar."); return; }
  if (!file.name.toLowerCase().endsWith(".py")) {
    message("Selecione um arquivo com extensão .py.", "error"); return;
  }
  if (file.size > 1024 * 1024) {
    message("O arquivo deve ter no máximo 1 MB.", "error"); return;
  }
  selectedFile = file;
  $("#file-name").textContent = file.name;
  $("#file-size").textContent = `${(file.size / 1024).toFixed(1)} KB`;
  $("#selected-file").hidden = false;
  button.disabled = false;
  message("Arquivo selecionado. Clique em Converter para Java.");
}

function stage(name, status) {
  const row = document.querySelector(`[data-stage="${name}"]`);
  if (!row) return;
  row.className = status;
  row.querySelector(".stage-icon").textContent = {running: "↻", done: "✓", error: "!"}[status] || "·";
  row.querySelector(".stage-status").textContent = {running: "Processando", done: "Concluída", error: "Erro"}[status] || "Pendente";
}

input.addEventListener("change", () => selectFile(input.files[0]));
$("#remove-file").addEventListener("click", () => selectFile(null));
zone.addEventListener("dragover", (event) => { event.preventDefault(); if (!busy) zone.classList.add("dragging"); });
zone.addEventListener("dragleave", () => zone.classList.remove("dragging"));
zone.addEventListener("drop", (event) => {
  event.preventDefault(); zone.classList.remove("dragging");
  if (event.dataTransfer.files.length !== 1) {
    if (!busy) { selectFile(null); message("Envie um arquivo .py por vez.", "error"); }
    return;
  }
  selectFile(event.dataTransfer.files[0]);
});

button.addEventListener("click", async () => {
  if (!selectedFile || busy) return;
  busy = true;
  button.disabled = true;
  input.disabled = true;
  $("#remove-file").disabled = true;
  button.textContent = "Convertendo…";
  clearResult();
  message("Compilação em andamento…");
  let finished = false;
  try {
    stage("upload", "running");
    const source = new TextDecoder("utf-8", {fatal: true}).decode(await selectedFile.arrayBuffer());
    const response = await fetch("/api/compile", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({filename: selectedFile.name, source})
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
      if (event.stage) stage(event.stage, event.status);
      if (event.status === "error") {
        finished = true;
        message(event.message, "error");
      }
      if (event.status === "complete") {
        finished = true;
        $("#java-code").textContent = event.java;
        downloadUrl = URL.createObjectURL(new Blob([event.java], {type: "text/plain;charset=utf-8"}));
        $("#download").href = downloadUrl;
        $("#result").hidden = false;
        message("Conversão concluída. Seu Main.java está disponível para download.", "success");
      }
    }
    while (true) {
      const {value, done} = await reader.read();
      buffer += decoder.decode(value, {stream: !done});
      const lines = buffer.split("\n");
      buffer = lines.pop();
      lines.forEach(handleLine);
      if (done) { handleLine(buffer); break; }
    }
    if (!finished) throw new Error("A conexão foi interrompida. Tente converter novamente.");
  } catch (error) {
    document.querySelectorAll(".checklist .running").forEach((row) => stage(row.dataset.stage, "error"));
    message(error instanceof TypeError
      ? "Não foi possível ler o arquivo em UTF-8 ou conectar ao servidor. Confira o arquivo e se o servidor está ativo."
      : error.message, "error");
  } finally {
    busy = false;
    button.disabled = !selectedFile;
    input.disabled = false;
    $("#remove-file").disabled = false;
    button.innerHTML = 'Converter para Java <span aria-hidden="true">→</span>';
  }
});
