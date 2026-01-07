(() => {
  const addCopyButtons = () => {
    document.querySelectorAll("pre > code").forEach((code) => {
      const pre = code.parentElement;
      if (!pre || pre.dataset.copyReady === "true") {
        return;
      }

      const button = document.createElement("button");
      button.type = "button";
      button.className = "code-copy-btn";
      button.textContent = "Copy";
      button.addEventListener("click", async () => {
        const text = code.textContent || "";
        try {
          await navigator.clipboard.writeText(text);
          button.textContent = "Copied";
          setTimeout(() => (button.textContent = "Copy"), 1200);
        } catch {
          const area = document.createElement("textarea");
          area.value = text;
          area.setAttribute("readonly", "");
          area.style.position = "absolute";
          area.style.left = "-9999px";
          document.body.appendChild(area);
          area.select();
          document.execCommand("copy");
          document.body.removeChild(area);
          button.textContent = "Copied";
          setTimeout(() => (button.textContent = "Copy"), 1200);
        }
      });

      pre.style.position = "relative";
      pre.appendChild(button);
      pre.dataset.copyReady = "true";
    });
  };

  document.addEventListener("DOMContentLoaded", addCopyButtons);
})();
