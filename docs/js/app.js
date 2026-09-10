
(function () {
  const tabs = document.querySelectorAll(".mobile-tabs button");
  const cols = document.querySelectorAll(".col");
  function activate(lane) {
    tabs.forEach((b) => b.classList.toggle("active", b.dataset.tab === lane));
    cols.forEach((c) => c.classList.toggle("active", c.dataset.laneCol === lane));
  }
  if (tabs.length) {
    activate("fundraises");
    tabs.forEach((b) => b.addEventListener("click", () => activate(b.dataset.tab)));
  }
})();
