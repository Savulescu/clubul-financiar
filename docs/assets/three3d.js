/* Clubul Financiar — hero 3D pe TEMĂ: grafic de creștere financiară (bare + linie care urcă)
   pe o grilă tip trading-floor, cu glow (bloom). Three.js + postprocessing prin importmap.
   Off pe mobil / reduced-motion / save-data. */
(async function () {
  const mount = document.getElementById("hero3d");
  if (!mount) return;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const saveData = navigator.connection && navigator.connection.saveData;
  if (reduce || saveData || innerWidth < 880) return;
  try { if (!document.createElement("canvas").getContext("webgl2") && !document.createElement("canvas").getContext("webgl")) return; }
  catch (e) { return; }

  let THREE, EffectComposer, RenderPass, UnrealBloomPass;
  try {
    THREE = await import("three");
    ({ EffectComposer } = await import("three/addons/postprocessing/EffectComposer.js"));
    ({ RenderPass } = await import("three/addons/postprocessing/RenderPass.js"));
    ({ UnrealBloomPass } = await import("three/addons/postprocessing/UnrealBloomPass.js"));
  } catch (e) { return; }

  const W = () => mount.clientWidth || 1, H = () => mount.clientHeight || 1;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(W(), H());
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  mount.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x081226, 0.052);
  const camera = new THREE.PerspectiveCamera(42, W() / H(), 0.1, 100);
  camera.position.set(-0.2, 2.4, 9);

  // mediu pt reflexii brand
  function envTexture() {
    const c = document.createElement("canvas"); c.width = 512; c.height = 256;
    const x = c.getContext("2d");
    const g = x.createLinearGradient(0, 0, 0, 256);
    g.addColorStop(0, "#0e2750"); g.addColorStop(0.45, "#123a5e"); g.addColorStop(0.72, "#36D67E"); g.addColorStop(1, "#E8C268");
    x.fillStyle = g; x.fillRect(0, 0, 512, 256);
    const r = x.createRadialGradient(380, 60, 6, 380, 60, 160);
    r.addColorStop(0, "rgba(255,255,255,.9)"); r.addColorStop(1, "rgba(255,255,255,0)");
    x.fillStyle = r; x.fillRect(0, 0, 512, 256);
    const t = new THREE.CanvasTexture(c); t.mapping = THREE.EquirectangularReflectionMapping; t.colorSpace = THREE.SRGBColorSpace; return t;
  }
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromEquirectangular(envTexture()).texture;

  scene.add(new THREE.AmbientLight(0xffffff, 0.35));
  const key = new THREE.DirectionalLight(0xfff0d6, 1.0); key.position.set(3, 8, 6); scene.add(key);
  const fill = new THREE.PointLight(0xE8C268, 42, 40); fill.position.set(-4, 3, 4); scene.add(fill);
  const fill2 = new THREE.PointLight(0x36D67E, 34, 40); fill2.position.set(5, 1, 4); scene.add(fill2);

  const chart = new THREE.Group();
  chart.position.set(1.0, -1.2, 0);
  chart.rotation.y = -0.32;
  scene.add(chart);

  // grilă „trading floor"
  const grid = new THREE.GridHelper(46, 46, 0x2bd4a0, 0x163a5e);
  grid.material.transparent = true; grid.material.opacity = 0.5;
  chart.add(grid);

  // bare care cresc (emerald -> auriu)
  const cE = new THREE.Color(0x36D67E), cG = new THREE.Color(0xE8C268);
  const heights = [0.7, 1.0, 0.9, 1.5, 1.75, 1.6, 2.15, 2.5, 2.8]; // 9 bare; ultima = dinamică (live)
  const LAST = heights.length - 1;
  const gap = 0.8, bw = 0.46;
  const bars = [];
  const topPts = [];
  heights.forEach((h, i) => {
    const col = cE.clone().lerp(cG, i / (heights.length - 1));
    const m = new THREE.Mesh(
      new THREE.BoxGeometry(bw, 1, bw),
      new THREE.MeshStandardMaterial({ color: col, emissive: col, emissiveIntensity: 0.5, metalness: 0.6, roughness: 0.22, envMapIntensity: 1.2 })
    );
    const x = i * gap;
    m.position.set(x, 0.0005, 0);
    m.userData = { h, x };
    chart.add(m);
    bars.push(m);
    topPts.push(new THREE.Vector3(x, h, 0));
  });
  const lastBar = bars[LAST], lastX = topPts[LAST].x, prevTop = topPts[LAST - 1];

  const cUp = new THREE.Color(0x36D67E), cDown = new THREE.Color(0xff5874);
  // linia STATICĂ prin start + barele 1..8 (penultima)
  const staticPts = [new THREE.Vector3(-0.6, 0.45, 0), ...topPts.slice(0, LAST)];
  const nodeMat = new THREE.MeshBasicMaterial({ color: 0xeafff6 });
  const nodeGeo = new THREE.SphereGeometry(0.07, 16, 16);
  for (let i = 0; i < staticPts.length - 1; i++) {
    const a = staticPts[i], b = staticPts[i + 1];
    const up = b.y >= a.y - 0.001;
    chart.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.LineCurve3(a, b), 1, 0.05, 12, false), new THREE.MeshBasicMaterial({ color: up ? cUp : cDown })));
    if (i > 0) { const n = new THREE.Mesh(nodeGeo, nodeMat); n.position.copy(a); chart.add(n); }
  }
  const nodeP = new THREE.Mesh(nodeGeo, nodeMat); nodeP.position.copy(prevTop); chart.add(nodeP);

  // segment DINAMIC (penultima -> ultima bară care se mișcă) + vârf luminos + SĂGEATĂ
  const dynMat = new THREE.MeshBasicMaterial({ color: 0x36D67E });
  let dynSeg = new THREE.Mesh(new THREE.TubeGeometry(new THREE.LineCurve3(prevTop, topPts[LAST]), 1, 0.055, 12, false), dynMat);
  chart.add(dynSeg);
  const tip = new THREE.Mesh(new THREE.SphereGeometry(0.13, 24, 24), new THREE.MeshBasicMaterial({ color: 0xffffff }));
  chart.add(tip);
  function glowTex() {
    const c = document.createElement("canvas"); c.width = c.height = 128; const x = c.getContext("2d");
    const g = x.createRadialGradient(64, 64, 2, 64, 64, 64);
    g.addColorStop(0, "rgba(155,255,217,.95)"); g.addColorStop(0.4, "rgba(80,230,180,.4)"); g.addColorStop(1, "rgba(0,0,0,0)");
    x.fillStyle = g; x.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c);
  }
  const tipGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex(), transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false }));
  tipGlow.scale.set(2.2, 2.2, 1); chart.add(tipGlow);
  const arrowMat = new THREE.MeshBasicMaterial({ color: 0x36D67E });
  const arrow = new THREE.Mesh(new THREE.ConeGeometry(0.27, 0.62, 26), arrowMat);
  chart.add(arrow);

  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(W(), H()), 0.85, 0.7, 0.7);
  composer.addPass(bloom);

  let tx = 0, ty = 0, cx = 0, cy = 0;
  addEventListener("pointermove", e => { tx = e.clientX / innerWidth - 0.5; ty = e.clientY / innerHeight - 0.5; }, { passive: true });
  function resize() { camera.aspect = W() / H(); camera.updateProjectionMatrix(); renderer.setSize(W(), H()); composer.setSize(W(), H()); }
  addEventListener("resize", resize);

  let running = false, raf = 0, t0 = performance.now();
  function ease(x) { return 1 - Math.pow(1 - x, 3); }
  function loop() {
    if (!running) return;
    raf = requestAnimationFrame(loop);
    const t = (performance.now() - t0) / 1000;
    cx += (tx - cx) * 0.05; cy += (ty - cy) * 0.05;
    camera.position.x = -0.2 + cx * 1.4; camera.position.y = 2.4 - cy * 0.8; camera.lookAt(0.3, 0.95, 0);
    // barele cresc (staggered); ULTIMA e LIVE (oscilează sus-jos)
    bars.forEach((b, i) => {
      const g = ease(Math.min(1, Math.max(0, (t - i * 0.12) / 0.7)));
      if (i === LAST) {
        const osc = Math.sin(t * 1.5) * 0.62 * Math.min(1, Math.max(0, (t - 1.4)));
        const hh = Math.max(0.06, b.userData.h * g + osc);
        b.scale.y = hh; b.position.y = hh / 2; b.userData.curH = hh;
      } else {
        const breathe = 1 + Math.sin(t * 1.3 + i) * 0.025;
        const hh = b.userData.h * g * breathe;
        b.scale.y = Math.max(0.001, hh); b.position.y = b.scale.y / 2;
      }
    });
    // ultima bară + săgeata + segmentul dinamic (verde la urcare, roșu la coborâre)
    const curH = lastBar.userData.curH;
    const prevH = lastBar.userData.prevH != null ? lastBar.userData.prevH : curH;
    const rising = curH >= prevH;
    lastBar.userData.prevH = curH;
    const movingTop = new THREE.Vector3(lastX, curH, 0);
    const dirCol = rising ? cUp : cDown;
    dynSeg.geometry.dispose();
    dynSeg.geometry = new THREE.TubeGeometry(new THREE.LineCurve3(prevTop, movingTop), 1, 0.055, 12, false);
    dynMat.color.copy(dirCol);
    tip.position.copy(movingTop); tipGlow.position.copy(movingTop);
    arrow.position.set(lastX, curH + 0.6, 0);
    arrow.rotation.x = rising ? 0 : Math.PI;
    arrowMat.color.copy(dirCol);
    chart.rotation.y = -0.35 + Math.sin(t * 0.25) * 0.06;
    const pulse = 1 + Math.sin(t * 2.2) * 0.18;
    tipGlow.scale.set(2.2 * pulse, 2.2 * pulse, 1);
    composer.render();
  }
  function start() { if (!running) { running = true; t0 = performance.now(); loop(); } }
  function stop() { running = false; if (raf) cancelAnimationFrame(raf); raf = 0; }
  new IntersectionObserver(es => { es[0].isIntersecting ? start() : stop(); }, { threshold: 0 }).observe(mount);
  document.addEventListener("visibilitychange", () => { document.hidden ? stop() : start(); });
  start();
})();
