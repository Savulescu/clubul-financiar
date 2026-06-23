#!/usr/bin/env node
/* Clubul Financiar — reliable full-page screenshots via Chrome + CDP.
 * Waits for fonts + images, sizes the viewport to full content height so
 * scroll-triggered .reveal elements actually show, lets the WebGL 3D hero
 * paint (settle), then captures. One Chrome instance for the whole batch.
 *
 * Usage:  node _shot.js <label> [page1.html page2.html ...]
 *   CF_SHOTDIR  override output dir   CF_PORT override server port
 *   CF_WIDTHS   comma list, default "1440,390"   CF_SETTLE ms, default 2200
 */
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const DOCS = path.join(ROOT, 'docs');
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = parseInt(process.env.CF_PORT || String(8700 + (process.pid % 200)), 10);
const DBG = 9300 + (process.pid % 400);
const PROFILE = `/tmp/cf_shot_profile_${process.pid}`;
const SHOTROOT = process.env.CF_SHOTDIR ||
  '/private/tmp/claude-501/-Users-savulescucristian/164f0cba-a983-42c1-b0b3-2ecb290ca3d2/scratchpad/shots';
const WIDTHS = (process.env.CF_WIDTHS || '1440,390').split(',').map(s => parseInt(s, 10));
const SETTLE = parseInt(process.env.CF_SETTLE || '2200', 10);

const label = process.argv[2] || 'shot';
let pages = process.argv.slice(3);
if (pages.length === 0) pages = [
  'index.html','premium.html','educatie.html','calculatoare.html','instrumente.html',
  'masterclass.html','stiri.html','glosar.html','incepe-aici.html','investitii.html',
  'credite.html','despre.html','contact.html','login.html','account.html','ultra.html',
  'cursuri.html','teste.html','statistici.html','feedback.html','stiri-externe.html',
  'reset.html','privacy.html','terms.html','dezabonare.html',
];

const OUT = path.join(SHOTROOT, label);
fs.mkdirSync(OUT, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));

// ---- serve docs/ ----
const server = spawn('python3', ['-m', 'http.server', String(PORT)],
  { cwd: DOCS, stdio: 'ignore' });

// ---- launch chrome ----
fs.rmSync(PROFILE, { recursive: true, force: true });
const chrome = spawn(CHROME, [
  '--headless=new', '--use-angle=swiftshader', '--disable-gpu', '--hide-scrollbars',
  `--remote-debugging-port=${DBG}`, '--force-device-scale-factor=1',
  `--user-data-dir=${PROFILE}`, 'about:blank',
], { stdio: 'ignore' });

function die(code) { try { chrome.kill(); } catch (e) {} try { server.kill(); } catch (e) {} process.exit(code); }

async function wsUrl() {
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch(`http://localhost:${DBG}/json`);
      const list = await r.json();
      const p = list.find(t => t.type === 'page' && t.webSocketDebuggerUrl);
      if (p) return p.webSocketDebuggerUrl;
    } catch (e) {}
    await sleep(200);
  }
  throw new Error('devtools not reachable');
}
async function waitServer() {
  for (let i = 0; i < 40; i++) {
    try { const r = await fetch(`http://localhost:${PORT}/index.html`); if (r.ok) return; } catch (e) {}
    await sleep(200);
  }
}

(async () => {
  await waitServer();
  const ws = new WebSocket(await wsUrl());
  let id = 0; const pending = new Map(); const evWaiters = [];
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result); pending.delete(m.id); }
    else if (m.method) evWaiters.forEach(w => w(m));
  });
  await new Promise(r => ws.addEventListener('open', r));
  const cmd = (method, params = {}) => new Promise(res => {
    const mid = ++id; pending.set(mid, res);
    ws.send(JSON.stringify({ id: mid, method, params }));
  });
  const waitEvent = (method, ms = 8000) => new Promise(res => {
    const to = setTimeout(() => { const i = evWaiters.indexOf(h); if (i>=0) evWaiters.splice(i,1); res(false); }, ms);
    const h = m => { if (m.method === method) { clearTimeout(to); const i = evWaiters.indexOf(h); if (i>=0) evWaiters.splice(i,1); res(true); } };
    evWaiters.push(h);
  });
  const eval_ = expr => cmd('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });

  await cmd('Page.enable'); await cmd('Runtime.enable');

  const capture = async (page, w, name) => {
      const url = `http://localhost:${PORT}/${page}`;
      const mobile = w < 700;
      await cmd('Emulation.setDeviceMetricsOverride', { width: w, height: 900, deviceScaleFactor: 1, mobile });
      const nav = waitEvent('Page.loadEventFired', 12000);
      await cmd('Page.navigate', { url });
      await nav;
      try { await eval_('document.fonts.ready.then(()=>1)'); } catch (e) {}
      try { await eval_('Promise.all([...document.images].map(i=>i.complete?1:new Promise(r=>{i.onload=i.onerror=r;setTimeout(r,2000)}))).then(()=>1)'); } catch (e) {}
      // size viewport to full content so .reveal (scroll-triggered) elements show
      let h = 2200;
      try {
        const m = await cmd('Page.getLayoutMetrics');
        h = Math.min(Math.ceil((m.cssContentSize && m.cssContentSize.height) || m.contentSize.height || 2200), 14000);
      } catch (e) {}
      await cmd('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile });
      // nudge IntersectionObserver + give WebGL/animation time
      try { await eval_('window.scrollTo(0,document.body.scrollHeight);1'); } catch (e) {}
      await sleep(400);
      try { await eval_('window.scrollTo(0,0);1'); } catch (e) {}
      await sleep(SETTLE);
      const shot = await cmd('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true,
        clip: { x: 0, y: 0, width: w, height: h, scale: 1 } });
      const file = path.join(OUT, `${name}__${w}.png`);
      fs.writeFileSync(file, Buffer.from(shot.data, 'base64'));
      console.log(`${page}  ${w}px  ${h}h  -> ${path.basename(file)}`);
  };

  for (const page of pages) {
    const name = page.replace(/\//g, '_').replace(/\.html$/, '');
    for (const w of WIDTHS) {
      const timeout = new Promise(r => setTimeout(() => r('TIMEOUT'), 25000));
      const res = await Promise.race([capture(page, w, name).catch(e => 'ERR:' + e.message), timeout]);
      if (res === 'TIMEOUT' || (typeof res === 'string' && res.startsWith('ERR'))) {
        console.log(`${page}  ${w}px  -> SKIP (${res})`);
        // reset the tab so a hung page doesn't poison the next capture
        try { await cmd('Page.navigate', { url: 'about:blank' }); await sleep(300); } catch (e) {}
      }
    }
  }
  ws.close(); console.log('==> ' + OUT); die(0);
})().catch(e => { console.error(e); die(1); });
