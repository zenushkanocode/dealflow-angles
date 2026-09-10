
(function () {
  // Lane tabs (mobile)
  const tabs = document.querySelectorAll(".mobile-tabs button");
  const cols = document.querySelectorAll(".col");
  function activateLane(lane) {
    tabs.forEach((b) => b.classList.toggle("active", b.dataset.tab === lane));
    cols.forEach((c) => c.classList.toggle("active", c.dataset.laneCol === lane));
  }
  if (tabs.length) {
    activateLane("fundraises");
    tabs.forEach((b) => b.addEventListener("click", () => activateLane(b.dataset.tab)));
  }

  // Platform tabs inside each card
  document.querySelectorAll(".angles").forEach((root) => {
    const platTabs = root.querySelectorAll(".plat-tab");
    const panels = root.querySelectorAll(".plat-panel");
    platTabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        const plat = tab.dataset.plat;
        platTabs.forEach((t) => {
          const on = t.dataset.plat === plat;
          t.classList.toggle("is-active", on);
          t.setAttribute("aria-selected", on ? "true" : "false");
        });
        panels.forEach((p) => {
          const on = p.dataset.platPanel === plat;
          p.classList.toggle("is-active", on);
          if (on) p.removeAttribute("hidden");
          else p.setAttribute("hidden", "");
        });
      });
    });
  });

  // One-click Copy
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand("copy");
        resolve();
      } catch (e) {
        reject(e);
      } finally {
        document.body.removeChild(ta);
      }
    });
  }

  document.addEventListener("click", function (e) {
    const btn = e.target.closest(".copy-btn");
    if (!btn) return;
    const piece = btn.closest(".angle-piece");
    if (!piece) return;
    const source = piece.querySelector(".copyable");
    if (!source) return;
    const text = (source.textContent || "").trim();
    if (!text) return;
    copyText(text).then(function () {
      const prev = btn.textContent;
      btn.textContent = "Copied";
      btn.classList.add("copied");
      setTimeout(function () {
        btn.textContent = prev || "Copy";
        btn.classList.remove("copied");
      }, 1400);
    }).catch(function () {
      btn.textContent = "Failed";
      setTimeout(function () { btn.textContent = "Copy"; }, 1400);
    });
  });
})();
