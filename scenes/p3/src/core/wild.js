// Golden-hour pine forest with a dirt trail, and a sculpted grizzly bear (posable: walk / gallop / head / jaw).
// forest(E) -> { scene, key, aim(center, box), update(t) } · trailX(z) = trail centre line · new Bear()
import * as THREE from 'three';
import { ellipsoid, capsule, sphere, smin, smax, ssub, noise3, mesh, rgb, len } from './sdf.js';
import { SHADOW } from './engine.js';

const D = THREE.MathUtils.degToRad;
const mixc = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
const ss = (a, b, x) => { const t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const R = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
export const trailX = (z) => 0.7 * Math.sin(z * 0.07) + 0.25 * Math.sin(z * 0.19 + 1);

function canvasTex(w, h, draw, rep = [1, 1]) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...rep); t.anisotropy = 8; return t; }

// cone along +y: base radius r at y0, apex at y0 + h
function cone(p, y0, h, r) { const q = Math.hypot(p[0], p[2]), y = p[1] - y0; return Math.max((q * h - (h - y) * r) / Math.hypot(h, r), -y); }

function pineGeo(step, seed = 0) {
  const f = (p) => {
    let d = capsule(p, [0, 0, 0], [0, 0.5, 0], 0.016, 0.009);
    const a = Math.atan2(p[2], p[0]);
    for (let i = 0; i < 7; i++) {
      const y0 = 0.3 + i * 0.095, r = 0.16 * (1 - i / 8.2), h = 0.17 + (i === 6 ? 0.1 : 0);
      const q = [p[0], p[1], p[2]];
      d = smin(d, cone(q, y0, h, r), 0.025);
    }
    return d;
  };
  const dark = rgb('#1F4335'), mid = rgb('#285640'), tip = rgb('#33694B'), bark = rgb('#4A3030');
  return mesh(f, [[-0.27, -0.02, -0.27], [0.27, 1.02, 0.27]], step, (p) => {
    const q = Math.hypot(p[0], p[2]); if (q < 0.025 && p[1] < 0.42) return bark;
    const k = ss(0.04, 0.2, q) * 0.7 + ss(0.6, 1.0, p[1]) * 0.3;
    return k < 0.5 ? mixc(dark, mid, k * 2) : mixc(mid, tip, (k - 0.5) * 2);
  });
}
function rockGeo() {
  return mesh((p) => ellipsoid(p, [0, 0.1, 0], [0.5, 0.32, 0.4]) + 0.05 * noise3(p[0] * 3, p[1] * 3, p[2] * 3),
    [[-0.65, -0.3, -0.55], [0.65, 0.5, 0.55]], 0.03, (p) => mixc(rgb('#6F6A80'), rgb('#9A95A8'), ss(0, 0.35, p[1])));
}
function bushGeo() {
  return mesh((p) => {
    let d = ellipsoid(p, [0, 0.3, 0], [0.6, 0.4, 0.55]);
    for (let i = 0; i < 6; i++) d = smin(d, sphere(p, [Math.cos(i * 1.1) * 0.45, 0.25 + R(i) * 0.25, Math.sin(i * 1.1) * 0.4], 0.28), 0.12);
    return d;
  }, [[-0.95, -0.05, -0.9], [0.95, 0.85, 0.9]], 0.03, (p) => mixc(rgb('#2C5A3C'), rgb('#4E8350'), ss(0.1, 0.7, p[1])));
}
// grass clump: tapered bent blades, built directly as triangles (cheap)
function grassGeo(n = 11) {
  const pos = [], col = [], base = rgb('#3E4A22'), tip = rgb('#C9B46A');
  for (let b = 0; b < n; b++) {
    const a = R(b + 3) * 6.28, lean = 0.25 + R(b + 9) * 0.5, h = 0.28 + R(b + 5) * 0.32, w = 0.018, ox = Math.cos(a) * 0.06 * R(b), oz = Math.sin(a) * 0.06 * R(b + 1);
    const P = (t, s) => [ox + Math.cos(a) * lean * h * t * t + s * w * (1 - t) * Math.sin(a), h * t, oz + Math.sin(a) * lean * h * t * t - s * w * (1 - t) * Math.cos(a)];
    for (let k = 0; k < 3; k++) {
      const t0 = k / 3, t1 = (k + 1) / 3, a0 = P(t0, -1), b0 = P(t0, 1), a1 = P(t1, -1), b1 = P(t1, 1);
      pos.push(...a0, ...b0, ...b1, ...a0, ...b1, ...a1);
      for (const t of [t0, t0, t1, t0, t1, t1]) col.push(...mixc(base, tip, t));
    }
  }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); g.computeVertexNormals(); return g;
}
function instanced(geo, mat, list, shadow = true) {
  const m = new THREE.InstancedMesh(geo, mat, list.length), o = new THREE.Object3D();
  list.forEach((it, i) => { o.position.set(it.x, it.y || 0, it.z); o.rotation.set(it.rx || 0, it.ry || 0, it.rz || 0); o.scale.set(it.sx ?? it.s, it.sy ?? it.s, it.sz ?? it.s); o.updateMatrix(); m.setMatrixAt(i, o.matrix); });
  m.castShadow = shadow; m.receiveShadow = true; return m;
}

export function forest(E) {
  const scene = new THREE.Scene(); scene.environment = E.envMap; scene.environmentIntensity = 0.25;
  scene.background = canvasTex(32, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#46578A'); gr.addColorStop(0.38, '#8A8AB2'); gr.addColorStop(0.5, '#D8B8AC'); gr.addColorStop(0.56, '#E9C6A8'); gr.addColorStop(1, '#6E8A5C'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  scene.fog = new THREE.Fog('#B9A9C0', 22, 95);
  const SUN = new THREE.Vector3(-0.45, 0.7, -0.4).normalize();

  // ground: big plane, vertex-coloured large-scale variation over a fine litter texture
  const litter = canvasTex(1024, 1024, (g, w, h) => {
    g.fillStyle = '#6F6A3C'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 9000; i++) { const l = R(i) * 60; g.fillStyle = `rgba(${70 + l},${68 + l * 0.8},${30 + l * 0.3},0.5)`; g.save(); g.translate(R(i + 1) * w, R(i + 2) * h); g.rotate(R(i + 3) * 6.3); g.fillRect(0, 0, 4 + R(i + 4) * 22, 2); g.restore(); }
    for (let i = 0; i < 600; i++) { g.fillStyle = `rgba(40,45,20,${0.15 + R(i + 7) * 0.2})`; g.beginPath(); g.arc(R(i + 8) * w, R(i + 9) * h, 6 + R(i + 10) * 26, 0, 7); g.fill(); }
  }, [40, 40]);
  const gg = new THREE.PlaneGeometry(200, 200, 160, 160); gg.rotateX(-Math.PI / 2);
  { const p = gg.attributes.position, c = []; for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i), dt = Math.abs(x - trailX(z)); p.setY(i, -0.02); const n = noise3(x * 0.06, 1, z * 0.06) * 0.5 + 0.5; c.push(...mixc(rgb('#3F6E3E'), rgb('#5E9150'), n)); } gg.setAttribute('color', new THREE.Float32BufferAttribute(c, 3)); gg.computeVertexNormals(); }
  const ground = new THREE.Mesh(gg, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 1 })); ground.receiveShadow = true; scene.add(ground);
  // trail: ribbon with soft edges
  const dirt = canvasTex(256, 1024, (g, w, h) => {
    const gr = g.createLinearGradient(0, 0, w, 0); gr.addColorStop(0, 'rgba(196,150,112,0)'); gr.addColorStop(0.22, 'rgba(196,150,112,0.95)'); gr.addColorStop(0.78, 'rgba(196,150,112,0.95)'); gr.addColorStop(1, 'rgba(196,150,112,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 0; i++) { const x = 40 + R(i) * (w - 80), y = R(i + 1) * h, l = R(i + 2); g.fillStyle = l > 0.5 ? `rgba(215,190,150,${0.25 + l * 0.3})` : `rgba(110,82,55,${0.2 + l * 0.4})`; g.beginPath(); g.arc(x, y, 1 + R(i + 3) * 3.5, 0, 7); g.fill(); }
  }, [1, 30]);
  { const pos = [], uv = [], idx = [], N = 400, z0 = -110, z1 = 40, half = 1.15;
    for (let i = 0; i <= N; i++) { const z = z0 + (z1 - z0) * i / N, x = trailX(z); pos.push(x - half, 0.005, z, x + half, 0.005, z); uv.push(0, i / N, 1, i / N); if (i < N) { const a = i * 2; idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); } }
    const tg = new THREE.BufferGeometry(); tg.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); tg.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); tg.setIndex(idx); tg.computeVertexNormals();
    const tr = new THREE.Mesh(tg, new THREE.MeshStandardMaterial({ map: dirt, transparent: true, roughness: 0.95, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2 })); tr.receiveShadow = true; scene.add(tr); }

  // trees: detailed near the trail, cheap ones further out
  const treeM = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.9 });
  const near = [], far = [];
  for (let i = 0; i < 900; i++) {
    const z = -100 + R(i) * 135, side = R(i + 50) < 0.5 ? -1 : 1, dx = 4.2 + Math.pow(R(i + 99), 1.6) * 40, x = trailX(z) + side * dx, s = 9 + R(i + 7) * 9;
    if (z > -14 && z < -6 && side < 0 && dx < 7) continue;       // a clearing where the bear comes out
    (dx < 14 && z > -45 ? near : far).push({ x, z, s, sy: s * (0.9 + R(i + 3) * 0.3), ry: R(i + 4) * 6.3 });
  }
  scene.add(instanced(pineGeo(0.016, 1), treeM, near)); scene.add(instanced(pineGeo(0.035, 2), treeM, far, false));
  // rocks, bushes, grass
  const rocks = [], bushes = [], grass = [];
  for (let i = 0; i < 60; i++) { const z = -60 + R(i + 300) * 80, side = R(i + 301) < 0.5 ? -1 : 1; rocks.push({ x: trailX(z) + side * (1.6 + R(i + 302) * 9), z, s: 0.4 + R(i + 303) * 1.1, ry: R(i + 304) * 6, y: -0.05 }); }
  for (let i = 0; i < 110; i++) { const z = -60 + R(i + 400) * 80, side = R(i + 401) < 0.5 ? -1 : 1; bushes.push({ x: trailX(z) + side * (1.9 + R(i + 402) * 10), z, s: 0.6 + R(i + 403) * 0.9, ry: R(i + 404) * 6 }); }
  bushes.push({ x: trailX(-10) - 2.6, z: -10.6, s: 1.5, ry: 0.3 }, { x: trailX(-10) - 3.4, z: -9.2, s: 1.2, ry: 1.3 });   // the bear's cover
  for (let i = 0; i < 1400; i++) { const z = -60 + R(i + 600) * 85, side = R(i + 601) < 0.5 ? -1 : 1; grass.push({ x: trailX(z) + side * (1.0 + Math.pow(R(i + 602), 2) * 12), z, s: 0.7 + R(i + 603) * 0.9, ry: R(i + 604) * 6 }); }
  scene.add(instanced(rockGeo(), new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.85 }), rocks));
  scene.add(instanced(bushGeo(), new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.9 }), bushes));
  

  // sun disc + glow (bloom picks it up)
  const glowTex = canvasTex(256, 256, (g, w) => { const gr = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); gr.addColorStop(0, 'rgba(255,250,235,1)'); gr.addColorStop(0.12, 'rgba(255,236,190,1)'); gr.addColorStop(0.35, 'rgba(255,200,120,0.35)'); gr.addColorStop(1, 'rgba(255,170,90,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });
  const sun = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: new THREE.Color(2.2, 1.9, 1.5), fog: false, depthWrite: false, blending: THREE.AdditiveBlending })); sun.scale.setScalar(26);
  // light shafts through the trees (very faint additive cards)
  const shaftTex = canvasTex(64, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, w, 0); gr.addColorStop(0, 'rgba(255,220,160,0)'); gr.addColorStop(0.5, 'rgba(255,220,160,1)'); gr.addColorStop(1, 'rgba(255,220,160,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); const v = g.createLinearGradient(0, 0, 0, h); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(0.3, 'rgba(0,0,0,1)'); g.globalCompositeOperation = 'destination-in'; g.fillStyle = v; g.fillRect(0, 0, w, h); });
  const shafts = new THREE.Group();
  for (let i = 0; i < 9; i++) { const m = new THREE.Mesh(new THREE.PlaneGeometry(1.4 + R(i + 900) * 2.5, 30), new THREE.MeshBasicMaterial({ map: shaftTex, transparent: true, opacity: 0.05 + R(i + 901) * 0.05, blending: THREE.AdditiveBlending, depthWrite: false, fog: false, side: THREE.DoubleSide })); const z = -30 + i * 5 + R(i + 902) * 3; m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), SUN); m.position.set(trailX(z) - 3 + R(i + 903) * 8, 0, z).addScaledVector(SUN, 15); shafts.add(m); }
  // drifting dust motes in the light
  const N = 500, mp = new Float32Array(N * 3); for (let i = 0; i < N; i++) { mp[i * 3] = (R(i + 1000) - 0.5) * 14; mp[i * 3 + 1] = R(i + 1001) * 4; mp[i * 3 + 2] = -18 + R(i + 1002) * 26; }
  const mg = new THREE.BufferGeometry(); mg.setAttribute('position', new THREE.BufferAttribute(mp, 3));
  const dotTex = canvasTex(32, 32, (g) => { const gr = g.createRadialGradient(16, 16, 0, 16, 16, 16); gr.addColorStop(0, 'rgba(255,240,210,1)'); gr.addColorStop(1, 'rgba(255,240,210,0)'); g.fillStyle = gr; g.fillRect(0, 0, 32, 32); });
  const motes = new THREE.Points(mg, new THREE.PointsMaterial({ size: 0.035, map: dotTex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: '#FFE2B0', opacity: 0.8 }));

  // light: low warm sun (casts), cool sky fill, warm ground bounce
  const key = new THREE.DirectionalLight('#FFE6CC', 2.7); key.castShadow = true; key.shadow.mapSize.set(SHADOW, SHADOW); key.shadow.bias = -0.0005; key.shadow.normalBias = 0.03; key.shadow.radius = 9; scene.add(key, key.target);
  scene.add(new THREE.HemisphereLight('#D2CCEA', '#4A5C40', 1.9));
  const fill = new THREE.DirectionalLight('#FFE6C8', 0.7); fill.position.set(3, 4, 6); scene.add(fill);
  const aim = (c, box = 8) => {
    key.target.position.copy(c); key.position.copy(c).addScaledVector(SUN, 40);
    Object.assign(key.shadow.camera, { left: -box, right: box, top: box, bottom: -box, near: 1, far: 90 }); key.shadow.camera.updateProjectionMatrix();
    sun.position.copy(c).addScaledVector(SUN, 90);
  };
  aim(new THREE.Vector3(0, 0, -4), 12);
  return {
    scene, key, aim, SUN,
    update(t, cam) { motes.position.set(Math.sin(t * 0.3) * 0.4, Math.sin(t * 0.5) * 0.15, 0); if (cam) { motes.position.x += cam.position.x; motes.position.z += cam.position.z - 4; } motes.rotation.y = t * 0.02; },
  };
}

// ═════════════════════════ GRIZZLY ═════════════════════════
// faces +z, paws on y = 0. b.walk(ph) / b.gallop(ph, amt) / b.stand(); b.headYaw, b.headPitch, b.jaw (0..1) set before pose
export class Bear {
  constructor() {
    const base = rgb('#7A4A2C'), top = rgb('#9E6E46'), tipc = rgb('#B48256'), dark = rgb('#4E2F22'), muz = rgb('#D3A57A'), claw = rgb('#F1E6D2');
    this.mat = new THREE.MeshPhysicalMaterial({ vertexColors: true, roughness: 0.75, sheen: 0.6, sheenRoughness: 0.6, sheenColor: new THREE.Color('#F2CDA0') });
    const fur = (p, a = 0.014) => a * 0.25 * noise3(p[0] * 9, p[1] * 9, p[2] * 9);
    const add = (parent, geo, pos = [0, 0, 0]) => { const m = new THREE.Mesh(geo, this.mat); m.castShadow = m.receiveShadow = true; m.position.set(...pos); parent.add(m); return m; };
    const G = (parent, pos) => { const g = new THREE.Group(); g.position.set(...pos); parent.add(g); return g; };
    this.group = new THREE.Group();
    this.body = G(this.group, [0, 0.9, 0]);
    add(this.body, mesh((p) => {
      let d = ellipsoid(p, [0, 0.03, 0.3], [0.36, 0.4, 0.4]);
      d = smin(d, ellipsoid(p, [0, 0.0, -0.3], [0.34, 0.37, 0.4]), 0.14);
      d = smin(d, ellipsoid(p, [0, -0.1, 0], [0.31, 0.29, 0.45]), 0.12);
      d = smin(d, ellipsoid(p, [0, 0.34, 0.24], [0.27, 0.21, 0.3]), 0.14);                      // shoulder hump
      d = smin(d, capsule(p, [0, 0.16, 0.46], [0, 0.13, 0.72], 0.27, 0.21), 0.1);              // neck
      for (const s of [-1, 1]) { d = smin(d, ellipsoid(p, [s * 0.2, -0.12, 0.36], [0.15, 0.28, 0.19]), 0.08); d = smin(d, ellipsoid(p, [s * 0.19, -0.06, -0.38], [0.16, 0.29, 0.24]), 0.09); }
      d = smin(d, sphere(p, [0, 0.06, -0.7], 0.07), 0.05);
      return d + fur(p);
    }, [[-0.48, -0.5, -0.86], [0.48, 0.6, 0.98]], 0.013, (p) => {
      const n = noise3(p[0] * 9, p[1] * 9, p[2] * 9) * 0.5 + 0.5, g = ss(0.08, 0.45, p[1] + 0.12 * n) * (0.65 + 0.35 * ss(-0.3, 0.3, p[2]));
      let c = mixc(base, top, g); c = mixc(c, tipc, ss(0.75, 1, n) * g * 0.6); return mixc(c, dark, ss(-0.12, -0.38, p[1]));
    }));
    // head (pivot at the end of the neck)
    this.head = G(this.body, [0, 0.15, 0.76]); this.head.scale.setScalar(1.25);
    add(this.head, mesh((p) => {
      let d = ellipsoid(p, [0, 0.04, 0], [0.2, 0.18, 0.19]);
      for (const s of [-1, 1]) { d = smin(d, ellipsoid(p, [s * 0.1, -0.03, 0.02], [0.12, 0.12, 0.13]), 0.06); d = ssub(d, sphere(p, [s * 0.075, 0.07, 0.172], 0.024), 0.02); d = smin(d, ellipsoid(p, [s * 0.075, 0.108, 0.15], [0.06, 0.028, 0.05]), 0.03); }
      d = smin(d, capsule(p, [0, 0.0, 0.1], [0, -0.03, 0.31], 0.11, 0.075), 0.07);
      for (const s of [-1, 1]) { let e = sphere(p, [s * 0.14, 0.18, -0.05], 0.07); e = ssub(e, sphere(p, [s * 0.145, 0.185, 0.0], 0.045), 0.01); d = smin(d, e, 0.03); }
      return d + fur(p, 0.007);
    }, [[-0.28, -0.22, -0.25], [0.28, 0.3, 0.42]], 0.0085, (p) => {
      const ear = Math.hypot(Math.abs(p[0]) - 0.145, p[1] - 0.185, p[2]) < 0.06 && p[2] > -0.02;
      if (ear) return dark;
      return mixc(mixc(base, top, ss(0.0, 0.2, p[1]) * 0.7), muz, ss(0.15, 0.24, p[2]) * ss(0.06, -0.02, p[1]));
    }));
    const nose = new THREE.Mesh(new THREE.SphereGeometry(0.048, 24, 16), new THREE.MeshPhysicalMaterial({ color: '#141010', roughness: 0.25, clearcoat: 1 })); nose.scale.set(0.95, 0.62, 0.7); nose.position.set(0, -0.012, 0.37); this.head.add(nose);
    const eyeM = new THREE.MeshPhysicalMaterial({ color: '#1B0F08', roughness: 0.1, clearcoat: 1 });
    for (const s of [-1, 1]) { const e = new THREE.Mesh(new THREE.SphereGeometry(0.022, 20, 14), eyeM); e.position.set(s * 0.08, 0.068, 0.183); this.head.add(e); const hl = new THREE.Mesh(new THREE.SphereGeometry(0.006, 10, 8), new THREE.MeshBasicMaterial({ color: '#FFFFFF' })); hl.position.set(s * 0.08 - 0.007, 0.078, 0.203); this.head.add(hl); }
    // lower jaw + mouth + teeth
    this.jawG = G(this.head, [0, -0.06, 0.06]);
    add(this.jawG, mesh((p) => capsule(p, [0, -0.01, 0.0], [0, -0.025, 0.23], 0.06, 0.04) + fur(p, 0.004), [[-0.12, -0.14, -0.1], [0.12, 0.06, 0.32]], 0.008, (p) => mixc(dark, mixc(dark, muz, 0.5), ss(0.1, 0.2, p[2]))));
    const mouthM = new THREE.MeshStandardMaterial({ color: '#5A1C1E', roughness: 0.6 }), toothM = new THREE.MeshPhysicalMaterial({ color: '#F1EADB', roughness: 0.3, clearcoat: 0.6 });
    const mouth = new THREE.Mesh(new THREE.SphereGeometry(0.07, 20, 14), mouthM); mouth.scale.set(0.9, 0.55, 1.9); mouth.position.set(0, -0.055, 0.17); this.head.add(mouth);
    for (const s of [-1, 1]) {
      const up = new THREE.Mesh(new THREE.ConeGeometry(0.011, 0.05, 10), toothM); up.rotation.x = Math.PI; up.position.set(s * 0.045, -0.06, 0.29); this.head.add(up);
      
    }
    // legs: shoulder/hip pivot -> elbow/knee pivot
    const legGeo = (front) => {
      const up = mesh((p) => capsule(p, [0, 0.02, 0], [0, -0.36, front ? 0.02 : -0.04], front ? 0.14 : 0.16, 0.11) + fur(p, 0.01), [[-0.2, -0.54, -0.22], [0.2, 0.18, 0.2]], 0.012, (p) => mixc(base, dark, ss(-0.05, -0.3, p[1])));
      const lo = mesh((p) => {
        let d = capsule(p, [0, 0, 0], [0, -0.34, front ? 0 : 0.03], 0.098, 0.082);
        d = smin(d, ellipsoid(p, [0, -0.37, front ? 0.05 : 0.07], [0.1, 0.05, 0.14]), 0.05);
        d = smax(d, -(p[1] + 0.415), 0.01);
        if (front) for (let i = -1.5; i <= 1.5; i++) d = Math.min(d, capsule(p, [i * 0.04, -0.385, 0.16], [i * 0.045, -0.41, 0.24], 0.012, 0.004));
        return d + fur(p, 0.006) * ss(-0.32, -0.2, p[1]);
      }, [[-0.17, -0.44, -0.16], [0.17, 0.12, 0.28]], 0.009, (p) => (front && p[2] > 0.17 && p[1] < -0.37 ? claw : dark));
      return [up, lo];
    };
    const FG = legGeo(true), HG = legGeo(false);
    this.legs = {};
    for (const [k, s, front] of [['FL', -1, true], ['FR', 1, true], ['HL', -1, false], ['HR', 1, false]]) {
      const sh = G(this.body, front ? [s * 0.21, -0.13, 0.36] : [s * 0.2, -0.09, -0.38]); add(sh, (front ? FG : HG)[0]);
      const kn = G(sh, front ? [0, -0.36, 0.02] : [0, -0.36, -0.04]); add(kn, (front ? FG : HG)[1]);
      this.legs[k] = { sh, kn, front };
    }
    this.headYaw = 0; this.headPitch = 0; this.jaw = 0; this.stand();
  }
  _head(extraPitch = 0) { this.head.rotation.set(D(this.headPitch + extraPitch), D(this.headYaw), D(this.headYaw * -0.15)); this.jawG.rotation.x = D(this.jaw * 38); }
  stand() { for (const l of Object.values(this.legs)) { l.sh.rotation.set(0, 0, 0); l.kn.rotation.set(0, 0, 0); } this.body.position.set(0, 0.9, 0); this.body.rotation.set(0, 0, 0); this._head(); }
  /** walking, lateral sequence. ph in cycles */
  walk(ph, amt = 1) {
    const off = { HL: 0, FL: 0.25, HR: 0.5, FR: 0.75 };
    for (const [k, l] of Object.entries(this.legs)) {
      const a = (ph + off[k]) * Math.PI * 2, sw = Math.sin(a) * 22 * amt, lift = Math.max(0, Math.cos(a)) * amt;
      l.sh.rotation.set(-D(sw), 0, 0); l.kn.rotation.set(l.front ? D(lift * 45) : -D(lift * 25 - 5), 0, 0);
    }
    this.body.position.set(Math.sin(ph * Math.PI * 2) * 0.015 * amt, 0.9 - Math.abs(Math.sin(ph * Math.PI * 4)) * 0.012 * amt, 0);
    this.body.rotation.set(0, 0, Math.sin(ph * Math.PI * 2) * 0.03 * amt); this._head(Math.sin(ph * Math.PI * 4) * 2 * amt);
  }
  /** rotary gallop. ph in cycles */
  gallop(ph, amt = 1) {
    const off = { FL: 0, FR: 0.12, HL: 0.5, HR: 0.6 };
    for (const [k, l] of Object.entries(this.legs)) {
      const a = (ph + off[k]) * Math.PI * 2, sw = Math.sin(a) * (l.front ? 48 : 42) * amt, lift = Math.max(0, Math.cos(a)) * amt;
      l.sh.rotation.set(-D(sw), 0, 0); l.kn.rotation.set(l.front ? D(lift * 85) : -D(lift * 40) + D(Math.max(0, -Math.cos(a)) * 25 * amt), 0, 0);
    }
    const b = Math.sin(ph * Math.PI * 2 + 0.6);
    this.body.position.set(0, 0.88 + b * 0.07 * amt - 0.04 * amt, 0); this.body.rotation.set(D(-b * 7 * amt), 0, 0); this._head(b * 6 * amt);
  }
}

/** a soft dust puff texture for kicked-up dirt (sprites) */
export function dustPuffs(scene, n = 40) {
  const tex = canvasTex(64, 64, (g) => { const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(214,180,130,0.9)'); gr.addColorStop(1, 'rgba(214,180,130,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); });
  const list = []; for (let i = 0; i < n; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false, opacity: 0 })); scene.add(s); list.push(s); }
  /** emit along a path: src(i) -> { x, z, t0 }, t = now */
  return (t, events) => list.forEach((s, i) => {
    const e = events[i]; if (!e || t < e.t0) { s.material.opacity = 0; return; }
    const age = t - e.t0, k = Math.min(1, age / 1.4); s.position.set(e.x + (R(i) - 0.5) * age * 0.8, 0.15 + age * 0.35, e.z + (R(i + 1) - 0.5) * age * 0.5);
    s.scale.setScalar(0.4 + age * 1.1); s.material.opacity = 0.55 * (1 - k) * Math.min(1, age * 8);
  });
}
