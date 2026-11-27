// "The Syrup Tsunami": the 1919 Boston molasses flood. Timeline of shots on the voice clock (lines.json, Liam v4),
// the flood physics (tau = seconds since the tank burst) and the camera per shot (smootherstep glides + slow push-ins).
export const FPS = 30;
export const TOTAL = 1692; // 56.4 s
export type V3 = [number, number, number];
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const glide = (u: number) => { const x = clamp01(u); return x * x * x * (x * (6 * x - 15) + 10); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 3;

// ---------------- the place ----------------
export const TANK: V3 = [-12, 0, -32]; // centre of the tank base
export const TANK_R = 13.7, TANK_H = 15.2; // 90 ft wide, 50 ft tall
export const STREET0 = -14; // the street starts here and runs toward +z
export const RAIL_X = 3.5, RAIL_Y = 5.4; // elevated railway along the street
/** direction from the tank centre to the street mouth, and the tank wall point facing the street */
const dl = Math.hypot(0 - TANK[0], STREET0 - TANK[2]);
export const TDIR: [number, number] = [(0 - TANK[0]) / dl, (STREET0 - TANK[2]) / dl];
export const TFRONT: V3 = [TANK[0] + TDIR[0] * TANK_R, 0, TANK[2] + TDIR[1] * TANK_R];
const onT = (k: number, y: number, side = 0): V3 => [TFRONT[0] + TDIR[0] * k - TDIR[1] * side, y, TFRONT[2] + TDIR[1] * k + TDIR[0] * side];

// ---------------- flood physics ----------------
export const BURST_T = 22.85; // "the tank BURST open"
/** path distance from the tank wall: radial on the plaza, along the street once inside it */
export const pathS = (x: number, z: number) => {
  if (z > STREET0) return Math.abs(x) < 7.6 ? z - STREET0 + (dl - TANK_R) : -1;
  return Math.max(0, Math.hypot(x - TANK[0], z - TANK[2]) - TANK_R);
};
export const frontZ = (tau: number) => frontS(tau) - (dl - TANK_R) + STREET0;
export const frontS = (tau: number) => (tau <= 0 ? 0 : 62 * (1 - Math.exp(-tau / 3.6)) + 1.9 * tau);
/** molasses height at (x, z) tau seconds after the burst */
export const flood = (x: number, z: number, tau: number) => {
  if (tau <= 0) return 0;
  const s0 = pathS(x, z);
  if (s0 < 0) return 0;
  const s = s0 + (z > STREET0 ? 0.045 * x * x : 0);
  const r = Math.hypot(x - TANK[0], z - TANK[2]);
  const F = frontS(tau), u = F - s;
  const pool = 0.95 * smooth(tau / 1.5);
  const col = r < TANK_R ? TANK_H * Math.exp(-tau / 0.55) : 0; // the column collapsing out of the tank
  if (u < 0) return col;
  const Hf = 7.6 * Math.exp(-tau / 12) + 0.25, Lf = 3.5 + tau * 0.7;
  const front = Hf * (1 + 0.16 * Math.sin(x * 0.85 + tau * 2.4) * Math.exp(-tau / 10)) * Math.exp(-((u / Lf) ** 2)) * smooth(u / 0.9);
  const rip = 0.08 * Math.sin(x * 1.3 + tau * 2) * Math.sin(z * 0.9 - tau * 3) * Math.exp(-tau / 12);
  return Math.max(col, front + pool * smooth(u / 3) + rip);
};

// ---------------- shots ----------------
export type Light = "day" | "golden";
export type Cam = { pos: V3; look: V3; fov: number; roll: number };
export type ShotDef = {
  id: number; a: number; b: number; light: Light; tau: (t: number) => number; cInf: number;
  keys: { t: number; pos: V3; look: V3; fov?: number; roll?: number; dur?: number }[]; push?: number; sunAz?: number; sunEl?: number;
  brown?: boolean; paint?: (t: number) => number; panels?: (t: number) => number; clean?: boolean;
};
const F = (s: number) => Math.round(s * FPS);
const before = () => -99;
const P = TFRONT;
export const SHOTS: ShotDef[] = [
  // 1 HOOK: the brown wave towering over the street, low camera, people looking up
  { id: 1, a: 0, b: F(3.15), light: "day", tau: (t) => 3.1 + t * 0.22, cInf: 5, push: 0.002,
    keys: [{ t: 0, pos: [-3.2, 2.4, 39], look: [0.8, 3.6, 18], fov: 46 }, { t: 3.1, pos: [-2.9, 2.2, 37.5], look: [0.8, 3.4, 18], fov: 44 }] },
  // 2 "made of syrup": a man waist-deep licks his finger
  { id: 2, a: F(3.15), b: F(5.0), light: "day", tau: () => 40, cInf: 13, push: 0.003,
    keys: [{ t: 3.15, pos: [0.5, 1.85, 34.6], look: [1.6, 1.5, 30.2], fov: 34 }] },
  // 3 establishing: the harbour, the plaza, the giant tank; crane up "five stories tall"
  { id: 3, a: F(5.0), b: F(10.6), light: "day", tau: before, cInf: 0, push: 0.0015, sunAz: 110,
    keys: [{ t: 5.0, pos: [0.6, 3.4, 30], look: [-8, 6, -30], fov: 42 }, { t: 7.5, dur: 1.4, pos: [10, 9, 12], look: [-10, 10.5, -32], fov: 44 }] },
  // 4 leaks + painted brown + the boss whistling
  { id: 4, a: F(10.6), b: F(15.27), light: "day", tau: before, cInf: 9, push: 0.002, paint: (t) => smooth((t - 12.1) / 1.4), sunAz: 150,
    keys: [{ t: 10.6, pos: [7.0, 8.6, -2], look: onT(0, 5.5, 0), fov: 44 }, { t: 13.7, dur: 0.8, pos: onT(9.5, 1.9, 1.2), look: onT(2.6, 1.6, 0), fov: 38 }] },
  // 5 neighbours with buckets under the drips
  { id: 5, a: F(15.27), b: F(19.2), light: "day", tau: before, cInf: 11, push: 0.003, paint: () => 1, sunAz: 150,
    keys: [{ t: 15.27, pos: onT(7.0, 1.8, 0.3), look: onT(1.0, 1.4, 0.3), fov: 40 }] },
  // 6 warm afternoon, creaks, the tank bursts
  { id: 6, a: F(19.2), b: F(23.9), light: "day", tau: (t) => t - BURST_T, cInf: 0, push: 0.002, paint: () => 1, sunEl: 58,
    panels: (t) => clamp01((t - BURST_T) / 1.0),
    sunAz: 140, keys: [{ t: 19.2, pos: [3.0, 7.0, 30], look: onT(0, 6.0, 0), fov: 40 }, { t: 22.3, dur: 0.5, pos: [2.6, 6.4, 26], look: onT(0, 5.0, 0), fov: 46 }] },
  // 7 the wave races down the street toward us
  { id: 7, a: F(23.9), b: F(28.7), light: "day", tau: (t) => 0.9 + (t - 23.9) * 0.95, cInf: 0, push: 0.0, panels: () => 1,
    keys: [{ t: 23.9, pos: [-2.2, 2.2, 36], look: [0, 3.5, 4], fov: 44 }, { t: 24.2, dur: 4.4, pos: [-1.8, 2.6, 47], look: [0, 3.2, 14], fov: 44 }] },
  // 8 it smashes into the elevated railway, a house is shoved off its foundation
  { id: 8, a: F(28.7), b: F(32.93), light: "day", tau: (t) => 2.4 + (t - 28.7) * 0.55, cInf: 0, push: 0.002, panels: () => 1,
    keys: [{ t: 28.7, pos: [-2.5, 8.5, 44], look: [2.5, 4.5, -10], fov: 44 }, { t: 30.4, dur: 0.7, pos: [-2.0, 8.0, 42], look: [-8, 3.5, 19], fov: 44 }] },
  // 9 people stuck in it
  { id: 9, a: F(32.93), b: F(36.27), light: "day", tau: () => 45, cInf: 12, push: 0.0025, panels: () => 1,
    keys: [{ t: 32.93, pos: [1.2, 2.7, 33.8], look: [0.2, 1.3, 24.0], fov: 40 }] },
  // 10 evening: it gets thicker as it cools, the street turns to glue
  { id: 10, a: F(36.27), b: F(42.6), light: "golden", tau: () => 400, cInf: 6, push: 0.0018, panels: () => 1, sunAz: 0, sunEl: 13,
    keys: [{ t: 36.27, pos: [0.9, 2.4, 33.5], look: [0.0, 1.5, 25], fov: 40 }, { t: 39.0, dur: 1.2, pos: [-2.5, 6.5, 42], look: [0, 1.0, 20], fov: 44 }] },
  // 11 the harbour stayed brown until summer
  { id: 11, a: F(42.6), b: F(46.67), light: "golden", tau: () => 500, cInf: 0, push: 0.0015, panels: () => 1, brown: true,
    keys: [{ t: 42.6, pos: [17, 3.2, -41], look: [-8, -0.8, -72], fov: 46 }] },
  // 12 the company blamed anarchists ... paid up
  { id: 12, a: F(46.67), b: F(50.67), light: "day", tau: () => 900, cInf: 11, push: 0.0028, panels: () => 1, clean: true,
    keys: [{ t: 46.67, pos: onT(9.0, 1.75, -1.2), look: onT(4.6, 1.55, 0.6), fov: 36 }] },
  // 13 decades later, hot summer days: the neighbourhood still smells sweet
  { id: 13, a: F(50.67), b: TOTAL, light: "day", tau: () => 1e4, cInf: 9, push: 0.0022, clean: true, sunEl: 62,
    keys: [{ t: 50.67, pos: [2.2, 1.7, 33.5], look: [0.4, 1.55, 28.6], fov: 38 }, { t: 53.0, dur: 2.2, pos: [1.6, 2.5, 36.2], look: [0.4, 2.1, 28.6], fov: 40 }] },
];
export const XFADE: Record<number, number> = { 3: 6, 10: 10, 11: 10, 12: 8, 13: 10 };
export const FLASH_AT = F(3.15);
export const KICKS: [number, number][] = [[F(BURST_T), 0.35], [F(29.1), 0.25], [F(30.85), 0.18]];

export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => {
  for (const s of SHOTS) {
    const x = XFADE[s.id];
    if (x && f >= s.a - x / 2 && f < s.a + x / 2) return [{ id: s.id - 1, alpha: 1 }, { id: s.id, alpha: (f - (s.a - x / 2) + 1) / (x + 1) }];
  }
  return [{ id: shotAt(f).id, alpha: 1 }];
};

const lerp3 = (a: V3, b: V3, k: number): V3 => [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k];
export const camAt = (id: number, f: number): Cam => {
  const s = SHOTS[id - 1], t = f / FPS, K = s.keys;
  let c: Cam = { pos: K[0].pos, look: K[0].look, fov: K[0].fov ?? 40, roll: K[0].roll ?? 0 };
  for (let i = 1; i < K.length; i++) {
    const k = K[i];
    if (t < k.t) break;
    const u = glide((t - k.t) / (k.dur ?? 0.8));
    c = { pos: lerp3(c.pos, k.pos, u), look: lerp3(c.look, k.look, u), fov: c.fov + ((k.fov ?? c.fov) - c.fov) * u, roll: c.roll + ((k.roll ?? 0) - c.roll) * u };
  }
  // continuous push-in toward the look point (every hold creeps)
  const pk = Math.min(0.35, (s.push ?? 0) * Math.max(0, f - s.a));
  c = { ...c, pos: lerp3(c.pos, c.look, pk) };
  // impact kicks: sign-flipping shake, decaying over 7 frames
  for (const [kf, a] of KICKS) {
    const n = f - kf;
    if (n >= 0 && n < 7 && kf >= s.a && kf < s.b) {
      const m = a * (1 - n / 7) * (n % 2 ? -1 : 1);
      c = { ...c, pos: [c.pos[0] + m * 0.6, c.pos[1] + m, c.pos[2]], roll: c.roll + m * 0.08 };
    }
  }
  return c;
};
export const dofAt = (f: number) => ({ cInf: shotAt(f).cInf, focus: undefined as undefined | ((f: number) => V3) });

// ---------------- retiming to the narration (Brian v4): new clock -> the story clock the shots were built on ----------------
const NEW_T = [0, 0.15, 3.75, 5.44, 11.37, 16.02, 19.33, 22.81, 26.61, 31.09, 36.81, 45.48, 49.69, 54.43, 60.675];
const OLD_T = [0, 0.15, 3.26, 5.17, 10.79, 15.45, 19.40, 24.05, 28.86, 33.09, 36.41, 42.78, 46.86, 50.86, 56.4];
export const NEW_TOTAL = Math.round(60.675 * FPS);
export const warpF = (f: number) => {
  const t = f / FPS;
  for (let i = 1; i < NEW_T.length; i++) if (t <= NEW_T[i]) return (OLD_T[i - 1] + ((t - NEW_T[i - 1]) * (OLD_T[i] - OLD_T[i - 1])) / (NEW_T[i] - NEW_T[i - 1])) * FPS;
  return OLD_T[OLD_T.length - 1] * FPS;
};
