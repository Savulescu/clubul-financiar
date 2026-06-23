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

/* Bandă live date RO — grupată pe înțelesul tuturor: Curs BNR / Dividende / Preț / Inflația / Dobânzi. */
(function () {
  var tape = document.getElementById('cfTape'); if (!tape) return;
  var nf = new Intl.NumberFormat('ro-RO', { minimumFractionDigits: 2, maximumFractionDigits: 4 });
  var nf2 = new Intl.NumberFormat('ro-RO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  function ro(n) { return ('' + n).replace('.', ','); }
  function arrow(v) { if (v == null || isNaN(v)) return '';
    return ' <span class="' + (v >= 0 ? 'up' : 'dn') + '">' + (v >= 0 ? '▲' : '▼') + '</span>'; }
  function it(name, val, extra) {
    return '<span class="cf-tape-item"><span class="nm">' + name + '</span> <b>' + val + '</b>' + (extra || '') + '</span>'; }
  function grp(label, inner) {
    return '<span class="cf-tape-grp"><span class="cf-tape-lbl">' + label + '</span> ' + inner + '</span>'; }
  var SEP = ' <span class="cf-tape-dot">·</span> ';
  function seed() { return [
    grp('Curs BNR:', [it('Euro', '5,2386&nbsp;lei', arrow(-0.01)), it('Dolar', '4,5706&nbsp;lei', arrow(0.08)), it('Liră', '6,11&nbsp;lei', arrow(0.05))].join(SEP)),
    grp('Dividende:', [it('Banca Transilvania', '3,45%'), it('Nuclearelectrica', '5,38%'), it('Biofarm', '12,32%')].join(SEP)),
    grp('Inflația (anual):', [it('România', '8,6%'), it('Zona euro', '2,0%')].join(SEP)),
    grp('Dobânzi:', [it('ECB', '2,40%'), it('Euribor 3 luni', '2,23%')].join(SEP)) ]; }
  function build(groups) {
    if (!groups || !groups.length) groups = seed();
    var html = groups.join(' <span class="cf-tape-pipe">|</span> ');
    tape.innerHTML = '<span class="cf-tape-row-in">' + html + '</span><span class="cf-tape-row-in" aria-hidden="true">' + html + '</span>';
  }
  function J(u) { return fetch(u).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }); }
  Promise.all([J('/data/fx.json'), J('/data/dividends.json'), J('/data/macro.json')]).then(function (res) {
    var fx = res[0], div = res[1], macro = res[2], groups = [];
    var NAMES = { EUR: 'Euro', USD: 'Dolar', GBP: 'Liră', CHF: 'Franc elvețian' };
    try {
      if (fx && fx.rates) {
        var cur = ['EUR', 'USD', 'GBP', 'CHF'].map(function (c) {
          var r = fx.rates.filter(function (x) { return x.cur === c; })[0];
          return r ? it(NAMES[c] || c, nf.format(r.rate) + '&nbsp;lei', arrow(r.chg)) : null;
        }).filter(Boolean);
        if (cur.length) groups.push(grp('Curs BNR:', cur.join(SEP)));
      }
      if (div && div.items) {
        var keys = Object.keys(div.items);
        var dv = keys.filter(function (k) { return div.items[k] && div.items[k].y; }).slice(0, 5)
          .map(function (k) { return it(div.items[k].n || k, ro(div.items[k].y) + '%'); }).join(SEP);
        if (dv) groups.push(grp('Dividende (randament):', dv));
        var pr = keys.filter(function (k) { return div.items[k] && div.items[k].p; }).slice(0, 5)
          .map(function (k) { return it(div.items[k].n || k, nf2.format(div.items[k].p) + '&nbsp;lei'); }).join(SEP);
        if (pr) groups.push(grp('Preț acțiuni:', pr));
      }
      if (macro && macro.groups) {
        var find = function (re) { return (macro.groups.filter(function (g) { return re.test(g.title); })[0] || {}).items || []; };
        var infl = find(/Inflație/i).filter(function (i) { return i.value != null; })
          .map(function (i) { return it(i.label, ro(i.value) + '%'); }).join(SEP);
        if (infl) groups.push(grp('Inflația (anual):', infl));
        var rates = find(/Dobânzi/i).filter(function (i) { return i.value != null; })
          .map(function (i) { return it(i.label.replace(/\s*\(.*?\)/, '').replace(/Dobânda /, ''), ro(i.value) + '%'); }).join(SEP);
        if (rates) groups.push(grp('Dobânzi:', rates));
      }
    } catch (e) {}
    build(groups.length >= 2 ? groups : seed());
  }).catch(function () { build(seed()); });
})();
