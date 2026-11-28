// The Boston molasses flood as one three.js scene: harbour, plaza, the giant tank (16 riveted panels that burst outward),
// a street of houses under the elevated railway, the molasses surface (a height field driven by story.ts flood()), and
// the cast + effect cards. update(id, f, camera) poses everything for shot `id` at frame f.
import * as THREE from "three";
import { Batch, V, lam, Kit, house, boxGeo, quad } from "./build";
import { ctex, cobbleHD, stoneHD, cloudHD, rep, waterNear, waterFar } from "./paint";
import { Pen, Outfit, Expr, FrontOpts, townsfolk, KID, SKINS, INK } from "./toon";
import { LIGHTS, LOOK, LightPreset } from "./lights";
import { TONE, CHAR, LFB, twoTone, untone } from "./shade";
import { NOINK } from "./ink";
import { Pool, Actor, Fx, Stage, CamInfo, castBegin, person, blob, lidAt, viewOf, hh, q, Who } from "./cast";
import { WATER_DECL, WATER_COL, discTex, haloTex, smokeTex } from "./bworld";
import {
  FPS, SHOTS, TOTAL, camAt, frontZ, LAB, ShotDef, V3, smooth, clamp01, flood, TANK, TANK_R, TANK_H, STREET0, RAIL_X, RAIL_Y, TFRONT, TDIR, BURST_T,
} from "./story";

export const loadKit = () => Promise.resolve({} as Kit);

const up = (x0: number, x1: number, z0: number, z1: number, y: number, u: number, v: number) => {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute([x0, y, z1, x1, y, z1, x1, y, z0, x0, y, z1, x1, y, z0, x0, y, z0], 3));
  g.setAttribute("normal", new THREE.Float32BufferAttribute([0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute([0, 0, u, 0, u, v, 0, 0, u, v, 0, v], 2));
  return g;
};
const onT = (k: number, y: number, side = 0): V3 => [TFRONT[0] + TDIR[0] * k - TDIR[1] * side, y, TFRONT[2] + TDIR[1] * k + TDIR[0] * side];

// ---------------- painted textures ----------------
const NP = 16; // tank panels
const steelTex = (painted: boolean) => ctex(painted ? "tankBrown" : "tankGrey", 1024, 1024, (g, r) => {
  g.fillStyle = painted ? "#8a5230" : "#9aa3aa"; g.fillRect(0, 0, 1024, 1024);
  // plate seams + rivet rows (5 courses, 2 plates per panel)
  for (let k = 1; k < 5; k++) {
    const y = (k * 1024) / 5;
    g.fillStyle = painted ? "rgba(60,30,15,.55)" : "rgba(60,65,75,.5)"; g.fillRect(0, y - 3, 1024, 6);
    g.fillStyle = painted ? "rgba(255,200,150,.25)" : "rgba(255,255,255,.3)"; g.fillRect(0, y + 3, 1024, 2);
    for (let x = 10; x < 1024; x += 22) { g.beginPath(); g.arc(x, y - 12, 4, 0, 7); g.arc(x, y + 14, 4, 0, 7); g.fillStyle = painted ? "#5e3218" : "#6b737c"; g.fill(); }
  }
  for (const x of [0, 512, 1024]) { g.fillStyle = painted ? "rgba(60,30,15,.55)" : "rgba(60,65,75,.5)"; g.fillRect(x - 3, 0, 6, 1024); }
  // leak streaks running down from the seams (hidden under the brown coat)
  for (let i = 0; i < 26; i++) {
    const x = r() * 1024, y0 = Math.floor(r() * 5) * 205 + 200, len = 120 + r() * 520, w = 6 + r() * 14;
    const gr = g.createLinearGradient(0, y0, 0, y0 + len);
    gr.addColorStop(0, painted ? "rgba(70,32,12,.55)" : "rgba(92,45,15,.95)"); gr.addColorStop(1, "rgba(92,45,15,0)");
    g.fillStyle = gr; g.beginPath(); g.moveTo(x - w / 2, y0); g.lineTo(x + w / 2, y0); g.lineTo(x + w * 0.2, y0 + len); g.lineTo(x - w * 0.2, y0 + len); g.fill();
  }
  // soft weathering
  for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(0,0,0,${0.03 * r()})`; g.fillRect(r() * 1024, r() * 1024, 4 + r() * 30, 4 + r() * 30); }
});
const syrupTex = () => ctex("syrup", 512, 512, (g, r) => {
  g.fillStyle = "#ffffff"; g.fillRect(0, 0, 512, 512);
  // folds and glossy streaks of a thick flow
  for (let i = 0; i < 60; i++) {
    const y = r() * 512, x = r() * 512, len = 80 + r() * 260;
    g.strokeStyle = r() < 0.5 ? "rgba(255,226,170,.55)" : "rgba(90,40,20,.35)"; g.lineWidth = 3 + r() * 7; g.lineCap = "round";
    g.beginPath(); g.moveTo(x, y); g.bezierCurveTo(x + len * 0.3, y + 18 * (r() - 0.5), x + len * 0.6, y + 18 * (r() - 0.5), x + len, y + 10 * (r() - 0.5)); g.stroke();
  }
});
const sidewalkTex = () => stoneHD("sidewalk", ["#cfc4b4", "#c6baa9", "#d6ccbd", "#bfb3a2"], "#9c907f");

// ---------------- effect drawings (Pen, ink outlines) ----------------
const BROWN = "#6b3412", BROWN_HI = "#a8642e";
const fxBucket = (p: Pen, fill: number) => {
  p.poly([[40, 60], [260, 60], [230, 280], [70, 280]], "#9aa7b4", 10);
  p.ell(150, 60, 110, 26, "#5d6875", 10);
  if (fill > 0) p.ell(150, 62, 96 * (0.8 + 0.2 * fill), 20, BROWN, 0);
  p.arc(150, 70, 120, 120, 200, 340, 9);
};
const fxDrip = (p: Pen) => { p.poly([[60, 10], [84, 70], [84, 110], [60, 130], [36, 110], [36, 70]], BROWN, 7); p.ell(52, 82, 8, 16, BROWN_HI, 0); };
const fxBrush = (p: Pen) => {
  p.poly([[20, 120], [380, 120], [380, 200], [20, 200]], "#c99a5b", 10);
  p.poly([[30, 200], [370, 200], [360, 300], [40, 300]], "#7a4a2c", 10);
  p.poly([[170, 20], [230, 20], [230, 120], [170, 120]], "#8b5a33", 10);
};
const fxThermo = (p: Pen, k: number) => {
  p.poly([[110, 40], [190, 40], [190, 560], [110, 560]], "#f4f1ea", 12);
  p.ell(150, 640, 90, 90, "#d23b3b", 12);
  const top = 120 + 420 * k;
  p.poly([[132, top], [168, top], [168, 600], [132, 600]], "#d23b3b", 0);
  for (let y = 100; y < 560; y += 60) p.stroke([[190, y], [230, y]], 8);
  p.stroke([[120, 600 - 0], [120, 600]], 1);
};
const fxBag = (p: Pen) => {
  p.ell(200, 300, 160, 150, "#c9a35a", 12);
  p.poly([[140, 120], [260, 120], [240, 170], [160, 170]], "#b48c45", 10);
  p.stroke([[150, 175], [250, 175]], 12);
  const g = p.g; g.font = "900 190px Arial Black, sans-serif"; g.textAlign = "center"; g.textBaseline = "middle";
  g.lineWidth = 14; g.strokeStyle = INK; g.strokeText("$", 200, 315); g.fillStyle = "#2f7a3d"; g.fillText("$", 200, 315);
};
const fxBubble = (p: Pen) => {
  p.ell(300, 220, 270, 190, "#ffffff", 12);
  p.poly([[160, 360], [110, 470], [240, 385]], "#ffffff", 12);
  p.ell(300, 220, 270, 190, null, 12);
  // a cartoon bomb: the boss's excuse
  p.ell(300, 245, 95, 95, "#2b2b35", 10);
  p.ell(268, 210, 24, 18, "#6a6a78", 0);
  p.poly([[330, 150], [360, 140], [370, 170], [340, 180]], "#4a4a55", 8);
  p.stroke([[355, 145], [380, 110], [405, 100]], 9, "#8a6a3a");
  p.ell(412, 92, 22, 22, "#ffd23a", 7);
};
const fxSmell = (p: Pen, t: number) => {
  for (let k = 0; k < 3; k++) {
    const pts: [number, number][] = [];
    for (let i = 0; i <= 24; i++) { const y = 560 - i * 22, x = 100 + k * 100 + 22 * Math.sin(i * 0.55 - t * 6 + k * 1.7); pts.push([x, y]); }
    p.stroke(pts, 12, "#b5743a");
  }
};
const fxGlob = (p: Pen, k: number) => { const r = [70, 58, 80][k]; p.ell(100, 100, r, r * 0.85, "#4a2008", 8); p.ell(100 - r * 0.3, 100 - r * 0.3, r * 0.25, r * 0.18, "#c07a3a", 0); };
const fxCreakS = (p: Pen, t: number) => {
  const j = 8 * Math.sin(t * 40);
  for (const a of [-30, 0, 30]) { const b = ((a - 90) * Math.PI) / 180; p.stroke([[150 + 70 * Math.cos(b) + j, 230 + 70 * Math.sin(b)], [150 + 130 * Math.cos(b) + j, 230 + 130 * Math.sin(b)]], 12); }
};
const fxBurstS = (p: Pen, t: number) => {
  const c = 250, e = 1 - (1 - t) ** 3;
  for (let i = 0; i < 12; i++) {
    const a = (i * Math.PI * 2) / 12, ra = 40 + 200 * e * (i % 2 ? 0.75 : 1);
    p.poly([[c + 20 * Math.cos(a + 0.2), c + 20 * Math.sin(a + 0.2)], [c + ra * Math.cos(a), c + ra * Math.sin(a)], [c + 20 * Math.cos(a - 0.2), c + 20 * Math.sin(a - 0.2)]], "#fff3b0", Math.max(3, 8 * (1 - t)));
  }
};


const POO = "#5a3214", POO_D = "#3a1e0a", POO_HI = "#9a6430";
const fxPoop = (p: Pen) => {
  p.ell(150, 230, 120, 52, POO, 9); p.ell(150, 168, 92, 44, POO, 9); p.ell(150, 112, 62, 36, POO, 9);
  p.poly([[132, 82], [150, 30], [172, 84]], POO, 9);
  for (const [x, y, r] of [[105, 215, 22], [118, 156, 16], [130, 104, 12]] as const) p.ell(x, y, r, r * 0.6, POO_HI, 0);
};
const fxTP = (p: Pen, k: number) => {
  p.ell(110, 150, 70, 70, "#f6f3ea", 9); p.ell(110, 150, 22, 22, "#b89a6a", 7);
  const g = p.g; g.beginPath(); g.moveTo(150, 205); g.bezierCurveTo(200, 230 + 20 * k, 230, 150 - 30 * k, 285, 175); g.lineTo(290, 140); g.bezierCurveTo(235, 115 - 30 * k, 205, 200 + 20 * k, 165, 175); g.closePath();
  g.fillStyle = "#f6f3ea"; g.fill(); g.lineWidth = 8; g.strokeStyle = INK; g.stroke();
};
const fxFly = (p: Pen, k: number) => {
  p.ell(60 - 14, 34 - 8 * k, 20, 12, "rgba(220,235,255,.9)", 4, 0, 360, -30); p.ell(60 + 14, 34 - 8 * k, 20, 12, "rgba(220,235,255,.9)", 4, 0, 360, 30);
  p.ell(60, 58, 18, 24, "#1d1f26", 0); p.ell(60, 38, 11, 10, "#1d1f26", 0); p.dot(55, 36, 3.5, "#c0353a"); p.dot(65, 36, 3.5, "#c0353a");
};
const fxStink = (p: Pen, t: number) => {
  for (let k = 0; k < 3; k++) {
    const pts: [number, number][] = [];
    for (let i = 0; i <= 24; i++) { const y = 560 - i * 22, x = 100 + k * 100 + 22 * Math.sin(i * 0.55 - t * 6 + k * 1.7); pts.push([x, y]); }
    p.stroke(pts, 13, "#7fae3a");
  }
};
const fxGas = (p: Pen) => { for (const [x, y, r] of [[120, 150, 90], [230, 120, 110], [340, 150, 90], [230, 175, 130]] as const) p.ell(x, y, r, r * 0.55, "rgba(150,200,80,.35)", 0); };
const fxFish = (p: Pen) => {
  p.poly([[40, 100], [220, 60], [300, 100], [220, 140]], "#c9d6e0", 9); p.poly([[300, 100], [360, 60], [360, 140]], "#a9b8c4", 9);
  p.stroke([[80, 82], [100, 102]], 7); p.stroke([[100, 82], [80, 102]], 7); p.stroke([[60, 112], [78, 116]], 6);
};
const fxToiletBubble = (p: Pen) => {
  p.ell(300, 220, 270, 190, "#ffffff", 12); p.poly([[160, 360], [110, 470], [240, 385]], "#ffffff", 12); p.ell(300, 220, 270, 190, null, 12);
  p.poly([[220, 120], [300, 120], [300, 230], [220, 230]], "#f4f1ea", 9);
  p.ell(330, 250, 95, 38, "#f4f1ea", 9); p.poly([[255, 260], [405, 260], [380, 330], [280, 330]], "#f4f1ea", 9);
  p.ell(330, 250, 70, 24, "#9cc7e8", 0);
  for (const a of [-1, 1]) p.arc(330 + a * 130, 230, 40, 60, a < 0 ? 200 : -20, a < 0 ? 280 : 60, 9);
};
const fxSign = () => ctex("sewageSign", 1024, 300, (g) => {
  g.fillStyle = "#f2ead6"; g.fillRect(0, 0, 1024, 300); g.strokeStyle = "#2a2230"; g.lineWidth = 18; g.strokeRect(9, 9, 1006, 282);
  g.font = "900 150px Arial Black, sans-serif"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillStyle = "#2a2230"; g.fillText("SEWAGE", 512, 150);
});

// ---------------- the cast ----------------
const WORK: Outfit[] = [
  { jacket: "#3f6fb5", pants: "#3b3f52", boots: "#4a3426", hat: "cap", cap: "#5a4a3a", skin: SKINS[0] },
  { jacket: "#b5653f", pants: "#2f3445", boots: "#3a2a20", hat: "cap", cap: "#3a3d47", skin: SKINS[3], moustache: "#2a201a" },
  { jacket: "#5d7a3a", pants: "#3b3f52", boots: "#4a3426", hat: "cap", cap: "#7a5a3a", skin: SKINS[1] },
];
const BOSS: Outfit = { jacket: "#2b2f3d", pants: "#2b2f3d", boots: INK, hat: "tophat", moustache: "#3a2a20", buttons: "#e8c45a", build: "stout", skin: SKINS[0] };
const FOLK = [0, 1, 2, 3, 4, 5].map((v) => townsfolk(v));

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
  private panels: { pivot: THREE.Group; grey: THREE.Mesh; brown: THREE.Mesh; a: number }[] = [];
  private roof: THREE.Mesh; private paintBand: THREE.Mesh;
  private syrup: THREE.Mesh; private sg: THREE.BufferGeometry; private SX = 0; private SZ = 0;
  private railSeg = new THREE.Group(); private hero = new THREE.Group();
  private frustum = new THREE.Frustum(); private m4 = new THREE.Matrix4(); private v = new THREE.Vector3(); private sph = new THREE.Sphere();

  constructor(_kit: Kit) {
    const R = this.root;
    // ---- sky + light (as the bridge world) ----
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
    for (let i = 0; i < 10; i++) {
      const a = (i / 10) * Math.PI * 2 + 0.3, d = 620 + (i % 3) * 60;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: this.cloudMaps.day[i % 4], color: new THREE.Color(1.1, 1.1, 1.1), transparent: true, depthWrite: false, fog: false }));
      const w = 130 + (i % 4) * 30; m.position.set(Math.cos(a) * d, 110 + (i % 4) * 38, Math.sin(a) * d); m.scale.set(w, w / 2, 1); m.layers.set(NOINK);
      this.clouds.push(m); R.add(m);
    }

    // ---- ground: plaza + street cobbles, sidewalks, quay ----
    const b = new Batch();
    const cob = lam("cobbleHD", () => ({ map: cobbleHD() })), side = lam("sidewalk", () => ({ map: sidewalkTex() }));
    const ground = lam("ground", () => ({ color: "#b9ab92" }));
    b.add(up(-400, 400, -50, 600, -0.02, 1, 1), ground);
    b.add(up(-45, 30, -50, STREET0, 0, 37, 18), cob);
    b.add(up(-6, 6, STREET0, 160, 0, 3, 43.5), cob);
    for (const s of [-1, 1]) b.add(boxGeo(V(s < 0 ? -8.2 : 6, 0, STREET0), V(s < 0 ? -6 : 8.2, 0.14, 160), 2), side);
    // quay wall + harbour bed, water mesh below
    const quayM = lam("quay", () => ({ map: stoneHD("quayHD", ["#c9bcaa", "#bfb19f", "#d1c5b4", "#b8aa97"], "#958776") }));
    b.add(quad(V(-400, -2.4, -50), V(400, -2.4, -50), V(400, 0, -50), V(-400, 0, -50), 200, 1.2), quayM);
    b.add(boxGeo(V(-400, -0.05, -50.6), V(400, 0.25, -49.4), 2), lam("cope", () => ({ color: "#e6dccd" })));
    // bollards on the quay
    for (let x = -40; x <= 26; x += 6) b.add(new THREE.CylinderGeometry(0.22, 0.26, 0.7, 12).translate(x, 0.35, -48.8), lam("bollard", () => ({ color: "#3d414c" })));
    // tank plinth ring
    b.add(new THREE.CylinderGeometry(TANK_R + 0.6, TANK_R + 0.8, 0.5, 64).translate(TANK[0], 0.25, TANK[2]), lam("plinth", () => ({ map: rep(stoneHD("copeHD"), 6, 1) })));

    // ---- houses: two rows facing the street, warehouses round the plaza ----
    const r = (i: number, k: number) => hh(i, k);
    let z = -10;
    for (let i = 0; z < 150; i++) { const w = r(i, 1) < 0.5 ? 7 : 9, h = [7, 8.4, 9.8][Math.floor(r(i, 2) * 3)]; const cz = z + w / 2;
      if (!(cz > 16 && cz < 26)) house(b, -12.2, cz, Math.PI / 2, w, 8, h, Math.floor(r(i, 3) * 8), 0);
      z += w + 0.3; }
    z = -22;
    for (let i = 0; z < 150; i++) { const w = r(i, 4) < 0.5 ? 7 : 9, h = [7, 8.4, 9.8][Math.floor(r(i, 5) * 3)]; house(b, 12.2, z + w / 2, -Math.PI / 2, w, 8, h, Math.floor(r(i, 6) * 8) + 3, 0); z += w + 0.3; }
    for (const [x, zz, yaw, w, d, h, si] of [[22, -42, -Math.PI / 2, 12, 10, 11, 2], [-38, -12, Math.PI / 2, 14, 10, 12, 5], [-34, 4, Math.PI / 2, 12, 9, 10, 7], [26, -30, -Math.PI / 2, 10, 9, 9.8, 4]] as const)
      house(b, x, zz, yaw, w, d, h, si, 0);
    // the hero house (shoved off its foundation in shot 8): own batch, left row at z 21
    const hb = new Batch();
    house(hb, 0, 0, Math.PI / 2, 9, 8, 8.4, 6, 0);
    hb.build(this.hero); this.hero.position.set(-12.2, 0, 21); R.add(this.hero);

    // ---- elevated railway: two girders on steel posts, cross ties, rails ----
    const ironM = twoTone(new THREE.MeshPhongMaterial({ color: "#46604c", specular: "#7a8a7a", shininess: 30 }), 0.15);
    const tieM = lam("tie", () => ({ color: "#5a4636" })), railM = twoTone(new THREE.MeshPhongMaterial({ color: "#8a8f96", specular: "#cccccc", shininess: 60 }), 0.15);
    const rail = (bb: Batch, z0: number, z1: number) => {
      for (const s of [-1, 1]) bb.add(boxGeo(V(RAIL_X + s * 1.15 - 0.22, RAIL_Y - 0.9, z0), V(RAIL_X + s * 1.15 + 0.22, RAIL_Y, z1), 0, true), ironM);
      for (let zz = z0 + 0.3; zz < z1; zz += 0.9) bb.add(boxGeo(V(RAIL_X - 1.6, RAIL_Y, zz - 0.12), V(RAIL_X + 1.6, RAIL_Y + 0.18, zz + 0.12), 0, true), tieM);
      for (const s of [-1, 1]) bb.add(boxGeo(V(RAIL_X + s * 0.72 - 0.05, RAIL_Y + 0.18, z0), V(RAIL_X + s * 0.72 + 0.05, RAIL_Y + 0.3, z1)), railM);
    };
    rail(b, -8, 160);
    for (let zz = -4; zz < 160; zz += 12) for (const s of [-1, 1]) {
      b.add(boxGeo(V(RAIL_X + s * 1.15 - 0.18, 0, zz - 0.18), V(RAIL_X + s * 1.15 + 0.18, RAIL_Y - 0.9, zz + 0.18), 0, true), ironM);
      if (s > 0) b.add(boxGeo(V(RAIL_X - 1.4, RAIL_Y - 1.4, zz - 0.15), V(RAIL_X + 1.4, RAIL_Y - 0.9, zz + 0.15), 0, true), ironM);
    }
    const rb = new Batch(); rail(rb, -40, -8);
    for (let zz = -36; zz < -8; zz += 12) for (const s of [-1, 1]) rb.add(boxGeo(V(RAIL_X + s * 1.15 - 0.18, 0, zz - 0.18), V(RAIL_X + s * 1.15 + 0.18, RAIL_Y - 0.9, zz + 0.18), 0, true), ironM);
    rb.build(this.railSeg); R.add(this.railSeg);
    b.build(R);

    // ---- harbour water (the bridge's painted river shader, flat) ----
    const wNear = waterNear(), wFar = waterFar();
    for (const t of [wNear, wFar]) { t.colorSpace = THREE.NoColorSpace; t.anisotropy = 16; t.needsUpdate = true; }
    this.WU = {
      wNearC: { value: new THREE.Color() }, wMidC: { value: new THREE.Color() }, wFarC: { value: new THREE.Color() },
      wCrest: { value: new THREE.Color() }, wTrough: { value: new THREE.Color() }, wGlint: { value: new THREE.Color() },
      wShade: { value: new THREE.Vector3(0.5, 0.56, 0.72) }, wNearTex: { value: wNear }, wFarTex: { value: wFar }, wTime: { value: 0 },
    };
    const waterM = new THREE.MeshLambertMaterial({ color: 0xffffff });
    waterM.onBeforeCompile = (sh) => {
      Object.assign(sh.uniforms, this.WU);
      sh.vertexShader = sh.vertexShader.replace("#include <common>", "#include <common>\nvarying vec3 vWP;")
        .replace("#include <project_vertex>", "#include <project_vertex>\nvWP = (modelMatrix * vec4(transformed, 1.0)).xyz;");
      sh.fragmentShader = sh.fragmentShader.replace("#include <common>", WATER_DECL).replace("#include <map_fragment>", WATER_COL)
        .replace("#include <lights_fragment_begin>", "float sunVis = 1.0;\n" + LFB)
        .replace("#include <lights_fragment_end>", "#include <lights_fragment_end>\n  reflectedLight.directDiffuse = diffuseColor.rgb * mix(wShade, vec3(1.0), sunVis);\n  reflectedLight.indirectDiffuse = vec3(0.0);");
    };
    waterM.customProgramCacheKey = () => "harbour1";
    const wm = new THREE.Mesh(up(-900, 900, -900, -50, -1.4, 1, 1), waterM); wm.receiveShadow = true; R.add(wm);
    // far shore: a low line of hills + warehouses so the harbour has a horizon
    const fb = new Batch();
    for (let i = 0; i < 14; i++) house(fb, -160 + i * 26, -330 - hh(i, 9) * 30, 0, 16, 10, 10 + hh(i, 7) * 8, i, -1.4);
    fb.add(up(-500, 500, -420, -300, -1.3, 1, 1), lam("farShore", () => ({ color: "#9fb37a" })));
    fb.build(R, false);
    // a few boats moored in the harbour
    const hullM = lam("hull", () => ({ color: "#3d4a5e" })), deckM = lam("deck", () => ({ color: "#c9a36a" })), cabM = lam("cabin", () => ({ color: "#efe3c8" }));
    const bb = new Batch();
    for (const [x, zz, yaw, L] of [[-6, -64, 0.3, 14], [14, -78, -0.2, 18], [-28, -86, 0.1, 22], [30, -60, 1.2, 10]] as const) {
      const m = new THREE.Matrix4().makeRotationY(yaw).setPosition(x, -1.4, zz);
      bb.add(boxGeo(V(-L / 2, -0.6, -2.2), V(L / 2, 1.4, 2.2), 0, true), hullM, m);
      bb.add(boxGeo(V(-L / 2 + 0.3, 1.4, -2.0), V(L / 2 - 0.3, 1.5, 2.0)), deckM, m);
      bb.add(boxGeo(V(-L * 0.15, 1.5, -1.4), V(L * 0.2, 3.4, 1.4)), cabM, m);
      bb.add(boxGeo(V(L * 0.05, 3.4, -0.35), V(L * 0.12, 6.0, 0.35)), hullM, m);
    }
    bb.build(R);

    // ---- the tank: 16 riveted panels hinged at the base, a shallow cone roof, the paint coat ----
    const greyM = twoTone(new THREE.MeshLambertMaterial({ map: steelTex(false), side: THREE.FrontSide }));
    const brownM = twoTone(new THREE.MeshLambertMaterial({ map: steelTex(true), side: THREE.FrontSide }));
    const innerM = twoTone(new THREE.MeshLambertMaterial({ color: "#3a1a0a", side: THREE.BackSide }));
    for (const m of [greyM, brownM]) if (m.map) { m.map.wrapS = THREE.RepeatWrapping; m.map.anisotropy = 8; }
    for (let i = 0; i < NP; i++) {
      const a0 = (i / NP) * Math.PI * 2, da = (Math.PI * 2) / NP, mid = a0 + da / 2;
      const g = new THREE.CylinderGeometry(TANK_R, TANK_R, TANK_H, 6, 1, true, a0, da).translate(0, TANK_H / 2, 0);
      // move into the pivot frame: hinge line at the base of the panel's outer face
      const hx = Math.sin(mid) * TANK_R, hz = Math.cos(mid) * TANK_R;
      g.translate(-hx, 0, -hz);
      const pivot = new THREE.Group(); pivot.position.set(TANK[0] + hx, 0.5, TANK[2] + hz); pivot.rotation.y = mid;
      g.rotateY(-mid);
      const grey = new THREE.Mesh(g, greyM), brown = new THREE.Mesh(g, brownM), inner = new THREE.Mesh(g, innerM);
      for (const m of [grey, brown, inner]) { m.castShadow = true; m.receiveShadow = true; pivot.add(m); }
      if (i === Math.floor(((((Math.atan2(TDIR[0], TDIR[1]) / (Math.PI * 2)) % 1) + 1) % 1) * NP)) {
        const sign = new THREE.Mesh(new THREE.PlaneGeometry(4.6, 1.35), new THREE.MeshBasicMaterial({ map: fxSign(), color: 0xe8e8e8 }));
        sign.position.set(0, 10.2, 0.12); pivot.add(sign);
      }
      R.add(pivot); this.panels.push({ pivot, grey, brown, a: mid });
    }
    this.roof = new THREE.Mesh(new THREE.ConeGeometry(TANK_R + 0.25, 2.4, 64, 1, true).translate(0, 1.2, 0), twoTone(new THREE.MeshLambertMaterial({ color: "#8b939a", side: THREE.DoubleSide })));
    this.roof.castShadow = true; R.add(this.roof);
    // the coat of brown paint climbing the street-facing wall (shot 4): a thin open band in front of the panels
    this.paintBand = new THREE.Mesh(new THREE.CylinderGeometry(TANK_R + 0.04, TANK_R + 0.04, 1, 48, 1, true, Math.atan2(TDIR[0], TDIR[1]) - 0.9, 1.8).translate(0, 0.5, 0), brownM);
    this.paintBand.position.set(TANK[0], 0.5, TANK[2]); R.add(this.paintBand);

    // ---- the molasses: a height field over the plaza and the street ----
    const X0 = -34, X1 = 10, Z0 = -50, Z1 = 110; this.SX = 89; this.SZ = 161;
    const pos = new Float32Array(this.SX * this.SZ * 3), uv = new Float32Array(this.SX * this.SZ * 2), idx: number[] = [];
    for (let j = 0; j < this.SZ; j++) for (let i = 0; i < this.SX; i++) {
      const k = j * this.SX + i, x = X0 + ((X1 - X0) * i) / (this.SX - 1), zz = Z0 + ((Z1 - Z0) * j) / (this.SZ - 1);
      pos.set([x, -1, zz], k * 3); uv.set([x / 6, zz / 6], k * 2);
      if (i < this.SX - 1 && j < this.SZ - 1) idx.push(k, k + this.SX, k + this.SX + 1, k, k + this.SX + 1, k + 1);
    }
    this.sg = new THREE.BufferGeometry();
    this.sg.setAttribute("position", new THREE.BufferAttribute(pos, 3)); this.sg.setAttribute("uv", new THREE.BufferAttribute(uv, 2));
    this.sg.setIndex(idx); this.sg.computeVertexNormals();
    const st = syrupTex(); st.wrapS = st.wrapT = THREE.RepeatWrapping;
    this.sg.setAttribute("color", new THREE.BufferAttribute(new Float32Array(this.SX * this.SZ * 3), 3));
    const syrupM = twoTone(new THREE.MeshPhongMaterial({ color: "#ffffff", vertexColors: true, map: st, specular: "#b8a878", shininess: 45 }), 0.25);
    this.syrup = new THREE.Mesh(this.sg, syrupM); this.syrup.castShadow = true; this.syrup.receiveShadow = true; this.syrup.frustumCulled = false; R.add(this.syrup);
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

  update(id: number, f: number, cam: THREE.PerspectiveCamera, scene: THREE.Scene) {
    const t = f / FPS, s = SHOTS[id - 1], L = LIGHTS[s.light], K = LOOK[s.light];
    const tau = s.clean ? -99 : s.tau(t);
    // ---- camera ----
    const c = camAt(id, f);
    cam.position.set(...c.pos); cam.up.set(0, 1, 0); cam.lookAt(...c.look); cam.rotateZ(c.roll);
    cam.fov = c.fov; cam.near = 0.2; cam.far = 1500; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    const focus = V(...c.look), dist = cam.position.distanceTo(focus);
    cam.layers.enable(NOINK);
    // ---- light rig ----
    const sunDir = this.shotSun(id, s, L);
    this.hemi.color.set(L.sky); this.hemi.groundColor.set(L.ground); this.hemi.intensity = L.hemiI;
    this.sun.color.set(L.sunCol); this.sun.intensity = L.sunI;
    const Rr = THREE.MathUtils.clamp(dist * 1.3 + 12, 18, 80);
    this.sun.position.copy(focus).addScaledVector(sunDir, 220); this.sun.target.position.copy(focus);
    const sc = this.sun.shadow.camera; sc.left = -Rr; sc.right = Rr; sc.top = Rr; sc.bottom = -Rr; sc.near = 20; sc.far = 480; sc.updateProjectionMatrix();
    this.sun.shadow.bias = L.bias; this.sun.shadow.normalBias = L.normalBias * (Rr / 12);
    TONE.uLitCol.value.set(...L.lit); TONE.uShadeCol.value.set(...L.shade); TONE.uShadeLift.value.set(...L.lift);
    TONE.uLambert.value = L.lambert; TONE.uSideK.value = L.sideK; TONE.uTerm.value = L.term; TONE.uBounce.value.set(...K.bounce); TONE.uSat.value = K.sat;
    CHAR.uCharTint.value.set(...L.charTint); CHAR.uCharShade.value = L.charShade; CHAR.uGrad.value = L.charGrad; CHAR.uBodyGrad.value = L.bodyGrad; CHAR.uSideTint.value.set(...L.sideTint);
    // ---- sky, fog, sun, clouds ----
    const su = this.skyMat.uniforms;
    K.sky.c.forEach((h, i) => untone(h, su["c" + i].value));
    const e = K.sky.e.map((deg) => THREE.MathUtils.degToRad(deg)); su.e.value.set(e[1], e[2], e[3], e[4]);
    this.sky.position.copy(cam.position);
    untone(L.fog, this.fog.color); this.fog.near = L.fogNear; this.fog.far = L.fogFar; scene.fog = this.fog; scene.background = null;
    const showSun = s.light === "golden";
    this.sunDisc.visible = this.sunHalo.visible = showSun;
    if (showSun) {
      this.sunDisc.position.copy(cam.position).addScaledVector(sunDir, 900); this.sunDisc.scale.setScalar(2 * 900 * Math.tan(THREE.MathUtils.degToRad(1.7)));
      this.sunHalo.position.copy(this.sunDisc.position); this.sunHalo.scale.setScalar(2 * 900 * Math.tan(THREE.MathUtils.degToRad(24)));
      (this.sunHalo.material as THREE.SpriteMaterial).color.set(L.sunDisc).multiplyScalar(1.3);
    }
    for (let i = 0; i < this.clouds.length; i++) { const m = this.clouds[i]; m.lookAt(cam.position.x, m.position.y, cam.position.z); (m.material as THREE.MeshBasicMaterial).map = this.cloudMaps[s.light][i % 4]; }
    // ---- harbour colours (brown after the flood in shot 11) ----
    const W = this.WU, wc = s.brown ? { near: "#6e3a1c", mid: "#7c4724", far: "#b07a5a", crest: "#b8834e", trough: "#4a2410", glint: "#ffe2b0", shade: [0.5, 0.45, 0.5] as [number, number, number] } : K.water;
    untone(wc.near, W.wNearC.value); untone(wc.mid, W.wMidC.value); untone(wc.far, W.wFarC.value);
    untone(wc.crest, W.wCrest.value); untone(wc.trough, W.wTrough.value); untone(wc.glint, W.wGlint.value);
    W.wShade.value.set(...wc.shade); W.wTime.value = t;

    // ---- the tank ----
    const paint = s.paint ? s.paint(t) : id >= 6 ? 1 : 0, burst = s.panels ? s.panels(t) : 0;
    const creak = id === 6 && t > BURST_T - 1.6 && t < BURST_T ? Math.sin(t * 60) * 0.004 * ((t - BURST_T + 1.6) / 1.6) : 0;
    for (const p of this.panels) {
      p.pivot.visible = id < 11;
      p.grey.visible = paint < 1; p.brown.visible = paint >= 1;
      const k = smooth(burst), fly = burst > 0 ? 0.6 + 0.4 * hh(p.a * 10, 3) : 0;
      p.pivot.rotation.set(0, p.a, 0);
      p.pivot.rotateX(creak + k * fly * 1.45); // tip outward around the base hinge
    }
    this.paintBand.visible = paint > 0 && paint < 1; this.paintBand.scale.y = Math.max(0.01, paint * TANK_H);
    this.roof.position.set(TANK[0], TANK_H + 0.5 + smooth(burst) * 3, TANK[2]); this.roof.rotation.set(smooth(burst) * 0.5, 0, smooth(burst) * 0.3);
    this.roof.visible = burst < 0.99 && id < 11;
    // ---- rail + hero house knocked by the wave (shot 8 on) ----
    const hit = id === 8 ? smooth((t - 29.1) / 0.5) : id > 8 ? 1 : 0, shove = id === 8 ? smooth((t - 30.85) / 0.7) : id > 8 ? 1 : 0;
    const fixed = s.clean ? 0 : 1;
    const hk = hit * fixed; this.railSeg.position.set(0.9 * hk, -0.25 * hk, 0); this.railSeg.rotation.set(0, 0.012 * hk, -0.05 * hk);
    this.hero.position.set(-12.2 - 1.6 * shove * fixed, 0.3 * shove * fixed, 21 + 1.0 * shove * fixed); this.hero.rotation.set(0, 0.07 * shove * fixed, 0.06 * shove * fixed);
    // ---- molasses surface ----
    const pa = this.sg.attributes.position.array as Float32Array;
    let any = false;
    for (let k = 0; k < this.SX * this.SZ; k++) {
      const x = pa[k * 3], zz = pa[k * 3 + 2];
      const h = tau > 0 ? flood(x, zz, tau) : 0;
      pa[k * 3 + 1] = h > 0.03 ? h : -0.6;
      if (h > 0.03) any = true;
    }
    this.syrup.visible = any;
    if (any) {
      this.sg.attributes.position.needsUpdate = true; this.sg.computeVertexNormals(); this.sg.computeBoundingSphere();
      const nn = this.sg.attributes.normal.array as Float32Array, cc = this.sg.attributes.color.array as Float32Array;
      for (let k = 0; k < this.SX * this.SZ; k++) {
        const steep = clamp01((1 - nn[k * 3 + 1]) * 2.0), crest = clamp01((pa[k * 3 + 1] - 2.5) / 3) * clamp01(nn[k * 3 + 1] * 1.5);
        const kk = Math.max(steep * 0.6, crest);
        cc[k * 3] = 0.04 + 0.1 * kk; cc[k * 3 + 1] = 0.02 + 0.05 * kk; cc[k * 3 + 2] = 0.008 + 0.016 * kk;
      }
      this.sg.attributes.color.needsUpdate = true;
    }

    // ---- cast + effects ----
    const right = V(0, 0, 0).setFromMatrixColumn(cam.matrixWorld, 0);
    const ci: CamInfo = { pos: cam.position, right };
    castBegin(s.light, ci);
    const st: Stage = { places: [], fx: [] };
    this.stage(id, t, ci, st, tau);
    this.frustum.setFromProjectionMatrix(this.m4.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse));
    let ai = 0; const used: Actor[] = [];
    for (const p of st.places) {
      const sc2 = p.scale ?? 1;
      if (!this.frustum.intersectsSphere(this.sph.set(this.v.set(p.x, p.y + 1.1 * sc2, p.z), 3.5))) continue;
      const a = this.actor(ai++), [w, h, k] = p.size ?? [300, 500, 0.5];
      a.r = this.pool.req(p.key, w, h, k, p.draw); a.mesh.visible = true;
      a.mesh.position.set(p.x, p.y, p.z);
      a.mesh.rotation.set(0, p.yaw ?? Math.atan2(cam.position.x - p.x, cam.position.z - p.z), p.roll ?? 0);
      a.mesh.scale.set(p.mirror ? -sc2 : sc2, sc2, sc2); a.mesh.castShadow = L.actorShadow; used.push(a);
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

  /** green stink lines rising off someone + a few flies circling their head */
  private stinkAt(out: Stage, t: number, x: number, z: number, flies: number, seed = 0) {
    const u = q((t * 0.8 + seed * 0.31) % 1, 12);
    out.fx.push({ key: `stink${u}`, cw: 400, ch: 600, draw: (p) => fxStink(p, u), x: x + 0.55, y: 1.9, z: z + 0.1, w: 0.6, h: 0.9, soft: true });
    for (let k = 0; k < flies; k++) {
      const a = t * (5 + k) + seed + k * 2.1, w = Math.round(t * 30 + k) % 2;
      out.fx.push({ key: `fly${w}`, cw: 120, ch: 100, draw: (p) => fxFly(p, w), x: x + 0.45 * Math.cos(a), y: 2.15 + 0.12 * Math.sin(a * 1.7), z: z + 0.45 * Math.sin(a), w: 0.14, h: 0.12 });
    }
  }

  /** motion lab: each walker drawn front / three-quarter / side from its real direction against the camera */
  private stage(id: number, t: number, cam: CamInfo, out: Stage, _tau: number) {
    const cast: [Outfit, string, Expr, number][][] = [
      [], [[WORK[0], "w0", "neutral", 1]], [[FOLK[1], "f1", "smile", 1]], [[WORK[1], "w1", "whistle", 1], [FOLK[3], "f3", "smile_closed", 1], [KID, "kid", "grin", 0.72]],
      [[BOSS, "boss", "neutral", 1]], [[WORK[2], "w2", "neutral", 1]],
    ];
    LAB[id].forEach((w, n) => {
      const [o, okey, ex0, sc] = cast[id][n], [x, y, z] = w.pos(t), [dx, dz] = w.dir(t), mode = w.mode(t), amt = w.amt(t), ph = w.phase(t) + n * 0.37;
      const tx = cam.pos.x - x, tz = cam.pos.z - z, tl = Math.hypot(tx, tz) || 1, toward = (tx * dx + tz * dz) / tl, across = dx * cam.right.x + dz * cam.right.z;
      let expr = ex0, look = 0;
      if (id === 1 && t > 2.6) expr = "grin";
      if (id === 2 && t > 8.5) look = t < 9.2 ? -1 : 1;
      if (id === 5 && t > 19.86) expr = "shock";
      const i = 80 + id * 10 + n, blink = lidAt(t, i);
      if (mode === "jump") {
        out.places.push(person(cam, { i, o, okey }, x, y, z, { side: false, mirror: false }, { mode: "jump", pose: w.pose(t), expr, blink, look }, {}, sc));
      } else if (mode === "stand") {
        out.places.push(person(cam, { i, o, okey }, x, y, z, { side: false, mirror: false }, { mode: "stand", expr, blink, look }, {}, sc));
      } else if (Math.abs(toward) < 0.32) {
        // side view; stride shrinks with the foreshortening so the planted foot matches the ground speed on screen
        const fs = Math.sqrt(Math.max(0, 1 - toward * toward));
        out.places.push(person(cam, { i, o, okey }, x, y, z, { side: true, mirror: across < 0 }, {}, { mode, phase: q(ph % 1, 240), amt: q(amt, 40), stride: q(fs, 40), expr, blink }, sc));
      } else {
        const yaw = Math.max(-1, Math.min(1, across)) * Math.sign(toward);
        out.places.push(person(cam, { i, o, okey }, x, y, z, { side: false, mirror: false },
          { mode, phase: q(ph % 1, 240), amt: q(amt, 40), yaw: q(yaw, 40), expr, blink, look, facing: Math.abs(yaw) > 0.3 ? (yaw > 0 ? 1 : -1) : 0 }, {}, sc));
      }
      blob(out, x, 0, z, sc * (1 - 0.5 * y));
    });
    if (id === 5 && t > 19.84 && t < 20.3) {
      const u = (t - 19.84) / 0.46, [x, , z] = LAB[5][0].pos(19.84);
      out.fx.push({ key: `bang${q(u, 15)}`, cw: 500, ch: 500, draw: (p) => fxBurstS(p, q(u, 15)), x: x - 2.2, y: 1.4, z: z - 1.5, w: 2.6, h: 2.6 });
    }
  }
}
