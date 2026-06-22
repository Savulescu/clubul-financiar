// make_reel.js <slug> — construieste un reel hook-first cu voce RO (Ioana), sincronizat.
// Pipeline: say (VO/beat) -> masoara durata -> timeline -> randare CDP cadru-cu-cadru -> ffmpeg (cadre + voce + muzica).
const { spawnSync, spawn } = require('child_process');
const fs = require('fs'); const path = require('path');
const DIR = __dirname;
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const FPS = 30, PORT = 9344;
const slug = process.argv[2];
if (!slug) { console.error("usage: node make_reel.js <slug>"); process.exit(1); }
const reels = JSON.parse(fs.readFileSync(path.join(DIR,'reels.json')));
const reel = reels[slug]; if (!reel) { console.error("slug necunoscut:", slug); process.exit(1); }
const work = path.join('/tmp','reel_'+slug); fs.rmSync(work,{recursive:true,force:true}); fs.mkdirSync(work,{recursive:true});
const framesDir = path.join(work,'frames'); fs.mkdirSync(framesDir);

function sh(cmd,args){ const r=spawnSync(cmd,args,{encoding:'utf8'}); if(r.status!==0){console.error(cmd,args.join(' '),r.stderr);} return r; }
function dur(f){ const r=spawnSync('ffprobe',['-v','quiet','-show_entries','format=duration','-of','csv=p=0',f],{encoding:'utf8'}); return parseFloat(r.stdout.trim())||0; }

// 1) VO per beat (Ioana), masoara, construieste timeline
const LEAD=0.3, TAIL=0.34, ENDPAD=0.5;
let beats=reel.beats.map((b,i)=>({...b}));
let cum=LEAD; const segWavs=[];
beats.forEach((b,i)=>{
  const aiff=path.join(work,`vo${i}.aiff`), wav=path.join(work,`vo${i}.wav`), seg=path.join(work,`seg${i}.wav`);
  sh('say',['-v','Ioana','-r','190','-o',aiff,b.vo||'']);
  sh('ffmpeg',['-y','-i',aiff,'-ar','48000','-ac','2',wav]);
  const vd=dur(wav); const bd=Math.max(vd+TAIL, 1.9);   // beat min 2.2s
  // seg = vo + silenta pana la durata beat-ului
  sh('ffmpeg',['-y','-i',wav,'-af',`apad=pad_dur=${(bd-vd).toFixed(3)}`,'-t',bd.toFixed(3),seg]);
  segWavs.push(seg);
  b.start=+cum.toFixed(3); b.dur=+bd.toFixed(3); cum+=bd;
});
const TOTAL=+(cum+ENDPAD).toFixed(2);
console.log(`${slug}: ${beats.length} beats, TOTAL ${TOTAL}s`);

// 2) audio: lead silence + segmente concat -> voce; apoi mix cu muzica soft (pad sintetic)
const leadSil=path.join(work,'lead.wav');
sh('ffmpeg',['-y','-f','lavfi','-i',`anullsrc=r=48000:cl=stereo`,'-t',LEAD.toFixed(3),leadSil]);
const endSil=path.join(work,'end.wav');
sh('ffmpeg',['-y','-f','lavfi','-i',`anullsrc=r=48000:cl=stereo`,'-t',ENDPAD.toFixed(3),endSil]);
const listF=path.join(work,'list.txt');
fs.writeFileSync(listF,[leadSil,...segWavs,endSil].map(f=>`file '${f}'`).join('\n'));
const voice=path.join(work,'voice.wav');
sh('ffmpeg',['-y','-f','concat','-safe','0','-i',listF,'-c','copy',voice]);
// muzica soft: 2 sine joase (acord) filtrate + tremolo, volum mic, fade
const music=path.join(work,'music.wav');
sh('ffmpeg',['-y','-f','lavfi','-i',`sine=frequency=146.83:duration=${TOTAL}`,'-f','lavfi','-i',`sine=frequency=220:duration=${TOTAL}`,
  '-filter_complex',`[0:a]volume=0.10[a];[1:a]volume=0.07[b];[a][b]amix=inputs=2,lowpass=f=380,tremolo=f=0.18:d=0.25,afade=t=in:d=1.2,afade=t=out:st=${(TOTAL-1.4).toFixed(2)}:d=1.4[m]`,
  '-map','[m]','-ar','48000','-ac','2',music]);
const audio=path.join(work,'audio.wav');
sh('ffmpeg',['-y','-i',voice,'-i',music,'-filter_complex','[0:a]volume=1.0[v];[1:a]volume=0.5[m];[v][m]amix=inputs=2:duration=first:dropout_transition=0[out]','-map','[out]','-ar','48000','-ac','2',audio]);

// 3) randare cadre via CDP
const N=Math.round(TOTAL*FPS);
const chrome=spawn(CHROME,['--headless=new','--use-angle=swiftshader','--disable-gpu','--hide-scrollbars',
  `--remote-debugging-port=${PORT}`,'--window-size=1080,1920','--force-device-scale-factor=1',
  '--user-data-dir=/tmp/cf_cdp2',`file://${DIR}/scene.html?static`],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let nextId=1; const pend={};
function send(ws,method,params){return new Promise((res)=>{const id=nextId++;pend[id]=res;ws.send(JSON.stringify({id,method,params:params||{}}));});}
(async()=>{
  // ws url
  let wsUrl; for(let i=0;i<80;i++){try{const r=await fetch(`http://localhost:${PORT}/json`);const l=await r.json();const p=l.find(t=>t.type==='page'&&t.webSocketDebuggerUrl);if(p){wsUrl=p.webSocketDebuggerUrl;break;}}catch(e){}await sleep(200);}
  const ws=new WebSocket(wsUrl);
  await new Promise(r=>ws.addEventListener('open',r));
  ws.addEventListener('message',ev=>{const m=JSON.parse(ev.data);if(m.id&&pend[m.id]){pend[m.id](m.result);delete pend[m.id];}});
  await send(ws,'Page.enable'); await send(ws,'Runtime.enable');
  await sleep(900); // fonturi
  await send(ws,'Runtime.evaluate',{expression:`window.BEATS=${JSON.stringify(beats)};window.TOTAL=${TOTAL};document.fonts.ready`});
  await sleep(500);
  for(let i=0;i<N;i++){
    const t=i/FPS;
    await send(ws,'Runtime.evaluate',{expression:`frame(${t})`});
    const r=await send(ws,'Page.captureScreenshot',{format:'png',clip:{x:0,y:0,width:1080,height:1920,scale:1}});
    fs.writeFileSync(path.join(framesDir,`f${String(i).padStart(4,'0')}.png`),Buffer.from(r.data,'base64'));
    if(i%30===0)process.stdout.write('.');
  }
  console.log(' randat '+N+' cadre');
  ws.close(); chrome.kill();
  await sleep(400);
  // 4) ffmpeg final
  const out=path.join(DIR,`reel_${slug}.mp4`);
  const r=spawnSync('ffmpeg',['-y','-framerate',String(FPS),'-i',path.join(framesDir,'f%04d.png'),'-i',audio,
    '-c:v','libx264','-pix_fmt','yuv420p','-profile:v','high','-crf','19','-preset','medium',
    '-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',out],{encoding:'utf8'});
  if(r.status===0){console.log('GATA -> '+out+' ('+(fs.statSync(out).size/1e6).toFixed(1)+' MB, '+TOTAL+'s)');}
  else console.error('ffmpeg final FAIL',r.stderr.slice(-400));
  process.exit(0);
})();
