/* Clubul Financiar — hero 3D ultra-premium: bijuterie iridescentă fațetată + particule + bloom.
   Three.js + postprocessing prin importmap. Off pe mobil / reduced-motion / save-data. */
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
  renderer.toneMappingExposure = 1.15;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  mount.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, W() / H(), 0.1, 100);
  camera.position.set(0, 0, 7);

  // ---- mediu (reflexii pe culorile brandului) ----
  function envTexture() {
    const c = document.createElement("canvas"); c.width = 512; c.height = 256;
    const x = c.getContext("2d");
    const g = x.createLinearGradient(0, 0, 0, 256);
    g.addColorStop(0.0, "#0a1830"); g.addColorStop(0.42, "#0f3a52");
    g.addColorStop(0.6, "#10b981"); g.addColorStop(0.8, "#1d4ed8"); g.addColorStop(1.0, "#E8C268");
    x.fillStyle = g; x.fillRect(0, 0, 512, 256);
    const r = x.createRadialGradient(384, 64, 6, 384, 64, 150);
    r.addColorStop(0, "rgba(255,255,255,.95)"); r.addColorStop(1, "rgba(255,255,255,0)");
    x.fillStyle = r; x.fillRect(0, 0, 512, 256);
    const r2 = x.createRadialGradient(120, 200, 4, 120, 200, 120);
    r2.addColorStop(0, "rgba(232,194,104,.8)"); r2.addColorStop(1, "rgba(232,194,104,0)");
    x.fillStyle = r2; x.fillRect(0, 0, 512, 256);
    const t = new THREE.CanvasTexture(c);
    t.mapping = THREE.EquirectangularReflectionMapping; t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envRT = pmrem.fromEquirectangular(envTexture());
  scene.environment = envRT.texture;

  const group = new THREE.Group();
  group.position.x = 2.35;
  scene.add(group);

  // ---- bijuteria fațetată iridescentă ----
  const gem = new THREE.Mesh(
    new THREE.IcosahedronGeometry(1.9, 1),
    new THREE.MeshPhysicalMaterial({
      color: 0xeaf1ff, metalness: 1.0, roughness: 0.12,
      iridescence: 1.0, iridescenceIOR: 2.0, iridescenceThicknessRange: [100, 800],
      clearcoat: 1.0, clearcoatRoughness: 0.1, envMapIntensity: 1.8, flatShading: true,
      emissive: 0x07221c, emissiveIntensity: 0.5,
    })
  );
  group.add(gem);
  // halou luminos în spatele bijuteriei (amplificat de bloom)
  function haloTex() {
    const c = document.createElement("canvas"); c.width = c.height = 256;
    const x = c.getContext("2d");
    const g = x.createRadialGradient(128, 128, 4, 128, 128, 128);
    g.addColorStop(0, "rgba(120,240,200,.8)"); g.addColorStop(0.3, "rgba(232,194,104,.4)");
    g.addColorStop(0.6, "rgba(37,99,235,.16)"); g.addColorStop(1, "rgba(0,0,0,0)");
    x.fillStyle = g; x.fillRect(0, 0, 256, 256);
    return new THREE.CanvasTexture(c);
  }
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({
    map: haloTex(), color: 0xffffff, transparent: true, opacity: 0.6,
    blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false,
  }));
  halo.scale.set(6.4, 6.4, 1); halo.position.z = -2;
  group.add(halo);

  // ---- înveliș wireframe (adâncime/tech) ----
  const shell = new THREE.Mesh(
    new THREE.IcosahedronGeometry(2.35, 1),
    new THREE.MeshBasicMaterial({ color: 0x10b981, wireframe: true, transparent: true, opacity: 0.16 })
  );
  group.add(shell);
  const shell2 = new THREE.Mesh(
    new THREE.IcosahedronGeometry(2.9, 0),
    new THREE.MeshBasicMaterial({ color: 0xE8C268, wireframe: true, transparent: true, opacity: 0.09 })
  );
  group.add(shell2);

  // ---- particule ----
  const N = 700;
  const pos = new Float32Array(N * 3), spd = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    pos[i * 3] = (Math.random() - 0.35) * 16;
    pos[i * 3 + 1] = (Math.random() - 0.5) * 11;
    pos[i * 3 + 2] = (Math.random() - 0.5) * 10 - 1;
    spd[i] = 0.1 + Math.random() * 0.5;
  }
  const pg = new THREE.BufferGeometry();
  pg.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  const points = new THREE.Points(pg, new THREE.PointsMaterial({
    color: 0xF0D58A, size: 0.05, transparent: true, opacity: 0.85,
    blending: THREE.AdditiveBlending, depthWrite: false, sizeAttenuation: true,
  }));
  scene.add(points);

  // ---- lumini ----
  scene.add(new THREE.AmbientLight(0xffffff, 0.35));
  const key = new THREE.DirectionalLight(0xfff0d0, 1.1); key.position.set(4, 5, 6); scene.add(key);
  const pEm = new THREE.PointLight(0x10b981, 60, 30); scene.add(pEm);
  const pBl = new THREE.PointLight(0x2563eb, 55, 30); scene.add(pBl);
  const pGo = new THREE.PointLight(0xE8C268, 45, 30); scene.add(pGo);

  // ---- bloom ----
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(W(), H()), 0.9, 0.75, 0.78);
  composer.addPass(bloom);

  // ---- interacțiune + resize ----
  let tx = 0, ty = 0, cx = 0, cy = 0;
  addEventListener("pointermove", e => { tx = e.clientX / innerWidth - 0.5; ty = e.clientY / innerHeight - 0.5; }, { passive: true });
  function resize() {
    camera.aspect = W() / H(); camera.updateProjectionMatrix();
    renderer.setSize(W(), H()); composer.setSize(W(), H());
  }
  addEventListener("resize", resize);

  let running = false, raf = 0, t0 = performance.now();
  function loop() {
    if (!running) return;
    raf = requestAnimationFrame(loop);
    const t = (performance.now() - t0) / 1000;
    cx += (tx - cx) * 0.05; cy += (ty - cy) * 0.05;
    camera.position.x = cx * 1.6; camera.position.y = -cy * 1.0; camera.lookAt(0.9, 0, 0);
    gem.rotation.y = t * 0.28; gem.rotation.x = Math.sin(t * 0.3) * 0.25;
    group.position.y = Math.sin(t * 0.5) * 0.18;
    shell.rotation.y = -t * 0.18; shell.rotation.x = t * 0.1;
    shell2.rotation.y = t * 0.12; shell2.rotation.z = -t * 0.08;
    pEm.position.set(Math.cos(t * 0.7) * 4 + 2.3, Math.sin(t * 0.6) * 3, Math.sin(t * 0.7) * 3 + 2);
    pBl.position.set(Math.cos(t * 0.5 + 2) * 4 + 2.3, Math.sin(t * 0.8 + 1) * 3, Math.cos(t * 0.6) * 3 + 2);
    pGo.position.set(Math.cos(t * 0.9 + 4) * 3 + 2.3, Math.cos(t * 0.5) * 3, Math.sin(t * 0.4) * 3 + 1);
    const p = pg.attributes.position.array;
    for (let i = 0; i < N; i++) {
      p[i * 3 + 1] += spd[i] * 0.012;
      if (p[i * 3 + 1] > 5.5) p[i * 3 + 1] = -5.5;
    }
    pg.attributes.position.needsUpdate = true;
    composer.render();
  }
  function start() { if (!running) { running = true; loop(); } }
  function stop() { running = false; if (raf) cancelAnimationFrame(raf); raf = 0; }
  new IntersectionObserver(es => { es[0].isIntersecting ? start() : stop(); }, { threshold: 0 }).observe(mount);
  document.addEventListener("visibilitychange", () => { document.hidden ? stop() : start(); });
  start();
})();
