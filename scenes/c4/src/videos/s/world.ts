// "The Light Next Door" set: two houses facing each other across a garden. House A (the kid's)
// is a hollow dollhouse: kitchen below, bedroom above, attic under the roof, real window holes. House B (Mr. Hale's)
// is its mirror, with the lamp window that flashes. update(id, f, camera) poses lights, flashes, beams and the cast.
import * as THREE from "three";
import { Batch, V, lam, Kit, house, boxGeo } from "./build";
import { ctex, rep, grassHD, cloudHD } from "./paint";
import { Pen, Outfit, Expr, FrontOpts, SKINS, INK, fxPuff, fxBurst } from "./toon";
import { LIGHTS, LOOK, LightPreset } from "./lights";
import { TONE, CHAR, twoTone, untone } from "./shade";
import { NOINK } from "./ink";
import { Pool, Actor, Fx, Stage, CamInfo, castBegin, person, blob, lidAt, q, hh } from "./cast";
import { discTex, haloTex, beamBetween } from "./bworld";
import {
  FPS, SHOTS, camAt, ShotDef, V3, clamp01, smooth, ramp, haleFlash, torchFlash, runSoFar,
  FL1, CEIL, ATTIC, WIN_Z, WIN_Y, A_X, B_X, BED, HATCH, DESK, HALE_WIN, KID_WIN,
} from "./story";

export const loadKit = () => Promise.resolve({} as Kit);

// ---------------- dollhouse builder ----------------
type Hole = [number, number, number, number]; // u0, u1, v0, v1
/** a wall slab in local house coords. axis "x": wall plane x in [c0, c1], spanning z (u) and y (v); axis "z": plane z in [c0, c1], spanning x (u) and y */
class House {
  constructor(public b: Batch, public cx: number, public s: 1 | -1) {}
  X(x: number) { return this.cx + this.s * x; }
  box(mat: THREE.Material, x0: number, x1: number, y0: number, y1: number, z0: number, z1: number) {
    const a = this.X(x0), c = this.X(x1);
    this.b.add(boxGeo(V(Math.min(a, c), y0, z0), V(Math.max(a, c), y1, z1), 0, true), mat);
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
  /** gable triangle at local x = xw (thickness t) with an optional square vent */
  gable(mat: THREE.Material, xw: number, t: number, vent?: [number, number, number, number]) {
    const sh = new THREE.Shape([new THREE.Vector2(-5.4, ATTIC), new THREE.Vector2(5.4, ATTIC), new THREE.Vector2(0, 10)]);
    if (vent) sh.holes.push(new THREE.Path([new THREE.Vector2(vent[0], vent[2]), new THREE.Vector2(vent[1], vent[2]), new THREE.Vector2(vent[1], vent[3]), new THREE.Vector2(vent[0], vent[3])]));
    const g = new THREE.ExtrudeGeometry(sh, { depth: t, bevelEnabled: false }); // shape in (z, y) after rotation
    g.rotateY(-Math.PI / 2); // shape x -> world z, extrude z -> world x (towards -x)
    // after rotateY(-90): (x, y, z) -> (-z, y, x)  => shape-x lands on world z, extrusion runs along -x
    const a = this.X(xw), b2 = this.X(xw - this.s * t);
    g.translate(Math.max(a, b2), 0, 0);
    this.b.add(g, mat);
  }
}
const buildShell = (H: House, sid: "A" | "B", wallC: string, trimC: string, roofC: string, inC: string) => {
  const W = lam("wall" + sid, () => ({ color: wallC })), T = lam("trim" + sid, () => ({ color: trimC })), R = lam("roof" + sid, () => ({ color: roofC }));
  const IN = lam("in" + sid, () => ({ color: inC })), SL = lam("slab", () => ({ color: "#d8d0c4" }));
  const t = 0.25, winK: Hole = [WIN_Z - 0.8, WIN_Z + 0.8, 1.1, 2.4], winB: Hole = [WIN_Z - 0.8, WIN_Z + 0.8, 4.1, 5.6];
  // gap-facing wall (+x local): kitchen window, bedroom window
  H.wall(W, "x", 4.5 - t, 4.5, -5, 5, 0, ATTIC, [winK, winB, [1.6, 3.0, 4.1, 5.6]]);
  H.wall(W, "x", -4.5, -4.5 + t, -5, 5, 0, ATTIC, [[-1.5, 0, 1.1, 2.4], [-1.5, 0, 4.1, 5.6]]);
  H.wall(W, "z", 5 - t, 5, -4.5, 4.5, 0, ATTIC, [[-0.6, 0.6, 0.2, 2.4], [-3.4, -1.8, 1.1, 2.4], [1.8, 3.4, 1.1, 2.4], [-3.4, -1.8, 4.1, 5.6], [1.8, 3.4, 4.1, 5.6]]);
  H.wall(W, "z", -5, -5 + t, -4.5, 4.5, 0, ATTIC, [[-2.8, -1.2, 1.1, 2.4]]);
  // window trims (frames) on the gap side
  for (const [v0, v1] of [[1.1, 2.4], [4.1, 5.6]]) {
    H.box(T, 4.5, 4.62, v0 - 0.12, v0, WIN_Z - 0.92, WIN_Z + 0.92); H.box(T, 4.5, 4.62, v1, v1 + 0.12, WIN_Z - 0.92, WIN_Z + 0.92);
    H.box(T, 4.5, 4.62, v0, v1, WIN_Z - 0.92, WIN_Z - 0.8); H.box(T, 4.5, 4.62, v0, v1, WIN_Z + 0.8, WIN_Z + 0.92);
  }
  // floors / ceilings
  H.box(SL, -4.5, 4.5, 0, 0.2, -5, 5); H.box(SL, -4.5, 4.5, FL1 - 0.2, FL1, -5, 5);
  // attic floor with the hatch hole (A only) over the bed
  // inner partitions: bedroom/kitchen walls (x = 0 with a door, z = 0)
  H.wall(IN, "x", -0.06, 0.06, -4.75, 0, 0.2, FL1 - 0.2, [[-1.3, -0.3, 0.2, 2.3]]);
  H.wall(IN, "x", -0.06, 0.06, -4.75, 0, FL1, CEIL, [[-1.3, -0.3, FL1, FL1 + 2.15]]);
  H.box(IN, 0, 4.25, 0.2, CEIL, -0.06, 0.06);
  // roof: two slabs from the ridge (y 10, z 0) to the eaves (y ATTIC, z +-5.4), overhanging the gables
  const ang = Math.atan2(10 - ATTIC, 5.4), len = Math.hypot(10 - ATTIC, 5.4) + 0.5;
  for (const sz of [-1, 1]) {
    const g = new THREE.BoxGeometry(9.8, 0.22, len).translate(0, 0.11, len / 2).rotateX(ang);
    if (sz < 0) g.rotateY(Math.PI);
    H.b.add(g.translate(H.cx + H.s * 0, 10, 0), R);
  }
  H.gable(W, 4.5, t, sid === "A" ? [-0.55, 0.55, 7.3, 8.3] : undefined);
  H.gable(W, -4.5 + t, t);
  H.box(T, 4.5, 4.6, 7.2, 7.3, -0.65, 0.65); H.box(T, 4.5, 4.6, 8.3, 8.4, -0.65, 0.65);
  // front door + step
  H.box(lam("door" + sid, () => ({ color: sid === "A" ? "#3f6fb5" : "#7a3a3a" })), -0.58, 0.58, 0.2, 2.35, 4.9, 4.95);
  H.box(SL, -1.0, 1.0, 0, 0.2, 5, 5.8);
};

// ---------------- painted bits ----------------
const clockTex = () => ctex("clock300", 256, 128, (g) => {
  g.fillStyle = "#14121a"; g.fillRect(0, 0, 256, 128);
  g.font = "900 92px Arial Black, sans-serif"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillStyle = "#ff3b30"; g.fillText("3:00", 128, 66);
});
const posterTex = (k: number) => ctex("poster" + k, 256, 360, (g, r) => {
  const bg = ["#2f4a8a", "#c0353a", "#2b7a4b"][k]; g.fillStyle = bg; g.fillRect(0, 0, 256, 360);
  g.fillStyle = "#f2c230";
  if (k === 0) { for (let i = 0; i < 30; i++) g.fillRect(r() * 256, r() * 360, 4, 4); g.beginPath(); g.arc(150, 120, 50, 0, 7); g.fill(); g.fillStyle = bg; g.beginPath(); g.arc(170, 105, 46, 0, 7); g.fill(); }
  if (k === 1) { g.beginPath(); g.moveTo(128, 50); g.lineTo(210, 300); g.lineTo(46, 300); g.fill(); }
  if (k === 2) { g.fillRect(40, 140, 176, 70); g.beginPath(); g.arc(90, 230, 26, 0, 7); g.arc(166, 230, 26, 0, 7); g.fill(); }
  g.strokeStyle = INK; g.lineWidth = 10; g.strokeRect(5, 5, 246, 350);
});
/** notebook page: rows of dots and dashes (n symbols written), and the decoded word */
const drawNote = (p: Pen, n: number, word: number, chart: number) => {
  const g = p.g; g.fillStyle = "#f6f1e2"; g.fillRect(0, 0, 900, 600);
  g.strokeStyle = "rgba(80,120,200,.35)"; g.lineWidth = 3; for (let y = 80; y < 600; y += 60) { g.beginPath(); g.moveTo(0, y); g.lineTo(900, y); g.stroke(); }
  const syms = ".-.|..-|-.".split("|"); let k = 0, x0 = 90;
  for (let gi = 0; gi < 3; gi++) {
    let x = x0;
    for (const c of syms[gi]) {
      if (k++ >= n) break;
      g.fillStyle = "#1d1b22";
      if (c === ".") { g.beginPath(); g.arc(x + 14, 230, 16, 0, 7); g.fill(); x += 52; } else { g.fillRect(x, 218, 78, 26); x += 104; }
    }
    if (word > gi) { g.font = "900 150px Arial Black, sans-serif"; g.textAlign = "center"; g.fillStyle = "#d1262b"; g.fillText("RUN"[gi], x0 + 80, 430); }
    x0 += 280;
  }
  if (chart > 0) {
    g.globalAlpha = chart; g.fillStyle = "#fffbe8"; g.fillRect(560, 20, 320, 140); g.strokeStyle = INK; g.lineWidth = 6; g.strokeRect(560, 20, 320, 140);
    g.font = "900 40px Arial Black, sans-serif"; g.fillStyle = INK; g.textAlign = "left"; g.fillText("MORSE CODE", 580, 70);
    g.font = "700 30px Arial, sans-serif"; g.fillText("A .-   N -.   R .-.", 580, 112); g.fillText("U ..-   O ---   S ...", 580, 148); g.globalAlpha = 1;
  }
};
/** floating morse symbols over the gap */
const drawSyms = (p: Pen, s: string) => {
  const g = p.g; let x = 40;
  for (const c of s) {
    g.fillStyle = "#ffe9a8"; g.strokeStyle = INK; g.lineWidth = 8;
    if (c === ".") { g.beginPath(); g.arc(x + 22, 100, 22, 0, 7); g.fill(); g.stroke(); x += 70; } else { g.beginPath(); g.roundRect(x, 82, 110, 36, 12); g.fill(); g.stroke(); x += 140; }
  }
};
const beamTex = () => ctex("beam", 64, 256, (g) => {
  const gr = g.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = gr; g.fillRect(0, 0, 64, 256);
  const h = g.createLinearGradient(0, 0, 64, 0); h.addColorStop(0, "rgba(0,0,0,1)"); h.addColorStop(0.5, "rgba(0,0,0,0)"); h.addColorStop(1, "rgba(0,0,0,1)");
  g.globalCompositeOperation = "destination-out"; g.fillStyle = h; g.fillRect(0, 0, 64, 256);
});
const patchTex = () => ctex("patch", 256, 256, (g) => {
  const gr = g.createRadialGradient(128, 128, 20, 128, 128, 128); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
});
const tree = (b: Batch, x: number, z: number, h: number, s: number) => {
  b.add(new THREE.CylinderGeometry(0.05 * h, 0.08 * h, 0.5 * h, 8).translate(x, 0.25 * h, z), lam("bark", () => ({ color: "#6b4a32" })));
  const leaf = lam("leaf" + (s % 3), () => ({ color: ["#4f8a3a", "#5f9a3e", "#3f7a3a"][s % 3] }));
  for (let k = 0; k < 3; k++) { const a = s * 2.1 + k * 2.2; b.add(new THREE.IcosahedronGeometry(0.28 * h * (1 - 0.12 * k), 1).translate(x + 0.17 * h * Math.cos(a), (0.6 + 0.12 * k) * h, z + 0.17 * h * Math.sin(a)), leaf); }
};

// ---------------- cast ----------------
const KID: Outfit = { jacket: "#5b7fc4", pants: "#3f5a96", boots: "#e8e2d4", hat: "hair", hair: "#3a2a20", skin: SKINS[1], build: "kid" };
const KID_DAY: Outfit = { ...KID, jacket: "#e07b2e", pants: "#3b3f52", boots: "#f4f1ea" };
const MUM: Outfit = { jacket: "#b05a7a", pants: "#b05a7a", boots: "#e8e2d4", dress: "#b05a7a", hat: "hair", hair: "#5a3a2a", skin: SKINS[1] };
const MUM_DAY: Outfit = { ...MUM, jacket: "#2b7a8a", dress: "#2b7a8a" };
const HALE: Outfit = { jacket: "#7a6a4a", pants: "#4a4f58", boots: "#3a2a20", hat: "hair", hair: "#e8e4dc", moustache: "#e8e4dc", skin: SKINS[0], build: "stout" };
const MAN: Outfit = { jacket: "#4a5a3a", pants: "#3a3530", boots: "#2a2230", hat: "hair", hair: "#2a2420", moustache: "#2a2420", skin: SKINS[0] };
const COP: Outfit = { jacket: "#22304f", pants: "#22304f", boots: "#14121a", hat: "cap", cap: "#1a2238", skin: SKINS[3] };
const COP2: Outfit = { ...COP, skin: SKINS[2] };

export class World {
  root = new THREE.Group();
  private pool = new Pool(); private actors: Actor[] = []; private fxs: Fx[] = [];
  private hemi: THREE.HemisphereLight; private sun: THREE.DirectionalLight;
  private sky: THREE.Mesh; private skyMat: THREE.ShaderMaterial; private fog = new THREE.Fog("#1c2650", 30, 240);
  private moon: THREE.Sprite; private sunCache = new Map<number, THREE.Vector3>();
  private clouds: THREE.Mesh[] = []; private cloudMaps: Record<string, THREE.Texture[]>;
  private halePane: THREE.Mesh; private haleGlow: THREE.Sprite; private beam: THREE.Mesh; private torch: THREE.Mesh; private patch: THREE.Mesh;
  private lampBulb: THREE.Mesh; private fridgeLight: THREE.Mesh; private fridgeDoor = new THREE.Group();
  private copBeams: THREE.Mesh[] = []; private siren: THREE.Mesh[] = []; private car = new THREE.Group();
  private attic = new THREE.Group(); private hatchLid: THREE.Mesh; private streetBulb: THREE.Mesh;
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
    // ---- street, gardens, neighbours ----
    const b = new Batch();
    b.add(new THREE.PlaneGeometry(900, 900).rotateX(-Math.PI / 2).translate(0, -0.01, 0), lam("grassG", () => ({ map: rep(grassHD(), 300, 300) })));
    b.add(boxGeo(V(-400, -0.01, 12), V(400, 0.02, 20), 0, false), lam("asphalt", () => ({ color: "#3a3d47" })));
    b.add(boxGeo(V(-400, 0, 10), V(400, 0.12, 12), 0, false), lam("pavement", () => ({ color: "#b8b2a6" })));
    for (let x = -60; x < 60; x += 6) b.add(boxGeo(V(x, 0.021, 15.9), V(x + 3, 0.03, 16.1)), lam("lane", () => ({ color: "#f2ead6" })));
    b.add(boxGeo(V(-0.6, 0.01, 5.8), V(0.6, 0.04, 10)), lam("path", () => ({ color: "#c9bfae" })));
    b.add(boxGeo(V(14.4, 0.01, 5.8), V(15.6, 0.04, 10)), lam("path", () => ({ color: "#c9bfae" })));
    // picket fence between the gardens (x 7.5) and along the front
    const fM = lam("fence", () => ({ color: "#f4f1ea" }));
    for (let z = -9; z <= 9.5; z += 0.45) b.add(boxGeo(V(7.43, 0, z), V(7.57, 1.05, z + 0.12)), fM);
    b.add(boxGeo(V(7.45, 0.35, -9), V(7.55, 0.45, 9.6)), fM); b.add(boxGeo(V(7.45, 0.8, -9), V(7.55, 0.9, 9.6)), fM);
    for (const [x, z, h, s] of [[-7, 2, 7, 1], [-8, -6, 9, 2], [22, -6, 8, 0], [23, 3, 6.5, 1], [6.2, -8, 5.5, 2], [12.5, 7.5, 3.2, 0], [2.5, 8, 2.8, 1]] as const) tree(b, x, z, h, s);
    for (const [x, z] of [[11.8, 5.4], [13.6, 0.5], [4.9, -7.5]] as const) b.add(new THREE.IcosahedronGeometry(0.7, 1).scale(1, 0.75, 1).translate(x, 0.5, z), lam("bush", () => ({ color: "#4f8a3a" })));
    house(b, -14, 2, 0, 9, 8, 7, 2, 0); house(b, 30, 2, 0, 9, 8, 7.5, 4, 0); house(b, -4, 30, Math.PI, 10, 8, 7, 5, 0); house(b, 12, 30, Math.PI, 9, 8, 8, 1, 0); house(b, 28, 30, Math.PI, 9, 8, 7, 6, 0);
    // streetlamp
    b.add(beamBetween(V(7.5, 0, 11.2), V(7.5, 5.2, 11.2), 0.14), lam("lampPost", () => ({ color: "#2a2230" })));
    b.add(beamBetween(V(7.5, 5.2, 11.2), V(7.5, 5.2, 12.4), 0.1), lam("lampPost", () => ({ color: "#2a2230" })));
    // ---- the two houses ----
    const A = new House(b, 0, 1), Bh = new House(b, 15, -1);
    buildShell(A, "A", "#9fb6d0", "#f4f1ea", "#8a4a3a", "#8fb0d8");
    buildShell(Bh, "B", "#d9c9a0", "#f4f1ea", "#5a4a5a", "#d8c8a8");
    // attic floor of A with the hatch hole over the bed (the shell placeholder slab spans the hole, so rebuild properly)
    const SL = lam("slab", () => ({ color: "#d8d0c4" }));
    const [hx, , hz] = HATCH;
    A.box(SL, -4.5, 4.5, CEIL, ATTIC, -5, hz - 0.45); A.box(SL, -4.5, 4.5, CEIL, ATTIC, hz + 0.45, 5);
    A.box(SL, -4.5, hx - 0.45, CEIL, ATTIC, hz - 0.45, hz + 0.45); A.box(SL, hx + 0.45, 4.5, CEIL, ATTIC, hz - 0.45, hz + 0.45);
    Bh.box(SL, -4.5, 4.5, CEIL, ATTIC, -5, 5);
    // ---- bedroom (A, x 0..4.25, z -4.75..0) ----
    const bedM = lam("bedFrame", () => ({ color: "#a07850" })), sheet = lam("sheet", () => ({ color: "#f2c230" })), pil = lam("pillow", () => ({ color: "#f4f1ea" }));
    b.add(boxGeo(V(0.3, FL1, -4.6), V(2.4, FL1 + 0.35, -3.2), 0, true), bedM);
    b.add(boxGeo(V(0.3, FL1 + 0.35, -4.6), V(2.4, FL1 + 0.55, -3.2), 0, true), sheet);
    b.add(boxGeo(V(0.3, FL1, -4.65), V(0.42, FL1 + 1.0, -3.15), 0, true), bedM);
    b.add(boxGeo(V(0.45, FL1 + 0.55, -4.45), V(0.85, FL1 + 0.7, -3.35), 0, true), pil);
    b.add(boxGeo(V(0.3, FL1, -3.05), V(0.85, FL1 + 0.6, -2.55), 0, true), bedM);
    b.add(boxGeo(V(2.3, FL1, -0.75), V(4.0, FL1 + 0.76, -0.12), 0, true), lam("desk", () => ({ color: "#c9a36a" })));
    b.add(boxGeo(V(2.55, FL1 + 0.76, -0.8), V(3.75, FL1 + 0.79, -0.25), 0, true), lam("notebook", () => ({ color: "#f6f1e2" })));
    b.add(boxGeo(V(0.5, FL1, -2.0), V(3.6, FL1 + 0.01, -0.9), 0, true), lam("rug", () => ({ color: "#c0353a" })));
    b.add(boxGeo(V(0.12, FL1, -4.7), V(0.12, FL1, -4.7)), bedM);
    for (const [k, z, y] of [[0, -4.0, FL1 + 1.6], [1, -2.2, FL1 + 1.7]] as const) {
      const pm = new THREE.Mesh(new THREE.PlaneGeometry(0.7, 1.0).rotateY(Math.PI / 2).translate(0.07, y, z), twoTone(new THREE.MeshLambertMaterial({ map: posterTex(k) }))); R.add(pm);
    }
    const pm2 = new THREE.Mesh(new THREE.PlaneGeometry(0.8, 1.1).translate(1.6, FL1 + 1.7, -4.74), twoTone(new THREE.MeshLambertMaterial({ map: posterTex(2) }))); R.add(pm2);
    const clock = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.2, 0.38), [0, 1, 2, 3, 4, 5].map((i) => i === 0 ? new THREE.MeshBasicMaterial({ map: clockTex() }) : new THREE.MeshLambertMaterial({ color: "#2a2230" })));
    clock.position.set(0.62, FL1 + 0.7, -2.8); R.add(clock);
    // ---- kitchen (A ground floor) ----
    const cab = lam("cabinet", () => ({ color: "#f4f1ea" })), top = lam("counter", () => ({ color: "#5a5f6a" }));
    b.add(boxGeo(V(0.2, 0.2, -4.75), V(4.25, 1.1, -4.1), 0, true), cab); b.add(boxGeo(V(0.2, 1.1, -4.8), V(4.25, 1.16, -4.05), 0, true), top);
    b.add(boxGeo(V(2.9, 0.2, -0.85), V(3.8, 2.1, -0.12), 0, true), lam("fridge", () => ({ color: "#e8eef4" })));
    b.add(boxGeo(V(0.5, 0.2, -1.6), V(1.5, 0.95, -0.6), 0, true), lam("table", () => ({ color: "#c9a36a" })));
    this.fridgeLight = new THREE.Mesh(new THREE.PlaneGeometry(0.8, 1.7).translate(3.35, 1.15, -0.87), new THREE.MeshBasicMaterial({ color: new THREE.Color(3.2, 3.0, 2.4), side: THREE.DoubleSide }));
    this.fridgeLight.layers.set(NOINK); R.add(this.fridgeLight);
    const door = new THREE.Mesh(new THREE.BoxGeometry(0.9, 1.9, 0.06).translate(-0.45, 0, 0), twoTone(new THREE.MeshLambertMaterial({ color: "#e8eef4" })));
    this.fridgeDoor.add(door); this.fridgeDoor.position.set(3.8, 1.15, -0.88); R.add(this.fridgeDoor);
    // ---- attic: rafters, mattress, wrappers, backpack ----
    const at = new Batch(), wood = lam("rafter", () => ({ color: "#8a6a4a" }));
    for (let x = -4.0; x <= 4.0; x += 1.0) for (const sz of [-1, 1]) at.add(beamBetween(V(x, ATTIC, sz * 5.1), V(x, 9.9, 0), 0.12), wood);
    at.add(boxGeo(V(-0.6, ATTIC, -3.6), V(1.2, ATTIC + 0.22, -1.6), 0, true), lam("mattress", () => ({ color: "#c9c2a8" })));
    at.add(boxGeo(V(-0.4, ATTIC + 0.22, -3.4), V(0.8, ATTIC + 0.28, -2.2), 0, true), lam("blanket", () => ({ color: "#6a4a8a" })));
    for (let i = 0; i < 22; i++) {
      const x = -1.6 + 3.6 * hh(i, 3), z = -4.2 + 3.6 * hh(i, 4), c = ["#c0353a", "#f2c230", "#3f6fb5", "#e07b2e", "#f4f1ea"][i % 5];
      if (x > -0.6 && x < 1.2 && z > -3.6 && z < -1.6) continue;
      at.add(boxGeo(V(x, ATTIC, z), V(x + 0.18 + 0.1 * hh(i, 5), ATTIC + 0.05 + 0.12 * hh(i, 6), z + 0.12 + 0.1 * hh(i, 7)), 0, true), lam("wrap" + (i % 5), () => ({ color: c })));
    }
    at.add(boxGeo(V(-1.6, ATTIC, -1.4), V(-1.0, ATTIC + 0.55, -1.0), 0, true), lam("backpack", () => ({ color: "#2b7a4b" })));
    at.build(this.attic); R.add(this.attic);
    { const hb = new Batch(), fm = lam("hatchFrame", () => ({ color: "#6b4a32" }));
      for (const [x0, x1, z0, z1] of [[hx - 0.55, hx + 0.55, hz - 0.55, hz - 0.45], [hx - 0.55, hx + 0.55, hz + 0.45, hz + 0.55], [hx - 0.55, hx - 0.45, hz - 0.45, hz + 0.45], [hx + 0.45, hx + 0.55, hz - 0.45, hz + 0.45]]) hb.add(boxGeo(V(x0, CEIL - 0.05, z0), V(x1, CEIL + 0.01, z1), 0, true), fm);
      hb.build(R); }
    this.hatchLid = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.08, 0.9), twoTone(new THREE.MeshLambertMaterial({ color: "#cfc6b8" })));
    this.hatchLid.position.set(hx, CEIL + 0.04, hz); R.add(this.hatchLid);
    // ---- Hale's room (B): table, lamp at the window ----
    b.add(boxGeo(V(10.85, FL1, WIN_Z - 0.5), V(11.55, FL1 + 0.8, WIN_Z + 0.5), 0, true), lam("haleTable", () => ({ color: "#7a5a3a" })));
    b.add(new THREE.CylinderGeometry(0.06, 0.12, 0.5, 10).translate(11.2, FL1 + 1.05, WIN_Z + 0.25), lam("lampBase", () => ({ color: "#2a2230" })));
    b.add(boxGeo(V(14.6, FL1, -4.7), V(14.9, FL1 + 2.0, -0.2), 0, true), lam("haleShelf", () => ({ color: "#7a5a3a" })));
    b.build(R);
    this.lampBulb = new THREE.Mesh(new THREE.SphereGeometry(0.2, 14, 10), new THREE.MeshBasicMaterial({ color: new THREE.Color(1, 1, 1) }));
    this.lampBulb.position.set(11.2, FL1 + 1.42, WIN_Z + 0.25); this.lampBulb.layers.set(NOINK); R.add(this.lampBulb);
    // Hale's window pane, glow and the beam across the gap
    this.halePane = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.5).rotateY(Math.PI / 2).translate(B_X + 0.06, WIN_Y, WIN_Z), new THREE.MeshBasicMaterial({ color: new THREE.Color(4.5, 3.6, 2.0), side: THREE.DoubleSide }));
    this.halePane.layers.set(NOINK); R.add(this.halePane);
    this.haleGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map: haloTex(), color: new THREE.Color(1.6, 1.25, 0.7), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }));
    this.haleGlow.position.set(B_X - 0.3, WIN_Y, WIN_Z); this.haleGlow.scale.setScalar(5); this.haleGlow.layers.set(NOINK); R.add(this.haleGlow);
    const bt = beamTex();
    const cone = (r0: number, r1: number) => {
      const g = new THREE.CylinderGeometry(r0, r1, 1, 24, 1, true).translate(0, -0.5, 0).rotateX(-Math.PI / 2); // along -z? -> along +z after rotate
      const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ map: bt, color: new THREE.Color(1.2, 1.0, 0.65), transparent: true, opacity: 0.5, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, fog: false }));
      m.layers.set(NOINK); m.frustumCulled = false; R.add(m); return m;
    };
    this.beam = cone(0.6, 1.6); this.torch = cone(0.06, 1.0);
    for (let i = 0; i < 2; i++) this.copBeams.push(cone(0.06, 1.1));
    this.patch = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 2.2).rotateY(Math.PI / 2).translate(0.09, FL1 + 1.55, WIN_Z - 0.4), new THREE.MeshBasicMaterial({ map: patchTex(), color: new THREE.Color(0.9, 0.7, 0.4), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }));
    this.patch.layers.set(NOINK); R.add(this.patch);
    // streetlamp bulb
    this.streetBulb = new THREE.Mesh(new THREE.SphereGeometry(0.22, 12, 10), new THREE.MeshBasicMaterial({ color: new THREE.Color(3.5, 2.8, 1.6) }));
    this.streetBulb.position.set(7.5, 5.05, 12.4); this.streetBulb.layers.set(NOINK); R.add(this.streetBulb);
    // police car
    {
      const cb = new Batch();
      cb.add(boxGeo(V(-2.3, 0.35, -0.9), V(2.3, 1.15, 0.9), 0, true), lam("carBody", () => ({ color: "#f4f1ea" })));
      cb.add(boxGeo(V(-1.2, 1.15, -0.82), V(1.0, 1.75, 0.82), 0, true), lam("carTop", () => ({ color: "#22304f" })));
      cb.add(boxGeo(V(-2.32, 0.55, -0.92), V(2.32, 0.8, 0.92), 0, true), lam("carStripe", () => ({ color: "#3f6fb5" })));
      for (const x of [-1.5, 1.5]) for (const z of [-0.9, 0.9]) cb.add(new THREE.CylinderGeometry(0.38, 0.38, 0.25, 14).rotateX(Math.PI / 2).translate(x, 0.38, z), lam("tyre", () => ({ color: "#2a2a30" })));
      cb.build(this.car);
      for (const [i, z] of [[0, -0.35], [1, 0.35]] as const) {
        const s = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.18, 0.6), new THREE.MeshBasicMaterial({ color: i ? new THREE.Color(0.4, 0.6, 5) : new THREE.Color(5, 0.4, 0.4) }));
        s.position.set(-0.1, 1.84, z); s.layers.set(NOINK); this.car.add(s); this.siren.push(s);
      }
      this.car.position.set(4.6, 0, 14.6); this.car.rotation.y = 0.05; R.add(this.car);
    }
  }

  private shotSun(id: number, s: ShotDef, L: LightPreset) {
    let v = this.sunCache.get(id); if (v) return v;
    let fx = 0, fz = 0;
    for (let f = s.a; f < s.b; f += 3) { const c = camAt(id, f), x = c.look[0] - c.pos[0], zz = c.look[2] - c.pos[2], n = Math.hypot(x, zz) || 1; fx += x / n; fz += zz / n; }
    const n = Math.hypot(fx, fz) || 1; fx /= n; fz /= n;
    const az = THREE.MathUtils.degToRad(s.sunAz ?? L.az), el = THREE.MathUtils.degToRad(s.sunEl ?? L.el);
    const hx = fx * Math.cos(az) - fz * Math.sin(az), hz = fz * Math.cos(az) + fx * Math.sin(az);
    v = new THREE.Vector3(hx * Math.cos(el), Math.sin(el), hz * Math.cos(el)).normalize();
    // inside the bedroom the moon comes through the window (from +x)
    if (s.light === "room") v = new THREE.Vector3(0.82, 0.45, 0.2).normalize();
    this.sunCache.set(id, v); return v;
  }
  private actor(i: number) { while (this.actors.length <= i) this.actors.push(new Actor(this.root)); return this.actors[i]; }
  private fx(i: number) { while (this.fxs.length <= i) this.fxs.push(new Fx(this.root)); return this.fxs[i]; }
  private aim(m: THREE.Mesh, a: THREE.Vector3, b: THREE.Vector3) {
    m.position.copy(a); m.lookAt(b); m.scale.set(1, 1, a.distanceTo(b));
  }

  update(id: number, f: number, cam: THREE.PerspectiveCamera, scene: THREE.Scene) {
    const t = f / FPS, s = SHOTS[id - 1], Lp = LIGHTS[s.light], K = LOOK[s.light];
    const c = camAt(id, f);
    cam.position.set(...c.pos); cam.up.set(0, 1, 0); cam.lookAt(...c.look); cam.rotateZ(c.roll);
    cam.fov = c.fov; cam.near = 0.05; cam.far = 1600; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    const focus = V(...c.look), dist = cam.position.distanceTo(focus);
    cam.layers.enable(NOINK);
    const night = s.light === "night" || s.light === "room";
    const fl = night ? haleFlash(t) : 0, tf = torchFlash(t);
    // ---- light rig ----
    const sunDir = this.shotSun(id, s, Lp);
    this.hemi.color.set(Lp.sky); this.hemi.groundColor.set(Lp.ground); this.hemi.intensity = Lp.hemiI;
    this.sun.color.set(Lp.sunCol); this.sun.intensity = Lp.sunI;
    const Rr = THREE.MathUtils.clamp(dist * 1.3 + 8, 12, 60);
    this.sun.position.copy(focus).addScaledVector(sunDir, 120); this.sun.target.position.copy(focus);
    const sc = this.sun.shadow.camera; sc.left = -Rr; sc.right = Rr; sc.top = Rr; sc.bottom = -Rr; sc.near = 5; sc.far = 300; sc.updateProjectionMatrix();
    this.sun.shadow.bias = Lp.bias; this.sun.shadow.normalBias = Lp.normalBias * (Rr / 12);
    // the flash warms the whole room (and the kid) for a moment
    const room = s.light === "room", warm = room ? fl * 0.9 + tf * 0.25 : id === 8 ? fl * 0.7 : 0;
    const lit = Lp.lit.map((x, i) => x + warm * [1.0, 0.7, 0.25][i]) as [number, number, number];
    const shd = Lp.shade.map((x, i) => x + warm * [0.55, 0.38, 0.12][i]) as [number, number, number];
    const dark = id === 11 ? 0.72 : 1; // the creak: darker
    TONE.uLitCol.value.set(lit[0] * dark, lit[1] * dark, lit[2] * dark); TONE.uShadeCol.value.set(shd[0] * dark, shd[1] * dark, shd[2] * dark); TONE.uShadeLift.value.set(...Lp.lift);
    TONE.uLambert.value = Lp.lambert; TONE.uSideK.value = Lp.sideK; TONE.uTerm.value = Lp.term; TONE.uBounce.value.set(...K.bounce); TONE.uSat.value = K.sat;
    const ct = Lp.charTint.map((x, i) => (x + warm * [0.35, 0.18, -0.05][i]) * (id === 11 ? 0.85 : 1)) as [number, number, number];
    CHAR.uCharTint.value.set(...ct); CHAR.uCharShade.value = Lp.charShade; CHAR.uGrad.value = Lp.charGrad; CHAR.uBodyGrad.value = Lp.bodyGrad; CHAR.uSideTint.value.set(...Lp.sideTint);
    // ---- sky ----
    const su = this.skyMat.uniforms;
    K.sky.c.forEach((h, i) => untone(h, su["c" + i].value));
    const e = K.sky.e.map((deg) => THREE.MathUtils.degToRad(deg)); su.e.value.set(e[1], e[2], e[3], e[4]);
    su.uStars.value = night ? 1 : 0;
    this.sky.position.copy(cam.position);
    const k = typeof s.fog === "number" ? s.fog : 1;
    untone(Lp.fog, this.fog.color); this.fog.near = Lp.fogNear * k; this.fog.far = Lp.fogFar * k; scene.fog = this.fog; scene.background = null;
    this.moon.visible = night;
    if (night) { const md = V(-0.35, 0.55, -0.75).normalize(); this.moon.position.copy(cam.position).addScaledVector(md, 700); this.moon.scale.setScalar(36); }
    const cm = (s.light === "golden" ? this.cloudMaps.golden : s.light === "day" ? this.cloudMaps.day : this.cloudMaps.night);
    this.clouds.forEach((m, i) => { m.lookAt(cam.position.x, m.position.y, cam.position.z); (m.material as THREE.MeshBasicMaterial).map = cm[i % 4]; });
    // ---- practical lights ----
    this.halePane.visible = fl > 0; this.haleGlow.visible = fl > 0;
    const golden = s.light === "golden", lampOn = golden && haleFlash(t) > 0;
    (this.lampBulb.material as THREE.MeshBasicMaterial).color.setRGB(...(fl > 0 || lampOn ? [6, 4.8, 2.6] : [0.5, 0.45, 0.4]) as [number, number, number]);
    if (lampOn) { this.haleGlow.visible = true; this.haleGlow.position.set(11.0, FL1 + 1.42, WIN_Z + 0.25); this.haleGlow.scale.setScalar(3); }
    else { this.haleGlow.position.set(B_X - 0.3, WIN_Y, WIN_Z); this.haleGlow.scale.setScalar(5); }
    this.beam.visible = fl > 0 && id !== 1 && id !== 3 && id !== 4;
    if (this.beam.visible) { this.aim(this.beam, V(B_X - 0.05, WIN_Y, WIN_Z), V(A_X + 0.2, WIN_Y - 0.2, WIN_Z)); (this.beam.material as THREE.MeshBasicMaterial).opacity = 0.55; }
    this.patch.visible = room && fl > 0; (this.patch.material as THREE.MeshBasicMaterial).opacity = 0.9;
    this.torch.visible = tf > 0;
    if (tf > 0) { this.aim(this.torch, V(3.85, FL1 + 1.35, WIN_Z + 0.35), V(B_X, WIN_Y, WIN_Z)); (this.torch.material as THREE.MeshBasicMaterial).opacity = 0.8; }
    this.streetBulb.visible = night;
    const sir = Math.floor(t * 4) % 2;
    this.siren[0].visible = sir === 0; this.siren[1].visible = sir === 1; this.car.visible = id === 12 || id === 13;
    const fo = id === 14; this.fridgeLight.visible = fo; this.fridgeDoor.rotation.y = fo ? -1.9 : 0;
    this.copBeams.forEach((m) => (m.visible = false));
    if (id === 13) {
      const sw = Math.sin(t * 2.1) * 0.15;
      this.aim(this.copBeams[0], V(1.75, ATTIC + 1.4, -1.25), V(0.4 + sw, ATTIC + 0.7, -2.75)); this.copBeams[0].visible = true;
      this.aim(this.copBeams[1], V(1.4, ATTIC + 0.4, -3.9), V(0.3 - sw, ATTIC + 0.9, -2.6)); this.copBeams[1].visible = t > 48.6;
      this.copBeams.forEach((m) => ((m.material as THREE.MeshBasicMaterial).opacity = 0.7));
    }
    this.hatchLid.position.y = CEIL + 0.04 + (id === 11 ? 0.03 * Math.max(0, Math.sin((t - 43.85) * 30)) * (t > 43.85 && t < 44.6 ? 1 : 0) : 0);
    this.hatchLid.visible = id !== 13;

    // ---- cast + effects ----
    const right = V(0, 0, 0).setFromMatrixColumn(cam.matrixWorld, 0);
    const ci: CamInfo = { pos: cam.position, right };
    castBegin(s.light, ci);
    const st: Stage = { places: [], fx: [] };
    this.stage(id, t, ci, st, fl);
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

  private put(out: Stage, cam: CamInfo, o: Outfit, key: string, i: number, x: number, y: number, z: number, t: number, opts: Partial<FrontOpts>, sc = 1, shadow = true) {
    out.places.push(person(cam, { i, o, okey: key }, x, y, z, { side: false, mirror: false }, { mode: "stand", blink: lidAt(t, i), ...opts }, {}, sc));
    if (shadow && opts.mode !== "sit") blob(out, x, y, z, sc);
  }

  private stage(id: number, t: number, cam: CamInfo, out: Stage, fl: number) {
    const KB: [number, number, number] = [BED[0] + 0.15, BED[1], BED[2] + 0.15];
    if (id === 1) this.put(out, cam, KID, "kid", 1, ...KB, t, { mode: "sit", expr: t < 2.2 ? "nervous" : "shock", look: 1, facing: 1 }, 0.9, false);
    if (id === 2 || id === 10) this.put(out, cam, KID, "kid", 1, 3.75, FL1 + 0.4, WIN_Z + 0.1, t, { expr: "shock", look: 1 }, 0.9, false);
    if (id === 2) {
      const sy = runSoFar(t), qk = sy;
      if (sy.length) out.fx.push({ key: `syms_${qk}`, cw: 900, ch: 200, draw: (p) => drawSyms(p, qk), x: 7.5, y: 6.9, z: WIN_Z, w: 3.6, h: 0.8 });
    }
    if (id === 3) {
      this.put(out, cam, KID, "kid", 1, ...KB, t, { mode: "sit", expr: "nervous", look: -1 }, 0.9, false);
      this.put(out, cam, MUM, "mum", 2, 0.2, FL1, -0.75, t, { expr: t < 13.5 ? "dazed" : "stern", headTilt: 0.08 });
    }
    if (id === 4 || id === 5) {
      if (id === 4) this.put(out, cam, KID, "kid", 1, 3.1, FL1, -1.2, t, { expr: t < 19.1 ? "stern" : "shock", look: 1 }, 0.9);
      const n = id === 5 ? 8 : Math.min(8, Math.floor((t - 15.4) / 0.42)), word = id === 5 ? (t > 22.85 ? 3 : 0) : 0, chart = id === 4 ? clamp01((t - 19.1) / 0.3) : 1;
      const qc = q(chart, 6), key = `note_${n}_${word}_${qc}`;
      out.fx.push({ key, cw: 900, ch: 600, draw: (p) => drawNote(p, n, word, qc), x: 3.15, y: FL1 + 0.8, z: -0.5, w: 0.6, h: 0.4, flat: true, rot: Math.PI });
      if (false) { const u = q((t - 22.85) / 0.55, 20); out.fx.push({ key: `burst${u}`, cw: 500, ch: 500, draw: (p) => fxBurst(p, u, "#ff6a5a", 12), x: 3.15, y: FL1 + 0.85, z: -0.62, w: 0.9, h: 0.9 }); }
    }
    if (id === 6) this.put(out, cam, HALE, "hale", 3, 9.4, 0, 1.0, t, { expr: "stern", look: -1, facing: -1 });
    if (id === 7) this.put(out, cam, HALE, "hale", 3, 9.2, 0, 2.7, t, { expr: "stern", look: -1, facing: -1, wave: q(clamp01((t - 29.3) / 0.8), 10) });
    if (id === 8) this.put(out, cam, KID, "kid", 1, 3.7, FL1 + 0.4, WIN_Z, t, { expr: t < 34.3 ? "nervous" : "shock", look: 0 }, 0.9);
    if (id === 9) this.put(out, cam, KID, "kid", 1, 3.55, FL1, WIN_Z + 0.55, t, { expr: t < 36.5 ? "nervous" : "stern", look: 1 }, 0.9);
    if (id === 11) {
      this.put(out, cam, KID, "kid", 1, ...KB, t, { mode: "sit", expr: t < 43.8 ? "nervous" : "shock", headTilt: -0.1 }, 0.9, false);
      if (t > 43.85 && t < 45.5) for (let j = 0; j < 3; j++) { const u = clamp01((t - 43.85 - j * 0.25) / 1.2), qk = q(u, 24); if (u > 0 && u < 1) out.fx.push({ key: `puff${qk}`, cw: 300, ch: 300, draw: (p) => fxPuff(p, qk), x: HATCH[0] - 0.3 + 0.3 * j, y: CEIL - 0.2 - 0.9 * u, z: HATCH[2] + 0.2, w: 0.8, h: 0.8, soft: true }); }
    }
    if (id === 12) {
      const w = clamp01((t - 45.85) / 2.5);
      this.put(out, cam, COP, "cop1", 4, 1.6 - 1.0 * w, 0, 9.0 - 2.4 * w, t, { mode: "walk", phase: t * 1.6, amt: 1, yaw: 0.2, expr: "stern" });
      this.put(out, cam, COP2, "cop2", 5, 2.8 - 1.2 * w, 0, 9.8 - 2.4 * w, t, { mode: "walk", phase: t * 1.6 + 0.5, amt: 1, yaw: 0.2, expr: "stern" });
      this.put(out, cam, MUM, "mum", 2, -0.4, 0.2, 5.7, t, { expr: "nervous" });
      this.put(out, cam, KID, "kid", 1, 0.5, 0.2, 5.9, t, { expr: "shock" }, 0.9);
    }
    if (id === 13) {
      this.put(out, cam, MAN, "man", 6, 0.35, ATTIC + 0.22, -2.7, t, { mode: "sit", expr: t < 48.9 ? "nervous" : "shock", look: 1 }, 1, false);
      this.put(out, cam, COP, "cop1", 4, 1.9, ATTIC, -1.2, t, { expr: "stern", look: -1, facing: -1 });
    }
    if (id === 14) this.put(out, cam, MAN, "man", 6, 3.0, 0.2, -1.6, t, { expr: t < 54.4 ? "lick" : "grin", look: 1 });
    if (id === 15) {
      this.put(out, cam, MUM_DAY, "mumD", 2, 2.9, 0.2, -1.1, t, { expr: "stern", look: -1, facing: -1, wave: 0.7 });
      this.put(out, cam, KID_DAY, "kidD", 1, 1.9, 0.2, -1.6, t, { expr: "nervous", look: 1 }, 0.9);
    }
    if (id === 16) {
      this.put(out, cam, HALE, "hale", 3, 11.15, FL1, WIN_Z - 0.35, t, { expr: "smile", look: -1, facing: -1, wave: q(0.5 + 0.5 * Math.sin(t * 5), 16) });
      this.put(out, cam, KID_DAY, "kidD", 1, 8.0, 0, 0.4, t, { expr: "grin", look: 1, wave: q(0.5 + 0.5 * Math.sin(t * 6 + 1), 16) }, 0.9);
      this.put(out, cam, MUM_DAY, "mumD", 2, 7.1, 0, 1.1, t, { expr: "smile", look: 1 });
    }
    void fl; void smooth; void ramp; void HALE_WIN; void KID_WIN; void DESK; void untone; void Pen; void INK;
  }
}
