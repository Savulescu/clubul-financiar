/* Clubul Financiar — tilt 3D pe carduri: înclinare spre cursor + luciu, smooth pe GPU.
   Activ doar pe pointer fin (desktop) și fără reduced-motion — pe touch rămâne plat. */
(function () {
  const fine = matchMedia("(pointer: fine)").matches;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!fine || reduce) return;
  const SEL = ".card,.level,.price,.stat,.glasscard,.glos-card";
  const MAX = 7;

  function enhance(el) {
    if (el.dataset.tilt) return;
    el.dataset.tilt = "1";
    el.classList.add("tilt3d");
    const gloss = document.createElement("span");
    gloss.className = "tilt-gloss";
    el.appendChild(gloss);
    let raf = 0, rx = 0, ry = 0;
    function apply() {
      raf = 0;
      el.style.transform = "perspective(900px) rotateX(" + rx + "deg) rotateY(" + ry + "deg)";
    }
    el.addEventListener("pointerenter", () => { el.style.transition = "none"; });
    el.addEventListener("pointermove", e => {
      const r = el.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
      ry = (px - 0.5) * MAX * 2;
      rx = -(py - 0.5) * MAX * 2;
      gloss.style.opacity = "1";
      gloss.style.background = "radial-gradient(circle at " + (px * 100) + "% " + (py * 100) + "%, rgba(255,255,255,.22), transparent 55%)";
      if (!raf) raf = requestAnimationFrame(apply);
    });
    el.addEventListener("pointerleave", () => {
      el.style.transition = "transform .55s cubic-bezier(.22,.61,.36,1)";
      el.style.transform = "perspective(900px) rotateX(0deg) rotateY(0deg)";
      gloss.style.opacity = "0";
    });
  }
  function scan() { document.querySelectorAll(SEL).forEach(enhance); }
  if (document.readyState !== "loading") scan();
  else window.addEventListener("DOMContentLoaded", scan);
  // re-scan după ce site.js/article.js injectează carduri noi (conexe, etc.)
  setTimeout(scan, 1300);
  setTimeout(scan, 2600);
})();
