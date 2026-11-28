// Lake Peigneur as one three.js scene: the lake (a polar water mesh with the whirlpool funnel over a polar bed that
// collapses into a crater), the drilling rig, eleven barges, a tug, the fisherman's rowboat, Jefferson Island's wooded
// bank, the shore (trees, houses, canal, mine headframe), the waterfall, the salt mine set far below, and the
// cross-section diagram. update(id, f, camera) poses everything for shot `id` at frame f from story.ts lakeAt().
import * as THREE from "three";
import { Batch, V, lam, Kit, house, boxGeo } from "./build";
import { ctex, rep, grassHD, cloudHD, waterNear, waterFar } from "./paint";
import { Pen, Outfit, Expr, FrontOpts, SKINS, INK, fxSplash, fxCreak, fxBurst, fxPuff } from "./toon";
import { LIGHTS, LOOK, LightPreset } from "./lights";
import { TONE, CHAR, LFB, twoTone, untone } from "./shade";
import { NOINK } from "./ink";
import { Pool, Actor, Fx, Stage, CamInfo, castBegin, person, blob, lidAt, hh, q } from "./cast";
import { WATER_DECL, WATER_COL, discTex, haloTex, beamBetween } from "./bworld";
import {
  FPS, SHOTS, camAt, ShotDef, V3, smooth, clamp01, ramp, lakeAt, Lake, surfY, bedY, swirlAngle,
  LAKE_R, GROUND_Y, RIG, DECK, BARGES, BARGE_DECK, TUG, FISH, ISLAND, ISLAND_R, GAUGE, MINE_Y, CAGE, CUT_X, HEAD, CANAL_W,
} from "./story";

export const loadKit = () => Promise.resolve({} as Kit);

const up = (x0: number, x1: number, z0: number, z1: number, y: number, u: number, v: number) => {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute([x0, y, z1, x1, y, z1, x1, y, z0, x0, y, z1, x1, y, z0, x0, y, z0], 3));
  g.setAttribute("normal", new THREE.Float32BufferAttribute([0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute([0, 0, u, 0, u, v, 0, 0, u, v, 0, v], 2));
  return g;
};
const lin = (hex: string) => new THREE.Color(hex); // linear rgb of an sRGB hex
const mixC = (a: THREE.Color, b: THREE.Color, k: number, out: THREE.Color) => out.copy(a).lerp(b, clamp01(k));

// ---------------- a polar grid (whirlpool water, lake bed) ----------------
class Polar {
  NA = 144; NR: number; r: Float32Array; geo = new THREE.BufferGeometry(); pos: Float32Array; col: Float32Array; uv: Float32Array;
  constructor(public R: number, NR: number, k = 1.7) {
    this.NR = NR; this.r = new Float32Array(NR + 1);
    for (let i = 0; i <= NR; i++) this.r[i] = R * (i / NR) ** k;
    const n = (NR + 1) * (this.NA + 1);
    this.pos = new Float32Array(n * 3); this.col = new Float32Array(n * 3).fill(1); this.uv = new Float32Array(n * 2);
    const idx: number[] = [];
    for (let i = 0; i <= NR; i++) for (let j = 0; j <= this.NA; j++) {
      const k2 = i * (this.NA + 1) + j, th = (j / this.NA) * Math.PI * 2;
      this.pos.set([this.r[i] * Math.cos(th), 0, this.r[i] * Math.sin(th)], k2 * 3);
      if (i < NR && j < this.NA) { const a = k2, b = a + 1, c = a + this.NA + 1, d = c + 1; idx.push(a, b, c, b, d, c); }
    }
    this.geo.setAttribute("position", new THREE.BufferAttribute(this.pos, 3));
    this.geo.setAttribute("color", new THREE.BufferAttribute(this.col, 3));
    this.geo.setAttribute("uv", new THREE.BufferAttribute(this.uv, 2));
    this.geo.setIndex(idx); this.geo.computeVertexNormals();
  }
  each(fn: (k: number, r: number, th: number) => void) {
    for (let i = 0; i <= this.NR; i++) for (let j = 0; j <= this.NA; j++) fn(i * (this.NA + 1) + j, this.r[i], (j / this.NA) * Math.PI * 2);
  }
  commit(normals = true) {
    this.geo.attributes.position.needsUpdate = true; this.geo.attributes.color.needsUpdate = true; this.geo.attributes.uv.needsUpdate = true;
    if (normals) this.geo.computeVertexNormals();
    this.geo.computeBoundingSphere();
  }
}

// ---------------- painted textures ----------------
const swirlTex = () => ctex("swirl", 1024, 512, (g, r) => {
  g.fillStyle = "#000"; g.fillRect(0, 0, 1024, 512); g.lineCap = "round";
  for (let i = 0; i < 70; i++) {
    const x = r() * 1024, y = r() * 512, len = 60 + r() * 300, w = 2 + r() * 7, a = 0.35 + r() * 0.65;
    g.strokeStyle = `rgba(255,255,255,${a.toFixed(2)})`; g.lineWidth = w;
    g.beginPath(); g.moveTo(x, y); g.bezierCurveTo(x + len * 0.33, y + 6 * (r() - 0.5), x + len * 0.66, y + 6 * (r() - 0.5), x + len, y + 4 * (r() - 0.5)); g.stroke();
    if (x + len > 1024) { g.beginPath(); g.moveTo(x - 1024, y); g.lineTo(x + len - 1024, y); g.stroke(); }
  }
});
const fallTex = () => ctex("fall", 256, 1024, (g, r) => {
  g.fillStyle = "#7fbfd0"; g.fillRect(0, 0, 256, 1024);
  for (let i = 0; i < 90; i++) {
    const x = r() * 256, y = r() * 1024, len = 80 + r() * 380, w = 2 + r() * 9;
    g.fillStyle = r() < 0.6 ? "rgba(255,255,255,.8)" : "rgba(60,120,150,.45)"; g.fillRect(x, y, w, len); if (y + len > 1024) g.fillRect(x, y - 1024, w, len);
  }
});
const floodTex = () => ctex("flood", 512, 512, (g, r) => {
  g.fillStyle = "#6f9a98"; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 80; i++) {
    const x = r() * 512, y = r() * 512, len = 30 + r() * 160;
    g.fillStyle = r() < 0.6 ? "rgba(255,255,255,.7)" : "rgba(40,80,80,.35)"; g.fillRect(x, y, len, 3 + r() * 5); if (x + len > 512) g.fillRect(x - 512, y, len, 4);
  }
});
const kellyTex = () => ctex("kelly", 128, 64, (g) => { g.fillStyle = "#4a4f58"; g.fillRect(0, 0, 128, 64); g.fillStyle = "#c9ccd2"; g.fillRect(0, 0, 32, 64); g.fillRect(64, 0, 32, 64); });
const saltFloor = () => ctex("saltFloor", 1024, 1024, (g, r) => {
  g.fillStyle = "#bdb7ac"; g.fillRect(0, 0, 1024, 1024);
  for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(${r() < 0.5 ? "120,110,100" : "255,255,255"},${(0.05 + 0.08 * r()).toFixed(3)})`; g.fillRect(r() * 1024, r() * 1024, 6 + r() * 40, 4 + r() * 20); }
  g.strokeStyle = "rgba(110,100,90,.18)"; g.lineWidth = 14;
  for (let k = 0; k < 6; k++) { const x = r() * 1024; g.beginPath(); g.moveTo(x, 0); g.bezierCurveTo(x + 80, 340, x - 80, 680, x + 30, 1024); g.stroke(); }
});
const saltWall = () => ctex("saltWall", 1024, 1024, (g, r) => {
  g.fillStyle = "#c2bcb0"; g.fillRect(0, 0, 1024, 1024);
  // continuous-miner cutter marks: rows of shallow arcs
  g.strokeStyle = "rgba(120,110,100,.28)"; g.lineWidth = 5;
  for (let y = 40; y < 1024; y += 70) for (let x = -40; x < 1064; x += 90) { g.beginPath(); g.arc(x + (y % 140 ? 45 : 0), y, 60, 0.2 * Math.PI, 0.8 * Math.PI); g.stroke(); }
  for (let i = 0; i < 500; i++) { g.fillStyle = `rgba(255,255,255,${(0.08 * r()).toFixed(3)})`; g.fillRect(r() * 1024, r() * 1024, 10 + r() * 60, 6 + r() * 30); }
  // soft grey banding of the salt
  for (let k = 0; k < 8; k++) { g.fillStyle = `rgba(90,85,80,${(0.04 + 0.05 * r()).toFixed(3)})`; g.fillRect(0, r() * 1024, 1024, 20 + r() * 60); }
});
const gaugeTex = () => ctex("gauge", 64, 1024, (g) => {
  g.fillStyle = "#f4f1ea"; g.fillRect(0, 0, 64, 1024);
  for (let ft = 0; ft <= 17; ft++) { const y = 1024 - ft * (1024 / 17.06); g.fillStyle = ft % 5 === 0 ? "#c0353a" : INK; g.fillRect(0, y - (ft % 5 === 0 ? 10 : 5), ft % 5 === 0 ? 64 : 40, ft % 5 === 0 ? 20 : 10); }
});
const signTex = () => ctex("gaugeSign", 512, 256, (g) => {
  g.fillStyle = "#f2ead6"; g.fillRect(0, 0, 512, 256); g.strokeStyle = INK; g.lineWidth = 16; g.strokeRect(8, 8, 496, 240);
  g.font = "900 140px Arial Black, sans-serif"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillStyle = INK; g.fillText("10 FT", 256, 134);
});
// cross-section diagram, 160 x 240 m: x -80..80, y -140..100 -> 2048 x 3072 px
const DX = (x: number) => (x + 80) * 12.8, DY = (y: number) => (100 - y) * 12.8;
const cutTex = () => ctex("cutaway", 2048, 3072, (g) => {
  const p = new Pen(g), P = (x: number, y: number): [number, number] => [DX(x), DY(y)];
  g.fillStyle = "#b8d6ee"; g.fillRect(0, 0, 2048, DY(60));
  // soil layers
  const bands: [number, string][] = [[60, "#9a7a52"], [44, "#8a6a46"], [20, "#7c5e40"], [-10, "#6e5238"], [-60, "#614832"], [-140, "#614832"]];
  for (let i = 0; i < bands.length - 1; i++) { g.fillStyle = bands[i][1]; g.fillRect(0, DY(bands[i][0]), 2048, DY(bands[i + 1][0]) - DY(bands[i][0]) + 2); }
  // wavy strata lines
  g.strokeStyle = "rgba(40,25,20,.35)"; g.lineWidth = 6;
  for (const y0 of [44, 20, -10, -60]) { g.beginPath(); for (let x = -80; x <= 80; x += 4) { const [a, b] = P(x, y0 + 1.5 * Math.sin(x * 0.12)); x === -80 ? g.moveTo(a, b) : g.lineTo(a, b); } g.stroke(); }
  // salt dome rising from the deep
  const dome: [number, number][] = [];
  for (let k = 0; k <= 40; k++) { const a = Math.PI * (k / 40), x = -58 * Math.cos(a), y = -140 + 155 * Math.sin(a) ** 0.55; dome.push(P(x, y)); }
  p.poly(dome, "#e8e4dc", 14);
  for (let i = 0; i < 40; i++) { const x = -45 + 90 * hh(i, 1), y = -130 + 130 * hh(i, 2); p.stroke([P(x, y), P(x + 3, y + 2)], 6, "rgba(150,140,130,.6)"); }
  // two mine levels: rooms with pillars
  for (const [y0, y1] of [[-58, -42], [-86, -74]] as const) {
    p.poly([P(-40, y0), P(40, y0), P(40, y1), P(-40, y1)], "#4a4450", 12);
    for (let x = -20; x <= 30; x += 25) p.poly([P(x - 4.5, y0), P(x + 4.5, y0), P(x + 4.5, y1), P(x - 4.5, y1)], "#d8d3ca", 8);
  }
  // shaft and headframe on the right
  p.poly([P(50, 60), P(54, 60), P(54, -86), P(50, -86)], "#3a3540", 10);
  p.poly([P(40, -86), P(54, -86), P(54, -82), P(40, -82)], "#3a3540", 0);
  p.poly([P(40, -58), P(54, -58), P(54, -54), P(40, -54)], "#3a3540", 0);
  p.stroke([P(48, 60), P(51, 78), P(53, 78), P(56, 60)], 9); p.ell(DX(52), DY(78.5), 22, 22, "#c0353a", 8);
  // grass, shore and the lake basin
  g.fillStyle = "#6fa04a"; g.fillRect(0, DY(61.2), 2048, DY(58.8) - DY(61.2));
  p.poly([P(-46, 60.4), P(46, 60.4), P(42, 54), P(-42, 54)], "#7a6a50", 10);
  // the rig on the lake, drill pipe drawn in 3D (world.ts)
  p.poly([P(-40, 60.2), P(-28, 60.2), P(-28, 62.4), P(-40, 62.4)], "#5a6a7a", 8);
  p.stroke([P(-38, 62.4), P(-34, 80), P(-30, 62.4)], 9, "#d2452f"); p.stroke([P(-37, 67), P(-31, 67)], 7, "#d2452f"); p.stroke([P(-36, 72), P(-32, 72)], 7, "#d2452f");
  // labels
  g.font = "900 120px Arial Black, sans-serif"; g.textAlign = "center"; g.textBaseline = "middle"; g.lineWidth = 18; g.strokeStyle = INK;
  g.strokeText("SALT MINE", DX(-4), DY(-34)); g.fillStyle = "#ffffff"; g.fillText("SALT MINE", DX(-4), DY(-34));
  g.strokeText("LAKE", DX(4), DY(50)); g.fillText("LAKE", DX(4), DY(50));
});

// ---------------- props ----------------
const LEAF = ["#4f8a3a", "#5f9a3e", "#3f7a3a", "#6aa04a"];
const tree = (b: Batch, x: number, y: number, z: number, h: number, s: number, m?: THREE.Matrix4) => {
  const M = (g: THREE.BufferGeometry) => (m ? g.applyMatrix4(m) : g);
  b.add(M(new THREE.CylinderGeometry(0.045 * h, 0.07 * h, 0.5 * h, 8).translate(x, y + 0.25 * h, z)), lam("bark", () => ({ color: "#6b4a32" })));
  const leaf = lam("leaf" + (s % 4), () => ({ color: LEAF[s % 4] }));
  for (let k = 0; k < 3; k++) {
    const a = s * 2.1 + k * 2.2, rr = 0.17 * h;
    b.add(M(new THREE.IcosahedronGeometry(0.27 * h * (1 - 0.12 * k), 1).translate(x + rr * Math.cos(a), y + (0.58 + 0.12 * k) * h, z + rr * Math.sin(a))), leaf);
  }
};
const hullM = () => lam("bargeHull", () => ({ color: "#7a4630" })), bdeckM = () => lam("bargeDeck", () => ({ color: "#5a524c" }));
const buildBarge = (k: number) => {
  const g = new THREE.Group(), b = new Batch();
  b.add(boxGeo(V(-14, -1.2, -4), V(14, BARGE_DECK - 0.12, 4), 0, true), hullM());
  b.add(boxGeo(V(-13.6, BARGE_DECK - 0.12, -3.6), V(13.6, BARGE_DECK, 3.6)), bdeckM());
  for (const s of [-1, 1]) b.add(boxGeo(V(-14, BARGE_DECK - 0.12, s * 4 - 0.2), V(14, BARGE_DECK + 0.35, s * 4 + 0.2)), lam("coaming", () => ({ color: "#8a5236" })));
  if (k > 0 && k % 3 === 1) for (let i = 0; i < 6; i++) b.add(new THREE.CylinderGeometry(0.45, 0.45, 18, 12).rotateZ(Math.PI / 2).translate(0, BARGE_DECK + 0.45 + 0.8 * Math.floor(i / 3), -1.6 + (i % 3) * 1.4 + (i >= 3 ? 0.7 : 0)), lam("pipeStack", () => ({ color: "#8f969e" })));
  if (k > 0 && k % 3 === 2) for (let i = 0; i < 3; i++) b.add(boxGeo(V(-10 + i * 7, BARGE_DECK, -2.6), V(-4.5 + i * 7, BARGE_DECK + 2.6, 2.6)), lam("crate" + i, () => ({ color: ["#3f6fb5", "#c94a3a", "#d9a441"][i] })));
  b.build(g); return g;
};
const buildTug = () => {
  const g = new THREE.Group(), b = new Batch();
  b.add(boxGeo(V(-8, -1.4, -3), V(6, 1.4, 3), 0, true), lam("tugHull", () => ({ color: "#2f4a6a" })));
  const bow = new THREE.CylinderGeometry(3, 3, 2.8, 16, 1, false, 0, Math.PI).rotateY(Math.PI).translate(6, 0, 0); b.add(bow, lam("tugHull", () => ({ color: "#2f4a6a" })));
  b.add(boxGeo(V(-8, 1.4, -2.9), V(7, 1.6, 2.9)), lam("tugDeck", () => ({ color: "#c9a36a" })));
  b.add(boxGeo(V(-3, 1.6, -2.0), V(3.5, 4.6, 2.0)), lam("tugCab", () => ({ color: "#f2ede2" })));
  b.add(boxGeo(V(-1.5, 4.6, -1.6), V(2.5, 6.4, 1.6)), lam("tugCab", () => ({ color: "#f2ede2" })));
  b.add(new THREE.CylinderGeometry(0.7, 0.8, 3.2, 12).translate(-4.6, 4.2, 0), lam("tugStack", () => ({ color: "#c0353a" })));
  b.add(new THREE.CylinderGeometry(0.72, 0.72, 0.6, 12).translate(-4.6, 5.9, 0), lam("ink", () => ({ color: "#2a2230" })));
  for (const x of [-7, -4, -1, 2, 5]) b.add(new THREE.TorusGeometry(0.5, 0.18, 8, 16).translate(x, 0.6, 3.05), lam("tyre", () => ({ color: "#2a2a30" })));
  b.build(g); return g;
};

// ---------------- the cast ----------------
const HAT = "#f2c230";
const CREW: Outfit[] = [
  { jacket: "#e07b2e", pants: "#3b3f52", boots: "#3a2a20", hat: "cap", cap: "#f4f1ea", skin: SKINS[0] },
  { jacket: "#3f6fb5", pants: "#2f3445", boots: "#3a2a20", hat: "cap", cap: HAT, skin: SKINS[3], moustache: "#2a201a" },
  { jacket: "#c94a3a", pants: "#3b3f52", boots: "#4a3426", hat: "cap", cap: HAT, skin: SKINS[1] },
];
const FISHER: Outfit = { jacket: "#5d7a3a", pants: "#6b5a40", boots: "#4a3426", hat: "cap", cap: "#b8863a", skin: SKINS[2], moustache: "#8a7a6a", build: "stout" };
const ELEC: Outfit = { jacket: "#2f63b0", pants: "#2f63b0", boots: "#2a2230", hat: "cap", cap: "#f4f1ea", skin: SKINS[1] };
const MINERS: Outfit[] = [
  { jacket: "#9aa0a8", pants: "#9aa0a8", boots: "#2a2230", hat: "cap", cap: HAT, skin: SKINS[0] },
  { jacket: "#a89a74", pants: "#a89a74", boots: "#3a2a20", hat: "cap", cap: HAT, skin: SKINS[3] },
  { jacket: "#e07b2e", pants: "#4a4f58", boots: "#2a2230", hat: "cap", cap: HAT, skin: SKINS[2], moustache: "#3a2a20" },
  { jacket: "#7a8a5a", pants: "#4a4f58", boots: "#3a2a20", hat: "cap", cap: HAT, skin: SKINS[1], build: "stout" },
];

// ---------------- walkers: [t, x, z, mode of the segment that starts here] ----------------
type Mode = "walk" | "run" | "stand" | "jump" | "sit";
type Key = [number, number, number, Mode?];
type W = { x: number; z: number; dx: number; dz: number; mode: Mode; phase: number; amt: number; pose: number };
const CYC: Record<string, number> = { walk: 1.3, run: 1.81 };
const walkAt = (keys: Key[], t: number): W => {
  let ph = 0, dx = 0, dz = 1;
  for (let i = 0; i < keys.length; i++) {
    const [t0, x0, z0, m0] = keys[i], nx = keys[i + 1];
    const ex = nx ? nx[1] - x0 : 0, ez = nx ? nx[2] - z0 : 0, d = Math.hypot(ex, ez);
    if (d > 1e-3) { dx = ex / d; dz = ez / d; }
    const mode: Mode = m0 ?? (d > 1e-3 ? "run" : "stand");
    if (!nx || t < nx[0]) {
      const k = nx && t > t0 ? (t - t0) / (nx[0] - t0) : 0;
      if (mode === "walk" || mode === "run") ph += (d * k) / CYC[mode];
      const moving = (mode === "walk" || mode === "run") && t >= t0 && !!nx;
      return { x: x0 + ex * k, z: z0 + ez * k, dx, dz, mode: t < t0 ? (keys[0][3] === "sit" ? "sit" : "stand") : moving ? mode : mode === "jump" ? "jump" : mode === "sit" ? "sit" : "stand", phase: ph, amt: moving ? 1 : 0, pose: k };
    }
    if (mode === "walk" || mode === "run") ph += d / CYC[mode];
  }
  const l = keys[keys.length - 1];
  return { x: l[1], z: l[2], dx, dz, mode: "stand", phase: ph, amt: 0, pose: 0 };
};

type Member = { o: Outfit; key: string; i: number; w: W; y: number; expr: Expr; look?: number; sc?: number; extra?: Partial<FrontOpts> };

export class World {
  root = new THREE.Group();
  private pool = new Pool();
  private actors: Actor[] = [];
  private fxs: Fx[] = [];
  private hemi: THREE.HemisphereLight; private sun: THREE.DirectionalLight;
  private sky: THREE.Mesh; private skyMat: THREE.ShaderMaterial;
  private fog = new THREE.Fog("#bccbec", 25, 420);
  private WU: Record<string, THREE.IUniform>;
  private sunDisc: THREE.Sprite; private sunHalo: THREE.Sprite;
  private sunCache = new Map<number, THREE.Vector3>();
  private cloudMaps: Record<"day" | "golden", THREE.Texture[]>;
  private clouds: THREE.Mesh[] = [];
  private water: Polar; private waterMesh: THREE.Mesh; private calmM: THREE.Material; private swirlM: THREE.MeshLambertMaterial; private uFoam = { value: 0.5 };
  private bed: Polar; private bedMesh: THREE.Mesh;
  private rig = new THREE.Group(); private rigTilt = new THREE.Group(); private kelly: THREE.Mesh;
  private barges: THREE.Group[] = []; private tug: THREE.Group; private rowboat = new THREE.Group();
  private island = new THREE.Group(); private islandTrees: { g: THREE.Group; near: number; x: number; z: number }[] = [];
  private gauge = new THREE.Group();
  private fall: THREE.Mesh; private fallGeo: THREE.BufferGeometry; private fallMap: THREE.Texture;
  private mine = new THREE.Group(); private flood: THREE.Mesh; private floodGeo: THREE.BufferGeometry; private floodMap: THREE.Texture; private alarm: THREE.Mesh;
  private cut = new THREE.Group(); private cutParts: Record<string, THREE.Mesh> = {};
  private ground: THREE.Object3D[] = [];
  private frustum = new THREE.Frustum(); private m4 = new THREE.Matrix4(); private v = new THREE.Vector3(); private sph = new THREE.Sphere();
  private tmpC = new THREE.Color(); private tmpC2 = new THREE.Color();

  constructor(_kit: Kit) {
    const R = this.root;
    // ---- sky + light ----
    this.skyMat = new THREE.ShaderMaterial({
      uniforms: { c0: { value: new THREE.Color() }, c1: { value: new THREE.Color() }, c2: { value: new THREE.Color() }, c3: { value: new THREE.Color() }, c4: { value: new THREE.Color() }, e: { value: new THREE.Vector4() } },
      vertexShader: "varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
      fragmentShader: `uniform vec3 c0, c1, c2, c3, c4; uniform vec4 e; varying vec3 vP;
        void main(){ float el = asin(clamp(normalize(vP).y, -1.0, 1.0));
          vec3 c = mix(c0, c1, smoothstep(0.0, e.x, el)); c = mix(c, c2, smoothstep(e.x, e.y, el));
          c = mix(c, c3, smoothstep(e.y, e.z, el)); c = mix(c, c4, smoothstep(e.z, e.w, el)); gl_FragColor = vec4(c, 1.0); }`,
      side: THREE.BackSide, depthWrite: false, fog: false,
    });
    this.sky = new THREE.Mesh(new THREE.SphereGeometry(1100, 48, 24), this.skyMat);
    this.sky.renderOrder = -1; this.sky.frustumCulled = false; this.sky.layers.set(NOINK); R.add(this.sky);
    this.sunDisc = new THREE.Sprite(new THREE.SpriteMaterial({ map: discTex(), color: new THREE.Color(6.0, 4.4, 2.4), fog: false, depthWrite: false }));
    this.sunHalo = new THREE.Sprite(new THREE.SpriteMaterial({ map: haloTex(), color: new THREE.Color(1, 1, 1), fog: false, depthWrite: false, transparent: true, blending: THREE.AdditiveBlending }));
    this.sunDisc.renderOrder = -0.5; this.sunHalo.renderOrder = 5;
    for (const m of [this.sunDisc, this.sunHalo]) { m.frustumCulled = false; m.layers.set(NOINK); R.add(m); }
    this.hemi = new THREE.HemisphereLight("#cfe6ff", "#6c5c8c", 1.1);
    this.sun = new THREE.DirectionalLight("#fff0d6", 2.6); this.sun.castShadow = true; this.sun.shadow.mapSize.set(2048, 2048);
    R.add(this.hemi, this.sun, this.sun.target);
    this.cloudMaps = { day: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.day.cloud)), golden: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.golden.cloud)) };
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2 + 0.3, d = 640 + (i % 3) * 70;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: this.cloudMaps.day[i % 4], color: new THREE.Color(1.1, 1.1, 1.1), transparent: true, depthWrite: false, fog: false }));
      const w = 150 + (i % 4) * 35; m.position.set(Math.cos(a) * d, 120 + (i % 4) * 40, Math.sin(a) * d); m.scale.set(w, w / 2, 1); m.layers.set(NOINK);
      this.clouds.push(m); R.add(m);
    }

    // ---- shore: grass ring, canal, trees, farmhouses ----
    const b = new Batch();
    const grassM = lam("grassRing", () => ({ map: rep(grassHD(), 260, 260) }));
    const ring = new THREE.RingGeometry(LAKE_R, 1050, 160, 6).rotateX(-Math.PI / 2).translate(0, GROUND_Y, 0);
    b.add(ring, grassM);
    const bermM = lam("berm", () => ({ color: "#8fa860" }));
    for (const s of [-1, 1]) b.add(boxGeo(V(-1050, GROUND_Y - 0.1, s * (CANAL_W / 2 + 0.2) - 0.8), V(-LAKE_R - 1, GROUND_Y + 0.55, s * (CANAL_W / 2 + 0.2) + 0.8)), bermM);
    let n = 0;
    for (let i = 0; i < 900 && n < 170; i++) {
      const a = hh(i, 1) * Math.PI * 2, r = LAKE_R + 14 + 130 * hh(i, 2) ** 1.4, x = r * Math.cos(a), z = r * Math.sin(a);
      if (x < -LAKE_R + 20 && Math.abs(z) < 16) continue; // canal
      if (Math.hypot(x - HEAD[0], z - HEAD[2]) < 46) continue; // mine yard
      tree(b, x, GROUND_Y, z, 9 + 9 * hh(i, 3), i); n++;
    }
    for (let i = 0; i < 9; i++) {
      const a = -0.9 + i * 0.72 + 0.2 * hh(i, 4), r = LAKE_R + 40 + 50 * hh(i, 5), x = r * Math.cos(a), z = r * Math.sin(a);
      if (x < -LAKE_R + 30 && Math.abs(z) < 30) continue;
      if (Math.hypot(x - HEAD[0], z - HEAD[2]) < 40) continue;
      house(b, x, z, Math.atan2(-x, -z), 9, 8, 7 + 2 * hh(i, 6), i % 8, GROUND_Y);
    }
    // ---- mine yard on the east shore: headframe, hoist house, sheds ----
    const ironM = twoTone(new THREE.MeshPhongMaterial({ color: "#5d6a78", specular: "#8a96a2", shininess: 30 }), 0.15);
    const [hx, hy, hz] = HEAD, hf = (x: number, y: number, z: number) => V(hx + x, hy + y, hz + z - 6);
    for (const sx of [-1, 1]) for (const sz of [-1, 1]) b.add(beamBetween(hf(sx * 3.2, 0, sz * 3.2), hf(sx * 1.1, 22, sz * 1.1), 0.36), ironM);
    for (let k = 1; k < 6; k++) {
      const y = k * 4, w = 3.2 - (2.1 * y) / 22;
      for (const [a, c] of [[[-w, -w], [w, -w]], [[w, -w], [w, w]], [[w, w], [-w, w]], [[-w, w], [-w, -w]]] as const) b.add(beamBetween(hf(a[0], y, a[1]), hf(c[0], y, c[1]), 0.22), ironM);
    }
    b.add(boxGeo(hf(-1.8, 22, -1.8), hf(1.8, 22.6, 1.8)), ironM);
    for (const sz of [-0.6, 0.6]) b.add(new THREE.TorusGeometry(2.0, 0.22, 8, 28).translate(hx, hy + 24.2, hz - 6 + sz), lam("sheave", () => ({ color: "#c0353a" })));
    b.add(boxGeo(V(hx - 22, hy, hz - 14), V(hx - 10, hy + 9, hz - 4)), lam("hoistHouse", () => ({ color: "#b8a68a" })));
    b.add(boxGeo(V(hx - 22.4, hy + 9, hz - 14.4), V(hx - 9.6, hy + 9.6, hz - 3.6)), lam("hoistRoof", () => ({ color: "#5a4a44" })));
    b.add(beamBetween(V(hx - 10, hy + 7, hz - 9), V(hx, hy + 24, hz - 6), 0.08), lam("cable", () => ({ color: "#2a2230" })));
    house(b, hx + 18, hz - 10, -Math.PI / 2, 10, 8, 7, 3, GROUND_Y);
    house(b, hx - 20, hz + 14, Math.PI, 8, 7, 6.5, 5, GROUND_Y);
    b.build(R);

    // ---- water: calm (painted harbour shader) and whirlpool (swirl streaks) on one polar mesh ----
    const wNear = waterNear(), wFar = waterFar();
    for (const t of [wNear, wFar]) { t.colorSpace = THREE.NoColorSpace; t.anisotropy = 16; t.needsUpdate = true; }
    this.WU = {
      wNearC: { value: new THREE.Color() }, wMidC: { value: new THREE.Color() }, wFarC: { value: new THREE.Color() },
      wCrest: { value: new THREE.Color() }, wTrough: { value: new THREE.Color() }, wGlint: { value: new THREE.Color() },
      wShade: { value: new THREE.Vector3(0.5, 0.56, 0.72) }, wNearTex: { value: wNear }, wFarTex: { value: wFar }, wTime: { value: 0 },
    };
    const calm = new THREE.MeshLambertMaterial({ color: 0xffffff });
    calm.onBeforeCompile = (sh) => {
      Object.assign(sh.uniforms, this.WU);
      sh.vertexShader = sh.vertexShader.replace("#include <common>", "#include <common>\nvarying vec3 vWP;")
        .replace("#include <project_vertex>", "#include <project_vertex>\nvWP = (modelMatrix * vec4(transformed, 1.0)).xyz;");
      sh.fragmentShader = sh.fragmentShader.replace("#include <common>", WATER_DECL).replace("#include <map_fragment>", WATER_COL)
        .replace("#include <lights_fragment_begin>", "float sunVis = 1.0;\n" + LFB)
        .replace("#include <lights_fragment_end>", "#include <lights_fragment_end>\n  reflectedLight.directDiffuse = diffuseColor.rgb * mix(wShade, vec3(1.0), sunVis);\n  reflectedLight.indirectDiffuse = vec3(0.0);");
    };
    calm.customProgramCacheKey = () => "lakeCalm1";
    this.calmM = calm;
    const st = swirlTex(); st.colorSpace = THREE.NoColorSpace; st.needsUpdate = true;
    const sw = twoTone(new THREE.MeshLambertMaterial({ color: 0xffffff, vertexColors: true, map: st }), 0.4);
    const base = sw.onBeforeCompile;
    sw.onBeforeCompile = (sh, rr) => {
      base.call(sw, sh, rr);
      sh.uniforms.uFoam = this.uFoam;
      sh.fragmentShader = sh.fragmentShader.replace("#include <common>", "#include <common>\nuniform float uFoam;")
        .replace("#include <map_fragment>", "vec4 txS = texture2D( map, vMapUv );\n diffuseColor.rgb = mix( vColor, vec3( 0.86, 0.93, 0.95 ), txS.r * uFoam );")
        .replace("#include <color_fragment>", "");
    };
    sw.customProgramCacheKey = () => "lakeSwirl1";
    this.swirlM = sw;
    this.water = new Polar(LAKE_R + 4, 110);
    this.waterMesh = new THREE.Mesh(this.water.geo, calm); this.waterMesh.receiveShadow = true; this.waterMesh.frustumCulled = false; R.add(this.waterMesh);
    // ---- lake bed / crater ----
    this.bed = new Polar(LAKE_R + 14, 120, 1.5);
    this.bedMesh = new THREE.Mesh(this.bed.geo, twoTone(new THREE.MeshLambertMaterial({ color: 0xffffff, vertexColors: true }), 0.6));
    this.bedMesh.receiveShadow = true; this.bedMesh.castShadow = true; this.bedMesh.frustumCulled = false; R.add(this.bedMesh);
    // canal (calm shader, sits on the ground)
    const canal = new THREE.Mesh(up(-1050, -LAKE_R - 1, -CANAL_W / 2, CANAL_W / 2, GROUND_Y + 0.04, 1, 1), calm); canal.receiveShadow = true; R.add(canal);

    // ---- the drilling rig: deck, red derrick, drawworks house, pipe rack, kelly ----
    {
      const rb = new Batch(), deckM = lam("rigDeck", () => ({ color: "#6a7a8a" })), redM = lam("derrick", () => ({ color: "#d2452f" }));
      rb.add(boxGeo(V(-8, -1.2, -6), V(8, DECK, 6), 0, true), deckM);
      rb.add(boxGeo(V(-8.2, DECK - 0.4, -6.2), V(8.2, DECK - 0.1, 6.2)), lam("rigBand", () => ({ color: "#f2c230" })));
      const L = (x: number, y: number, z: number) => V(x, DECK + y, z);
      for (const sx of [-1, 1]) for (const sz of [-1, 1]) rb.add(beamBetween(L(sx * 3, 0, sz * 3), L(sx * 0.8, 24, sz * 0.8), 0.3), redM);
      for (let k = 1; k <= 5; k++) {
        const y = k * 4.4, w = 3 - (2.2 * y) / 24, y2 = y - 4.4, w2 = 3 - (2.2 * y2) / 24;
        const c = [[-w, -w], [w, -w], [w, w], [-w, w]], c2 = [[-w2, -w2], [w2, -w2], [w2, w2], [-w2, w2]];
        for (let e = 0; e < 4; e++) {
          const a = c[e], d = c[(e + 1) % 4], a2 = c2[e];
          rb.add(beamBetween(L(a[0], y, a[1]), L(d[0], y, d[1]), 0.18), redM);
          if (k > 1) rb.add(beamBetween(L(a2[0], y2, a2[1]), L(d[0], y, d[1]), 0.12), redM);
        }
      }
      rb.add(boxGeo(L(-1.1, 24, -1.1), L(1.1, 25.2, 1.1)), lam("crown", () => ({ color: "#f2c230" })));
      rb.add(boxGeo(L(-0.6, 13.2, -0.5), L(0.6, 14.8, 0.5)), lam("block", () => ({ color: "#f2c230" })));
      for (const s of [-0.25, 0.25]) rb.add(beamBetween(L(s, 14.8, 0), L(s, 24, 0), 0.05), lam("cable", () => ({ color: "#2a2230" })));
      rb.add(new THREE.CylinderGeometry(1.3, 1.3, 0.35, 24).translate(0, DECK + 0.17, 0), lam("rotary", () => ({ color: "#3a3d47" })));
      rb.add(boxGeo(L(-7.6, 0, -5.6), L(-2.6, 3.0, -1.6)), lam("drawworks", () => ({ color: "#f2ede2" })));
      rb.add(boxGeo(L(-7.8, 3.0, -5.8), L(-2.4, 3.3, -1.4)), lam("dwRoof", () => ({ color: "#3f6fb5" })));
      rb.add(boxGeo(L(-7.6, 0, 1.8), L(-3.2, 2.6, 5.6)), lam("doghouse", () => ({ color: "#e8dcc4" })));
      for (let i = 0; i < 8; i++) rb.add(new THREE.CylinderGeometry(0.16, 0.16, 8.5, 8).rotateZ(Math.PI / 2).translate(3.9, DECK + 0.25 + 0.3 * Math.floor(i / 4), -5 + (i % 4) * 0.34 + (i >= 4 ? 0.17 : 0)), lam("pipe", () => ({ color: "#8f969e" })));
      for (let x = -7.8; x <= 7.8; x += 1.95) for (const s of [-1, 1]) rb.add(beamBetween(L(x, 0, s * 5.85), L(x, 1.05, s * 5.85), 0.07), lam("rail", () => ({ color: "#f2c230" })));
      for (const s of [-1, 1]) rb.add(beamBetween(L(-7.8, 1.05, s * 5.85), L(7.8, 1.05, s * 5.85), 0.07), lam("rail", () => ({ color: "#f2c230" })));
      rb.build(this.rigTilt);
      const kt = kellyTex(); kt.colorSpace = THREE.SRGBColorSpace;
      this.kelly = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 11, 12).translate(0, DECK + 0.3 + 5.5, 0), twoTone(new THREE.MeshLambertMaterial({ map: kt })));
      this.kelly.castShadow = true; this.rigTilt.add(this.kelly);
      this.rig.add(this.rigTilt); this.rig.position.set(...RIG); R.add(this.rig);
    }
    for (let k = 0; k < BARGES.length; k++) { const g = buildBarge(k); this.barges.push(g); R.add(g); }
    this.tug = buildTug(); R.add(this.tug);
    {
      const bb = new Batch();
      const hs = new THREE.Shape([[-1.8, -0.72], [1.2, -0.72], [2.1, 0], [1.2, 0.72], [-1.8, 0.72], [-2.0, 0]].map(([x, z]) => new THREE.Vector2(x, z)));
      bb.add(new THREE.ExtrudeGeometry(hs, { depth: 0.7, bevelEnabled: false }).rotateX(Math.PI / 2).translate(0, 0.45, 0), lam("rowboat", () => ({ color: "#8a5a36" })));
      bb.add(boxGeo(V(-1.7, 0.3, -0.62), V(1.1, 0.34, 0.62)), lam("rowboatIn", () => ({ color: "#b98a5a" })));
      bb.add(boxGeo(V(-0.25, 0.34, -0.7), V(0.25, 0.45, 0.7)), lam("rowboat", () => ({ color: "#8a5a36" })));
      bb.add(beamBetween(V(0.35, 1.05, 0.3), V(3.6, 3.1, 0.6), 0.04), lam("rod", () => ({ color: "#2a2230" })));
      bb.add(beamBetween(V(3.6, 3.1, 0.6), V(5.2, 0.0, 0.8), 0.012), lam("line", () => ({ color: "#f4f1ea" })));
      for (const s of [-1, 1]) bb.add(beamBetween(V(-0.2, 0.5, s * 0.75), V(-1.4, -0.1, s * 1.9), 0.06), lam("oar", () => ({ color: "#c9a36a" })));
      bb.build(this.rowboat); this.rowboat.position.set(FISH[0], 0, FISH[2]); this.rowboat.rotation.y = 0.5; R.add(this.rowboat);
    }
    // ---- Jefferson Island bank: wooded mound that slides into the hole ----
    {
      const ib = new Batch();
      ib.add(new THREE.SphereGeometry(ISLAND_R, 40, 12, 0, Math.PI * 2, 0, Math.PI / 2).scale(1, 0.26, 1), lam("islandGrass", () => ({ map: rep(grassHD(), 6, 6) })));
      ib.add(new THREE.CylinderGeometry(ISLAND_R, ISLAND_R * 0.92, 4, 40, 1, true).translate(0, -2, 0), lam("islandMud", () => ({ color: "#7a6448" })));
      ib.build(this.island);
      for (let i = 0; i < 12; i++) {
        const a = (i / 12) * Math.PI * 2 + 0.3 * hh(i, 7), rr = ISLAND_R * (0.25 + 0.6 * hh(i, 8)), x = rr * Math.cos(a), z = rr * Math.sin(a);
        const g = new THREE.Group(), tb = new Batch(); tree(tb, 0, 0, 0, 8 + 4 * hh(i, 9), i + 3); tb.build(g);
        const yb = 5.2 * (1 - (rr / ISLAND_R) ** 2) ** 0.5 - 0.3; g.position.set(x, yb, z); this.island.add(g);
        // "near" = how far this tree sits on the side facing the hole
        const cx = ISLAND[0] + x, cz = ISLAND[2] + z, near = clamp01((ISLAND_R * 0.6 - (Math.hypot(cx, cz) - Math.hypot(ISLAND[0], ISLAND[2]))) / (ISLAND_R * 1.2));
        this.islandTrees.push({ g, near, x, z });
      }
      this.island.position.set(ISLAND[0], -2.4, ISLAND[2]); R.add(this.island);
    }
    // ---- depth gauge post ----
    {
      const gt = gaugeTex(); const post = new THREE.Mesh(new THREE.BoxGeometry(0.3, 5.2, 0.3).translate(0, -0.8, 0), twoTone(new THREE.MeshLambertMaterial({ map: gt })));
      post.castShadow = true; this.gauge.add(post);
      const sign = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.75, 0.08).translate(0, 2.2, 0.2), twoTone(new THREE.MeshLambertMaterial({ map: signTex() })));
      sign.castShadow = true; this.gauge.add(sign);
      this.gauge.position.set(GAUGE[0], 0, GAUGE[2]); this.gauge.rotation.y = -0.6; R.add(this.gauge);
    }
    // ---- waterfall ribbon (rebuilt per frame) ----
    {
      const NS = 48; this.fallGeo = new THREE.BufferGeometry();
      this.fallGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array((NS + 1) * 2 * 3), 3));
      this.fallGeo.setAttribute("uv", new THREE.BufferAttribute(new Float32Array((NS + 1) * 2 * 2), 2));
      const idx: number[] = []; for (let i = 0; i < NS; i++) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
      this.fallGeo.setIndex(idx);
      this.fallMap = fallTex();
      this.fall = new THREE.Mesh(this.fallGeo, twoTone(new THREE.MeshLambertMaterial({ map: this.fallMap, side: THREE.DoubleSide }), 0.6));
      this.fall.frustumCulled = false; R.add(this.fall);
    }

    // ---- the salt mine, far below: rooms and pillars, string lights, loader, panel, the one cage ----
    {
      const mb = new Batch(), M = this.mine;
      const fl = saltFloor(), wl = saltWall();
      mb.add(up(-210, 210, -210, 210, 0, 30, 30), lam("saltFloor", () => ({ map: fl })));
      const ceil = new THREE.Mesh(new THREE.PlaneGeometry(420, 420).rotateX(Math.PI / 2).translate(0, 24, 0), twoTone(new THREE.MeshLambertMaterial({ color: "#8f8a84" })));
      ceil.castShadow = false; ceil.receiveShadow = false; M.add(ceil);
      const pM = lam("saltWall", () => ({ map: rep(wl, 1.5, 1.8) }));
      for (let i = -6; i < 6; i++) for (let j = -6; j < 6; j++) { const x = 17 + 34 * i, z = 17 + 34 * j; mb.add(boxGeo(V(x - 10, 0, z - 10), V(x + 10, 24, z + 10)), pM); }
      for (const [a, c] of [[V(-212, 0, -212), V(212, 24, -208)], [V(-212, 0, 208), V(212, 24, 212)], [V(-212, 0, -212), V(-208, 24, 212)], [V(208, 0, -212), V(212, 24, 212)]] as const) mb.add(boxGeo(a, c), pM);
      // loader (yellow, big wheels, bucket)
      const yM = lam("loader", () => ({ color: "#e8b02a" })), tM = lam("tyre", () => ({ color: "#2a2a30" }));
      mb.add(boxGeo(V(-9.5, 1.0, -12), V(-4.5, 2.8, -6)), yM); mb.add(boxGeo(V(-8.8, 2.8, -9.5), V(-5.6, 4.4, -7.2)), lam("loaderCab", () => ({ color: "#3a3d47" })));
      mb.add(boxGeo(V(-10, 0.3, -5.6), V(-4, 1.6, -4.4)), yM);
      for (const x of [-9.6, -4.4]) for (const z of [-11, -7]) mb.add(new THREE.CylinderGeometry(1.0, 1.0, 0.8, 16).rotateZ(Math.PI / 2).translate(x, 1.0, z), tM);
      // panel the electrician works at
      mb.add(boxGeo(V(2.8, 0, -2.4), V(3.6, 1.9, -0.8)), lam("panel", () => ({ color: "#7a848f" })));
      mb.add(boxGeo(V(2.75, 1.2, -2.2), V(2.8, 1.7, -1.0)), lam("panelFace", () => ({ color: "#3a3d47" })));
      // the cage: steel frame, open to +z, guide rails up into the dark
      const cM = lam("cage", () => ({ color: "#4a4f58" })), [cx, , cz] = CAGE;
      for (const sx of [-2, 2]) for (const sz of [-1.5, 1.5]) mb.add(beamBetween(V(cx + sx, 0, cz + sz), V(cx + sx, 3.2, cz + sz), 0.16), cM);
      for (const y of [0.05, 1.6, 3.2]) for (const [a, c] of [[[-2, -1.5], [2, -1.5]], [[-2, -1.5], [-2, 1.5]], [[2, -1.5], [2, 1.5]]] as const) mb.add(beamBetween(V(cx + a[0], y, cz + a[1]), V(cx + c[0], y, cz + c[1]), 0.1), cM);
      for (let x = -1.6; x <= 1.6; x += 0.4) mb.add(beamBetween(V(cx + x, 0, cz - 1.5), V(cx + x, 3.2, cz - 1.5), 0.04), cM);
      mb.add(boxGeo(V(cx - 2, 3.2, cz - 1.5), V(cx + 2, 3.4, cz + 1.5)), cM);
      for (const sx of [-2.4, 2.4]) mb.add(beamBetween(V(cx + sx, 0, cz - 1.8), V(cx + sx, 24, cz - 1.8), 0.22), cM);
      mb.add(boxGeo(V(cx - 2.6, 0, cz - 2.0), V(cx + 2.6, 0.06, cz + 2.0)), lam("cagePlate", () => ({ color: "#e8b02a" })));
      mb.build(M);
      // string lights: warm bulbs on a cable along the corridors (bloom)
      const bulbM = new THREE.MeshBasicMaterial({ color: new THREE.Color(5, 3.8, 2.2) }), bulbG = new THREE.SphereGeometry(0.16, 10, 8);
      const cable = new Batch();
      for (const along of ["z", "x"] as const) for (let s = -200; s <= 200; s += 9) {
        const p = along === "z" ? V(0, 21.5, s) : V(s, 21.5, 0); const bm = new THREE.Mesh(bulbG, bulbM); bm.position.copy(p); bm.layers.set(NOINK); M.add(bm);
      }
      cable.add(beamBetween(V(0, 21.7, -200), V(0, 21.7, 200), 0.04), lam("cable", () => ({ color: "#2a2230" })));
      cable.add(beamBetween(V(-200, 21.7, 0), V(200, 21.7, 0), 0.04), lam("cable", () => ({ color: "#2a2230" })));
      cable.build(M, false);
      // alarm beacon on the panel
      this.alarm = new THREE.Mesh(new THREE.SphereGeometry(0.22, 12, 10), new THREE.MeshBasicMaterial({ color: new THREE.Color(6, 0.4, 0.3) }));
      this.alarm.position.set(3.2, 2.15, -1.6); this.alarm.layers.set(NOINK); M.add(this.alarm);
      // flood water rushing down the z corridor (rebuilt per frame)
      const NX = 8, NZ = 150; this.floodGeo = new THREE.BufferGeometry();
      const fp = new Float32Array((NX + 1) * (NZ + 1) * 3), fu = new Float32Array((NX + 1) * (NZ + 1) * 2), fi: number[] = [];
      for (let j = 0; j <= NZ; j++) for (let i = 0; i <= NX; i++) {
        const k = j * (NX + 1) + i; fp.set([-7 + (14 * i) / NX, 0, -200 + (210 * j) / NZ], k * 3); fu.set([i / NX * 2, (-200 + (210 * j) / NZ) / 14], k * 2);
        if (i < NX && j < NZ) fi.push(k, k + NX + 1, k + 1, k + 1, k + NX + 1, k + NX + 2);
      }
      this.floodGeo.setAttribute("position", new THREE.BufferAttribute(fp, 3)); this.floodGeo.setAttribute("uv", new THREE.BufferAttribute(fu, 2)); this.floodGeo.setIndex(fi);
      this.floodMap = floodTex();
      this.flood = new THREE.Mesh(this.floodGeo, twoTone(new THREE.MeshLambertMaterial({ map: this.floodMap }), 0.5)); this.flood.frustumCulled = false; this.flood.receiveShadow = true; M.add(this.flood);
      M.position.set(0, MINE_Y, 0); R.add(M);
    }

    // ---- cross-section diagram ----
    {
      const C = this.cut, basic = (col: string) => new THREE.MeshBasicMaterial({ color: untone(col), fog: false });
      const plate = new THREE.Mesh(new THREE.PlaneGeometry(160, 240).translate(0, -20, 0), new THREE.MeshBasicMaterial({ map: cutTex(), fog: false }));
      C.add(plate);
      const part = (k: string, col: string) => { const m = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 0.6).translate(0.5, -0.5, 0), basic(col)); this.cutParts[k] = m; C.add(m); return m; };
      part("lake", "#3f8fd0"); part("pipe", "#2a2230"); part("stream", "#4aa0e0"); part("pool", "#4aa0e0");
      C.position.set(CUT_X, 0, 0); R.add(C);
    }
  }

  private shotSun(id: number, s: ShotDef, L: LightPreset) {
    let v = this.sunCache.get(id);
    if (v) return v;
    let fx = 0, fz = 0;
    for (let f = s.a; f < s.b; f += 3) { const c = camAt(id, f), x = c.look[0] - c.pos[0], zz = c.look[2] - c.pos[2], n = Math.hypot(x, zz) || 1; fx += x / n; fz += zz / n; }
    const n = Math.hypot(fx, fz) || 1; fx /= n; fz /= n;
    const az = THREE.MathUtils.degToRad(s.sunAz ?? L.az), el = THREE.MathUtils.degToRad(s.sunEl ?? L.el);
    const hx = fx * Math.cos(az) - fz * Math.sin(az), hz = fz * Math.cos(az) + fx * Math.sin(az);
    v = new THREE.Vector3(hx * Math.cos(el), Math.sin(el), hz * Math.cos(el)).normalize();
    this.sunCache.set(id, v);
    return v;
  }
  private actor(i: number) { while (this.actors.length <= i) this.actors.push(new Actor(this.root)); return this.actors[i]; }
  private fx(i: number) { while (this.fxs.length <= i) this.fxs.push(new Fx(this.root)); return this.fxs[i]; }

  // ---------------- lake posing ----------------
  private poseWater(L: Lake, id: number, t: number) {
    const swirl = !L.refilled && (id === 1 || (id >= 6 && id <= 9) || id === 12);
    this.waterMesh.material = swirl ? this.swirlM : this.calmM;
    this.uFoam.value = 0.12 + 0.8 * L.spin;
    const W = this.water, deep = lin("#163f4a"), shallow = lin("#3f8e86"), mid = lin("#2b6c72"), c = this.tmpC;
    W.each((k, r, th) => {
      const y = swirl ? surfY(L, r) : L.level;
      W.pos[k * 3 + 1] = y;
      if (swirl) {
        const dip = L.level - y, rot = L.swirl * (1.25 / (1 + (r / (1.6 * L.Rf + 6)) ** 1.3));
        W.uv[k * 2] = ((th + rot + 0.55 * Math.log(r + 2)) / (Math.PI * 2)) * 5; W.uv[k * 2 + 1] = Math.sqrt(r) * 0.9;
        mixC(shallow, mid, dip / 4, c); mixC(c, deep, (dip - 4) / 14, c);
        W.col[k * 3] = c.r; W.col[k * 3 + 1] = c.g; W.col[k * 3 + 2] = c.b;
      }
    });
    W.commit(swirl);
  }
  private poseBed(L: Lake) {
    const B = this.bed, sand = lin("#bba97c"), mud = lin("#7f7458"), wet = lin("#5f5a48"), wall = lin("#8a7a62"), wall2 = lin("#a3937a"), deepC = lin("#4c443c"), salt = lin("#d8d2c6"), c = this.tmpC, c2 = this.tmpC2;
    B.each((k, r, th) => {
      const y = bedY(L, r, th); B.pos[k * 3 + 1] = y;
      if (y > -4.4) { mixC(wet, mud, (r / LAKE_R - 0.5) * 2, c); mixC(c, sand, (y + 0.4) / 1.2, c); }
      else { mixC(wall, wall2, 0.5 + 0.5 * Math.sin(y * 0.9), c2); mixC(c2, deepC, (-y - 10) / 40, c); mixC(c, salt, (-y - 60) / 10, c); }
      B.col[k * 3] = c.r; B.col[k * 3 + 1] = c.g; B.col[k * 3 + 2] = c.b;
    });
    B.commit();
  }
  /** a floating thing at (x0, z0) swallowed with progress p: spirals into the funnel, nose down */
  private swallow(o: THREE.Object3D, L: Lake, x0: number, z0: number, yaw0: number, p: number, floatOff: number, driftK = 1) {
    if (p >= 0.985) { o.visible = false; return; }
    o.visible = true;
    const r0 = Math.hypot(x0, z0), a0 = Math.atan2(z0, x0), drift = driftK * 0.28 * Math.max(0, L.swirl - swirlAngle(24.6)) / (1 + (r0 / 45) ** 2);
    const r = r0 * (1 - p ** 1.2), a = a0 + drift + 2.2 * p * p, x = r * Math.cos(a), z = r * Math.sin(a);
    const yS = Math.max(surfY(L, r), bedY(L, r, a) + 1.2) + floatOff;
    o.position.set(x, yS - 34 * p * p, z);
    o.rotation.set(0, yaw0 - (a - a0), 0);
    // lean into the funnel (towards the centre) as the slope steepens
    const slope = clamp01((surfY(L, r + 3) - surfY(L, Math.max(0, r - 3))) / 6);
    o.rotateOnWorldAxis(V(Math.sin(a), 0, -Math.cos(a)), -(Math.atan(slope * 1.2) + 1.1 * p));
  }
  private poseRig(L: Lake, t: number) {
    const R = this.rig, p = L.rigSink;
    if (p >= 0.97) { R.visible = false; return; }
    R.visible = true;
    const r0 = Math.hypot(RIG[0], RIG[2]), dirx = -RIG[0] / r0, dirz = -RIG[2] / r0, r = r0 * (1 - p);
    const base = Math.max(surfY(L, r), -2.6) * 0.65;
    R.position.set(-dirx * r, base - 42 * p * p, -dirz * r);
    R.quaternion.setFromAxisAngle(V(dirz, 0, -dirx), THREE.MathUtils.degToRad(12 * L.tilt + 45 * p));
    R.rotateY(0.8 * p);
    const jolt = t > 15.5 && t < 16.2 ? 0.02 * Math.sin((t - 15.5) * 60) * (1 - (t - 15.5) / 0.7) : 0;
    this.kelly.rotation.y = (t < 15.5 ? t : 15.5) * 4.2 + jolt;
    R.updateMatrixWorld(true);
  }
  private poseFall(L: Lake, t: number) {
    const k = L.fall, NS = 48;
    this.fall.visible = k > 0.01;
    if (!this.fall.visible) return;
    const pa = this.fallGeo.attributes.position.array as Float32Array, ua = this.fallGeo.attributes.uv.array as Float32Array;
    const pt = (s: number): [number, number] => {
      // canal end -> over the bank -> lip -> free fall into the crater (y -50)
      if (s < 0.25) { const u = s / 0.25; return [-238 + 20 * u, GROUND_Y + 0.05 - 0.8 * u * u]; }
      const tt = ((s - 0.25) / 0.75) * 3.2; return [-218 + 7.5 * tt, GROUND_Y - 0.75 - 0.5 * 9.8 * tt * tt];
    };
    const shown = Math.max(0.02, k);
    for (let i = 0; i <= NS; i++) {
      const s = (i / NS) * shown, [x, y] = pt(s), w = CANAL_W / 2 + 3 * clamp01((s - 0.25) / 0.75);
      for (let e = 0; e < 2; e++) { const o = (i * 2 + e) * 3; pa[o] = x; pa[o + 1] = y; pa[o + 2] = e ? w : -w; ua[(i * 2 + e) * 2] = e * 1.5; ua[(i * 2 + e) * 2 + 1] = s * 6; }
    }
    this.fallGeo.attributes.position.needsUpdate = true; this.fallGeo.attributes.uv.needsUpdate = true; this.fallGeo.computeVertexNormals(); this.fallGeo.computeBoundingSphere();
    this.fallMap.offset.y = -t * 1.4;
  }
  private poseIsland(L: Lake) {
    const I = this.island, s = L.slump;
    if (s >= 0.995) { I.visible = false; return; }
    I.visible = true;
    const r0 = Math.hypot(ISLAND[0], ISLAND[2]), dx = -ISLAND[0] / r0, dz = -ISLAND[2] / r0;
    I.position.set(ISLAND[0] + dx * 16 * s, -2.4 - 48 * s * s, ISLAND[2] + dz * 16 * s);
    I.quaternion.setFromAxisAngle(V(dz, 0, -dx), 0.6 * s);
    for (const tr of this.islandTrees) {
      const k = clamp01(L.trees * 1.4 - (1 - tr.near) * 0.9) * tr.near;
      tr.g.position.set(tr.x + dx * 9 * k * k, (5.2 * (1 - (Math.hypot(tr.x, tr.z) / ISLAND_R) ** 2) ** 0.5 - 0.3) - 7 * k * k, tr.z + dz * 9 * k * k);
      tr.g.quaternion.setFromAxisAngle(V(dz, 0, -dx), 1.2 * k);
      tr.g.visible = k < 0.98;
    }
  }
  private poseMine(t: number, on: boolean) {
    this.mine.visible = on;
    if (!on) return;
    const zf = t < 43.3 ? -260 : -110 + 92 * clamp01((t - 43.3) / 3.0) + 3.5 * Math.max(0, t - 46.3);
    const pa = this.floodGeo.attributes.position.array as Float32Array;
    for (let k = 0; k < pa.length / 3; k++) {
      const x = pa[k * 3], z = pa[k * 3 + 2], d = zf - z;
      pa[k * 3 + 1] = d > 0 ? 1.4 * smooth(d / 5) + 0.35 * Math.exp(-((d - 2.2) ** 2) / 2) + 0.12 * Math.sin(z * 0.8 + t * 11 + x) : -0.4;
    }
    this.floodGeo.attributes.position.needsUpdate = true; this.floodGeo.computeVertexNormals(); this.floodGeo.computeBoundingSphere();
    this.floodMap.offset.y = -t * 2.2;
    this.flood.visible = t > 43.3;
    this.alarm.visible = t > 44.3 && Math.floor((t - 44.3) * 4) % 2 === 0;
  }
  private poseCut(t: number, on: boolean) {
    this.cut.visible = on;
    if (!on) return;
    const P = this.cutParts, set = (m: THREE.Mesh, x0: number, y0: number, w: number, h: number, z = 0.4) => { m.visible = w > 0.01 && h > 0.01; m.position.set(x0, y0, z); m.scale.set(Math.max(0.01, w), Math.max(0.01, h), 1); };
    const punch = ramp(t, 56.85, 57.15), pour = clamp01((t - 57.15) / 1.3), spread = ramp(t, 58.0, 59.6), drain = ramp(t, 57.4, 59.6);
    set(P.lake, -44, 60, 88, 6 - 3.2 * drain, 0.3);
    set(P.pipe, -34.4, 60.4, 0.8, 60.4 + 40 + 7 * punch, 0.5);
    set(P.stream, -35.3, 55, 2.6, pour * (55 + 44), 0.45);
    set(P.pool, -36 - 4 * spread, -58 + 4.5 * spread, 76 * spread + 2.6 * pour * (pour > 0.99 ? 1 : 0), 4.5 * spread, 0.42);
    if (spread < 0.01) P.pool.visible = false;
  }

  update(id: number, f: number, cam: THREE.PerspectiveCamera, scene: THREE.Scene) {
    const t = f / FPS, s = SHOTS[id - 1], Lp = LIGHTS[s.light], K = LOOK[s.light];
    const L = lakeAt(id, t);
    // ---- camera ----
    const c = camAt(id, f);
    cam.position.set(...c.pos); cam.up.set(0, 1, 0); cam.lookAt(...c.look); cam.rotateZ(c.roll);
    cam.fov = c.fov; cam.near = 0.2; cam.far = 2000; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    const focus = V(...c.look), dist = cam.position.distanceTo(focus);
    cam.layers.enable(NOINK);
    // ---- light rig ----
    const sunDir = this.shotSun(id, s, Lp);
    this.hemi.color.set(Lp.sky); this.hemi.groundColor.set(Lp.ground); this.hemi.intensity = Lp.hemiI;
    this.sun.color.set(Lp.sunCol); this.sun.intensity = Lp.sunI;
    const Rr = THREE.MathUtils.clamp(dist * 1.3 + 12, 18, 110);
    this.sun.position.copy(focus).addScaledVector(sunDir, 260); this.sun.target.position.copy(focus);
    const sc = this.sun.shadow.camera; sc.left = -Rr; sc.right = Rr; sc.top = Rr; sc.bottom = -Rr; sc.near = 20; sc.far = 560; sc.updateProjectionMatrix();
    this.sun.shadow.bias = Lp.bias; this.sun.shadow.normalBias = Lp.normalBias * (Rr / 12);
    TONE.uLitCol.value.set(...Lp.lit); TONE.uShadeCol.value.set(...Lp.shade); TONE.uShadeLift.value.set(...Lp.lift);
    TONE.uLambert.value = Lp.lambert; TONE.uSideK.value = Lp.sideK; TONE.uTerm.value = Lp.term; TONE.uBounce.value.set(...K.bounce); TONE.uSat.value = K.sat;
    CHAR.uCharTint.value.set(...Lp.charTint); CHAR.uCharShade.value = Lp.charShade; CHAR.uGrad.value = Lp.charGrad; CHAR.uBodyGrad.value = Lp.bodyGrad; CHAR.uSideTint.value.set(...Lp.sideTint);
    // ---- sky, fog, sun, clouds ----
    const su = this.skyMat.uniforms;
    K.sky.c.forEach((h, i) => untone(h, su["c" + i].value));
    const e = K.sky.e.map((deg) => THREE.MathUtils.degToRad(deg)); su.e.value.set(e[1], e[2], e[3], e[4]);
    this.sky.position.copy(cam.position);
    if (s.mine) { untone("#2c2830", this.fog.color); this.fog.near = 22; this.fog.far = 150; }
    else if (Array.isArray(s.fog)) { untone(s.fog[0], this.fog.color); this.fog.near = s.fog[1]; this.fog.far = s.fog[2]; }
    else { const k = typeof s.fog === "number" ? s.fog : 1; untone(Lp.fog, this.fog.color); this.fog.near = Lp.fogNear * k; this.fog.far = Lp.fogFar * k; }
    scene.fog = this.fog; scene.background = null;
    this.sky.visible = !s.mine;
    const showSun = s.light === "golden" && !s.mine;
    this.sunDisc.visible = this.sunHalo.visible = showSun;
    if (showSun) {
      this.sunDisc.position.copy(cam.position).addScaledVector(sunDir, 900); this.sunDisc.scale.setScalar(2 * 900 * Math.tan(THREE.MathUtils.degToRad(1.7)));
      this.sunHalo.position.copy(this.sunDisc.position); this.sunHalo.scale.setScalar(2 * 900 * Math.tan(THREE.MathUtils.degToRad(24)));
      (this.sunHalo.material as THREE.SpriteMaterial).color.set(Lp.sunDisc).multiplyScalar(1.3);
    }
    for (let i = 0; i < this.clouds.length; i++) { const m = this.clouds[i]; m.visible = !s.mine && id !== 13; m.position.y = m.position.y; m.lookAt(cam.position.x, m.position.y, cam.position.z); (m.material as THREE.MeshBasicMaterial).map = this.cloudMaps[s.light][i % 4]; }
    // lake water colours: a greener freshwater lake than the bridge river
    const W = this.WU, wc = s.light === "golden"
      ? { near: "#2f5a64", mid: "#3d6a80", far: "#c9a08c", crest: "#d9a088", trough: "#1d3a48", glint: "#ffe2b0", shade: [0.42, 0.46, 0.72] as [number, number, number] }
      : { near: "#3f9a8e", mid: "#357f88", far: "#5f93a6", crest: "#a6e0d2", trough: "#24606a", glint: "#ffffff", shade: [0.5, 0.56, 0.72] as [number, number, number] };
    untone(wc.near, W.wNearC.value); untone(wc.mid, W.wMidC.value); untone(wc.far, W.wFarC.value);
    untone(wc.crest, W.wCrest.value); untone(wc.trough, W.wTrough.value); untone(wc.glint, W.wGlint.value);
    W.wShade.value.set(...wc.shade); W.wTime.value = t;

    // ---- the lake ----
    const surface = !s.mine && id !== 13;
    this.waterMesh.visible = this.bedMesh.visible = surface;
    if (surface) {
      this.poseWater(L, id, t); this.poseBed(L); this.poseRig(L, L.t); this.poseIsland(L); this.poseFall(L, t);
      for (let k = 0; k < this.barges.length; k++) {
        const [x0, z0, yaw] = BARGES[k], g = this.barges[k];
        if (L.refilled) {
          const p = L.pop(k);
          g.visible = p > 0;
          if (p > 0) {
            const a = hh(k, 11) * Math.PI * 2, rr = 6 + 26 * hh(k, 12), y = p < 0.45 ? -10 + 13.4 * Math.sin((p / 0.45) * Math.PI / 2) : 3.4 * Math.cos(((p - 0.45) / 0.55) * Math.PI / 2) ** 2 - 0.15 * Math.sin((p - 0.45) * 20) * (1 - p);
            g.position.set(rr * Math.cos(a), y, rr * Math.sin(a)); g.rotation.set(0.5 * (1 - p) * (k % 2 ? 1 : -1), yaw + 0.7 * k, 0.3 * (1 - p));
          }
        } else this.swallow(g, L, x0, z0, yaw, L.barge(k), 0, k === 0 ? 0 : 1);
      }
      if (L.refilled) this.tug.visible = false; else this.swallow(this.tug, L, TUG[0], TUG[1], TUG[2], L.tug, 0);
      this.rowboat.visible = id <= 6 && !L.refilled; this.rowboat.position.y = 0.05 * Math.sin(t * 1.3); this.rowboat.rotation.z = 0.03 * Math.sin(t * 1.1);
      this.gauge.visible = id <= 6; this.gauge.position.y = 0;
    } else { this.rig.visible = false; this.fall.visible = false; this.island.visible = false; this.tug.visible = false; this.rowboat.visible = false; this.gauge.visible = false; for (const g of this.barges) g.visible = false; }
    this.poseMine(t, !!s.mine);
    this.poseCut(t, id === 13);

    // ---- cast + effects ----
    const right = V(0, 0, 0).setFromMatrixColumn(cam.matrixWorld, 0);
    const ci: CamInfo = { pos: cam.position, right };
    castBegin(s.light, ci);
    const st: Stage = { places: [], fx: [] };
    this.stage(id, t, L, ci, st);
    this.frustum.setFromProjectionMatrix(this.m4.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse));
    let ai = 0; const used: Actor[] = [];
    for (const p of st.places) {
      const sc2 = p.scale ?? 1;
      if (!this.frustum.intersectsSphere(this.sph.set(this.v.set(p.x, p.y + 1.1 * sc2, p.z), 3.5))) continue;
      const a = this.actor(ai++), [w, h, k] = p.size ?? [300, 500, 0.5];
      a.r = this.pool.req(p.key, w, h, k, p.draw); a.mesh.visible = true;
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

  // ---------------- the cast per shot ----------------
  /** deck height of the (tilted) rig under world (x, z) */
  private deckY(x: number, z: number) {
    const p0 = this.rig.localToWorld(V(0, DECK, 0)), n = V(0, 1, 0).applyQuaternion(this.rig.quaternion);
    return p0.y - (n.x * (x - p0.x) + n.z * (z - p0.z)) / n.y;
  }
  private onRig(lx: number, lz: number) { return this.rig.localToWorld(V(lx, DECK, lz)); }

  private put(out: Stage, cam: CamInfo, id: number, m: Member, t: number) {
    const { o, key: okey, i, w, y, expr, look = 0, sc = 1, extra = {} } = m;
    const blink = lidAt(t, i), ph = q(((w.phase % 1) + 1) % 1, 240);
    const tx = cam.pos.x - w.x, tz = cam.pos.z - w.z, tl = Math.hypot(tx, tz) || 1, toward = (tx * w.dx + tz * w.dz) / tl, across = w.dx * cam.right.x + w.dz * cam.right.z;
    if (w.mode === "jump") out.places.push(person(cam, { i, o, okey }, w.x, y, w.z, { side: false, mirror: false }, { mode: "jump", pose: q(w.pose, 30), expr, blink, look, ...extra }, {}, sc));
    else if (w.mode === "stand" || w.mode === "sit") out.places.push(person(cam, { i, o, okey }, w.x, y, w.z, { side: false, mirror: false }, { mode: w.mode, expr, blink, look, ...extra }, {}, sc));
    else if (Math.abs(toward) < 0.32) {
      const fs = Math.sqrt(Math.max(0, 1 - toward * toward));
      out.places.push(person(cam, { i, o, okey }, w.x, y, w.z, { side: true, mirror: across < 0 }, {}, { mode: w.mode, phase: ph, amt: q(w.amt, 40), stride: q(fs, 40), expr, blink }, sc));
    } else {
      const yaw = Math.max(-1, Math.min(1, across)) * Math.sign(toward);
      out.places.push(person(cam, { i, o, okey }, w.x, y, w.z, { side: false, mirror: false },
        { mode: w.mode, phase: ph, amt: q(w.amt, 40), yaw: q(yaw, 40), expr, blink, look, facing: Math.abs(yaw) > 0.3 ? (yaw > 0 ? 1 : -1) : 0, ...extra }, {}, sc));
    }
    if (w.mode !== "sit") blob(out, w.x, y, w.z, sc);
  }
  private splash(out: Stage, key: string, u: number, x: number, y: number, z: number, s: number) {
    if (u < 0 || u >= 1) return;
    const k = q(u, 30); out.fx.push({ key: `splash${k}`, cw: 800, ch: 800, draw: (p) => fxSplash(p, k), x, y: y + 0.37 * s, z, w: s, h: s });
  }

  private stage(id: number, t: number, L: Lake, cam: CamInfo, out: Stage) {
    const S = (w: Partial<W> & { x: number; z: number }): W => ({ dx: 0, dz: 1, mode: "stand", phase: 0, amt: 0, pose: 0, ...w });
    const crewLocal: [number, number][] = [[-0.8, 3.0], [0.7, 3.3], [1.9, 2.0]];
    if (id >= 2 && id <= 5) {
      // the drill crew on deck
      crewLocal.forEach(([lx, lz], n) => {
        const p = this.onRig(lx, lz);
        let expr: Expr = (["whistle", "smile", "neutral"] as Expr[])[n], look = 0;
        const extra: Partial<FrontOpts> = {};
        if (id === 4) {
          expr = t < 15.45 ? expr : t < 16.4 ? "shock" : (["pained", "nervous", "pained"] as Expr[])[n];
          if (t > 16.4) extra.tilt = (n === 1 ? -1 : 1) * 0.08 * (0.6 + 0.4 * Math.sin(t * 7 + n));
        }
        if (id === 5) { expr = "shock"; look = n === 0 ? 1 : -1; extra.tilt = -0.12 * L.tilt; }
        this.put(out, cam, id, { o: CREW[n], key: `crew${n}`, i: 10 + n, w: S({ x: p.x, z: p.z }), y: p.y, expr, look, extra }, t);
      });
      if (id === 4 && t > 15.5 && t < 17.8) {
        const p = this.onRig(0, 0), u = q((t * 1.3) % 1, 30);
        out.fx.push({ key: `creak${u}`, cw: 300, ch: 300, draw: (pp) => fxCreak(pp, u), x: p.x + 0.9, y: p.y + 1.6, z: p.z + 0.4, w: 0.9, h: 0.9, rot: -0.5 });
      }
      if (id === 5) {
        const p = this.onRig(0, 0), u = q((t * 1.5) % 1, 30);
        out.fx.push({ key: `creak${u}`, cw: 300, ch: 300, draw: (pp) => fxCreak(pp, u), x: p.x + 2.4, y: p.y + 9, z: p.z + 1, w: 3, h: 3, rot: -0.6 });
      }
    }
    if (id >= 2 && id <= 6 && !L.refilled) {
      // the fisherman in his rowboat
      const b = this.rowboat.position;
      this.put(out, cam, id, { o: FISHER, key: "fisher", i: 20, w: S({ x: b.x - 0.15, z: b.z + 0.1, mode: "sit" }), y: b.y + 0.32, expr: id >= 5 ? "shock" : t > 13.6 ? "whistle" : "smile_closed" }, t);
    }
    if (id === 6) {
      // jump onto barge 0 and run
      const runs: Key[][] = [
        [[20.5, 6.0, 9.4, "stand"], [20.55, 6.0, 9.4, "run"], [20.85, 6.0, 10.6, "jump"], [21.45, 6.2, 13.4, "run"], [24.7, 20.4, 14.2]],
        [[20.5, 8.6, 8.6, "stand"], [20.75, 8.6, 8.6, "run"], [21.2, 8.6, 10.6, "jump"], [21.8, 8.8, 13.6, "run"], [24.7, 21.8, 15.4]],
        [[20.5, 3.6, 9.8, "stand"], [20.95, 3.6, 9.8, "run"], [21.2, 3.6, 10.6, "jump"], [21.8, 3.8, 13.2, "run"], [24.7, 16.4, 16.2]],
      ];
      const by = this.barges[0].position.y + BARGE_DECK;
      runs.forEach((keys, n) => {
        const w = walkAt(keys, t);
        const jk = keys.findIndex((k) => k[3] === "jump"), j0 = keys[jk][0], j1 = keys[jk + 1][0];
        const dy = this.deckY(keys[jk][1], keys[jk][2]);
        let y = t < j0 ? this.deckY(w.x, w.z) : t < j1 ? dy + (by - dy) * smooth((t - j0) / (j1 - j0)) + 0.6 * Math.sin(Math.PI * clamp01((t - j0) / (j1 - j0) * 1.3 - 0.15)) : by;
        if (w.mode === "stand" && t < j0) y = this.deckY(w.x, w.z);
        this.put(out, cam, id, { o: CREW[n], key: `crew${n}`, i: 10 + n, w, y, expr: t < 20.62 + n * 0.1 ? "shock" : n === 1 ? "pained" : "shock" }, t);
      });
    }
    if (id === 8) {
      // spray as each thing goes under
      const at = (o: THREE.Object3D) => o.position;
      const items: [THREE.Object3D, number, number][] = [[this.rig, L.rigSink, 22], [this.tug, L.tug, 12], ...this.barges.map((g, k) => [g, L.barge(k), 14] as [THREE.Object3D, number, number])];
      for (const [o, p, s] of items) if (p > 0.55 && p < 0.97 && o.visible) { const P = at(o); this.splash(out, "go", (p - 0.55) / 0.42, P.x, Math.max(P.y, surfY(L, Math.hypot(P.x, P.z)) - 2), P.z, s); }
    }
    if (id === 9 && L.slump > 0.05 && L.slump < 0.9) {
      for (let k = 0; k < 4; k++) {
        const u = clamp01((L.slump - 0.05 - k * 0.08) / 0.6); if (u <= 0 || u >= 1) continue;
        const a = Math.atan2(ISLAND[2], ISLAND[0]) + (k - 1.5) * 0.18, r = Math.hypot(ISLAND[0], ISLAND[2]) - ISLAND_R * 0.6, qk = q(u, 30);
        out.fx.push({ key: `puff${qk}`, cw: 300, ch: 300, draw: (p) => fxPuff(p, qk), x: r * Math.cos(a), y: -4 - 8 * u, z: r * Math.sin(a), w: 22, h: 22, soft: true });
      }
    }
    if (id === 12 && L.fall > 0.6) {
      for (let k = 0; k < 6; k++) {
        const u = ((t * 0.45 + k / 6) % 1), qk = q(u, 30);
        out.fx.push({ key: `puff${qk}`, cw: 300, ch: 300, draw: (p) => fxPuff(p, qk), x: -194 + 6 * hh(k, 3), y: -50 + 10 * u, z: -9 + 18 * (k / 5), w: 26, h: 26, soft: true });
      }
    }
    if (id === 10 || id === 11) this.mineCast(id, t, cam, out);
    if (id === 13 && t > 56.95 && t < 57.6) {
      const u = q((t - 56.95) / 0.65, 30);
      out.fx.push({ key: `burst${u}`, cw: 500, ch: 500, draw: (p) => fxBurst(p, u, "#fff3b0", 10), x: CUT_X - 34, y: -42, z: 1, w: 26, h: 26 });
    }
    if (id === 14) {
      const spots: [number, number, Outfit, Expr][] = [
        [-3.6, 3.2, MINERS[0], "laugh"], [-2.2, 4.6, CREW[1], "relief_open"], [-0.9, 2.9, ELEC, "laugh"], [0.6, 4.3, MINERS[2], "grin"],
        [1.9, 3.0, CREW[0], "relief_open"], [3.3, 4.5, MINERS[1], "laugh"], [-1.5, 6.2, MINERS[3], "grin"], [2.4, 6.4, CREW[2], "relief"],
      ];
      spots.forEach(([dx, dz, o, ex], n) => {
        const extra: Partial<FrontOpts> = n % 2 === 0 ? { wave: q(0.5 + 0.5 * Math.sin(t * 7 + n * 1.3), 20) } : {};
        this.put(out, cam, id, { o, key: `surv${n}`, i: 40 + n, w: S({ x: HEAD[0] + dx, z: HEAD[2] + dz }), y: HEAD[1], expr: ex, extra }, t);
      });
    }
    if (id === 15) {
      for (let k = 0; k < 9; k++) {
        const p = L.pop(k); if (p < 0.2 || p > 0.95) continue;
        const a = hh(k, 11) * Math.PI * 2, rr = 6 + 26 * hh(k, 12);
        this.splash(out, "pop", (p - 0.2) / 0.75, rr * Math.cos(a), -0.4, rr * Math.sin(a), 16);
      }
    }
  }

  private mineCast(id: number, t: number, cam: CamInfo, out: Stage) {
    const Y = MINE_Y, S = (w: Partial<W> & { x: number; z: number }): W => ({ dx: 0, dz: 1, mode: "stand", phase: 0, amt: 0, pose: 0, ...w });
    if (id === 10) {
      const m: Member[] = [
        { o: ELEC, key: "elec", i: 30, w: S({ x: 1.9, z: -1.0 }), y: Y, expr: "neutral", look: 1 },
        { o: MINERS[0], key: "m0", i: 31, w: walkAt([[38.3, -9, -3.5, "walk"], [43.3, -2.6, -3.5]], t), y: Y, expr: "whistle" },
        { o: MINERS[1], key: "m1", i: 32, w: S({ x: -0.6, z: -6.0 }), y: Y, expr: "smile" },
        { o: MINERS[2], key: "m2", i: 33, w: walkAt([[38.3, 1.5, -30, "walk"], [43.3, 1.0, -24]], t), y: Y, expr: "neutral" },
        { o: MINERS[3], key: "m3", i: 34, w: S({ x: 5.4, z: -13 }), y: Y, expr: "smile_closed" },
      ];
      for (const x of m) this.put(out, cam, id, x, t);
      return;
    }
    const E = walkAt([[43.25, 1.9, -1.0, "stand"], [44.5, 1.9, -1.0, "run"], [45.1, 2.2, 2.2, "run"], [47.5, 15.4, -2.6, "stand"]], t);
    const eExpr: Expr = t < 43.75 ? "neutral" : t < 44.25 ? "nervous" : "shock";
    const m: Member[] = [
      { o: ELEC, key: "elec", i: 30, w: E, y: Y, expr: eExpr, look: t > 43.75 && t < 44.4 ? -1 : 0 },
      { o: MINERS[0], key: "m0", i: 31, w: walkAt([[43.25, -2.6, -6, "stand"], [44.0, -2.6, -6, "run"], [45.4, -2.4, 1.4, "run"], [48.9, 13.6, -1.6]], t), y: Y, expr: t < 44 ? "neutral" : "shock" },
      { o: MINERS[1], key: "m1", i: 32, w: walkAt([[43.25, 1.4, -14, "stand"], [44.3, 1.4, -14, "run"], [47.0, 1.0, 0.2, "run"], [49.6, 12.6, -2.0]], t), y: Y, expr: t < 44.3 ? "neutral" : "pained" },
      { o: MINERS[2], key: "m2", i: 33, w: walkAt([[43.25, -1.2, -22, "stand"], [44.4, -1.2, -22, "run"], [48.6, 0.0, 0.8]], t), y: Y, expr: "shock" },
      { o: MINERS[3], key: "m3", i: 34, w: walkAt([[43.25, 4, 1.6, "stand"], [46.2, 4, 1.6, "run"], [48.3, 16.4, -2.4, "stand"]], t), y: Y, expr: t < 46.4 ? "nervous" : "shock" },
    ];
    for (const x of m) this.put(out, cam, id, x, t);
    // foam crest along the flood front
    const zf = -110 + 92 * clamp01((t - 43.3) / 3.0) + 3.5 * Math.max(0, t - 46.3);
    if (t > 43.3) for (let k = 0; k < 5; k++) { const u = (t * 1.6 + k * 0.23) % 1; this.splash(out, "foam", u, -5.6 + k * 2.8, Y + 0.6, zf - 0.5, 3.2); }
  }
}
