// "Sixty Seconds". Voice clock (Ethan v4, lines.json, 73.28 s), the countdown, the collapse timeline, and one camera per shot.
// House A sits at the origin: ground floor y 0.2, upstairs y 3.2, front door at z = 5 facing the street (+z).
import type { LName } from "./lights";
export const FPS = 30;
export const TOTAL = 2199;
export const NEW_TOTAL = TOTAL;
export const warpF = (f: number) => f;
export type V3 = [number, number, number];
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const glide = (u: number) => { const x = clamp01(u); return x * x * x * (x * (6 * x - 15) + 10); };
const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
const lerp3 = (a: V3, b: V3, k: number): V3 => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)];
export const ramp = (t: number, a: number, b: number) => smooth((t - a) / (b - a));

export const G0 = 0.2, FL1 = 3.2;
export const GREEN_AT = 21.45;
/** the countdown shown on screen (story seconds left), null when hidden */
export const timerAt = (t: number): number | null => {
  if (t < 22.35 || t > 47.2) return null;
  const K: [number, number][] = [[22.35, 60], [28.45, 40], [35.05, 20], [42.5, 5], [46.3, 0]];
  for (let i = 0; i < K.length - 1; i++) if (t < K[i + 1][0]) return Math.ceil(lerp(K[i][1], K[i + 1][1], (t - K[i][0]) / (K[i + 1][0] - K[i][0])));
  return 0;
};
/** the house + its lot sinking: 0 .. 1 */
export const sinkAt = (t: number) => clamp01((t - 55.97) / 2.4);
export const sinkY = (t: number) => { const u = sinkAt(t); return -22 * u * u; };

// ---------------- shots ----------------
export type Light = LName;
export type Cam = { pos: V3; look: V3; fov: number; roll: number };
export type ShotDef = { id: number; a: number; b: number; light: Light; cInf: number; cam: (t: number, u: number) => Cam; sunAz?: number; sunEl?: number; fog?: number; inside?: boolean };
const F = (s: number) => Math.round(s * FPS);
const C = (pos: V3, look: V3, fov = 42, roll = 0): Cam => ({ pos, look, fov, roll });
const mv = (a: Cam, b: Cam, k: number): Cam => ({ pos: lerp3(a.pos, b.pos, k), look: lerp3(a.look, b.look, k), fov: lerp(a.fov, b.fov, k), roll: lerp(a.roll, b.roll, k) });
const seg = (t: number, a: number, b: number) => glide((t - a) / (b - a));
export const CUT_X = 3000;
export const SHOTS: ShotDef[] = [
  // 1 night street: a red light above every door; drift in to ours
  { id: 1, a: 0, b: F(5.95), light: "night", cInf: 0, cam: (t) => mv(C([-24, 3.4, 23], [-8, 2.4, 5], 44), C([-1.6, 2.3, 11.5], [0, 2.6, 5.1], 40), seg(t, 0, 5.95)) },
  // 2 flashback, golden: grandpa shows me the light
  { id: 2, a: F(5.95), b: F(13.08), light: "golden", cInf: 10, sunAz: 40, cam: (t) => mv(C([3.4, 1.3, 11.0], [0, 1.6, 6.3], 44), C([-2.4, 1.3, 10.4], [0, 1.5, 6.4], 42), seg(t, 5.95, 13.08)) },
  // 3 the dog growling at the kitchen floor
  { id: 3, a: F(13.08), b: F(17.2), light: "room", cInf: 8, inside: true, cam: (t) => mv(C([3.7, 1.35, -0.4], [1.0, 0.45, -3.3], 46), C([3.4, 1.2, -0.9], [1.0, 0.45, -3.3], 42), seg(t, 13.08, 17.2)) },
  // 4 the glasses rattling in the cupboard
  { id: 4, a: F(17.2), b: F(21.0), light: "room", cInf: 6, inside: true, cam: (t) => mv(C([2.4, 2.1, -2.7], [2.4, 2.05, -4.7], 44), C([2.4, 2.1, -3.3], [2.4, 2.05, -4.7], 40), seg(t, 17.2, 21.0)) },
  // 5 the light turns green
  { id: 5, a: F(21.0), b: F(22.35), light: "night", cInf: 0, cam: (t) => mv(C([1.8, 1.9, 9.0], [0, 2.4, 5.1], 40), C([1.1, 2.2, 7.6], [0, 2.6, 5.1], 36), seg(t, 21.0, 22.35)) },
  // 6 sixty seconds: my face, then I run
  { id: 6, a: F(22.35), b: F(23.6), light: "room", cInf: 8, inside: true, cam: (t) => mv(C([1.0, 1.45, 1.6], [0.6, 1.25, 3.8], 42), C([1.0, 1.35, 1.3], [0.6, 1.2, 3.8], 46), seg(t, 22.35, 23.6)) },
  // 7 up the stairs (side), then mum's room
  { id: 7, a: F(23.6), b: F(28.4), light: "room", cInf: 0, inside: true, cam: (t) => t < 25.0
      ? (() => { const k = clamp01((t - 23.75) / 1.2), zk = -4.3 + 3.6 * k, yk = G0 + 3.0 * k; return C([-4.0, yk + 1.25, zk - 0.3], [-0.9, yk + 1.0, zk + 0.2], 52); })()
      : mv(C([-0.4, 5.0, 0.4], [-2.4, 4.0, 3.2], 54), C([-0.6, 4.9, 0.6], [-2.4, 4.0, 3.2], 50), seg(t, 25.0, 28.4)) },
  // 8 my sister's empty bed; then her eyes peeking out from under the stairs
  { id: 8, a: F(28.4), b: F(32.45), light: "room", cInf: 0, inside: true, cam: (t) => t < 31.1
      ? mv(C([0.6, 4.6, 0.5], [2.9, 3.8, 3.4], 50), C([0.8, 4.5, 0.8], [2.9, 3.8, 3.4], 46), seg(t, 28.4, 31.1))
      : mv(C([-3.3, 0.95, -3.0], [-1.55, 0.8, -1.45], 44), C([-3.0, 0.9, -2.75], [-1.55, 0.8, -1.45], 38), seg(t, 31.1, 32.45)) },
  // 9 I grab her hand and pull her out
  { id: 9, a: F(32.45), b: F(35.0), light: "room", cInf: 0, inside: true, cam: (t) => mv(C([-2.3, 1.35, 1.6], [-2.2, 0.9, -1.4], 50), C([-2.5, 1.3, 2.2], [-2.3, 0.95, -0.6], 50), seg(t, 32.45, 35.0)) },
  // 10 the front door won't open
  { id: 10, a: F(35.0), b: F(38.75), light: "room", cInf: 0, inside: true, cam: (t) => mv(C([2.9, 1.5, 3.7], [-0.2, 1.3, 4.5], 48), C([2.6, 1.45, 3.9], [-0.2, 1.4, 4.6], 44), seg(t, 35.0, 38.75)) },
  // 11 a crack runs across the wall through our photos
  { id: 11, a: F(38.75), b: F(42.45), light: "room", cInf: 0, inside: true, cam: (t) => mv(C([-0.9, 1.55, 1.2], [-4.2, 1.6, 2.4], 50), C([-1.3, 1.5, 1.5], [-4.2, 1.5, 2.4], 46), seg(t, 38.75, 42.45)) },
  // 12 the chair through the window (inside), then the jump (outside)
  { id: 12, a: F(42.45), b: F(46.4), light: "room", cInf: 0, inside: true, cam: (t) => t < 44.3
      ? mv(C([0.4, 1.45, 1.5], [-2.3, 1.45, 4.6], 50), C([0.3, 1.4, 1.8], [-2.5, 1.55, 4.8], 50), seg(t, 42.45, 44.3))
      : mv(C([-7.0, 1.0, 10.5], [-2.6, 1.5, 5.6], 48), C([-6.6, 0.9, 10.2], [-2.6, 1.3, 6.2], 46), seg(t, 44.3, 46.4)) },
  // 13 we land on the grass, everyone's out
  { id: 13, a: F(46.4), b: F(51.3), light: "night", cInf: 8, cam: (t) => mv(C([-5.5, 1.3, 13.0], [-2.4, 0.8, 9.0], 44), C([-5.0, 1.25, 12.4], [-2.3, 0.85, 9.3], 40), seg(t, 46.4, 51.3)) },
  // 14 nothing happens
  { id: 14, a: F(51.3), b: F(55.9), light: "night", cInf: 0, cam: (t) => mv(C([3.0, 1.5, 18.0], [-2.5, 1.8, 7.0], 44), C([2.6, 1.5, 17.0], [-2.5, 1.8, 7.0], 42), seg(t, 51.3, 55.9)) },
  // 15 the house drops into the ground; then down into the hole
  { id: 15, a: F(55.9), b: F(62.1), light: "night", cInf: 0, cam: (t) => t < 58.75
      ? mv(C([11, 3.0, 19], [0, 2.0, 2], 46), C([11.5, 3.6, 19.5], [0, -2.5, 2], 48), seg(t, 55.9, 58.75))
      : mv(C([1.5, 7.5, 13.5], [0, -10, 0], 48), C([1.0, 6.2, 11.5], [0, -14, 0], 46), seg(t, 58.75, 62.1)) },
  // 16 the town over the old mine (cutaway)
  { id: 16, a: F(62.1), b: F(68.3), light: "day", cInf: 0, cam: (t) => mv(C([CUT_X, 8, 210], [CUT_X, 4, 0], 46), C([CUT_X - 8, -22, 140], [CUT_X - 8, -38, 0], 44), seg(t, 63.2, 67.8)) },
  // 17 grandpa fitting the lights (golden), then tonight: every door still glowing red
  { id: 17, a: F(68.3), b: TOTAL, light: "golden", cInf: 0, sunAz: 40, cam: (t) => t < 71.4
      ? mv(C([9.8, 1.4, 10.2], [13.0, 2.4, 5.6], 42), C([10.4, 1.6, 9.4], [13.0, 2.5, 5.6], 38), seg(t, 68.3, 71.4))
      : mv(C([11.6, 2.1, 9.4], [13, 2.6, 5.1], 40), C([12.0, 2.3, 7.8], [13, 2.7, 5.1], 34), seg(t, 71.4, 73.3)) },
];
/** shots that change lighting mid-way: [id, from t, light] */
export const LIGHT_SWITCH: [number, number, Light][] = [[17, 71.4, "night"]];
export const lightOf = (s: ShotDef, t: number): Light => { for (const [id, t0, L] of LIGHT_SWITCH) if (s.id === id && t >= t0) return L; return s.light; };
export const XFADE: Record<number, number> = { 2: 10, 3: 10, 16: 10, 17: 10 };
export const FLASH_AT = -100;
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => {
  for (const s of SHOTS) {
    const x = XFADE[s.id];
    if (x && f >= s.a - x / 2 && f < s.a + x / 2) return [{ id: s.id - 1, alpha: 1 }, { id: s.id, alpha: (f - (s.a - x / 2) + 1) / (x + 1) }];
  }
  return [{ id: shotAt(f).id, alpha: 1 }];
};
/** impact kicks: [frame, strength] */
export const KICKS: [number, number][] = [[F(21.45), 0.05], [F(26.6), 0.03], [F(38.8), 0.06], [F(43.95), 0.08], [F(46.55), 0.05], [F(56.1), 0.14], [F(57.0), 0.12], [F(57.9), 0.1]];
export const camAt = (id: number, f: number): Cam => {
  const s = SHOTS[id - 1], t = f / FPS, u = clamp01((f - s.a) / Math.max(1, s.b - s.a));
  let c = s.cam(t, u);
  for (const [kf, a] of KICKS) {
    const n = f - kf;
    if (n >= 0 && n < 8 && kf >= s.a && kf < s.b) { const m = a * (1 - n / 8) * (n % 2 ? -1 : 1); c = { ...c, pos: [c.pos[0] + m * 0.6, c.pos[1] + m, c.pos[2]], roll: c.roll + m * 0.08 }; }
  }
  // the house shaking from the green light on (inside shots): a constant low tremor that grows
  if (s.inside && t > 17.5 && t < 46.4) { const k = 0.004 + 0.012 * clamp01((t - 17.5) / 25); c = { ...c, pos: [c.pos[0] + k * Math.sin(t * 53), c.pos[1] + k * Math.sin(t * 61 + 1), c.pos[2]] }; }
  return c;
};
export const dofAt = (f: number) => ({ cInf: shotAt(f).cInf, focus: undefined as undefined | ((f: number) => V3) });
