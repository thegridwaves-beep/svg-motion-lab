// "The Light Next Door". Voice clock (Ethan v4, lines.json, 65.2 s), the Morse flash schedule the
// world is lit from, and one camera per shot. Two houses face each other across a garden; the kid's bedroom window
// (house A, +x wall) looks straight into Mr. Hale's window (house B, -x wall), 6 m away.
import type { LName } from "./lights";
export const FPS = 30;
export const TOTAL = 1957; // 65.21 s
export const NEW_TOTAL = TOTAL;
export const warpF = (f: number) => f;
export type V3 = [number, number, number];
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const glide = (u: number) => { const x = clamp01(u); return x * x * x * (x * (6 * x - 15) + 10); };
const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
const lerp3 = (a: V3, b: V3, k: number): V3 => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)];
export const ramp = (t: number, a: number, b: number) => smooth((t - a) / (b - a));

// ---------------- the set ----------------
export const FL1 = 3.2; // bedroom / Hale's room floor
export const CEIL = 6.2; // bedroom ceiling underside
export const ATTIC = 6.4; // attic floor
export const WIN_Z = -2.5, WIN_Y = 4.85; // window centres (both houses)
export const A_X = 4.5, B_X = 10.5; // facing walls
export const BED: V3 = [1.3, FL1 + 0.55, -3.9];
export const HATCH: V3 = [1.4, CEIL, -3.9];
export const DESK: V3 = [3.15, FL1 + 0.76, -0.45];
export const HALE_WIN: V3 = [B_X, WIN_Y, WIN_Z];
export const KID_WIN: V3 = [A_X, WIN_Y, WIN_Z];

// ---------------- Morse ----------------
const CODE: Record<string, string> = { R: ".-.", U: "..-", N: "-.", O: "---", T: "-", A: ".-", L: ".-..", E: ".", W: ".--", H: "....", " ": " " };
/** on/off intervals (in units) for a message; dot 1, dash 3, gap 1, letter gap 3, word gap 7 */
const morse = (msg: string): [number, number][] => {
  const out: [number, number][] = []; let u = 0;
  for (const w of msg.split(" ")) {
    for (const ch of w) { for (const s of CODE[ch]) { const d = s === "." ? 1 : 3; out.push([u, u + d]); u += d + 1; } u += 2; }
    u += 4;
  }
  return out;
};
const RUN = morse("RUN"), NA = morse("NOT ALONE"), WHO = morse("WHO");
const span = (m: [number, number][]) => m[m.length - 1][1];
const onIn = (m: [number, number][], x: number) => m.some(([a, b]) => x >= a && x < b);
/** Mr. Hale's lamp: 1 = on */
export const haleFlash = (t: number): number => {
  if (t < 11.7) { const unit = 0.15, cyc = span(RUN) + 7, x = ((t - 0.4) / unit) % cyc; return t > 0.4 && onIn(RUN, x) ? 1 : 0; }
  if (t >= 31.6 && t < 35.7) { const unit = (35.6 - 31.6) / span(NA); return onIn(NA, (t - 31.6) / unit) ? 1 : 0; }
  if (t >= 39.25 && t < 40.85) { const k = Math.floor((t - 39.25) / 0.066); const hv = Math.abs(Math.sin(k * 12.9898) * 43758.5) % 1; return hv > 0.35 ? 1 : 0; }
  if (t >= 63.4 && t < 63.75) return 1;
  if (t >= 64.05 && t < 64.4) return 1;
  return 0;
};
/** the kid's torch, flashing WHO back */
export const torchFlash = (t: number): number => {
  if (t >= 36.55 && t < 39.0) { const unit = (38.95 - 36.55) / span(WHO); return onIn(WHO, (t - 36.55) / unit) ? 1 : 0; }
  return 0;
};
/** the dots and dashes seen so far in the current repeat of RUN (for the floating symbols in shot 2) */
export const runSoFar = (t: number) => {
  const unit = 0.15, cyc = span(RUN) + 7, x = ((t - 0.4) / unit) % cyc; let s = "";
  const sym = ".-. ..- -.".replace(/ /g, ""); let k = 0;
  for (const [a, b] of RUN) { if (x >= a) s += sym[k]; k++; void b; }
  return s;
};

// ---------------- shots ----------------
export type Light = LName;
export type Cam = { pos: V3; look: V3; fov: number; roll: number };
export type ShotDef = { id: number; a: number; b: number; light: Light; cInf: number; cam: (t: number, u: number) => Cam; sunAz?: number; sunEl?: number; fog?: number };
const F = (s: number) => Math.round(s * FPS);
const C = (pos: V3, look: V3, fov = 40, roll = 0): Cam => ({ pos, look, fov, roll });
const mv = (a: Cam, b: Cam, k: number): Cam => ({ pos: lerp3(a.pos, b.pos, k), look: lerp3(a.look, b.look, k), fov: lerp(a.fov, b.fov, k), roll: lerp(a.roll, b.roll, k) });
const Y = FL1;
export const SHOTS: ShotDef[] = [
  // 1 hook: 3 AM, the kid sitting up in bed, the window behind him flashing
  { id: 1, a: 0, b: F(5.75), light: "room", cInf: 10, cam: (_t, u) => mv(C([3.55, Y + 1.35, -2.6], [1.4, Y + 1.05, -3.75], 50), C([3.15, Y + 1.25, -2.95], [1.4, Y + 1.0, -3.75], 44), glide(u)) },
  // 2 outside: the gap between the houses, his window flashing into mine
  { id: 2, a: F(5.75), b: F(11.7), light: "night", cInf: 0, cam: (_t, u) => mv(C([7.5, 3.0, 9.5], [7.5, 4.9, -2.5], 58), C([7.5, 3.6, 7.2], [7.5, 4.9, -2.5], 56), glide(u)) },
  // 3 mum in the doorway, half asleep
  { id: 3, a: F(11.7), b: F(15.05), light: "room", cInf: 10, cam: (_t, u) => mv(C([3.7, Y + 1.5, -3.0], [0.2, Y + 1.25, -0.8], 48), C([3.5, Y + 1.45, -2.7], [0.2, Y + 1.25, -0.8], 46), glide(u)) },
  // 4 at the desk with the torch, writing it down
  { id: 4, a: F(15.05), b: F(20.6), light: "room", cInf: 8, cam: (_t, u) => mv(C([3.0, Y + 1.45, -0.2], [3.1, Y + 0.95, -1.5], 52), C([3.05, Y + 1.4, -0.22], [3.1, Y + 0.95, -1.5], 46), glide(u)) },
  // 5 the notebook: the first word
  { id: 5, a: F(20.6), b: F(23.85), light: "room", cInf: 6, cam: (_t, u) => mv(C([3.15, Y + 2.05, -1.0], [3.15, Y + 0.79, -0.5], 44), C([3.15, Y + 1.85, -0.9], [3.15, Y + 0.79, -0.5], 40), glide(u)) },
  // 6 next morning: Mr. Hale in his garden, staring at our house
  { id: 6, a: F(23.85), b: F(29.3), light: "day", cInf: 12, sunAz: 120, sunEl: 30, cam: (_t, u) => mv(C([5.6, 1.8, 6.2], [9.4, 1.3, 1.0], 40), C([6.2, 1.75, 5.4], [9.4, 1.3, 1.0], 36), glide(u)) },
  // 7 he points up: low angle up our wall to the attic vent
  { id: 7, a: F(29.3), b: F(31.45), light: "day", cInf: 0, sunAz: 150, sunEl: 30, cam: (_t, u) => mv(C([9.7, 1.3, 6.0], [6.5, 3.0, 0.5], 46), C([9.6, 1.2, 5.9], [4.5, 7.9, 0.0], 42), glide(u)) },
  // 8 that night: my face in my window, his light flashing at me
  { id: 8, a: F(31.45), b: F(35.85), light: "night", cInf: 8, cam: (_t, u) => mv(C([9.4, 4.85, -2.3], [4.0, 4.75, -2.5], 38), C([8.2, 4.8, -2.4], [4.0, 4.75, -2.5], 34), glide(u)) },
  // 9 I flash back with my torch
  { id: 9, a: F(35.85), b: F(39.2), light: "room", cInf: 10, cam: (_t, u) => mv(C([1.6, Y + 1.5, -0.6], [4.2, Y + 1.5, -2.6], 48), C([1.9, Y + 1.5, -0.8], [4.2, Y + 1.5, -2.6], 46), glide(u)) },
  // 10 outside: his light goes crazy, then stops
  { id: 10, a: F(39.2), b: F(42.2), light: "night", cInf: 0, cam: (_t, u) => mv(C([7.5, 3.4, 8.2], [7.5, 4.9, -2.5], 56), C([7.5, 3.9, 6.6], [7.5, 4.9, -2.5], 54), glide(u)) },
  // 11 in bed, looking up: the ceiling creaks
  { id: 11, a: F(42.2), b: F(45.85), light: "room", cInf: 0, cam: (_t, u) => mv(C([3.2, Y + 0.6, -2.2], [1.5, Y + 2.0, -3.8], 58), C([3.0, Y + 0.65, -2.35], [1.5, Y + 2.2, -3.85], 52), glide(u)) },
  // 12 police out front
  { id: 12, a: F(45.85), b: F(48.4), light: "night", cInf: 0, cam: (_t, u) => mv(C([-3.6, 1.8, 19.0], [1.0, 1.8, 7.5], 46), C([-3.2, 1.8, 18.2], [0.9, 1.8, 7.2], 44), glide(u)) },
  // 13 the attic: a man has been living up there
  { id: 13, a: F(48.4), b: F(53.0), light: "night", cInf: 8, cam: (t) => mv(C([-2.8, ATTIC + 1.5, 0.8], [0.4, ATTIC + 0.9, -2.6], 46), C([-1.6, ATTIC + 1.35, 0.0], [0.4, ATTIC + 0.85, -2.6], 42), glide((t - 48.4) / 4.6)) },
  // 14 at night he'd sneak down to our fridge
  { id: 14, a: F(53.0), b: F(55.95), light: "night", cInf: 8, cam: (_t, u) => mv(C([1.0, 1.7, -3.6], [3.3, 1.2, -0.6], 46), C([1.3, 1.65, -3.2], [3.3, 1.2, -0.6], 42), glide(u)) },
  // 15 mum thought it was me
  { id: 15, a: F(55.95), b: F(57.6), light: "day", cInf: 10, sunAz: 100, cam: (_t, u) => mv(C([0.8, 1.65, -3.4], [2.6, 1.3, -1.0], 44), C([0.9, 1.6, -3.1], [2.6, 1.3, -1.0], 42), glide(u)) },
  // 16 Mr. Hale at his window, waving; the lamp blinks twice
  { id: 16, a: F(57.6), b: TOTAL, light: "golden", cInf: 0, sunAz: 30, cam: (_t, u) => mv(C([7.6, 3.6, 0.8], [11.0, 4.45, -2.7], 40), C([8.2, 3.9, 0.0], [11.0, 4.5, -2.75], 36), glide(u)) },
];
export const XFADE: Record<number, number> = { 6: 10, 16: 10 };
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
export const KICKS: [number, number][] = [[F(22.9), 0.05], [F(43.85), 0.06], [F(48.45), 0.05]];
export const camAt = (id: number, f: number): Cam => {
  const s = SHOTS[id - 1], t = f / FPS, u = clamp01((f - s.a) / Math.max(1, s.b - s.a));
  let c = s.cam(t, u);
  for (const [kf, a] of KICKS) {
    const n = f - kf;
    if (n >= 0 && n < 7 && kf >= s.a && kf < s.b) { const m = a * (1 - n / 7) * (n % 2 ? -1 : 1); c = { ...c, pos: [c.pos[0] + m * 0.6, c.pos[1] + m, c.pos[2]], roll: c.roll + m * 0.06 }; }
  }
  return c;
};
export const dofAt = (f: number) => ({ cInf: shotAt(f).cInf, focus: undefined as undefined | ((f: number) => V3) });
