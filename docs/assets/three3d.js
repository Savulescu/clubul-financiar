/* Clubul Financiar — scenă 3D în hero: monede aurii care plutesc, smooth.
   Three.js încărcat async; dezactivat pe mobil / reduced-motion / save-data. */
(function () {
  const mount = document.getElementById("hero3d");
  if (!mount) return;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const saveData = navigator.connection && navigator.connection.saveData;
  if (reduce || saveData || innerWidth < 880) return;
  let supported = false;
  try { supported = !!document.createElement("canvas").getContext("webgl"); } catch (e) {}
  if (!supported) return;

  import("https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js")
    .then(init).catch(() => {});

  function init(THREE) {
    const W = () => mount.clientWidth || 1, H = () => mount.clientHeight || 1;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(38, W() / H(), 0.1, 100);
    camera.position.set(0, 0, 11);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.setSize(W(), H());
    mount.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.55));
    const key = new THREE.DirectionalLight(0xfff2cc, 1.6); key.position.set(5, 6, 8); scene.add(key);
    const rim = new THREE.DirectionalLight(0x10b981, 0.95); rim.position.set(-6, -2, 4); scene.add(rim);
    const rim2 = new THREE.DirectionalLight(0x2563eb, 0.7); rim2.position.set(-3, 5, -4); scene.add(rim2);

    function euroTex() {
      const c = document.createElement("canvas"); c.width = c.height = 256;
      const x = c.getContext("2d");
      x.fillStyle = "#d9b259"; x.beginPath(); x.arc(128, 128, 128, 0, 7); x.fill();
      x.fillStyle = "rgba(120,90,20,.55)"; x.font = "bold 168px Georgia, 'Times New Roman', serif";
      x.textAlign = "center"; x.textBaseline = "middle"; x.fillText("€", 128, 146);
      const t = new THREE.CanvasTexture(c); t.anisotropy = 4; return t;
    }
    const faceMat = new THREE.MeshStandardMaterial({ map: euroTex(), metalness: 0.85, roughness: 0.32, color: 0xE8C268 });
    const bodyMat = new THREE.MeshStandardMaterial({ color: 0xE8C268, metalness: 0.9, roughness: 0.3 });
    const rimMat = new THREE.MeshStandardMaterial({ color: 0xd4af52, metalness: 0.95, roughness: 0.22 });
    const bodyGeo = new THREE.CylinderGeometry(1, 1, 0.16, 50);
    const rimGeo = new THREE.TorusGeometry(1, 0.07, 18, 50);
    const faceGeo = new THREE.CircleGeometry(0.9, 50);

    function makeCoin() {
      const g = new THREE.Group();
      const body = new THREE.Mesh(bodyGeo, bodyMat); body.rotation.x = Math.PI / 2; g.add(body);
      g.add(new THREE.Mesh(rimGeo, rimMat));
      const f1 = new THREE.Mesh(faceGeo, faceMat); f1.position.z = 0.085; g.add(f1);
      const f2 = new THREE.Mesh(faceGeo, faceMat); f2.position.z = -0.085; f2.rotation.y = Math.PI; g.add(f2);
      return g;
    }
    const defs = [
      { x: 3.1, y: 1.3, z: 0, s: 1.55, rs: 0.45 },
      { x: 4.7, y: -1.3, z: -2, s: 1.05, rs: 0.7 },
      { x: 1.7, y: -1.9, z: -1, s: 0.8, rs: 0.6 },
      { x: 5.5, y: 1.9, z: -3, s: 0.72, rs: 0.85 },
      { x: 2.5, y: 2.3, z: -2.4, s: 0.6, rs: 0.8 },
      { x: 0.3, y: 0.9, z: -3.2, s: 0.55, rs: 0.55 },
      { x: 3.9, y: -2.5, z: -1.6, s: 0.62, rs: 0.7 },
    ];
    const coins = defs.map(d => {
      const c = makeCoin(); c.position.set(d.x, d.y, d.z); c.scale.setScalar(d.s);
      c.userData = Object.assign({}, d, { ph: Math.random() * 6.28 });
      scene.add(c); return c;
    });

    let tx = 0, ty = 0, cx = 0, cy = 0;
    addEventListener("pointermove", e => { tx = e.clientX / innerWidth - 0.5; ty = e.clientY / innerHeight - 0.5; }, { passive: true });

    function resize() { camera.aspect = W() / H(); camera.updateProjectionMatrix(); renderer.setSize(W(), H()); }
    addEventListener("resize", resize);

    let running = false, raf = 0, t0 = performance.now();
    function loop() {
      if (!running) return;
      raf = requestAnimationFrame(loop);
      const t = (performance.now() - t0) / 1000;
      cx += (tx - cx) * 0.05; cy += (ty - cy) * 0.05;
      camera.position.x = cx * 1.7; camera.position.y = -cy * 1.05; camera.lookAt(2.6, 0, -1);
      for (const c of coins) {
        c.rotation.y = t * c.userData.rs;
        c.rotation.z = Math.sin(t * 0.5 + c.userData.ph) * 0.12;
        c.position.y = c.userData.y + Math.sin(t * 0.6 + c.userData.ph) * 0.2;
      }
      renderer.render(scene, camera);
    }
    function start() { if (!running) { running = true; loop(); } }
    function stop() { running = false; if (raf) cancelAnimationFrame(raf); raf = 0; }

    new IntersectionObserver(es => { es[0].isIntersecting ? start() : stop(); }, { threshold: 0 }).observe(mount);
    document.addEventListener("visibilitychange", () => { document.hidden ? stop() : start(); });
    start();
  }
})();
