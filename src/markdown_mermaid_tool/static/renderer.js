(function () {
  function fallbackMarkdown(text) {
    const escaped = String(text || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
    return "<pre><code>" + escaped + "</code></pre>";
  }

  function convertMermaidBlocks(root) {
    const blocks = root.querySelectorAll("pre code.language-mermaid, pre code.lang-mermaid");
    blocks.forEach(function (code, index) {
      const source = code.textContent || "";
      const div = document.createElement("div");
      div.className = "mermaid";
      div.id = "mermaid-block-" + Date.now() + "-" + index;
      div.textContent = source;
      const pre = code.closest("pre");
      if (pre && pre.parentNode) {
        pre.parentNode.replaceChild(div, pre);
      }
    });
  }

  async function render(markdownText, target) {
    if (!target) {
      return;
    }

    const source = String(markdownText || "");
    target.innerHTML = "";

    if (!window.marked || !window.marked.parse) {
      target.innerHTML = fallbackMarkdown(source);
      return;
    }

    try {
      target.innerHTML = window.marked.parse(source, {
        gfm: true,
        breaks: false,
        mangle: false,
        headerIds: false
      });
    } catch (err) {
      target.innerHTML = '<div class="render-error">' + String(err && err.message ? err.message : err) + "</div>";
      return;
    }

    target.querySelectorAll("a[href]").forEach(function (link) {
      link.setAttribute("target", "_blank");
      link.setAttribute("rel", "noopener noreferrer");
    });

    convertMermaidBlocks(target);

    const mermaidNodes = target.querySelectorAll(".mermaid");
    if (!mermaidNodes.length) {
      return;
    }
    if (!window.mermaid) {
      const warning = document.createElement("div");
      warning.className = "render-error";
      warning.textContent = "Mermaid renderer is not available.";
      target.prepend(warning);
      return;
    }

    try {
      window.mermaid.initialize({
        startOnLoad: false,
        securityLevel: "loose",
        theme: "default"
      });
      await window.mermaid.run({ nodes: mermaidNodes });
    } catch (err) {
      const warning = document.createElement("div");
      warning.className = "render-error";
      warning.textContent = "Mermaid render error: " + String(err && err.message ? err.message : err);
      target.prepend(warning);
    }
  }

  window.MarkdownMermaidRenderer = {
    render: render
  };
})();
