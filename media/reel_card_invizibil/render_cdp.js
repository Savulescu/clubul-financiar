// Fast deterministic render: one Chrome instance, call frame(t)+screenshot per frame via CDP.
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const DIR = __dirname;
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9333;
const FPS = 30, DUR = 28000;
const N = Math.round(DUR * FPS / 1000);
const URL = `file://${DIR}/scene.html?t=0`;
const framesDir = path.join(DIR, 'frames');

fs.rmSync(framesDir, { recursive: true, force: true });
fs.mkdirSync(framesDir, { recursive: true });
fs.rmSync('/tmp/cf_cdp', { recursive: true, force: true });

const chrome = spawn(CHROME, [
  '--headless=new', '--use-angle=swiftshader', '--disable-gpu', '--hide-scrollbars',
  `--remote-debugging-port=${PORT}`, '--window-size=1080,1920',
  '--force-device-scale-factor=1', '--user-data-dir=/tmp/cf_cdp', URL
], { stdio: 'ignore' });

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function getWsUrl() {
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch(`http://localhost:${PORT}/json`);
      const list = await r.json();
      const page = list.find(t => t.type === 'page' && t.webSocketDebuggerUrl);
      if (page) return page.webSocketDebuggerUrl;
    } catch (e) {}
    await sleep(200);
  }
  throw new Error('devtools not reachable');
}

(async () => {
  const ws = new WebSocket(await getWsUrl());
  let id = 0; const pending = new Map();
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  });
  await new Promise(r => ws.addEventListener('open', r));
  const cmd = (method, params = {}) => new Promise(res => {
    const mid = ++id; pending.set(mid, res);
    ws.send(JSON.stringify({ id: mid, method, params }));
  });

  await cmd('Page.enable');
  await cmd('Runtime.enable');
  await cmd('Emulation.setDeviceMetricsOverride', { width: 1080, height: 1920, deviceScaleFactor: 1, mobile: false });

  // wait until frame() defined
  for (let i = 0; i < 60; i++) {
    const r = await cmd('Runtime.evaluate', { expression: 'typeof frame' });
    if (r.result?.result?.value === 'function') break;
    await sleep(150);
  }
  await cmd('Runtime.evaluate', { expression: 'document.fonts.ready.then(()=>true)', awaitPromise: true });
  await cmd('Runtime.evaluate', { expression: 'Promise.all([...document.images].map(i=>i.complete?1:new Promise(r=>{i.onload=i.onerror=r}))).then(()=>true)', awaitPromise: true });
  await sleep(300);

  const t0 = Date.now();
  for (let i = 0; i < N; i++) {
    const t = Math.round(i * 1000 / FPS);
    await cmd('Runtime.evaluate', { expression: `frame(${t})` });
    const shot = await cmd('Page.captureScreenshot', {
      format: 'png', clip: { x: 0, y: 0, width: 1080, height: 1920, scale: 1 }
    });
    fs.writeFileSync(path.join(framesDir, `f${String(i).padStart(4, '0')}.png`),
      Buffer.from(shot.result.data, 'base64'));
    if (i % 50 === 0) console.log(`frame ${i}/${N} (${((Date.now()-t0)/1000).toFixed(1)}s)`);
  }
  console.log(`frames done: ${N} in ${((Date.now()-t0)/1000).toFixed(1)}s`);
  ws.close(); chrome.kill(); process.exit(0);
})().catch(e => { console.error(e); chrome.kill(); process.exit(1); });
