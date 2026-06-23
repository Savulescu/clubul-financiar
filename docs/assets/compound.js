/* Semnătură homepage: instrument dobândă compusă. 100% local, zero network.
   FV contribuții lunare: PMT * ((1+r)^n - 1)/r,  r=8%/12, n=ani*12. */
(function () {
  var mEl = document.getElementById('ccMonthly');
  if (!mEl) return;
  var R = 0.08, years = 20, fmt = new Intl.NumberFormat('ro-RO');
  var monthlyOut = document.getElementById('ccMonthlyOut'),
      yearsEl = document.getElementById('ccYears'),
      totalEl = document.getElementById('ccTotal'),
      paidEl = document.getElementById('ccPaid'),
      gainEl = document.getElementById('ccGain'),
      area = document.getElementById('ccArea'),
      line = document.getElementById('ccLine'),
      contrib = document.getElementById('ccContrib'),
      reduce = matchMedia('(prefers-reduced-motion:reduce)').matches;

  function fv(pmt, yrs) { var r = R / 12, n = yrs * 12; return pmt * ((Math.pow(1 + r, n) - 1) / r); }

  function buildPath(yrs, pmt, W, H) {
    var pts = [], cpts = [], maxV = fv(pmt, yrs) || 1, step = Math.max(1, Math.floor(yrs / 40));
    for (var y = 0; y <= yrs; y += step) {
      var v = fv(pmt, y), c = pmt * y * 12,
          x = (y / yrs) * W, y1 = H - (v / maxV) * H, y2 = H - (c / maxV) * H;
      pts.push(x.toFixed(1) + ',' + y1.toFixed(1));
      cpts.push(x.toFixed(1) + ',' + y2.toFixed(1));
    }
    return { line: 'M' + pts.join(' L'), contrib: 'M' + cpts.join(' L'),
             area: 'M0,' + H + ' L' + pts.join(' L') + ' L' + W + ',' + H + ' Z' };
  }

  var animT = null;
  function render(animate) {
    var pmt = +mEl.value, total = fv(pmt, years), paid = pmt * years * 12, gain = total - paid;
    mEl.style.setProperty('--cc-pct', ((pmt - 50) / (2500 - 50) * 100) + '%');
    monthlyOut.innerHTML = fmt.format(pmt) + '&nbsp;lei';
    yearsEl.textContent = years;
    paidEl.textContent = fmt.format(Math.round(paid));
    gainEl.textContent = '+' + fmt.format(Math.round(gain));
    var p = buildPath(years, pmt, 320, 90);
    line.setAttribute('d', p.line); contrib.setAttribute('d', p.contrib); area.setAttribute('d', p.area);
    if (animT) cancelAnimationFrame(animT);
    if (reduce || !animate) { totalEl.innerHTML = fmt.format(Math.round(total)) + '&nbsp;lei'; return; }
    var t0 = null, from = 0;
    (function step(ts) {
      if (!t0) t0 = ts;
      var k = Math.min(1, (ts - t0) / 520), e = 1 - Math.pow(1 - k, 3);
      totalEl.innerHTML = fmt.format(Math.round(from + (total - from) * e)) + '&nbsp;lei';
      if (k < 1) animT = requestAnimationFrame(step);
    })(performance.now());
  }

  mEl.addEventListener('input', function () { render(false); });
  Array.prototype.forEach.call(document.querySelectorAll('.cf-comp-yr'), function (b) {
    b.addEventListener('click', function () {
      document.querySelectorAll('.cf-comp-yr').forEach(function (x) { x.classList.remove('is-on'); });
      b.classList.add('is-on'); years = +b.dataset.y; render(true);
    });
  });
  render(true);
})();

/* Stat count-up pe scroll-into-view (homepage). Reduced-motion safe; fallback = valoarea finală. */
(function () {
  if (matchMedia('(prefers-reduced-motion:reduce)').matches) return;
  var nums = [].slice.call(document.querySelectorAll('.u-page .stat .num'));
  if (!nums.length || !('IntersectionObserver' in window)) return;
  var fmt = new Intl.NumberFormat('ro-RO');
  function parse(txt) { var m = txt.match(/^([\d.,]+)(.*)$/); if (!m) return null;
    return { target: parseInt(m[1].replace(/[.,]/g, ''), 10), suffix: m[2] || '' }; }
  function run(el) {
    var d = parse(el.textContent.trim()); if (!d || isNaN(d.target)) return;
    var t0 = null;
    function step(ts) { if (!t0) t0 = ts; var k = Math.min(1, (ts - t0) / 1100), e = 1 - Math.pow(1 - k, 3);
      el.textContent = fmt.format(Math.round(d.target * e)) + d.suffix;
      if (k < 1) requestAnimationFrame(step); }
    requestAnimationFrame(step);
  }
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (en) { if (en.isIntersecting) { run(en.target); io.unobserve(en.target); } });
  }, { threshold: 0.5 });
  nums.forEach(function (n) { io.observe(n); });
})();
