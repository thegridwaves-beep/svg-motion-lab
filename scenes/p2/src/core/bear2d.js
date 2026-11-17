// Cartoon grizzly cut-out in the Tall Tale look (thick ink outline, flat colours, big expressive eyes) plus a
// low-poly pine forest set with a winding dirt trail.
//   new BearToon() : .set({ view: 'side'|'front', gait: 'stand'|'walk'|'run', phase, mouth 0..1, mood: 'calm'|'alert'|'angry', flip, bob })
//   forestSet(E) -> { scene, sun, trailX }
import * as THREE from 'three';
import { INK } from './toon.js';
import * as WD from './world.js';

const BR = '#8A5A34', BR2 = '#6E4527', BR3 = '#A87347', MUZ = '#D9AE7C', DARK = '#4A2E1C', CLAW = '#F2E6CF';
const LW = 11;

function eye(g, x, y, r, mood, lookx = 0, looky = 0, side = 1) {
  g.fillStyle = '#FFFFFF'; g.strokeStyle = INK; g.lineWidth = 6;
  const h = mood === 'angry' ? r * 0.72 : r;
  g.beginPath(); g.ellipse(x, y, r * 0.85, h, 0, 0, 7); g.fill(); g.stroke();
  g.fillStyle = INK; g.beginPath(); g.arc(x + lookx * r * 0.3, y + looky * r * 0.3 + (mood === 'angry' ? r * 0.1 : 0), r * 0.48, 0, 7); g.fill();
  g.fillStyle = '#FFFFFF'; g.beginPath(); g.arc(x + lookx * r * 0.3 - r * 0.15, y - r * 0.18, r * 0.14, 0, 7); g.fill();
  if (mood === 'angry' || mood === 'alert') {                       // brow
    g.strokeStyle = INK; g.lineWidth = 12; g.lineCap = 'round';
    const tilt = mood === 'angry' ? 0.45 : -0.1;
    g.beginPath(); g.moveTo(x - r * 1.0 * side, y - h - 14 - tilt * 30 * -1); g.lineTo(x + r * 0.9 * side, y - h - 14 + tilt * 30 * 1); g.stroke();
  }
}

function leg(g, x, y, len, ang, bend, col, near, front) {
  // two thick rounded segments (ink outline drawn as a wider stroke underneath), paw at the end
  const w = front ? 84 : 96, u = len * 0.52, l = len * 0.42;
  const kx = x + Math.sin(-ang) * -u, ky = y + Math.cos(ang) * u;
  const b2 = ang + bend, px = kx - Math.sin(b2) * l * -1 * -1, py = ky + Math.cos(b2) * l;
  const fx = kx + Math.sin(b2) * l * -1 + 0, fy = py;
  const P = [[x, y - 30], [kx, ky], [kx - Math.sin(b2) * l, ky + Math.cos(b2) * l]];
  const path = () => { g.beginPath(); g.moveTo(...P[0]); g.lineTo(...P[1]); g.lineTo(...P[2]); };
  g.lineCap = 'round'; g.lineJoin = 'round';
  g.strokeStyle = INK; g.lineWidth = w + 2 * LW; path(); g.stroke();
  g.strokeStyle = col; g.lineWidth = w; path(); g.stroke();
  const [ex, ey] = P[2];
  g.fillStyle = col; g.strokeStyle = INK; g.lineWidth = LW; g.beginPath(); g.ellipse(ex + 16, ey + 18, w * 0.62, w * 0.3, 0, 0, 7); g.fill(); g.stroke();
  if (near) { g.strokeStyle = CLAW; g.lineWidth = 7; for (let i = 0; i < 3; i++) { g.beginPath(); g.moveTo(ex + w * 0.5, ey + 8 + i * 10); g.lineTo(ex + w * 0.5 + 22, ey + 14 + i * 10); g.stroke(); } }
}

export function drawBear(g, st = {}) {
  const S = { view: 'side', gait: 'stand', phase: 0, mouth: 0, mood: 'calm', bob: 0, ...st };
  g.save(); g.lineCap = 'round'; g.lineJoin = 'round';
  if (S.flip) { g.translate(1024, 0); g.scale(-1, 1); }
  const ph = S.phase, run = S.gait === 'run', walk = S.gait === 'walk';
  const bounce = run ? Math.sin(ph * 2) * 22 : walk ? Math.abs(Math.sin(ph)) * 6 : 0;
  g.translate(0, -bounce + (S.bob || 0));
  if (S.view === 'side') {
    const pitch = run ? Math.sin(ph) * 0.06 : 0;
    g.translate(512, 760); g.rotate(pitch); g.translate(-512, -760);
    const sw = (o, amp) => (run || walk ? Math.sin(ph + o) * amp : 0), lift = (o) => (run || walk ? Math.max(0, Math.cos(ph + o)) * (run ? 1.1 : 0.6) : 0);
    const A = run ? 0.55 : 0.28;
    // far legs (darker)
    leg(g, 690, 690, 300, sw(0.6, A), lift(0.6), BR2, false, true);
    leg(g, 300, 680, 310, sw(Math.PI + 0.6, A), -lift(Math.PI + 0.6) * 0.5, BR2, false, false);
    // body
    const b = new Path2D();
    b.moveTo(180, 640);
    b.bezierCurveTo(150, 520, 260, 440, 420, 440);          // rump to back
    b.bezierCurveTo(520, 440, 560, 360, 650, 370);           // shoulder hump
    b.bezierCurveTo(760, 380, 820, 470, 830, 560);           // neck
    b.bezierCurveTo(840, 680, 790, 770, 700, 790);           // chest
    b.bezierCurveTo(560, 820, 380, 820, 270, 790);           // belly
    b.bezierCurveTo(200, 770, 190, 710, 180, 640); b.closePath();
    g.fillStyle = BR; g.fill(b);
    g.save(); g.clip(b);
    g.fillStyle = BR3; g.beginPath(); g.ellipse(600, 390, 170, 60, -0.1, 0, 7); g.fill();          // light hump
    g.fillStyle = BR2; g.beginPath(); g.ellipse(500, 860, 380, 110, 0, 0, 7); g.fill();            // shaded belly
    g.strokeStyle = BR2; g.lineWidth = 5; for (let i = 0; i < 7; i++) { const x = 300 + i * 70; g.beginPath(); g.moveTo(x, 520 + (i % 2) * 30); g.lineTo(x + 18, 548 + (i % 2) * 30); g.stroke(); }
    g.restore();
    g.strokeStyle = INK; g.lineWidth = LW; g.stroke(b);
    // tail nub
    g.fillStyle = BR2; g.beginPath(); g.arc(178, 560, 26, 0, 7); g.fill(); g.stroke();
    // near legs
    leg(g, 330, 690, 310, sw(Math.PI, A), -lift(Math.PI) * 0.5, BR, true, false);
    leg(g, 720, 700, 300, sw(0, A), lift(0), BR, true, true);
    // head
    const hx = 850, hy = 540 + (run ? Math.sin(ph * 2 + 1) * 10 : 0);
    g.save(); g.translate(hx, hy); g.rotate(run ? -0.08 : 0);
    g.fillStyle = BR; g.strokeStyle = INK; g.lineWidth = LW;
    g.beginPath(); g.arc(-60, -110, 44, 0, 7); g.fill(); g.stroke();                                  // ear
    g.fillStyle = DARK; g.beginPath(); g.arc(-60, -110, 22, 0, 7); g.fill();
    g.fillStyle = BR; const hd = new Path2D(); hd.ellipse(0, 0, 125, 115, 0, 0, 7); g.fill(hd); g.stroke(hd);
    if (S.mouth > 0.05) {                                                                               // open jaw
      g.fillStyle = '#8E2A2E'; g.beginPath(); g.moveTo(40, 40); g.lineTo(170, 40 + S.mouth * 10); g.lineTo(130, 40 + S.mouth * 90); g.lineTo(40, 70); g.closePath(); g.fill(); g.stroke();
      g.fillStyle = '#FFFFFF'; [[150, 44], [100, 44]].forEach(([x, y]) => { g.beginPath(); g.moveTo(x - 12, y); g.lineTo(x + 12, y); g.lineTo(x, y + 26); g.closePath(); g.fill(); });
      g.fillStyle = MUZ; g.beginPath(); g.ellipse(95, 45 + S.mouth * 70, 60, 26, 0.25, 0, 7); g.fill(); g.stroke();
    }
    g.fillStyle = MUZ; g.beginPath(); g.ellipse(95, 20, 85, 55, 0.05, 0, 7); g.fill(); g.stroke();      // muzzle
    g.fillStyle = INK; g.beginPath(); g.ellipse(172, 2, 30, 22, 0.2, 0, 7); g.fill();                    // nose
    g.fillStyle = '#FFFFFF'; g.beginPath(); g.ellipse(166, -6, 9, 5, 0.2, 0, 7); g.fill();
    if (S.mouth <= 0.05) { g.strokeStyle = INK; g.lineWidth = 7; g.beginPath(); g.moveTo(150, 40); g.quadraticCurveTo(120, 58, 90, 48); g.stroke(); }
    eye(g, 30, -34, 30, S.mood, 0.6, 0);
    g.restore();
  } else {
    // FRONT VIEW: body blob behind, two front legs, big head
    const sw = (o) => (run ? Math.max(0, Math.sin(ph + o)) * 70 : walk ? Math.max(0, Math.sin(ph + o)) * 30 : 0);
    g.fillStyle = BR; g.strokeStyle = INK; g.lineWidth = LW;
    const b = new Path2D(); b.moveTo(250, 760); b.bezierCurveTo(200, 560, 300, 330, 512, 320); b.bezierCurveTo(724, 330, 824, 560, 774, 760); b.bezierCurveTo(700, 860, 324, 860, 250, 760); b.closePath();
    g.fill(b); g.save(); g.clip(b); g.fillStyle = BR3; g.beginPath(); g.ellipse(512, 330, 210, 70, 0, 0, 7); g.fill(); g.restore(); g.stroke(b);
    for (const [x, o] of [[400, 0], [624, Math.PI]]) {
      const up = sw(o); g.fillStyle = BR; g.beginPath(); g.roundRect(x - 58, 690 - up * 0.3, 116, 300 - up, 50); g.fill(); g.stroke();
      g.strokeStyle = CLAW; g.lineWidth = 7; for (let i = -1; i <= 1; i++) { g.beginPath(); g.moveTo(x + i * 28, 975 - up * 1.3); g.lineTo(x + i * 30, 1000 - up * 1.3); g.stroke(); } g.strokeStyle = INK; g.lineWidth = LW;
    }
    const hx = 512, hy = 470 + (run ? Math.sin(ph * 2 + 1) * 12 : 0);
    g.fillStyle = BR; for (const s of [-1, 1]) { g.beginPath(); g.arc(hx + s * 130, hy - 130, 52, 0, 7); g.fill(); g.stroke(); g.fillStyle = DARK; g.beginPath(); g.arc(hx + s * 130, hy - 130, 26, 0, 7); g.fill(); g.fillStyle = BR; }
    const hd = new Path2D(); hd.ellipse(hx, hy, 175, 160, 0, 0, 7); g.fill(hd); g.save(); g.clip(hd); g.fillStyle = BR3; g.beginPath(); g.ellipse(hx - 40, hy - 90, 120, 50, -0.2, 0, 7); g.fill(); g.restore(); g.stroke(hd);
    const m = S.mouth;
    if (m > 0.05) {
      g.fillStyle = '#8E2A2E'; g.beginPath(); g.ellipse(hx, hy + 95 + m * 30, 70, 30 + m * 55, 0, 0, 7); g.fill(); g.stroke();
      g.fillStyle = '#FFFFFF'; for (const s of [-1, 1]) { g.beginPath(); g.moveTo(hx + s * 48, hy + 80); g.lineTo(hx + s * 28, hy + 80); g.lineTo(hx + s * 38, hy + 112); g.closePath(); g.fill(); g.beginPath(); g.moveTo(hx + s * 44, hy + 120 + m * 85); g.lineTo(hx + s * 24, hy + 120 + m * 85); g.lineTo(hx + s * 34, hy + 92 + m * 85); g.closePath(); g.fill(); }
    }
    g.fillStyle = MUZ; g.beginPath(); g.ellipse(hx, hy + 55, 95, 62, 0, 0, 7); g.fill(); g.stroke();
    g.fillStyle = INK; g.beginPath(); g.ellipse(hx, hy + 32, 40, 27, 0, 0, 7); g.fill();
    g.fillStyle = '#FFFFFF'; g.beginPath(); g.ellipse(hx - 12, hy + 22, 12, 6, 0, 0, 7); g.fill();
    if (m <= 0.05) { g.strokeStyle = INK; g.lineWidth = 7; g.beginPath(); g.moveTo(hx, hy + 60); g.lineTo(hx, hy + 78); g.moveTo(hx - 34, hy + 86); g.quadraticCurveTo(hx, hy + 70, hx + 34, hy + 86); g.stroke(); }
    eye(g, hx - 68, hy - 40, 36, S.mood, 0, 0.2, 1); eye(g, hx + 68, hy - 40, 36, S.mood, 0, 0.2, -1);
  }
  g.restore();
}

let blobT = null;
function blob() { if (blobT) return blobT; const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d'); const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(30,20,40,0.7)'); gr.addColorStop(1, 'rgba(30,20,40,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); blobT = new THREE.CanvasTexture(c); return blobT; }

export class BearToon {
  constructor({ size = 2.4, res = 1 } = {}) {
    this.res = res; this.canvas = document.createElement('canvas'); this.canvas.width = this.canvas.height = 1024 * res; this.g = this.canvas.getContext('2d');
    this.tex = new THREE.CanvasTexture(this.canvas); this.tex.colorSpace = THREE.SRGBColorSpace;
    const geo = new THREE.PlaneGeometry(size, size); geo.translate(0, size / 2 - size * (24 / 1024), 0);
    this.mat = new THREE.MeshBasicMaterial({ map: this.tex, transparent: true, alphaTest: 0.04, side: THREE.DoubleSide, toneMapped: false });
    this.mesh = new THREE.Mesh(geo, this.mat); this.mesh.castShadow = true;
    this.mesh.customDepthMaterial = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: this.tex, alphaTest: 0.5 });
    this.shadow = new THREE.Mesh(new THREE.PlaneGeometry(size * 0.85, size * 0.3), new THREE.MeshBasicMaterial({ map: blob(), transparent: true, depthWrite: false, opacity: 0.6 })); this.shadow.rotation.x = -Math.PI / 2; this.shadow.position.y = 0.012;
    this.group = new THREE.Group(); this.pivot = new THREE.Group(); this.pivot.add(this.mesh); this.group.add(this.pivot, this.shadow);
    this.key = ''; this.set({});
  }
  set(st) {
    const key = JSON.stringify(st, (k, v) => (typeof v === 'number' ? Math.round(v * 100) / 100 : v)); if (key === this.key) return this; this.key = key;
    const g = this.g; g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, this.canvas.width, this.canvas.height); g.scale(this.res, this.res); drawBear(g, st); this.tex.needsUpdate = true; return this;
  }
  face(cam) { const p = new THREE.Vector3(); this.group.getWorldPosition(p); this.pivot.rotation.y = Math.atan2(cam.position.x - p.x, cam.position.z - p.z); return this; }
  at(x, y, z) { this.group.position.set(x, y, z); return this; }
}

// ═════════════ low-poly pine forest with a dirt trail (bright midday) ═════════════
const rnd = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
export const trailX = (z) => 0.9 * Math.sin(z * 0.06) + 0.3 * Math.sin(z * 0.17 + 1);
export function pine(s = 1, seed = 0) {
  const g = new THREE.Group(), flat = (c) => new THREE.MeshStandardMaterial({ color: c, roughness: 0.9, flatShading: true });
  const tr = new THREE.Mesh(new THREE.CylinderGeometry(0.12 * s, 0.2 * s, 1.4 * s, 6), flat('#7A5234')); tr.position.y = 0.7 * s; tr.castShadow = true; g.add(tr);
  const cols = ['#2F8A4C', '#3A9A55', '#287A44'];
  for (let i = 0; i < 4; i++) { const r = (1.5 - i * 0.3) * s, h = (1.6 - i * 0.15) * s, c = new THREE.Mesh(new THREE.ConeGeometry(r, h, 7), flat(cols[(i + seed) % 3])); c.position.y = (1.4 + i * 0.85) * s + h / 2 - 0.3 * s; c.rotation.y = rnd(seed * 7 + i) * 3; c.castShadow = c.receiveShadow = true; g.add(c); }
  return g;
}
export function forestSet(E) {
  const scene = new THREE.Scene();
  WD.sky(scene, { top: '#3D8EE0', horizon: '#CBEAF8' });
  const sun = WD.sunlight(scene, E, { pos: [9, 13, 7], box: 14 });
  WD.clouds(scene, [[-40, 26, -110, 16], [20, 34, -120, 20], [70, 22, -95, 13], [-8, 18, -70, 9], [45, 40, -60, 10], [-60, 30, -40, 12]]);
  scene.fog = new THREE.Fog('#CBEAF8', 50, 190);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), WD.mat({ map: WD.T.grass('#6DBB4A', [120, 120]) })); ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);
  { const pos = [], uv = [], idx = [], N = 300, z0 = -140, z1 = 40, half = 1.0;
    for (let i = 0; i <= N; i++) { const z = z0 + (z1 - z0) * i / N, x = trailX(z); pos.push(x - half, 0.01, z, x + half, 0.01, z); uv.push(0, i / N * 90, 1, i / N * 90); if (i < N) { const a = i * 2; idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); } }
    const tg = new THREE.BufferGeometry(); tg.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); tg.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); tg.setIndex(idx); tg.computeVertexNormals();
    const tr = new THREE.Mesh(tg, WD.mat({ map: WD.T.dirt('#D29A5E', [1, 1], false) })); tr.receiveShadow = true; scene.add(tr); }
  WD.hills(scene, { z: -120, col: '#79C25A', list: [[-60, -130, 40, 16], [0, -140, 55, 22], [70, -125, 45, 15], [-120, -110, 50, 14], [130, -115, 50, 18]] });
  for (let i = 0; i < 260; i++) {
    const z = -110 + rnd(i) * 140, side = rnd(i + 50) < 0.5 ? -1 : 1, dx = 3.8 + Math.pow(rnd(i + 99), 1.4) * 40;
    if (z > -13 && z < -7 && side < 0 && dx < 8) continue;
    if (side > 0 && z > -64 && z < -16 && dx < 15) continue;
    const t = pine(0.9 + rnd(i + 7) * 0.9, i); t.position.set(trailX(z) + side * dx, 0, z); scene.add(t);
  }
  const rockM = new THREE.MeshStandardMaterial({ color: '#9C9AA3', roughness: 0.9, flatShading: true }), bushM = new THREE.MeshStandardMaterial({ color: '#4FA845', roughness: 0.9, flatShading: true });
  for (let i = 0; i < 50; i++) { const z = -70 + rnd(i + 300) * 90, side = rnd(i + 301) < 0.5 ? -1 : 1; if (side > 0 && z > -64 && z < -16) continue; const r = new THREE.Mesh(new THREE.IcosahedronGeometry(0.3 + rnd(i + 302) * 0.5, 0), rockM); r.position.set(trailX(z) + side * (1.6 + rnd(i + 303) * 8), 0.1, z); r.scale.y = 0.6; r.castShadow = r.receiveShadow = true; scene.add(r); }
  const bush = (x, z, s) => { for (let k = 0; k < 3; k++) { const b = new THREE.Mesh(new THREE.IcosahedronGeometry(s * (0.7 - k * 0.12), 0), bushM); b.position.set(x + (k - 1) * s * 0.6, s * 0.45, z + (k % 2) * 0.2); b.castShadow = b.receiveShadow = true; scene.add(b); } };
  for (let i = 0; i < 60; i++) { const z = -70 + rnd(i + 400) * 90, side = rnd(i + 401) < 0.5 ? -1 : 1; if (side > 0 && z > -64 && z < -16) continue; bush(trailX(z) + side * (1.8 + rnd(i + 402) * 9), z, 0.6 + rnd(i + 403) * 0.5); }
  bush(trailX(-10) - 2.8, -10.6, 1.3); bush(trailX(-10) - 3.6, -9.0, 1.1);
  const fl = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(0.05, 0), new THREE.MeshStandardMaterial({ roughness: 0.6 }), 1500), m4 = new THREE.Matrix4();
  for (let i = 0; i < 1500; i++) { const z = -60 + rnd(i * 1.3) * 80, side = rnd(i * 2.2) < 0.5 ? -1 : 1; m4.makeTranslation(trailX(z) + side * (1.2 + rnd(i * 3.3) * 10), 0.08, z); fl.setMatrixAt(i, m4); fl.setColorAt(i, new THREE.Color(['#F2D23A', '#F29BB5', '#FFFFFF', '#B98ACF'][i % 4])); }
  scene.add(fl);
  const tufts = new THREE.InstancedMesh(new THREE.ConeGeometry(0.03, 0.2, 3), WD.mat({ color: '#5DA83E' }), 3000);
  for (let i = 0; i < 3000; i++) { const z = -60 + rnd(i * 1.7) * 80, side = rnd(i * 4.1) < 0.5 ? -1 : 1; m4.makeTranslation(trailX(z) + side * (1.1 + rnd(i * 5.1) * 12), 0.09, z); tufts.setMatrixAt(i, m4); }
  scene.add(tufts);
  const aim = (c, box = 14) => { sun.key.target.position.copy(c); sun.key.position.copy(c).add(new THREE.Vector3(9, 13, 7)); const sc = sun.key.shadow.camera; sc.left = sc.bottom = -box; sc.right = sc.top = box; sc.updateProjectionMatrix(); };
  return { scene, sun, aim };
}

/** big brother-style header: yellow title with a small white subtitle */
export function headline(ctx, text, sub, y = 330, sc = 1, col = '#FFD43B') {
  if (sc <= 0) return; ctx.save(); ctx.translate(540, y); ctx.scale(sc, sc); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  ctx.font = '900 120px Inter'; const fit = Math.min(1, 960 / ctx.measureText(text).width); ctx.scale(fit, fit);
  ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillText(text, 4, 12); ctx.lineWidth = 18; ctx.strokeStyle = '#1A1226'; ctx.strokeText(text, 0, 0); ctx.fillStyle = col; ctx.fillText(text, 0, 0);
  if (sub) { ctx.font = '900 46px Inter'; ctx.lineWidth = 10; ctx.strokeText(sub, 0, 95); ctx.fillStyle = '#FFFFFF'; ctx.fillText(sub, 0, 95); }
  ctx.restore();
}
