// "Sixty Seconds" set: a street of houses with a red light above every door. House A (ours) is a hollow dollhouse that
// sits on its own lot so the whole thing can drop into the pit: living room + kitchen + stair hall below, mum's and my
// sister's rooms above. Everything that moves (dog, chair, glass, photos, door, crack, lights) is posed per frame.
import * as THREE from "three";
import { Batch, V, lam, Kit, boxGeo } from "./build";
import { ctex, rep, grassHD, cloudHD } from "./paint";
import { Pen, Outfit, Expr, FrontOpts, SKINS, INK, fxPuff, fxBurst } from "./toon";
import { LIGHTS, LOOK, LightPreset, LName } from "./lights";
import { TONE, CHAR, twoTone, untone } from "./shade";
import { NOINK } from "./ink";
import { Pool, Actor, Fx, Stage, CamInfo, castBegin, person, blob, lidAt, q, hh } from "./cast";
import { discTex, haloTex, beamBetween } from "./bworld";
import { FPS, SHOTS, camAt, ShotDef, clamp01, smooth, ramp, G0, FL1, GREEN_AT, sinkY, sinkAt, CUT_X, lightOf } from "./story";

export const loadKit = () => Promise.resolve({} as Kit);
const CEIL = 6.2, ATTIC = 6.4;

// ---------------- dollhouse builder ----------------
type Hole = [number, number, number, number];
class House {
  constructor(public b: Batch, public cx: number) {}
  box(mat: THREE.Material, x0: number, x1: number, y0: number, y1: number, z0: number, z1: number) {
    this.b.add(boxGeo(V(this.cx + Math.min(x0, x1), y0, Math.min(z0, z1)), V(this.cx + Math.max(x0, x1), y1, Math.max(z0, z1)), 0, true), mat);
  }
  wall(mat: THREE.Material, axis: "x" | "z", c0: number, c1: number, u0: number, u1: number, v0: number, v1: number, holes: Hole[] = []) {
    const us = [u0, u1, ...holes.flatMap((h) => [h[0], h[1]])].filter((u) => u >= u0 && u <= u1).sort((a, b) => a - b);
    for (let i = 0; i < us.length - 1; i++) {
      const a = us[i], b = us[i + 1]; if (b - a < 1e-4) continue;
      const m = (a + b) / 2, cut = holes.filter((h) => m > h[0] && m < h[1]).sort((p, r) => p[2] - r[2]);
      let v = v0;
      for (const h of cut) { if (h[2] > v) this.seg(mat, axis, c0, c1, a, b, v, h[2]); v = Math.max(v, h[3]); }
      if (v1 > v) this.seg(mat, axis, c0, c1, a, b, v, v1);
    }
  }
  private seg(mat: THREE.Material, axis: "x" | "z", c0: number, c1: number, a: number, b: number, v0: number, v1: number) {
    if (axis === "x") this.box(mat, c0, c1, v0, v1, a, b); else this.box(mat, a, b, v0, v1, c0, c1);
  }
  gable(mat: THREE.Material, xw: number, t: number) {
    const sh = new THREE.Shape([new THREE.Vector2(-5.4, ATTIC), new THREE.Vector2(5.4, ATTIC), new THREE.Vector2(0, 10)]);
    const g = new THREE.ExtrudeGeometry(sh, { depth: t, bevelEnabled: false }).rotateY(-Math.PI / 2);
    this.b.add(g.translate(this.cx + xw, 0, 0), mat);
  }
  roof(mat: THREE.Material) {
    const ang = Math.atan2(10 - ATTIC, 5.4), len = Math.hypot(10 - ATTIC, 5.4) + 0.5;
    for (const sz of [-1, 1]) { const g = new THREE.BoxGeometry(9.8, 0.22, len).translate(0, 0.11, len / 2).rotateX(ang); if (sz < 0) g.rotateY(Math.PI); this.b.add(g.translate(this.cx, 10, 0), mat); }
  }
}
const FRONT_WIN: Hole[] = [[-0.6, 0.6, G0, 2.35], [-3.4, -1.8, 1.1, 2.4], [1.8, 3.4, 1.1, 2.4], [-3.4, -1.8, 4.1, 5.6], [1.8, 3.4, 4.1, 5.6]];
/** a neighbour: closed shell with lit-looking dark windows */
const neighbour = (b: Batch, cx: number, wallC: string, roofC: string, k: number) => {
  const H = new House(b, cx), W = lam("nW" + k, () => ({ color: wallC })), R = lam("nR" + k, () => ({ color: roofC })), D = lam("nD", () => ({ color: "#1a1a2a" }));
  H.wall(W, "z", 4.75, 5, -4.5, 4.5, 0, ATTIC, FRONT_WIN); H.wall(W, "z", -5, -4.75, -4.5, 4.5, 0, ATTIC);
  H.wall(W, "x", -4.5, -4.25, -5, 5, 0, ATTIC, [[-1, 1, 1.1, 2.4], [-1, 1, 4.1, 5.6]]); H.wall(W, "x", 4.25, 4.5, -5, 5, 0, ATTIC, [[-1, 1, 1.1, 2.4], [-1, 1, 4.1, 5.6]]);
  H.box(D, -4.25, 4.25, 0, ATTIC, -4.7, 4.7); // dark interior block behind the glass
  H.box(lam("slab", () => ({ color: "#d8d0c4" })), -4.5, 4.5, ATTIC - 0.2, ATTIC, -5, 5);
  H.roof(R); H.gable(W, 4.5, 0.25); H.gable(W, -4.25, 0.25);
  H.box(lam("nDoor" + k, () => ({ color: ["#7a3a3a", "#2b7a4b", "#3f6fb5", "#8a6a3a"][k % 4] })), -0.58, 0.58, G0, 2.35, 4.9, 4.98);
  H.box(lam("step", () => ({ color: "#c9bfae" })), -1.0, 1.0, 0, 0.2, 5, 5.8);
};

// ---------------- painted bits ----------------
const photoTex = (k: number) => ctex("photo" + k, 200, 160, (g) => {
  g.fillStyle = ["#9fc7e8", "#f2d08a", "#b8e0b0"][k]; g.fillRect(0, 0, 200, 160);
  g.fillStyle = "#6fa04a"; g.fillRect(0, 115, 200, 45);
  const xs = k === 0 ? [60, 100, 140] : k === 1 ? [80, 125] : [70, 105, 135];
  xs.forEach((x, i) => { g.fillStyle = ["#e0b48a", "#c98d6a", "#f0c8a0"][i % 3]; g.beginPath(); g.arc(x, 70, 14, 0, 7); g.fill(); g.fillStyle = ["#c0353a", "#3f6fb5", "#f2c230"][i % 3]; g.fillRect(x - 13, 85, 26, 32); });
});
const notesDraw = (p: Pen, u: number) => {
  const g = p.g; g.font = "900 150px Arial, sans-serif"; g.textAlign = "center"; g.fillStyle = INK; g.globalAlpha = Math.sin(Math.PI * u);
  g.fillText("♪", 150, 190 - 60 * u); g.globalAlpha = 1;
};
const cutTex = () => ctex("cutTown", 2048, 2048, (g) => {
  // 160 m x 160 m: x -80..80, y -110..50 -> px
  const X = (x: number) => (x + 80) * 12.8, Y = (y: number) => (50 - y) * 12.8, p = new Pen(g);
  g.fillStyle = "#1b2550"; g.fillRect(0, 0, 2048, Y(0));
  for (let i = 0; i < 90; i++) { g.fillStyle = "rgba(255,255,255,.8)"; g.fillRect((i * 337) % 2048, (i * 191) % Y(8), 4, 4); }
  const bands: [number, string][] = [[0, "#7a5a3a"], [-14, "#6a4c32"], [-40, "#5c412c"], [-80, "#4e3726"], [-110, "#4e3726"]];
  for (let i = 0; i < bands.length - 1; i++) { g.fillStyle = bands[i][1]; g.fillRect(0, Y(bands[i][0]), 2048, Y(bands[i + 1][0]) - Y(bands[i][0]) + 2); }
  g.fillStyle = "#4f8a3a"; g.fillRect(0, Y(0.8), 2048, Y(-1) - Y(0.8));
  // tunnels with timber props
  const tun = (x0: number, x1: number, y0: number, y1: number) => {
    p.poly([[X(x0), Y(y0)], [X(x1), Y(y0)], [X(x1), Y(y1)], [X(x0), Y(y1)]], "#1d1820", 10);
    for (let x = x0 + 4; x < x1; x += 8) { g.fillStyle = "#8a6a4a"; g.fillRect(X(x) - 10, Y(y1), 20, Y(y0) - Y(y1)); g.fillRect(X(x) - 40, Y(y1), 80, 16); }
  };
  tun(-75, 75, -36, -28); tun(-60, 40, -64, -56); tun(-10, -2, -56, -36);
  // houses on top, each with its red light; ours (x 0) gone into a collapse
  for (const x of [-60, -40, -20, 20, 40, 60]) {
    p.poly([[X(x - 6), Y(0.8)], [X(x + 6), Y(0.8)], [X(x + 6), Y(9)], [X(x), Y(14)], [X(x - 6), Y(9)]], "#9fb6d0", 8);
    g.fillStyle = "#3a3d47"; g.fillRect(X(x - 1.2), Y(4.4), 2.4 * 12.8, 3.6 * 12.8);
    g.fillStyle = "#ff3b30"; g.beginPath(); g.arc(X(x), Y(5.4), 14, 0, 7); g.fill();
  }
  // the collapse: a pit from the surface into the upper tunnel, our house tipped inside
  p.poly([[X(-8), Y(0.8)], [X(8), Y(0.8)], [X(6), Y(-30)], [X(-6), Y(-30)]], "#1a1418", 10);
  g.save(); g.translate(X(0), Y(-20)); g.rotate(0.35);
  p.poly([[-70, 60], [70, 60], [70, -50], [0, -110], [-70, -50]], "#9fb6d0", 8); g.restore();
  // a young miner with a headlamp and pick in the lower tunnel
  const mx = X(-30), my = Y(-64);
  g.fillStyle = "#f2c230"; g.beginPath(); g.arc(mx, my - 150, 34, Math.PI, 0); g.fill();
  g.fillStyle = "#e0b48a"; g.beginPath(); g.arc(mx, my - 120, 30, 0, 7); g.fill();
  g.fillStyle = "#5a6a8a"; g.fillRect(mx - 30, my - 92, 60, 70); g.fillStyle = "#3a3d47"; g.fillRect(mx - 26, my - 22, 22, 22); g.fillRect(mx + 4, my - 22, 22, 22);
  g.strokeStyle = "#8a6a4a"; g.lineWidth = 12; g.beginPath(); g.moveTo(mx + 30, my - 70); g.lineTo(mx + 90, my - 140); g.stroke();
  g.strokeStyle = "#8f969e"; g.lineWidth = 14; g.beginPath(); g.moveTo(mx + 60, my - 160); g.quadraticCurveTo(mx + 100, my - 150, mx + 120, my - 110); g.stroke();
  g.fillStyle = "rgba(255,240,180,.35)"; g.beginPath(); g.moveTo(mx + 20, my - 150); g.lineTo(mx + 300, my - 220); g.lineTo(mx + 300, my - 60); g.fill();
  g.font = "900 110px Arial Black, sans-serif"; g.textAlign = "center"; g.lineWidth = 18; g.strokeStyle = INK; g.fillStyle = "#ffffff";
  g.strokeText("OLD MINE", X(30), Y(-74)); g.fillText("OLD MINE", X(30), Y(-74));
});

// ---------------- the dog (3D) ----------------
class Dog {
  g = new THREE.Group(); body = new THREE.Group(); head = new THREE.Group(); tail = new THREE.Group(); legs: THREE.Group[] = [];
  constructor(parent: THREE.Object3D) {
    const fur = twoTone(new THREE.MeshLambertMaterial({ color: "#c98a3e" })), dark = twoTone(new THREE.MeshLambertMaterial({ color: "#6b4426" })), red = twoTone(new THREE.MeshLambertMaterial({ color: "#c0353a" }));
    const blk = new THREE.MeshBasicMaterial({ color: "#1d1b22" });
    const M = (g: THREE.BufferGeometry, m: THREE.Material) => { const x = new THREE.Mesh(g, m); x.castShadow = true; return x; };
    this.body.add(M(new THREE.CapsuleGeometry(0.17, 0.42, 6, 12).rotateZ(Math.PI / 2), fur));
    this.body.position.y = 0.44; this.g.add(this.body);
    this.head.position.set(0.33, 0.12, 0); this.body.add(this.head);
    this.head.add(M(new THREE.SphereGeometry(0.15, 16, 12).scale(1.05, 0.95, 0.95), fur));
    this.head.add(M(new THREE.BoxGeometry(0.16, 0.1, 0.12).translate(0.15, -0.04, 0), fur));
    this.head.add(M(new THREE.SphereGeometry(0.035, 10, 8).translate(0.235, -0.01, 0), blk));
    for (const s of [-1, 1]) {
      this.head.add(M(new THREE.SphereGeometry(0.022, 8, 6).translate(0.12, 0.05, s * 0.07), blk));
      this.head.add(M(new THREE.BoxGeometry(0.06, 0.15, 0.1).translate(-0.02, 0.1, s * 0.12).rotateX(s * 0.5), dark));
    }
    this.body.add(M(new THREE.TorusGeometry(0.11, 0.025, 6, 16).rotateY(Math.PI / 2).translate(0.27, 0.04, 0), red));
    this.tail.position.set(-0.36, 0.06, 0); this.body.add(this.tail);
    this.tail.add(M(new THREE.CylinderGeometry(0.03, 0.02, 0.24, 8).translate(0, 0.12, 0).rotateZ(0.6), fur));
    for (const [x, z] of [[0.22, 0.09], [0.22, -0.09], [-0.22, 0.09], [-0.22, -0.09]]) {
      const l = new THREE.Group(); l.position.set(x, -0.05, z); this.body.add(l);
      l.add(M(new THREE.CylinderGeometry(0.045, 0.04, 0.34, 8).translate(0, -0.17, 0), fur));
      l.add(M(new THREE.SphereGeometry(0.05, 8, 6).scale(1.3, 0.6, 1).translate(0.02, -0.35, 0), dark));
      this.legs.push(l);
    }
    parent.add(this.g);
  }
  /** mode: stand / growl / run / bark / jump; yaw = heading (0 = +x) */
  pose(x: number, y: number, z: number, yaw: number, mode: string, t: number, lift = 0) {
    this.g.visible = true; this.g.position.set(x, y + lift, z); this.g.rotation.set(0, -yaw, 0);
    let legA = 0, head = 0, bodyY = 0.44, tail = Math.sin(t * 14) * 0.5, pitch = 0;
    if (mode === "run") { legA = 0.8; const ph = t * 13; this.legs.forEach((l, i) => (l.rotation.z = legA * Math.sin(ph + (i < 2 ? 0 : Math.PI) + (i % 2) * 0.6))); bodyY = 0.44 + 0.04 * Math.abs(Math.sin(ph)); tail = 0.3; }
    else this.legs.forEach((l) => (l.rotation.z = 0));
    if (mode === "growl") { head = -0.45; bodyY = 0.4 + 0.006 * Math.sin(t * 70); tail = -0.6; pitch = 0.08; }
    if (mode === "bark") { head = 0.25 * Math.max(0, Math.sin(t * 9)); tail = Math.sin(t * 18) * 0.4; }
    if (mode === "jump") { this.legs.forEach((l, i) => (l.rotation.z = i < 2 ? -0.9 : 0.9)); pitch = -0.2; }
    this.body.position.y = bodyY; this.body.rotation.z = pitch; this.head.rotation.z = head; this.tail.rotation.x = tail;
  }
  hide() { this.g.visible = false; }
}

// ---------------- cast ----------------
const KID: Outfit = { jacket: "#5b7fc4", pants: "#3f5a96", boots: "#e8e2d4", hat: "hair", hair: "#3a2a20", skin: SKINS[1], build: "kid" };
const SIS: Outfit = { jacket: "#e88aa8", pants: "#c86a8a", boots: "#f4f1ea", hat: "hair", hair: "#5a3a2a", skin: SKINS[1], build: "kid" };
const MUM: Outfit = { jacket: "#8a6ab0", pants: "#8a6ab0", boots: "#e8e2d4", dress: "#8a6ab0", hat: "hair", hair: "#5a3a2a", skin: SKINS[1] };
const GRANDPA: Outfit = { jacket: "#7a6a4a", pants: "#4a4f58", boots: "#3a2a20", hat: "cap", cap: "#6b5a40", moustache: "#e8e4dc", skin: SKINS[1], build: "stout" };
const KID_SMALL: Outfit = { ...KID, jacket: "#e07b2e", pants: "#3b3f52" };

type Mode = "walk" | "run" | "stand" | "jump" | "sit";
type Key = [number, number, number, Mode?, number?]; // t, x, z, mode of the segment starting here, y
type W = { x: number; y: number; z: number; dx: number; dz: number; mode: Mode; phase: number; amt: number; pose: number };
const CYC: Record<string, number> = { walk: 1.3, run: 1.81 };
const walkAt = (keys: Key[], t: number): W => {
  let ph = 0, dx = 0, dz = 1;
  for (let i = 0; i < keys.length; i++) {
    const [t0, x0, z0, m0, y0 = G0] = keys[i], nx = keys[i + 1];
    const ex = nx ? nx[1] - x0 : 0, ez = nx ? nx[2] - z0 : 0, d = Math.hypot(ex, ez), ey = nx ? (nx[4] ?? G0) - y0 : 0;
    if (d > 1e-3) { dx = ex / d; dz = ez / d; }
    const mode: Mode = m0 ?? (d > 1e-3 ? "run" : "stand");
    if (!nx || t < nx[0]) {
      const k = nx && t > t0 ? (t - t0) / (nx[0] - t0) : 0;
      if (mode === "walk" || mode === "run") ph += (Math.hypot(d, ey) * k) / CYC[mode];
      const moving = (mode === "walk" || mode === "run") && t >= t0 && !!nx;
      return { x: x0 + ex * k, y: y0 + ey * k, z: z0 + ez * k, dx, dz, mode: t < t0 ? "stand" : moving ? mode : mode === "jump" ? "jump" : mode === "sit" ? "sit" : "stand", phase: ph, amt: moving ? 1 : 0, pose: k };
    }
    if (mode === "walk" || mode === "run") ph += Math.hypot(d, ey) / CYC[mode];
  }
  const l = keys[keys.length - 1];
  return { x: l[1], y: l[4] ?? G0, z: l[2], dx, dz, mode: "stand", phase: ph, amt: 0, pose: 0 };
};

export class World {
  root = new THREE.Group();
  private pool = new Pool(); private actors: Actor[] = []; private fxs: Fx[] = [];
  private hemi: THREE.HemisphereLight; private sun: THREE.DirectionalLight;
  private sky: THREE.Mesh; private skyMat: THREE.ShaderMaterial; private fog = new THREE.Fog("#1c2650", 30, 240);
  private moon: THREE.Sprite; private sunCache = new Map<string, THREE.Vector3>();
  private clouds: THREE.Mesh[] = []; private cloudMaps: Record<string, THREE.Texture[]>;
  private A = new THREE.Group(); // our house + lot: sinks
  private ourLight: THREE.Mesh; private ourGlow: THREE.Sprite; private nLights: { m: THREE.Mesh; s: THREE.Sprite; x: number }[] = [];
  private glasses: { m: THREE.Mesh; x: number; y: number; z: number }[] = []; private lamp = new THREE.Group();
  private door = new THREE.Group(); private doorFrame = new THREE.Group(); private cupDoor = new THREE.Group();
  private chair = new THREE.Group(); private pane: THREE.Mesh; private shards: THREE.Mesh[] = [];
  private crack: { m: THREE.Mesh; a: number; b: number }[] = []; private photos: { g: THREE.Group; z: number }[] = [];
  private dog: Dog; private ladder = new THREE.Group(); private cut = new THREE.Group();
  private frustum = new THREE.Frustum(); private m4 = new THREE.Matrix4(); private v = new THREE.Vector3(); private sph = new THREE.Sphere();

  constructor(_kit: Kit) {
    const R = this.root;
    // ---- sky with stars ----
    this.skyMat = new THREE.ShaderMaterial({
      uniforms: { c0: { value: new THREE.Color() }, c1: { value: new THREE.Color() }, c2: { value: new THREE.Color() }, c3: { value: new THREE.Color() }, c4: { value: new THREE.Color() }, e: { value: new THREE.Vector4() }, uStars: { value: 0 } },
      vertexShader: "varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
      fragmentShader: `uniform vec3 c0, c1, c2, c3, c4; uniform vec4 e; uniform float uStars; varying vec3 vP;
        float h(vec3 p){ return fract(sin(dot(p, vec3(12.9898, 78.233, 45.164))) * 43758.5453); }
        void main(){ vec3 d = normalize(vP); float el = asin(clamp(d.y, -1.0, 1.0));
          vec3 c = mix(c0, c1, smoothstep(0.0, e.x, el)); c = mix(c, c2, smoothstep(e.x, e.y, el));
          c = mix(c, c3, smoothstep(e.y, e.z, el)); c = mix(c, c4, smoothstep(e.z, e.w, el));
          vec3 q = floor(d * 260.0); float s = h(q); float st = step(0.9965, s) * smoothstep(0.03, 0.2, el) * uStars;
          c += vec3(0.9, 0.95, 1.0) * st * (0.4 + 0.6 * h(q + 3.1)); gl_FragColor = vec4(c, 1.0); }`,
      side: THREE.BackSide, depthWrite: false, fog: false,
    });
    this.sky = new THREE.Mesh(new THREE.SphereGeometry(900, 48, 24), this.skyMat); this.sky.renderOrder = -1; this.sky.frustumCulled = false; this.sky.layers.set(NOINK); R.add(this.sky);
    this.moon = new THREE.Sprite(new THREE.SpriteMaterial({ map: discTex(), color: new THREE.Color(3.2, 3.3, 3.6), fog: false, depthWrite: false }));
    this.moon.layers.set(NOINK); this.moon.frustumCulled = false; this.moon.renderOrder = -0.5; R.add(this.moon);
    this.hemi = new THREE.HemisphereLight("#cfe6ff", "#6c5c8c", 1.1);
    this.sun = new THREE.DirectionalLight("#fff0d6", 2.6); this.sun.castShadow = true; this.sun.shadow.mapSize.set(2048, 2048);
    R.add(this.hemi, this.sun, this.sun.target);
    this.cloudMaps = { day: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.day.cloud)), golden: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.golden.cloud)), night: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.night.cloud)) };
    for (let i = 0; i < 10; i++) {
      const a = (i / 10) * Math.PI * 2 + 0.3, d = 520 + (i % 3) * 60;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: this.cloudMaps.day[i % 4], transparent: true, depthWrite: false, fog: false }));
      const w = 130 + (i % 4) * 30; m.position.set(Math.cos(a) * d, 90 + (i % 4) * 35, Math.sin(a) * d); m.scale.set(w, w / 2, 1); m.layers.set(NOINK); this.clouds.push(m); R.add(m);
    }
    // ---- street, ground with the lot hole, the pit ----
    const b = new Batch(), grass = lam("grassG", () => ({ map: rep(grassHD(), 300, 300) }));
    const gs = new THREE.Shape([new THREE.Vector2(-450, -450), new THREE.Vector2(450, -450), new THREE.Vector2(450, 450), new THREE.Vector2(-450, 450)]);
    gs.holes.push(new THREE.Path().absarc(0, 0, 8.5, 0, Math.PI * 2, true));
    const gg = new THREE.ShapeGeometry(gs, 64).rotateX(-Math.PI / 2);
    { const p = gg.attributes.position, uv = gg.attributes.uv; for (let i = 0; i < p.count; i++) uv.setXY(i, (p.getX(i) + 450) / 900, (p.getZ(i) + 450) / 900); }
    b.add(gg, grass);
    b.add(boxGeo(V(-400, -0.01, 12), V(400, 0.02, 20), 0, false), lam("asphalt", () => ({ color: "#3a3d47" })));
    b.add(boxGeo(V(-400, 0, 10), V(400, 0.12, 12), 0, false), lam("pavement", () => ({ color: "#b8b2a6" })));
    for (let x = -80; x < 80; x += 6) b.add(boxGeo(V(x, 0.021, 15.9), V(x + 3, 0.03, 16.1)), lam("lane", () => ({ color: "#f2ead6" })));
    const pit = new THREE.Mesh(new THREE.CylinderGeometry(8.55, 7.6, 26, 48, 6, true).translate(0, -13, 0), twoTone(new THREE.MeshLambertMaterial({ color: "#5c412c", side: THREE.BackSide })));
    pit.receiveShadow = true; R.add(pit);
    const pitB = new THREE.Mesh(new THREE.CircleGeometry(7.7, 32).rotateX(-Math.PI / 2).translate(0, -25.9, 0), new THREE.MeshBasicMaterial({ color: "#120e12" })); R.add(pitB);
    neighbour(b, -13, "#d9c9a0", "#5a4a5a", 0); neighbour(b, 13, "#c9d9b0", "#7a3a3a", 1); neighbour(b, -26, "#e0b8b0", "#3a4a6a", 2); neighbour(b, 26, "#b8c8e0", "#6a4a3a", 3);
    for (const x of [-36, 36]) neighbour(b, x, "#d8d0c4", "#4a4a5a", 4 + (x > 0 ? 1 : 0));
    for (const [x, z, s] of [[-7.5, -7, 0], [7.5, -7.5, 1], [-19.5, 3, 2], [19.5, 3, 0]] as const) {
      b.add(new THREE.CylinderGeometry(0.3, 0.45, 3, 8).translate(x, 1.5, z), lam("bark", () => ({ color: "#6b4a32" })));
      for (let k = 0; k < 3; k++) b.add(new THREE.IcosahedronGeometry(1.7 - 0.2 * k, 1).translate(x + Math.cos(k * 2.1 + s), 3.6 + 0.7 * k, z + Math.sin(k * 2.1 + s)), lam("leaf" + ((s + k) % 3), () => ({ color: ["#4f8a3a", "#5f9a3e", "#3f7a3a"][(s + k) % 3] })));
    }
    for (const x of [-6.5, 6.5, -19.5, 19.5]) { b.add(beamBetween(V(x, 0, 11.2), V(x, 4.8, 11.2), 0.12), lam("lampPost", () => ({ color: "#2a2230" }))); }
    b.build(R);
    for (const x of [-6.5, 6.5, -19.5, 19.5]) { const s = new THREE.Mesh(new THREE.SphereGeometry(0.2, 10, 8), new THREE.MeshBasicMaterial({ color: new THREE.Color(3.5, 2.8, 1.6) })); s.position.set(x, 4.85, 11.2); s.layers.set(NOINK); R.add(s); }
    // ---- door lights (neighbours) ----
    const lightGeo = new THREE.BoxGeometry(0.32, 0.2, 0.12);
    for (const x of [-36, -26, -13, 13, 26, 36]) {
      const m = new THREE.Mesh(lightGeo, new THREE.MeshBasicMaterial({ color: new THREE.Color(5, 0.35, 0.3) })); m.position.set(x, 2.75, 5.06); m.layers.set(NOINK); R.add(m);
      const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: haloTex(), color: new THREE.Color(1.6, 0.15, 0.1), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }));
      s.position.set(x, 2.75, 5.3); s.scale.setScalar(2.2); s.layers.set(NOINK); R.add(s); this.nLights.push({ m, s, x });
    }

    // ---- our house (all in group A) ----
    const a = new Batch(), H = new House(a, 0);
    const W = lam("wallA", () => ({ color: "#9fb6d0" })), T = lam("trimA", () => ({ color: "#f4f1ea" })), IN = lam("inA", () => ({ color: "#e8d8b8" })), IN2 = lam("inA2", () => ({ color: "#b8d0e8" })), IN3 = lam("inA3", () => ({ color: "#f0c8d8" }));
    const SL = lam("slab", () => ({ color: "#d8d0c4" })), FLR = lam("floorA", () => ({ color: "#b08860" })), t = 0.25;
    // lot: grass disc under the house, flush with the ground
    a.add(new THREE.CylinderGeometry(8.5, 8.3, 1.2, 64).translate(0, -0.6, 0), grass);
    a.add(boxGeo(V(-0.6, 0.005, 5.8), V(0.6, 0.04, 8.4), 0, false), lam("path", () => ({ color: "#c9bfae" })));
    // exterior walls
    H.wall(W, "z", 5 - t, 5, -4.5, 4.5, 0, ATTIC, FRONT_WIN);
    H.wall(W, "z", -5, -5 + t, -4.5, 4.5, 0, ATTIC);
    H.wall(W, "x", -4.5, -4.5 + t, -5, 5, 0, ATTIC, [[-3.2, -1.8, 4.1, 5.6]]);
    H.wall(W, "x", 4.5 - t, 4.5, -5, 5, 0, ATTIC, [[1.4, 3.0, 1.1, 2.4], [1.4, 3.0, 4.1, 5.6]]);
    // inner face colours: living room (warm), upstairs rooms
    H.box(FLR, -4.5, 4.5, 0, G0, -5, 5);
    // first floor slab with the stair hole (x -1.6..-0.1, z -4.4..-0.9)
    H.box(SL, -4.5, 4.5, FL1 - 0.2, FL1, -0.9, 5); H.box(SL, -4.5, -1.6, FL1 - 0.2, FL1, -5, -0.9); H.box(SL, -0.1, 4.5, FL1 - 0.2, FL1, -5, -0.9);
    H.box(SL, -1.6, -0.1, FL1 - 0.2, FL1, -5, -4.4);
    H.box(SL, -4.5, 4.5, CEIL, ATTIC, -5, 5);
    // ground floor partitions: z = 0 (openings: hall x -3..-0.1, kitchen door x 1..2.2), x = 0 (back half)
    H.wall(IN, "z", -0.06, 0.06, -4.25, 4.25, G0, FL1 - 0.2, [[-3.0, -0.1, G0, 2.4], [1.0, 2.2, G0, 2.3]]);
    H.wall(IN, "x", -0.06, 0.06, -4.75, 0, G0, FL1 - 0.2);
    // upstairs partitions: z = 0 (doors: mum x -2.8..-1.9, sister x 1.0..1.9), x = 0 (front half)
    H.wall(IN2, "z", -0.06, 0.06, -4.25, 4.25, FL1, CEIL, [[-2.8, -1.9, FL1, FL1 + 2.15], [1.0, 1.9, FL1, FL1 + 2.15], [-1.6, -0.1, FL1, FL1 + 2.4]]);
    H.wall(IN3, "x", -0.06, 0.06, 0, 4.75, FL1, CEIL);
    // stairs: bottom at the back (z -4.4), top at the front (z -0.6); thin treads, a side wall with the cupboard door
    for (let i = 0; i < 13; i++) {
      const z0 = -4.4 + i * 0.29, y = G0 + (i + 1) * 0.23;
      H.box(lam("tread", () => ({ color: "#8a6a4a" })), -1.6, -0.1, y - 0.06, y, z0, z0 + 0.32);
      if (!(z0 > -1.95 && z0 < -0.95)) H.box(lam("stairSide", () => ({ color: "#e8d8b8" })), -1.66, -1.6, G0, y - 0.02, z0, z0 + 0.29);
      else H.box(lam("stairSide", () => ({ color: "#e8d8b8" })), -1.66, -1.6, G0 + 1.3, y - 0.02, z0, z0 + 0.29);
    }
    H.box(lam("rail", () => ({ color: "#6b4a32" })), -1.7, -1.62, G0 + 0.9, G0 + 1.0, -4.4, -0.6);
    // roof, gables, door light housing, step
    H.roof(lam("roofA", () => ({ color: "#8a4a3a" }))); H.gable(W, 4.5, t); H.gable(W, -4.25, t);
    H.box(SL, -1.0, 1.0, 0, G0, 5, 5.8);
    // window trims
    for (const [x0, x1, y0, y1] of [[-3.4, -1.8, 1.1, 2.4], [1.8, 3.4, 1.1, 2.4], [-3.4, -1.8, 4.1, 5.6], [1.8, 3.4, 4.1, 5.6]]) {
      H.box(T, x0 - 0.1, x1 + 0.1, y0 - 0.12, y0, 5, 5.1); H.box(T, x0 - 0.1, x1 + 0.1, y1, y1 + 0.1, 5, 5.1);
    }
    // ---- living room: sofa, TV, rug, the photos wall (x = -4.25) ----
    H.box(lam("sofa", () => ({ color: "#3f6fb5" })), 1.4, 3.9, G0, G0 + 0.45, 1.2, 2.1); H.box(lam("sofa", () => ({ color: "#3f6fb5" })), 1.4, 3.9, G0, G0 + 0.95, 1.9, 2.25);
    H.box(lam("rug", () => ({ color: "#c0353a" })), -2.6, 1.0, G0, G0 + 0.01, 1.2, 3.6);
    H.box(lam("tvUnit", () => ({ color: "#6b4a32" })), 1.6, 3.6, G0, G0 + 0.5, 4.3, 4.7); H.box(lam("tv", () => ({ color: "#1d1b22" })), 1.9, 3.3, G0 + 0.55, G0 + 1.35, 4.45, 4.55);
    // ---- kitchen: counter, cupboard with glass front, fridge, table ----
    H.box(lam("cab", () => ({ color: "#f4f1ea" })), 0.2, 4.2, G0, 1.1, -4.75, -4.1); H.box(lam("counter", () => ({ color: "#5a5f6a" })), 0.2, 4.2, 1.1, 1.16, -4.8, -4.05);
    H.box(lam("cab", () => ({ color: "#f4f1ea" })), 1.2, 3.6, 1.65, 1.7, -4.75, -4.3); H.box(lam("cab", () => ({ color: "#f4f1ea" })), 1.2, 3.6, 2.6, 2.65, -4.75, -4.3);
    H.box(lam("cab", () => ({ color: "#f4f1ea" })), 1.2, 3.6, 2.1, 2.14, -4.75, -4.3);
    H.box(lam("cab", () => ({ color: "#f4f1ea" })), 1.15, 1.2, 1.65, 2.65, -4.75, -4.3); H.box(lam("cab", () => ({ color: "#f4f1ea" })), 3.6, 3.65, 1.65, 2.65, -4.75, -4.3);
    H.box(lam("fridge", () => ({ color: "#e8eef4" })), 3.3, 4.2, G0, 2.1, -3.8, -3.0);
    H.box(lam("table", () => ({ color: "#c9a36a" })), 2.9, 4.1, G0, 0.95, -1.5, -0.6);
    // ---- upstairs: mum's bed (x -3.9..-1.9, z 2.6..4.4), my sister's bed + toys ----
    H.box(lam("bedFrame", () => ({ color: "#a07850" })), -4.0, -1.9, FL1, FL1 + 0.35, 2.5, 4.4); H.box(lam("sheetM", () => ({ color: "#f4f1ea" })), -4.0, -1.9, FL1 + 0.35, FL1 + 0.55, 2.5, 4.4);
    H.box(lam("duvet", () => ({ color: "#6a8ac4" })), -3.3, -1.9, FL1 + 0.55, FL1 + 0.62, 2.5, 4.4);
    H.box(lam("bedFrame", () => ({ color: "#a07850" })), 2.0, 4.0, FL1, FL1 + 0.35, 2.9, 4.4); H.box(lam("sheetS", () => ({ color: "#f2c230" })), 2.0, 4.0, FL1 + 0.35, FL1 + 0.55, 2.9, 4.4);
    H.box(lam("duvetS", () => ({ color: "#e88aa8" })), 2.6, 4.0, FL1 + 0.55, FL1 + 0.62, 2.9, 4.4);
    a.add(new THREE.SphereGeometry(0.2, 12, 10).translate(2.4, FL1 + 0.75, 3.9), lam("teddy", () => ({ color: "#a0703a" })));
    a.add(new THREE.SphereGeometry(0.14, 12, 10).translate(2.4, FL1 + 1.05, 3.9), lam("teddy", () => ({ color: "#a0703a" })));
    for (let i = 0; i < 6; i++) a.add(boxGeo(V(0.6 + 0.5 * hh(i, 1) * 2, FL1, 1.2 + hh(i, 2) * 1.2), V(0.85 + 0.5 * hh(i, 1) * 2, FL1 + 0.22, 1.45 + hh(i, 2) * 1.2), 0, true), lam("toy" + (i % 3), () => ({ color: ["#3f6fb5", "#f2c230", "#2b7a4b"][i % 3] })));
    a.build(this.A);
    // ---- moving parts inside A ----
    // our door light
    this.ourLight = new THREE.Mesh(lightGeo, new THREE.MeshBasicMaterial({ color: new THREE.Color(5, 0.35, 0.3) })); this.ourLight.position.set(0, 2.75, 5.06); this.ourLight.layers.set(NOINK); this.A.add(this.ourLight);
    this.ourGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map: haloTex(), color: new THREE.Color(1.6, 0.15, 0.1), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }));
    this.ourGlow.position.set(0, 2.75, 5.3); this.ourGlow.scale.setScalar(2.2); this.ourGlow.layers.set(NOINK); this.A.add(this.ourGlow);
    // glasses in the cupboard (two shelves) + plates
    const glassM = twoTone(new THREE.MeshLambertMaterial({ color: "#bfe3f2" }));
    for (let i = 0; i < 12; i++) {
      const row = i < 6 ? 0 : 1, x = 1.45 + (i % 6) * 0.38, y = row ? 2.14 : 1.7, z = -4.55;
      const m = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.06, 0.24, 14).translate(0, 0.12, 0), glassM); m.position.set(x, y, z); m.castShadow = true; this.A.add(m); this.glasses.push({ m, x, y, z });
    }
    // pendant lamp over the table (swings)
    this.lamp.position.set(2.1, FL1 - 0.2, -2.1);
    { const lb = new Batch(); lb.add(new THREE.CylinderGeometry(0.01, 0.01, 1.1, 6).translate(0, -0.55, 0), lam("cord", () => ({ color: "#2a2230" }))); lb.add(new THREE.ConeGeometry(0.32, 0.28, 18, 1, true).translate(0, -1.2, 0), lam("shade", () => ({ color: "#2b7a4b" }))); lb.build(this.lamp); }
    const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.08, 10, 8).translate(0, -1.27, 0), new THREE.MeshBasicMaterial({ color: new THREE.Color(3, 2.6, 1.8) })); bulb.layers.set(NOINK); this.lamp.add(bulb); this.A.add(this.lamp);
    // front door (hinged at x -0.58) and its frame
    { const d = new THREE.Mesh(new THREE.BoxGeometry(1.16, 2.15, 0.08).translate(0.58, 1.075, 0), twoTone(new THREE.MeshLambertMaterial({ color: "#3f6fb5" }))); d.castShadow = true; this.door.add(d);
      const kn = new THREE.Mesh(new THREE.SphereGeometry(0.05, 8, 6).translate(1.0, 1.0, -0.08), twoTone(new THREE.MeshLambertMaterial({ color: "#f2c230" }))); this.door.add(kn);
      this.door.position.set(-0.58, G0, 4.88); this.A.add(this.door);
      const fb = new Batch(), fm = lam("doorFrame", () => ({ color: "#f4f1ea" }));
      fb.add(boxGeo(V(-0.7, 0, -0.06), V(-0.6, 2.25, 0.06)), fm); fb.add(boxGeo(V(0.6, 0, -0.06), V(0.7, 2.25, 0.06)), fm); fb.add(boxGeo(V(-0.7, 2.15, -0.06), V(0.7, 2.27, 0.06)), fm);
      fb.build(this.doorFrame); this.doorFrame.position.set(0, G0, 4.82); this.A.add(this.doorFrame); }
    // cupboard-under-the-stairs door (hinged at z -0.95, on the x = -1.66 side)
    { const d = new THREE.Mesh(new THREE.BoxGeometry(0.05, 1.28, 0.98).translate(0, 0.64, -0.49), twoTone(new THREE.MeshLambertMaterial({ color: "#c9a36a" }))); this.cupDoor.add(d); this.cupDoor.position.set(-1.69, G0, -0.95); this.A.add(this.cupDoor); }
    // the chair
    { const cb = new Batch(), wm = lam("chair", () => ({ color: "#c0353a" }));
      cb.add(boxGeo(V(-0.22, 0.42, -0.22), V(0.22, 0.48, 0.22), 0, true), wm); cb.add(boxGeo(V(-0.22, 0.48, -0.24), V(0.22, 0.95, -0.19), 0, true), wm);
      for (const [x, z] of [[-0.19, -0.19], [0.19, -0.19], [-0.19, 0.19], [0.19, 0.19]]) cb.add(boxGeo(V(x - 0.025, 0, z - 0.025), V(x + 0.025, 0.42, z + 0.025), 0, true), wm);
      cb.build(this.chair); this.A.add(this.chair); }
    // the window glass we smash (front left, ground floor) and its shards
    this.pane = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.3).translate(-2.6, 1.75, 4.93), new THREE.MeshBasicMaterial({ color: "#a8d0e8", transparent: true, opacity: 0.35, side: THREE.DoubleSide, depthWrite: false }));
    this.pane.layers.set(NOINK); this.A.add(this.pane);
    const shG = new THREE.BufferGeometry(); shG.setAttribute("position", new THREE.Float32BufferAttribute([0, 0.09, 0, -0.07, -0.06, 0, 0.08, -0.05, 0], 3)); shG.computeVertexNormals();
    for (let i = 0; i < 36; i++) { const s = new THREE.Mesh(shG, new THREE.MeshBasicMaterial({ color: "#d8f0ff", side: THREE.DoubleSide })); s.layers.set(NOINK); s.visible = false; this.A.add(s); this.shards.push(s); }
    // the crack on the photo wall (x = -4.24): segments revealed in order
    const pts: [number, number][] = [[0.3, 0.7], [0.75, 1.15], [1.05, 1.5], [1.45, 1.75], [1.7, 2.25], [1.55, 2.7], [1.95, 3.1], [2.35, 3.45], [2.55, 3.95], [3.0, 4.5]];
    const crM = new THREE.MeshBasicMaterial({ color: "#1d1820" });
    for (let i = 0; i < pts.length - 1; i++) {
      const [y0, z0] = pts[i], [y1, z1] = pts[i + 1], len = Math.hypot(y1 - y0, z1 - z0);
      const g = new THREE.BoxGeometry(0.02, 0.055, len).translate(0, 0, len / 2);
      const m = new THREE.Mesh(g, crM); m.position.set(-4.23, y0, z0); m.lookAt(-4.23, y1, z1); m.layers.set(NOINK); this.A.add(m);
      this.crack.push({ m, a: 38.85 + i * 0.2, b: 38.85 + (i + 1) * 0.2 });
    }
    // family photos on that wall
    [1.5, 2.5, 3.5].forEach((z, k) => {
      const g = new THREE.Group(), f = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.46, 0.56), twoTone(new THREE.MeshLambertMaterial({ color: "#6b4a32" })));
      const ph = new THREE.Mesh(new THREE.PlaneGeometry(0.46, 0.36).rotateY(Math.PI / 2).translate(0.03, 0, 0), new THREE.MeshLambertMaterial({ map: photoTex(k) }));
      g.add(f, ph); g.position.set(-4.2, 1.85 + (k === 1 ? 0.15 : 0), z); this.A.add(g); this.photos.push({ g, z });
    });
    R.add(this.A);
    // ---- the dog ----
    this.dog = new Dog(R);
    // ---- grandpa's ladder (flashback, at the neighbour's door) ----
    { const lb = new Batch(), lm = lam("ladder", () => ({ color: "#c9a36a" }));
      for (const x of [-0.3, 0.3]) lb.add(beamBetween(V(x, 0, 0.9), V(x, 2.6, 0.15), 0.05), lm);
      for (let i = 1; i < 8; i++) { const k = i / 8; lb.add(beamBetween(V(-0.3, 2.6 * k, 0.9 - 0.75 * k), V(0.3, 2.6 * k, 0.9 - 0.75 * k), 0.035), lm); }
      lb.build(this.ladder); this.ladder.position.set(13.7, 0, 5.05); R.add(this.ladder); }
    // ---- cutaway diagram ----
    { const plate = new THREE.Mesh(new THREE.PlaneGeometry(160, 160).translate(0, -30, 0), new THREE.MeshBasicMaterial({ map: cutTex(), fog: false })); this.cut.add(plate); this.cut.position.set(CUT_X, 0, 0); R.add(this.cut); }
  }

  private shotSun(id: number, s: ShotDef, L: LightPreset, LN: LName) {
    const key = id + LN; let v = this.sunCache.get(key); if (v) return v;
    let fx = 0, fz = 0;
    for (let f = s.a; f < s.b; f += 3) { const c = camAt(id, f), x = c.look[0] - c.pos[0], zz = c.look[2] - c.pos[2], n = Math.hypot(x, zz) || 1; fx += x / n; fz += zz / n; }
    const n = Math.hypot(fx, fz) || 1; fx /= n; fz /= n;
    const az = THREE.MathUtils.degToRad(s.sunAz ?? L.az), el = THREE.MathUtils.degToRad(s.sunEl ?? L.el);
    const hx = fx * Math.cos(az) - fz * Math.sin(az), hz = fz * Math.cos(az) + fx * Math.sin(az);
    v = new THREE.Vector3(hx * Math.cos(el), Math.sin(el), hz * Math.cos(el)).normalize();
    if (LN === "room") v = new THREE.Vector3(0.3, 0.55, 0.78).normalize(); // moonlight through the front windows
    this.sunCache.set(key, v); return v;
  }
  private actor(i: number) { while (this.actors.length <= i) this.actors.push(new Actor(this.root)); return this.actors[i]; }
  private fx(i: number) { while (this.fxs.length <= i) this.fxs.push(new Fx(this.root)); return this.fxs[i]; }

  update(id: number, f: number, cam: THREE.PerspectiveCamera, scene: THREE.Scene) {
    const t = f / FPS, s = SHOTS[id - 1], LN = lightOf(s, t), Lp = LIGHTS[LN], K = LOOK[LN];
    const c = camAt(id, f);
    cam.position.set(...c.pos); cam.up.set(0, 1, 0); cam.lookAt(...c.look); cam.rotateZ(c.roll);
    cam.fov = c.fov; cam.near = 0.05; cam.far = 1600; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    const focus = V(...c.look), dist = cam.position.distanceTo(focus);
    cam.layers.enable(NOINK);
    const night = LN === "night" || LN === "room";
    // ---- light rig ----
    const sunDir = this.shotSun(id, s, Lp, LN);
    this.hemi.color.set(Lp.sky); this.hemi.groundColor.set(Lp.ground); this.hemi.intensity = Lp.hemiI;
    this.sun.color.set(Lp.sunCol); this.sun.intensity = Lp.sunI;
    const Rr = THREE.MathUtils.clamp(dist * 1.3 + 8, 12, 70);
    this.sun.position.copy(focus).addScaledVector(sunDir, 120); this.sun.target.position.copy(focus);
    const sc = this.sun.shadow.camera; sc.left = -Rr; sc.right = Rr; sc.top = Rr; sc.bottom = -Rr; sc.near = 5; sc.far = 300; sc.updateProjectionMatrix();
    this.sun.shadow.bias = Lp.bias; this.sun.shadow.normalBias = Lp.normalBias * (Rr / 12);
    const green = t >= GREEN_AT && id >= 5 && id <= 15, pulse = green ? 0.75 + 0.25 * Math.sin(t * 9) : 0;
    // inside after the light turns green: a faint green cast from the windows
    const gk = s.inside && green ? 0.18 : 0;
    TONE.uLitCol.value.set(Lp.lit[0] * (1 - gk), Lp.lit[1] * (1 + gk * 0.6), Lp.lit[2] * (1 - gk * 0.5)); TONE.uShadeCol.value.set(...Lp.shade); TONE.uShadeLift.value.set(...Lp.lift);
    TONE.uLambert.value = Lp.lambert; TONE.uSideK.value = Lp.sideK; TONE.uTerm.value = Lp.term; TONE.uBounce.value.set(...K.bounce); TONE.uSat.value = K.sat;
    CHAR.uCharTint.value.set(Lp.charTint[0] * (1 - gk), Lp.charTint[1] * (1 + gk * 0.4), Lp.charTint[2] * (1 - gk * 0.4)); CHAR.uCharShade.value = Lp.charShade; CHAR.uGrad.value = Lp.charGrad; CHAR.uBodyGrad.value = Lp.bodyGrad; CHAR.uSideTint.value.set(...Lp.sideTint);
    // ---- sky ----
    const su = this.skyMat.uniforms;
    K.sky.c.forEach((h, i) => untone(h, su["c" + i].value));
    const e = K.sky.e.map((deg) => THREE.MathUtils.degToRad(deg)); su.e.value.set(e[1], e[2], e[3], e[4]);
    su.uStars.value = night ? 1 : 0; this.sky.position.copy(cam.position);
    const k = typeof s.fog === "number" ? s.fog : 1;
    untone(Lp.fog, this.fog.color); this.fog.near = Lp.fogNear * k; this.fog.far = Lp.fogFar * k; scene.fog = this.fog; scene.background = null;
    if (id === 16) { this.fog.near = 2000; this.fog.far = 4000; }
    this.moon.visible = night; if (night) { this.moon.position.copy(cam.position).addScaledVector(V(-0.35, 0.55, -0.75).normalize(), 700); this.moon.scale.setScalar(36); }
    const cm = LN === "golden" ? this.cloudMaps.golden : LN === "day" ? this.cloudMaps.day : this.cloudMaps.night;
    this.clouds.forEach((m, i) => { m.visible = id !== 16; m.lookAt(cam.position.x, m.position.y, cam.position.z); (m.material as THREE.MeshBasicMaterial).map = cm[i % 4]; });

    // ---- door lights ----
    const ourC = green ? [0.3 * pulse, 5 * pulse, 0.8 * pulse] : [5, 0.35, 0.3];
    (this.ourLight.material as THREE.MeshBasicMaterial).color.setRGB(ourC[0], ourC[1], ourC[2]);
    (this.ourGlow.material as THREE.SpriteMaterial).color.setRGB(green ? 0.15 : 1.6, green ? 1.6 * pulse : 0.15, green ? 0.3 : 0.1);
    this.ourGlow.scale.setScalar(green ? 2.6 + 0.4 * pulse : 2.2);
    for (const n of this.nLights) { const on = !(id === 17 && t < 70.4 && n.x === 13); n.m.visible = n.s.visible = on; }
    // ---- house A: sink, door, glasses, lamp, crack, photos, chair, pane ----
    const sunk = id === 15 ? sinkY(t) : 0;
    this.A.visible = !(id === 17 && t >= 71.4); this.A.position.y = sunk;
    this.A.rotation.set(id === 15 ? 0.1 * sinkAt(t) : 0, 0, id === 15 ? -0.06 * sinkAt(t) : 0);
    const shakeAmp = t > 17.2 && t < 46.4 ? 0.004 + 0.02 * clamp01((t - 17.2) / 4) : 0;
    this.glasses.forEach((gl, i) => {
      const j = shakeAmp * (1 + (i % 3) * 0.4);
      gl.m.position.set(gl.x + j * Math.sin(t * 47 + i * 1.7), gl.y + Math.abs(j * Math.sin(t * 61 + i)), gl.z + j * 0.6 * Math.sin(t * 39 + i * 2.3));
      gl.m.rotation.set(j * 6 * Math.sin(t * 31 + i), 0, j * 8 * Math.sin(t * 43 + i * 0.7));
      if (i === 4 && t > 19.9) { const u = Math.min(1, (t - 19.9) / 0.45); gl.m.position.set(gl.x + 0.1 * u, gl.y - 1.55 * u * u, gl.z + 0.35 * u); gl.m.rotation.z = -2.5 * u; gl.m.visible = u < 1; } else gl.m.visible = true;
    });
    this.lamp.rotation.set(shakeAmp * 9 * Math.sin(t * 3.1), 0, shakeAmp * 12 * Math.sin(t * 2.7 + 1));
    const yank = id === 10 && t > 35.3 ? 1 : 0;
    this.door.rotation.y = yank * (0.04 * Math.max(0, Math.sin(t * 15)) - 0.01);
    this.doorFrame.rotation.z = (id >= 10 && id <= 15 && t > 37.3) ? -0.07 * smooth((t - 37.3) / 0.4) : 0;
    this.cupDoor.rotation.y = id === 8 && t > 31.1 ? 0.95 : id === 9 ? 0.95 + 0.5 * smooth((t - 32.9) / 0.35) : id > 9 && id < 15 ? 1.45 : 0;
    for (const cr of this.crack) { const u = id >= 11 && id <= 15 ? clamp01((t - cr.a) / (cr.b - cr.a)) : 0; cr.m.visible = u > 0; cr.m.scale.set(1, 1, Math.max(0.01, u)); }
    this.photos.forEach((p, k) => {
      const t0 = 40.6 + k * 0.25, u = id >= 11 && id <= 15 ? clamp01((t - t0) / 0.7) : 0;
      p.g.rotation.set(1.3 * u * (k % 2 ? 1 : -1) * 0.5, 0, 0);
      p.g.position.set(-4.2 + 0.25 * u, 1.85 + (k === 1 ? 0.15 : 0) - 1.55 * Math.max(0, u * u * 1.0) * (u > 0.15 ? 1 : 0), p.z);
      if (u >= 1) p.g.position.y = G0 + 0.03;
    });
    // chair: rest -> lifted -> thrown through the glass -> lawn
    {
      const rest = V(-1.25, G0, 2.55), hold = V(-1.55, 1.25, 3.05), over = V(-1.7, 1.75, 3.2), win = V(-2.6, 1.55, 4.95), land = V(-3.1, 0, 7.6);
      let p = rest, rx = 0, rz = 0;
      if (id >= 12 && id <= 15) {
        if (t < 42.7) p = rest;
        else if (t < 43.2) { p = rest.clone().lerp(hold, smooth((t - 42.7) / 0.5)); rx = -0.4 * smooth((t - 42.7) / 0.5); }
        else if (t < 43.7) { p = hold.clone().lerp(over, smooth((t - 43.2) / 0.5)); rx = -0.4 - 0.6 * smooth((t - 43.2) / 0.5); }
        else if (t < 43.95) { p = over.clone().lerp(win, (t - 43.7) / 0.25); rx = -1 + 2 * (t - 43.7); }
        else { const u = clamp01((t - 43.95) / 0.7); p = win.clone().lerp(land, u); p.y = win.y * (1 - u) + 1.2 * Math.sin(Math.PI * u) * (1 - u); rx = 3 * u; rz = 2 * u; }
      }
      this.chair.position.copy(p); this.chair.rotation.set(rx, 0.6, rz);
    }
    const smashed = (id === 12 && t >= 43.95) || id > 12;
    this.pane.visible = !smashed;
    this.shards.forEach((sh, i) => {
      const u = t - 43.95; sh.visible = id === 12 && u > 0 && u < 1.2;
      if (sh.visible) { const vx = (hh(i, 1) - 0.5) * 3, vy = hh(i, 2) * 2.5, vz = 1.5 + hh(i, 3) * 3; sh.position.set(-2.6 + (hh(i, 4) - 0.5) * 1.4 + vx * u, 1.75 + (hh(i, 5) - 0.5) * 1.1 + vy * u - 4.9 * u * u, 4.95 + vz * u); sh.rotation.set(u * 9 * hh(i, 6), u * 7, u * 11 * hh(i, 7)); sh.scale.setScalar(0.6 + hh(i, 8)); if (sh.position.y < 0.03) sh.position.y = 0.03; }
    });
    this.ladder.visible = id === 17 && t < 71.4;
    this.cut.visible = id === 16;

    // ---- cast + effects ----
    const right = V(0, 0, 0).setFromMatrixColumn(cam.matrixWorld, 0);
    const ci: CamInfo = { pos: cam.position, right };
    castBegin(LN, ci);
    const st: Stage = { places: [], fx: [] };
    this.dog.hide();
    this.stage(id, t, ci, st, sunk);
    this.frustum.setFromProjectionMatrix(this.m4.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse));
    let ai = 0; const used: Actor[] = [];
    for (const p of st.places) {
      const sc2 = p.scale ?? 1;
      if (!this.frustum.intersectsSphere(this.sph.set(this.v.set(p.x, p.y + 1.0 * sc2, p.z), 2))) continue;
      const a = this.actor(ai++), [w, h, kk] = p.size ?? [300, 500, 0.5];
      a.r = this.pool.req(p.key, w, h, kk, p.draw); a.mesh.visible = true;
      a.mesh.position.set(p.x, p.y, p.z);
      a.mesh.rotation.set(0, p.yaw ?? Math.atan2(cam.position.x - p.x, cam.position.z - p.z), p.roll ?? 0);
      a.mesh.scale.set(p.mirror ? -sc2 : sc2, sc2, sc2); a.mesh.castShadow = Lp.actorShadow; used.push(a);
    }
    for (let i = ai; i < this.actors.length; i++) this.actors[i].mesh.visible = false;
    let fi = 0; const fused: Fx[] = [];
    for (const p of st.fx) {
      if (!this.frustum.intersectsSphere(this.sph.set(this.v.set(p.x, p.y, p.z), Math.max(p.w, p.h)))) continue;
      const e2 = this.fx(fi++); e2.r = this.pool.req(p.key, p.cw, p.ch, 1, p.draw); e2.use(!!p.soft); e2.mesh.visible = true;
      e2.mesh.position.set(p.x, p.y, p.z);
      if (p.flat) e2.mesh.rotation.set(-Math.PI / 2, 0, p.rot ?? 0); else { e2.mesh.quaternion.copy(cam.quaternion); e2.mesh.rotateZ(p.rot ?? 0); }
      e2.mesh.scale.set(p.w, p.h, 1); fused.push(e2);
    }
    for (let i = fi; i < this.fxs.length; i++) this.fxs[i].mesh.visible = false;
    this.pool.flush();
    for (const a of used) a.bind();
    for (const e2 of fused) e2.bind();
    return focus;
  }

  // a card person posed from a walker (side view when moving across the camera, front otherwise)
  private put(out: Stage, cam: CamInfo, o: Outfit, key: string, i: number, w: W, t: number, expr: Expr, extra: Partial<FrontOpts> = {}, sc = 1, shadow = true, roll = 0) {
    const blink = (extra as { blink?: number }).blink ?? lidAt(t, i), ph = q(((w.phase % 1) + 1) % 1, 240);
    const tx = cam.pos.x - w.x, tz = cam.pos.z - w.z, tl = Math.hypot(tx, tz) || 1, toward = (tx * w.dx + tz * w.dz) / tl, across = w.dx * cam.right.x + w.dz * cam.right.z;
    let pl;
    if (w.mode === "jump") pl = person(cam, { i, o, okey: key }, w.x, w.y, w.z, { side: false, mirror: false }, { mode: "jump", pose: q(w.pose, 30), expr, blink, ...extra }, {}, sc);
    else if (w.mode === "stand" || w.mode === "sit") pl = person(cam, { i, o, okey: key }, w.x, w.y, w.z, { side: false, mirror: false }, { mode: w.mode, expr, blink, ...extra }, {}, sc);
    else if (Math.abs(toward) < 0.32) {
      const fs = Math.sqrt(Math.max(0, 1 - toward * toward));
      pl = person(cam, { i, o, okey: key }, w.x, w.y, w.z, { side: true, mirror: across < 0 }, {}, { mode: w.mode, phase: ph, amt: q(w.amt, 40), stride: q(fs, 40), expr, blink }, sc);
    } else {
      const yaw = Math.max(-1, Math.min(1, across)) * Math.sign(toward);
      pl = person(cam, { i, o, okey: key }, w.x, w.y, w.z, { side: false, mirror: false }, { mode: w.mode, phase: ph, amt: q(w.amt, 40), yaw: q(yaw, 40), expr, blink, facing: Math.abs(yaw) > 0.3 ? (yaw > 0 ? 1 : -1) : 0, ...extra }, {}, sc);
    }
    if (roll) pl.roll = roll;
    out.places.push(pl);
    if (shadow && w.mode !== "sit" && !roll) blob(out, w.x, w.y, w.z, sc);
  }
  /** side-view action pose (push / pull / shake / throw) facing +dir across the camera */
  private act(out: Stage, cam: CamInfo, o: Outfit, key: string, i: number, x: number, y: number, z: number, dirX: number, dirZ: number, t: number, expr: Expr, pose: number, sc = 1) {
    const across = dirX * cam.right.x + dirZ * cam.right.z;
    out.places.push(person(cam, { i, o, okey: key }, x, y, z, { side: true, mirror: across < 0 }, {}, { mode: "push", pose: q(pose, 20), expr, blink: lidAt(t, i) }, sc));
    blob(out, x, y, z, sc);
  }
  private puff(out: Stage, u: number, x: number, y: number, z: number, s: number) {
    if (u <= 0 || u >= 1) return; const k = q(u, 24);
    out.fx.push({ key: `puff${k}`, cw: 300, ch: 300, draw: (p) => fxPuff(p, k), x, y, z, w: s, h: s, soft: true });
  }
  private S(x: number, z: number, y = G0): W { return { x, y, z, dx: 0, dz: 1, mode: "stand", phase: 0, amt: 0, pose: 0 }; }

  private stage(id: number, t: number, cam: CamInfo, out: Stage, sunk: number) {
    const S = this.S.bind(this);
    if (id === 2) {
      const gp = walkAt([[5.95, 1.6, 9.6, "walk"], [7.6, 0.6, 6.6, "stand"]], t), kd = walkAt([[5.95, 0.4, 10.0, "walk"], [7.6, -0.5, 7.0, "stand"]], t);
      const point = t > 7.6 && t < 9.6 ? smooth((t - 7.6) / 0.4) : t > 10.0 ? 0.5 + 0.5 * Math.sin(t * 6) : 0;
      this.put(out, cam, GRANDPA, "gp", 7, gp, t, t > 9.6 ? "stern" : "smile", point > 0 ? { wave: q(point, 16), look: t < 9.6 ? 0 : -1 } : {});
      this.put(out, cam, KID_SMALL, "kidS", 1, kd, t, t > 10 ? "nervous" : "smile", { look: 1 }, 0.62);
    }
    if (id === 3) {
      this.dog.pose(1.0, G0, -3.3, 2.2, "growl", t);
      const kd = walkAt([[13.08, 1.6, 0.9, "walk"], [14.6, 1.6, -0.25, "stand"]], t);
      this.put(out, cam, KID, "kid", 1, kd, t, t < 15 ? "neutral" : "nervous", { look: -1 }, 0.9);
    }
    if (id === 4 && t > 19.6) { /* the glass hits the counter */ const u = clamp01((t - 20.35) / 0.5); if (u > 0 && u < 1) out.fx.push({ key: `burst${q(u, 20)}`, cw: 500, ch: 500, draw: (p) => fxBurst(p, q(u, 20), "#d8f0ff", 10), x: 2.95, y: 1.2, z: -4.2, w: 0.6, h: 0.6 }); }
    if (id === 6) {
      const kd = walkAt([[22.35, 0.6, 3.7, "stand"], [23.05, 0.6, 3.7, "run"], [23.6, 0.9, 1.6]], t);
      this.put(out, cam, KID, "kid", 1, kd, t, "shock", { look: t < 22.8 ? 0 : 0 }, 0.9);
    }
    if (id === 7) {
      if (t < 25.0) this.put(out, cam, KID, "kid", 1, walkAt([[23.6, -0.85, -4.6, "run", G0], [23.75, -0.85, -4.3, "run", G0], [24.95, -0.85, -0.7, "run", FL1]], t), t, "pained", {}, 0.9);
      else {
        // mum asleep (lying on the bed), notes from her headphones; I run in and shake her
        const wake = clamp01((t - 27.35) / 0.3);
        const shake = t > 26.55 && t < 27.4 ? 0.05 * Math.sin(t * 38) : 0;
        const mumW = { ...S(-3.05 + shake, 3.4, FL1 + 0.62), mode: "sit" as Mode };
        this.put(out, cam, MUM, "mum", 2, mumW, t, wake < 0.5 ? "neutral" : "shock", wake < 0.5 ? ({ blink: 1, headTilt: 0.25 } as Partial<FrontOpts>) : { look: 1 }, 1, false);
        if (wake < 0.5) { const u = (t * 0.8) % 1; out.fx.push({ key: `note${q(u, 20)}`, cw: 300, ch: 300, draw: (p) => notesDraw(p, q(u, 20)), x: -2.75, y: FL1 + 1.9, z: 3.3, w: 0.5, h: 0.5 }); }
        if (t < 26.5) this.put(out, cam, KID, "kid", 1, walkAt([[25.0, -2.35, 0.2, "run", FL1], [26.5, -1.7, 3.0, "stand", FL1]], t), t, "pained", {}, 0.9);
        else this.act(out, cam, KID, "kid", 1, -1.7, FL1, 3.0, -1, 0, t, "pained", t < 27.4 ? 0.55 + 0.45 * Math.abs(Math.sin(t * 19)) : 0.3, 0.9);
      }
    }
    if (id === 8) {
      if (t < 31.1) {
        const kd = walkAt([[28.4, 1.45, 0.2, "run", FL1], [29.4, 2.3, 1.9, "stand", FL1]], t);
        this.put(out, cam, KID, "kid", 1, kd, t, t < 30.2 ? "pained" : "nervous", { look: t > 29.6 ? (Math.sin(t * 3) > 0 ? 1 : -1) : 0 }, 0.9);
      } else this.put(out, cam, SIS, "sis", 3, S(-1.45, -1.45), t, t > 31.7 ? "laugh" : "grin", { look: -1 }, 0.62, false);
    }
    if (id === 9) {
      const kd = walkAt([[32.45, -3.0, -3.0, "run"], [32.95, -2.35, -1.45, "stand"], [33.35, -2.35, -1.45, "run"], [35.0, -2.6, 1.9]], t);
      const sd = walkAt([[32.45, -1.4, -1.45, "stand"], [33.35, -1.4, -1.45, "run"], [35.0, -2.0, 2.3]], t);
      if (t > 32.95 && t < 33.35) this.act(out, cam, KID, "kid", 1, kd.x, G0, kd.z, 1, 0, t, "pained", smooth((t - 32.95) / 0.3), 0.9);
      else this.put(out, cam, KID, "kid", 1, kd, t, "pained", {}, 0.9);
      this.put(out, cam, SIS, "sis", 3, sd, t, t < 33.3 ? "grin" : "shock", { look: 1 }, 0.62);
    }
    if (id === 10) {
      this.act(out, cam, KID, "kid", 1, 0.25, G0, 4.15, 0, 1, t, "pained", t > 35.3 ? 0.35 + 0.65 * Math.abs(Math.sin(t * 15)) : 0.2, 0.9);
      this.act(out, cam, MUM, "mum", 2, -0.55, G0, 4.0, 0, 1, t, "pained", t > 36.0 ? 0.5 + 0.5 * Math.abs(Math.sin(t * 13 + 1)) : 0.1);
      this.put(out, cam, SIS, "sis", 3, S(1.0, 3.3), t, "shock", { look: -1 }, 0.62);
      this.dog.pose(-1.3, G0, 3.5, Math.PI / 2, "bark", t);
    }
    if (id === 11) {
      const back = smooth((t - 39.0) / 0.8);
      this.put(out, cam, MUM, "mum", 2, S(-1.75 + 0.3 * back, 3.75), t, "shock", { look: -1 });
      this.put(out, cam, SIS, "sis", 3, S(-1.25 + 0.3 * back, 3.35), t, "shock", { look: -1 }, 0.62);
      this.dog.pose(-1.0, G0, 2.9, Math.PI, "bark", t);
      for (let kk = 0; kk < 3; kk++) this.puff(out, clamp01((t - 40.6 - kk * 0.25) / 0.9), -4.0, G0 + 0.3, [1.5, 2.5, 3.5][kk], 0.6);
    }
    if (id === 12) {
      if (t < 44.3) {
        const pose = t < 42.7 ? 0 : t < 43.6 ? 0.3 : t < 43.95 ? smooth((t - 43.6) / 0.25) : 1 - 0.5 * clamp01(t - 43.95);
        this.act(out, cam, KID, "kid", 1, -1.35, G0, 2.9, -0.5, 1, t, t < 43.6 ? "pained" : "shock", pose, 0.9);
        this.put(out, cam, MUM, "mum", 2, S(0.6, 3.4), t, "shock", { look: -1 });
        this.put(out, cam, SIS, "sis", 3, S(0.0, 3.1), t, "shock", { look: -1 }, 0.62);
        const u = clamp01((t - 43.95) / 0.5); if (u > 0 && u < 1) out.fx.push({ key: `burst${q(u, 20)}`, cw: 500, ch: 500, draw: (p) => fxBurst(p, q(u, 20), "#e8f6ff", 14), x: -2.6, y: 1.75, z: 4.95, w: 1.8, h: 1.8 });
      } else {
        // out through the window: up over the sill, arc, down onto the lawn
        const jump = (t0: number, x: number) => { const u = clamp01((t - t0) / 0.75); return { u, x, y: G0 * (1 - u) + 1.45 * Math.sin(Math.PI * Math.min(1, u * 1.15)) * (1 - 0.25 * u), z: 4.1 + 3.4 * u }; };
        const who: [Outfit, string, number, number, number, number][] = [[SIS, "sis", 3, 44.75, -2.35, 0.62], [MUM, "mum", 2, 45.05, -2.75, 1], [KID, "kid", 1, 45.4, -2.5, 0.9]];
        for (const [o, key, ii, t0, x, sc] of who) {
          const j = jump(t0, x); if (t < t0 - 0.05) continue;
          const w: W = { x: j.x, y: Math.max(0, j.y), z: j.z, dx: 0, dz: 1, mode: j.u < 1 ? "jump" : "stand", phase: 0, amt: 0, pose: 0.25 + 0.6 * j.u };
          this.put(out, cam, o, key, ii, w, t, "shock", {}, sc);
        }
        const dj = clamp01((t - 45.8) / 0.6); if (t > 45.75) this.dog.pose(-2.2, 0, 4.2 + 3.6 * dj, Math.PI / 2, dj < 1 ? "jump" : "run", t, 1.4 * Math.sin(Math.PI * dj));
      }
    }
    if (id === 13) {
      const land = (t0: number, x0: number, z0: number, x1: number, z1: number): W => walkAt([[46.4, x0, z0, "stand", 0], [t0, x0, z0, "run", 0], [t0 + 1.4, x1, z1, "stand", 0]], t);
      const kd = land(47.0, -2.5, 7.6, -2.2, 9.7), md = land(46.9, -2.75, 7.5, -3.3, 9.9), sd = land(46.8, -2.35, 7.5, -2.75, 10.3);
      const bw = (w: W) => { w.y = 0; return w; };
      this.put(out, cam, KID, "kid", 1, bw(kd), t, t < 47.6 ? "shock" : t < 48.1 ? "pained" : "relief_open", t > 48.1 && t < 49.2 ? { look: Math.sin(t * 4) > 0 ? -1 : 1 } : {}, 0.9);
      this.put(out, cam, MUM, "mum", 2, bw(md), t, t < 48 ? "shock" : "relief");
      this.put(out, cam, SIS, "sis", 3, bw(sd), t, t < 48 ? "shock" : "relief_open", {}, 0.62);
      const dd = walkAt([[46.4, -2.2, 7.8, "run", 0], [47.4, -0.8, 9.6, "run", 0], [48.4, -1.4, 10.6, "stand", 0]], t);
      this.dog.pose(dd.x, 0, dd.z, Math.atan2(dd.dz, dd.dx), dd.mode === "run" ? "run" : "stand", t);
    }
    if (id === 14 || id === 15) {
      const back = id === 15 ? smooth((t - 56.2) / 1.2) : 0;
      const turn = t > 53.45 && id === 14;
      this.put(out, cam, KID, "kid", 1, S(-2.2, 9.7 + 1.6 * back, 0), t, id === 15 ? "shock" : "nervous", { look: id === 14 ? -1 : 0 }, 0.9);
      this.put(out, cam, MUM, "mum", 2, S(-3.3, 9.9 + 1.6 * back, 0), t, id === 15 ? "shock" : turn ? "stern" : "dazed", turn ? { look: 1 } : {});
      this.put(out, cam, SIS, "sis", 3, S(-2.75, 10.3 + 1.6 * back, 0), t, id === 15 ? "shock" : "nervous", {}, 0.62);
      this.dog.pose(-1.4, 0, 10.6 + 1.6 * back, Math.PI / 2, id === 15 ? "bark" : "stand", t);
      if (id === 15) {
        for (let kk = 0; kk < 14; kk++) { const a = (kk / 14) * Math.PI * 2, u = clamp01((t - 56.1 - (kk % 4) * 0.15) / 2.6); this.puff(out, u, 8.6 * Math.cos(a), 0.5 + 4 * u, 8.6 * Math.sin(a), 4 + 5 * u); }
        if (t > 58.75) for (let kk = 0; kk < 3; kk++) this.puff(out, clamp01(((t - 58.75) * 0.4 + kk / 3) % 1), (kk - 1) * 3, -10 + 3 * kk, (kk % 2) * 2 - 1, 5);
      }
    }
    if (id === 16) for (let kk = 0; kk < 5; kk++) this.puff(out, ((t * 0.35 + kk / 5) % 1), CUT_X + (kk - 2) * 2.5, -12 - 6 * ((t * 0.35 + kk / 5) % 1), 1, 6);
    if (id === 17) {
      if (t < 71.4) {
        const reach = t > 69.0 ? 1 : 0.5 + 0.5 * Math.sin(t * 5);
        this.put(out, cam, GRANDPA, "gp", 7, S(13.7, 5.75, 1.05), t, t > 70.4 ? "smile" : "neutral", { wave: q(reach, 16), look: -1 });
        if (t > 70.4 && t < 70.9) out.fx.push({ key: `burst${q((t - 70.4) / 0.5, 20)}`, cw: 500, ch: 500, draw: (p) => fxBurst(p, q((t - 70.4) / 0.5, 20), "#ff8a7a", 10), x: 13, y: 2.75, z: 5.3, w: 1.2, h: 1.2 });
      } else {
        this.put(out, cam, KID, "kid", 1, S(-0.6, 10.6, 0), t, "neutral", {}, 0.9);
        this.put(out, cam, MUM, "mum", 2, S(-1.6, 10.9, 0), t, "neutral", {});
        this.put(out, cam, SIS, "sis", 3, S(0.3, 10.9, 0), t, "neutral", {}, 0.62);
        this.dog.pose(1.0, 0, 10.8, Math.PI / 2, "stand", t);
      }
    }
    void sunk; void ramp; void Pen;
  }
}
