// "The Syrup Tsunami": the 1919 Boston molasses flood. Timeline of shots on the voice clock (lines.json, Liam v4),
// the flood physics (tau = seconds since the tank burst) and the camera per shot (smootherstep glides + slow push-ins).
export const FPS = 30;
export const TOTAL = 660; // 22 s motion lab
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
  brown?: boolean; paint?: (t: number) => number; panels?: (t: number) => number; clean?: boolean; cam?: (t: number) => Cam;
};
const F = (s: number) => Math.round(s * FPS);
const before = () => -99;
const P = TFRONT;
export const SHOTS: ShotDef[] = [
  { id: 1, a: 0, b: F(5.0), light: "day", tau: before, cInf: 7, clean: true, keys: [{ t: 0, pos: [5, 1.6, 0], look: [0, 1, 0], fov: 40 }], cam: (t) => labCam(1, t) },
  { id: 2, a: F(5.0), b: F(10.0), light: "day", tau: before, cInf: 8, clean: true, keys: [{ t: 0, pos: [0, 1.6, 0], look: [0, 1, 0], fov: 38 }], cam: (t) => labCam(2, t) },
  { id: 3, a: F(10.0), b: F(14.5), light: "day", tau: before, cInf: 0, clean: true, keys: [{ t: 0, pos: [0, 1.6, 0], look: [0, 1, 0], fov: 44 }], cam: (t) => labCam(3, t) },
  { id: 4, a: F(14.5), b: F(18.5), light: "day", tau: before, cInf: 8, clean: true, keys: [{ t: 0, pos: [0, 1.6, 0], look: [0, 1, 0], fov: 40 }], cam: (t) => labCam(4, t) },
  { id: 5, a: F(18.5), b: F(22.0), light: "day", tau: before, cInf: 6, clean: true, keys: [{ t: 0, pos: [0, 1.6, 0], look: [0, 1, 0], fov: 42 }], cam: (t) => labCam(5, t) },
];
// ---------------- the motion lab: who walks where (shared by the camera and the cast) ----------------
export type Walker = { pos: (t: number) => V3; dir: (t: number) => [number, number]; mode: (t: number) => "walk" | "run" | "stand" | "jump"; amt: (t: number) => number; phase: (t: number) => number; lift: (t: number) => number; pose: (t: number) => number };
const integ = (v: (t: number) => number, t0: number, t: number) => { let d = 0; const n = Math.max(1, Math.round((t - t0) * 60)); for (let i = 0; i < n; i++) d += v(t0 + ((i + 0.5) * (t - t0)) / n) * ((t - t0) / n); return t > t0 ? d : 0; };
const WALK_CYC = 1.3, RUN_CYC = 1.81; // metres per gait cycle at full stride
const mk = (x0: number, z0: number, dx: number, dz: number, t0: number, speed: (t: number) => number, mode: (t: number) => "walk" | "run" | "stand" | "jump",
  amt: (t: number) => number = () => 1, pose: (t: number) => number = () => 0, lift: (t: number) => number = () => 0, turn?: { t: number; dx: number; dz: number }): Walker => {
  const n = Math.hypot(dx, dz); dx /= n; dz /= n;
  const dirAt = (t: number): [number, number] => { if (turn && t >= turn.t) { const m = Math.hypot(turn.dx, turn.dz); return [turn.dx / m, turn.dz / m]; } return [dx, dz]; };
  return {
    dir: dirAt, mode, amt, pose, lift,
    pos: (t) => {
      if (turn && t > turn.t) { const d0 = integ(speed, t0, turn.t), d1 = integ(speed, turn.t, t), [tx, tz] = dirAt(t); return [x0 + dx * d0 + tx * d1, lift(t), z0 + dz * d0 + tz * d1]; }
      const d = integ(speed, t0, t); return [x0 + dx * d, lift(t), z0 + dz * d];
    },
    // cadence is fixed per gait (stride shrinks with amt), so the feet stay planted through starts and stops
    phase: (t) => integ((u) => (mode(u) === "run" ? 3.8 / RUN_CYC : 1.35 / WALK_CYC) * (amt(u) > 0.02 ? 1 : 0), t0, t),
  };
};
const ramp = (t: number, a: number, b: number) => smooth((t - a) / (b - a));
export const LAB: Record<number, Walker[]> = {
  1: [mk(-1.2, -6, 0, 1, 0, (t) => 1.35 * ramp(t, 0.0, 0.5) + 2.45 * ramp(t, 2.6, 3.1), (t) => (t < 2.75 ? "walk" : "run"), (t) => ramp(t, 0, 0.5))],
  2: [mk(0.4, 8, 0, 1, 5.0, (t) => 1.3 * (1 - ramp(t, 7.5, 8.3)), (t) => (t < 8.3 ? "walk" : "stand"), (t) => 1 - ramp(t, 7.5, 8.3))],
  3: [mk(-3.6, 21, 0.8, 0.6, 10.0, () => 1.3, () => "walk"), mk(3.4, 22.5, -0.75, 0.66, 10.0, () => 1.1, () => "walk"),
      mk(-3.4, 26.5, 0.88, 0.47, 11.3, (t) => 3.2 * ramp(t, 11.3, 11.7), () => "run", (t) => ramp(t, 11.3, 11.7))],
  4: [mk(0.3, 12, 0, 1, 14.5, () => 1.15, () => "walk")],
  5: [mk(2.6, 22, -0.45, 0.89, 18.5, (t) => (t < 19.85 ? 1.3 : t < 20.75 ? 0 : 3.8 * ramp(t, 20.75, 21.1)), (t) => (t < 19.85 ? "walk" : t < 20.75 ? "jump" : "run"),
      (t) => (t < 19.85 ? 1 : t < 20.75 ? 0 : ramp(t, 20.75, 21.1)), (t) => clamp01((t - 19.9) / 0.8), (t) => (t > 20.08 && t < 20.55 ? 0.5 * Math.sin(Math.PI * (t - 20.08) / 0.47) : 0),
      { t: 20.75, dx: -0.75, dz: 0.66 })],
};
const labCam = (id: number, t: number): Cam => {
  const w = LAB[id][0].pos(t);
  if (id === 1) return { pos: [w[0] + 5.2, 1.5, w[2] - 0.6], look: [w[0], 1.05, w[2] + 0.4], fov: 40, roll: 0 };
  if (id === 2) { const z = 21.5 - 0.45 * (t - 5); return { pos: [0.9, 1.65, z], look: [0.4, 1.15, Math.min(w[2], z - 4)], fov: 38 - 2 * smooth((t - 8.3) / 1.5), roll: 0 }; }
  if (id === 3) return { pos: [0.4, 1.8, 34.5 - 0.45 * (t - 10)], look: [0, 1.0, 24], fov: 44, roll: 0 };
  if (id === 4) { const a = THREE_DEG * (8 + 92 * smooth((t - 14.6) / 3.6)), r = 4.6; return { pos: [w[0] + r * Math.sin(a), 1.7, w[2] + r * Math.cos(a)], look: [w[0], 1.05, w[2]], fov: 40, roll: 0 }; }
  return { pos: [1.4, 1.6, 30.5], look: [1.4, 1.1, 24.5], fov: 42, roll: 0 };
};
const THREE_DEG = Math.PI / 180;
export const XFADE: Record<number, number> = {};
export const FLASH_AT = -100;
export const KICKS: [number, number][] = [[F(19.88), 0.16]];

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
  if (s.cam) return s.cam(t);
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

export const NEW_TOTAL = TOTAL;
export const warpF = (f: number) => f;
