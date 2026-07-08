(function () {
  const els = {};
  let renderTimer = 0;

  function byId(id) {
    return document.getElementById(id);
  }

  function setStatus(text) {
    els.status.textContent = text || "Ready";
  }

  function appendLog(text) {
    const now = new Date();
    const stamp = now.toLocaleTimeString([], { hour12: false });
    els.log.textContent += "[" + stamp + "] " + text + "\n";
    els.log.scrollTop = els.log.scrollHeight;
  }

  function getState() {
    return {
      mdPath: els.mdPath.value.trim(),
      iniPath: els.iniPath.value.trim(),
      outputDir: els.outputDir.value.trim(),
      outputName: els.outputName.value.trim(),
      formats: {
        html: els.fmtHtml.checked,
        pdf: els.fmtPdf.checked,
        png: els.fmtPng.checked,
        jpg: els.fmtJpg.checked
      }
    };
  }

  function setState(state) {
    if (!state) {
      return;
    }
    els.mdPath.value = state.mdPath || "";
    els.iniPath.value = state.iniPath || "";
    els.outputDir.value = state.outputDir || "";
    els.outputName.value = state.outputName || "document";
    const formats = state.formats || {};
    els.fmtHtml.checked = Boolean(formats.html);
    els.fmtPdf.checked = Boolean(formats.pdf);
    els.fmtPng.checked = Boolean(formats.png);
    els.fmtJpg.checked = Boolean(formats.jpg);
  }

  async function api(path, body) {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {})
    });
    const data = await response.json().catch(function () {
      return {};
    });
    if (!response.ok) {
      throw new Error(data.error || response.statusText);
    }
    return data;
  }

  function renderNow() {
    clearTimeout(renderTimer);
    renderTimer = 0;
    if (window.MarkdownMermaidRenderer) {
      window.MarkdownMermaidRenderer.render(els.editor.value, els.preview);
    }
  }

  function scheduleRender() {
    clearTimeout(renderTimer);
    renderTimer = window.setTimeout(renderNow, 180);
  }

  async function loadInitialState() {
    const response = await fetch("/api/state");
    const data = await response.json();
    setState(data.state);
    setStatus(data.browserAvailable ? "Ready" : "Ready; PDF/PNG/JPG need Edge or Chrome");
    if (data.state && data.state.mdPath) {
      try {
        await loadMd({ preserveOutputDir: true });
        return;
      } catch (err) {
        appendLog("Error: " + String(err && err.message ? err.message : err));
      }
    }
    renderNow();
  }

  async function pick(endpoint, target, afterPick) {
    setStatus("Opening dialog...");
    const data = await api(endpoint, {});
    if (data.path) {
      target.value = data.path;
      if (afterPick) {
        await afterPick();
      }
    }
    setStatus("Ready");
  }

  async function loadMd(options) {
    const opts = options || {};
    const path = els.mdPath.value.trim();
    if (!path) {
      setStatus("MD path is empty");
      return;
    }
    setStatus("Loading MD...");
    const data = await api("/api/load-md", {
      path: path,
      preserveOutputDir: Boolean(opts.preserveOutputDir)
    });
    setState(data.state);
    els.editor.value = data.content || "";
    renderNow();
    appendLog("Loaded MD: " + data.state.mdPath);
    setStatus("MD loaded");
  }

  async function loadIni() {
    const path = els.iniPath.value.trim();
    if (!path) {
      setStatus("INI path is empty");
      return;
    }
    setStatus("Loading INI...");
    const data = await api("/api/load-ini", { path: path });
    setState(data.state);
    if (typeof data.content === "string" && data.content.length > 0) {
      els.editor.value = data.content;
      renderNow();
    }
    if (data.warning) {
      appendLog(data.warning);
    }
    appendLog("Loaded INI: " + data.state.iniPath);
    setStatus("INI loaded");
  }

  async function saveIni() {
    setStatus("Saving INI...");
    const data = await api("/api/save-ini", {
      path: els.iniPath.value.trim(),
      state: getState()
    });
    setState(data.state);
    appendLog("Saved INI: " + data.path);
    setStatus("INI saved");
  }

  async function generate() {
    setStatus("Generating...");
    els.generate.disabled = true;
    try {
      const data = await api("/api/generate", {
        state: getState(),
        markdown: els.editor.value
      });
      setState(data.state);
      (data.outputs || []).forEach(function (item) {
        appendLog("Generated " + item.format.toUpperCase() + ": " + item.path);
      });
      (data.warnings || []).forEach(function (item) {
        appendLog("Warning: " + item);
      });
      setStatus("Generate complete");
    } finally {
      els.generate.disabled = false;
    }
  }

  function bind(idMap) {
    Object.keys(idMap).forEach(function (key) {
      els[key] = byId(idMap[key]);
    });
  }

  function wireEvents() {
    els.editor.addEventListener("input", scheduleRender);
    els.loadMd.addEventListener("click", function () {
      run(loadMd);
    });
    els.loadIni.addEventListener("click", function () {
      run(loadIni);
    });
    els.saveIni.addEventListener("click", function () {
      run(saveIni);
    });
    els.pickMd.addEventListener("click", function () {
      run(function () {
        return pick("/api/pick-md", els.mdPath, loadMd);
      });
    });
    els.pickIniOpen.addEventListener("click", function () {
      run(function () {
        return pick("/api/pick-ini-open", els.iniPath, loadIni);
      });
    });
    els.pickIniSave.addEventListener("click", function () {
      run(function () {
        return pick("/api/pick-ini-save", els.iniPath, null);
      });
    });
    els.pickOutputDir.addEventListener("click", function () {
      run(function () {
        return pick("/api/pick-output-dir", els.outputDir, null);
      });
    });
    els.generate.addEventListener("click", function () {
      run(generate);
    });
  }

  async function run(fn) {
    try {
      await fn();
    } catch (err) {
      const message = String(err && err.message ? err.message : err);
      setStatus(message);
      appendLog("Error: " + message);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    bind({
      mdPath: "mdPath",
      iniPath: "iniPath",
      outputDir: "outputDir",
      outputName: "outputName",
      fmtHtml: "fmtHtml",
      fmtPdf: "fmtPdf",
      fmtPng: "fmtPng",
      fmtJpg: "fmtJpg",
      pickMd: "pickMd",
      loadMd: "loadMd",
      pickIniOpen: "pickIniOpen",
      loadIni: "loadIni",
      pickIniSave: "pickIniSave",
      saveIni: "saveIni",
      pickOutputDir: "pickOutputDir",
      generate: "generate",
      editor: "editor",
      preview: "preview",
      status: "status",
      log: "log"
    });
    wireEvents();
    run(loadInitialState);
  });
})();
