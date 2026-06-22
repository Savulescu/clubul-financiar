// Fast render: node render_cdp.js <reelKey> <framesDir>
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const KEY = process.argv[2] || 'fond_urgenta';
const framesDir = process.argv[3] || path.join(__dirname, 'frames_' + KEY);
const DIR = __dirname;
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9355;
const FPS = 30;
const URL = `file://${DIR}/reel.html?reel=${KEY}&t=0`;

fs.rmSync(framesDir, { recursive: true, force: true });
fs.mkdirSync(framesDir, { recursive: true });
const prof = '/tmp/cf_cdp_' + KEY;
fs.rmSync(prof, { recursive: true, force: true });

const chrome = spawn(CHROME, [
  '--headless=new', '--use-angle=swiftshader', '--disable-gpu', '--hide-scrollbars',
  `--remote-debugging-port=${PORT}`, '--window-size=1080,1920',
  '--force-device-scale-factor=1', `--user-data-dir=${prof}`, URL
], { stdio: 'ignore' });

const sleep = ms => new Promise(r => setTimeout(r, ms));
async function getWs() {
  for (let i = 0; i < 60; i++) {
    try { const r = await fetch(`http://localhost:${PORT}/json`); const l = await r.json();
      const p = l.find(t => t.type === 'page' && t.webSocketDebuggerUrl); if (p) return p.webSocketDebuggerUrl;
    } catch (e) {} await sleep(200);
  } throw new Error('no devtools');
}
(async () => {
  const ws = new WebSocket(await getWs());
  let id = 0; const pend = new Map();
  ws.addEventListener('message', ev => { const m = JSON.parse(ev.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } });
  await new Promise(r => ws.addEventListener('open', r));
  const cmd = (me, p = {}) => new Promise(res => { const mid = ++id; pend.set(mid, res); ws.send(JSON.stringify({ id: mid, method: me, params: p })); });
  await cmd('Page.enable'); await cmd('Runtime.enable');
  await cmd('Emulation.setDeviceMetricsOverride', { width: 1080, height: 1920, deviceScaleFactor: 1, mobile: false });
  for (let i = 0; i < 60; i++) { const r = await cmd('Runtime.evaluate', { expression: 'typeof frame' }); if (r.result?.result?.value === 'function') break; await sleep(150); }
  await cmd('Runtime.evaluate', { expression: 'document.fonts.ready.then(()=>true)', awaitPromise: true });
  await cmd('Runtime.evaluate', { expression: 'Promise.all([...document.images].map(i=>i.complete?1:new Promise(r=>{i.onload=i.onerror=r}))).then(()=>true)', awaitPromise: true });
  await sleep(300);
  const durR = await cmd('Runtime.evaluate', { expression: 'window.DUR||15000' });
  const DUR = (durR.result && durR.result.result && durR.result.result.value) || 15000;
  const N = Math.round(DUR * FPS / 1000);
  const t0 = Date.now();
  for (let i = 0; i < N; i++) {
    const t = Math.round(i * 1000 / FPS);
    await cmd('Runtime.evaluate', { expression: `frame(${t})` });
    const shot = await cmd('Page.captureScreenshot', { format: 'png', clip: { x: 0, y: 0, width: 1080, height: 1920, scale: 1 } });
    fs.writeFileSync(path.join(framesDir, `f${String(i).padStart(4, '0')}.png`), Buffer.from(shot.result.data, 'base64'));
  }
  console.log(`${KEY}: ${N} frames in ${((Date.now()-t0)/1000).toFixed(1)}s`);
  ws.close(); chrome.kill(); process.exit(0);
})().catch(e => { console.error(e); chrome.kill(); process.exit(1); });
