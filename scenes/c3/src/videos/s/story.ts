// "The Lake That Vanished": Lake Peigneur, Louisiana, 20 Nov 1980. Voice clock (Brian v4, lines.json), the disaster
// physics the world is posed from (crater, water level, whirlpool), the set positions, and one camera per shot.
export const FPS = 30;
export const TOTAL = 2113; // 70.44 s
export const NEW_TOTAL = TOTAL;
export const warpF = (f: number) => f;
export type V3 = [number, number, number];
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const glide = (u: number) => { const x = clamp01(u); return x * x * x * (x * (6 * x - 15) + 10); };
const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
const lerp3 = (a: V3, b: V3, k: number): V3 => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)];
export const ramp = (t: number, a: number, b: number) => smooth((t - a) / (b - a));

// ---------------- the place (metres; full lake surface y = 0, shore ground y = 1, whirlpool centred on the origin) ----------------
export const LAKE_R = 230;
export const GROUND_Y = 1.0;
export const RIG: V3 = [7, 0, 5]; // drilling platform, deck top 2.2 above the water
export const DECK = 2.2;
// barges [x, z, yaw]; 0 is moored alongside the rig (the crew's escape route)
export const BARGES: [number, number, number][] = [
  [7, 16.5, 0], [-34, 6, 0.4], [-30, -14, 1.2], [-6, -32, 0.1], [26, -22, 2.0], [38, 8, 1.5], [-46, 22, 0.8], [22, 40, 0.3], [-4, 54, 2.6], [46, -40, 1.0], [-50, -36, 0.6],
];
export const BARGE_DECK = 1.6;
export const TUG: [number, number, number] = [36, 30, 2.2];
export const FISH: V3 = [-12, 0, 26]; // the fisherman's rowboat
export const ISLAND: V3 = [66, 0, -38]; // wooded bank of Jefferson Island that slides into the hole
export const ISLAND_R = 20;
export const GAUGE: V3 = [-31, 0, 50]; // depth post in the opening shot
export const MINE_Y = -420; // salt mine set floor
export const CAGE: V3 = [17, 0, -5.5]; // the one elevator (mine coordinates, add MINE_Y)
export const CUT_X = 3000; // the cross-section diagram set
export const HEAD: V3 = [190, GROUND_Y, 170]; // mine headframe on the east shore
export const CANAL_W = 14; // canal along -x from the west shore, z in [-7, 7]

// ---------------- disaster physics (story seconds) ----------------
/** the hook is a flash-forward to the moment the rig goes under; everything else runs on the voice clock */
export const storyT = (id: number, t: number) => (id === 1 ? 29.0 + 2.2 * clamp01(t / 6.45) : t);
export const spinAt = (t: number) => ramp(t, 22.6, 28);
export const craterAt = (t: number) => 44 * ramp(t, 22.6, 30) + 26 * ramp(t, 30, 37) + 150 * ramp(t, 38, 50);
export const levelAt = (t: number) => -4 * ramp(t, 28, 36) - 46 * ramp(t, 36, 52);
const OMEGA: number[] = []; // integrated swirl angle, 0.1 s steps
for (let i = 0, a = 0; i <= 800; i++) { OMEGA.push(a); a += 0.1 * 1.9 * spinAt(i * 0.1); }
export const swirlAngle = (t: number) => { const k = clamp01(t / 80) * 800, i = Math.floor(k); return lerp(OMEGA[i], OMEGA[Math.min(800, i + 1)], k - i); };

export type Lake = {
  t: number; spin: number; level: number; cr: number; Rf: number; Df: number; drill: number; tilt: number; rigSink: number; tug: number;
  barge: (k: number) => number; trees: number; slump: number; fall: number; refilled: boolean; pop: (k: number) => number; swirl: number;
};
export const lakeAt = (id: number, t0: number): Lake => {
  const t = storyT(id, t0), refilled = id === 15;
  const spin = refilled ? 0 : spinAt(t), cr = refilled ? 0 : craterAt(t);
  return {
    t, spin, level: refilled ? 0 : levelAt(t), cr, Rf: 0.18 * cr + 3, Df: 10 + 0.3 * cr,
    drill: t < 15.5 ? 1 : 0, tilt: ramp(t, 18.4, 21.0) * 1.25, rigSink: refilled ? 1 : ramp(t, 28.7, 30.2), tug: refilled ? 1 : ramp(t, 30.3, 31.3),
    barge: (k) => (refilled ? 1 : ramp(t, 31.2 + k * 0.22, 32.3 + k * 0.22)),
    trees: refilled ? 1 : ramp(t, 33.8, 35.2), slump: refilled ? 1 : ramp(t, 34.9, 37.4), fall: refilled ? 0 : ramp(t, 49.0, 50.6),
    refilled, pop: (k) => (refilled && k < 9 ? clamp01((t - (65.0 + k * 0.42)) / 1.0) : -1), swirl: swirlAngle(t),
  };
};
/** water surface height at radius r from the whirlpool centre */
export const surfY = (L: Lake, r: number) => L.level - L.spin * L.Df / (1 + (r / L.Rf) ** 2);
/** lake bed: shallow 10 ft bowl, then the crater collapsing into the mine */
export const bedY = (L: Lake, r: number, th: number) => {
  let y = r >= LAKE_R ? GROUND_Y - 0.02 : GROUND_Y - 4.2 * (1 - (r / LAKE_R) ** 6);
  if (L.cr > 1) {
    const dth = Math.atan2(Math.sin(th - Math.PI), Math.cos(th - Math.PI)), ce = L.cr * (1 + 0.05 * Math.sin(3 * th + 1) + 0.035 * Math.sin(7 * th + 2) + 0.12 * Math.exp(-((dth / 0.12) ** 2)));
    if (r < ce) { const w = smooth((ce - r) / (0.12 * ce + 4)); y = lerp(y, -72, w); }
    y -= 25 * Math.exp(-((r / (0.1 * ce + 2)) ** 2)) * clamp01(L.cr / 30);
  }
  return y;
};

// ---------------- shots ----------------
export type Light = "day" | "golden";
export type Cam = { pos: V3; look: V3; fov: number; roll: number };
export type ShotDef = { id: number; a: number; b: number; light: Light; cInf: number; cam: (t: number, u: number) => Cam; sunAz?: number; sunEl?: number; fog?: [string, number, number] | number; mine?: boolean };
const F = (s: number) => Math.round(s * FPS);
const C = (pos: V3, look: V3, fov = 40, roll = 0): Cam => ({ pos, look, fov, roll });
const mv = (a: Cam, b: Cam, k: number): Cam => ({ pos: lerp3(a.pos, b.pos, k), look: lerp3(a.look, b.look, k), fov: lerp(a.fov, b.fov, k), roll: lerp(a.roll, b.roll, k) });
const orbit = (r: number, ang: number, y: number, look: V3, fov = 40): Cam => C([r * Math.sin(ang), y, r * Math.cos(ang)], look, fov);
const M = MINE_Y, H = HEAD;
export const SHOTS: ShotDef[] = [
  // 1 hook: from high above, the whirlpool eating the rig, the lake sinking
  { id: 1, a: 0, b: F(6.45), light: "day", cInf: 0, sunAz: 120, fog: 3, cam: (_t, u) => orbit(118 - 22 * glide(u), 0.55 + 0.35 * u, 74 - 16 * glide(u), [2, -6, 2], 46) },
  // 2 a normal Thursday: low over the calm lake, depth post in front, the rig out in the middle
  { id: 2, a: F(6.45), b: F(10.4), light: "day", cInf: 0, fog: 1.6, cam: (_t, u) => mv(C([-40, 2.6, 60], [7, 7, 5], 40), C([-35, 3.1, 53], [7, 7.5, 5], 38), glide(u)) },
  // 3 the crew drilling on deck; cut at "and a fisherman" to his rowboat with the rig behind
  { id: 3, a: F(10.4), b: F(15.15), light: "day", cInf: 12, cam: (t) => t < 13.35
      ? mv(C([7.8, 4.4, 19.5], [7.4, 3.3, 7], 40), C([7.6, 4.2, 18.0], [7.4, 3.3, 7], 39), glide((t - 10.4) / 2.95))
      : mv(C([-19, 1.9, 35], [-9, 2.2, 20], 40), C([-18, 1.7, 33.5], [-9, 2.0, 20], 39), glide((t - 13.35) / 1.8)) },
  // 4 the drill sticks: close on deck, the crew straining
  { id: 4, a: F(15.15), b: F(18.33), light: "day", cInf: 10, cam: (_t, u) => mv(C([7.7, 4.1, 16.4], [7.5, 3.4, 7.5], 38), C([7.6, 3.9, 15.2], [7.5, 3.4, 7.5], 36), glide(u)) },
  // 5 the whole rig starts to tilt: wide, low, dutch
  { id: 5, a: F(18.33), b: F(20.5), light: "day", cInf: 0, cam: (_t, u) => mv(C([36, 6, 46], [7, 8, 5], 40, 0), C([34, 5.5, 44], [7, 7.5, 5], 42, -0.03), glide(u)) },
  // 6 the men jump onto the barge and run; behind them the water starts to spin
  { id: 6, a: F(20.5), b: F(24.58), light: "day", cInf: 0, cam: (_t, u) => mv(C([8, 7.5, 29], [9, 2.0, 11], 42), C([15, 7.8, 30], [15, 1.8, 10], 44), glide(u)) },
  // 7 top down: the whirlpool opens and keeps growing
  { id: 7, a: F(24.58), b: F(28.65), light: "day", cInf: 0, fog: 3, cam: (_t, u) => C([0.01, 150 - 40 * glide(u), 0.02], [0, -10, 0], 52, u * 0.9) },
  // 8 it swallows the rig, the tug, the barges: tracking round the rim
  { id: 8, a: F(28.65), b: F(33.72), light: "day", cInf: 0, fog: 2.2, cam: (_t, u) => orbit(74, 2.2 + 0.45 * u, 27 - 6 * u, [0, -8, 0], 46) },
  // 9 trees slide in, then the land drops
  { id: 9, a: F(33.72), b: F(38.35), light: "day", cInf: 0, fog: 2, cam: (_t, u) => mv(C([10, 9, 20], [60, -2, -32], 42), C([16, 7, 14], [60, -10, -32], 44), glide(u)) },
  // 10 far below: the salt mine, miners working
  { id: 10, a: F(38.35), b: F(43.25), light: "day", cInf: 12, sunEl: 80, mine: true, cam: (_t, u) => mv(C([2.0, M + 3.2, 13], [0, M + 1.6, -6], 42), C([1.4, M + 2.7, 9.5], [0, M + 1.5, -6], 40), glide(u)) },
  // 11 the electrician sees the water coming; hard cut at "they have one way out" to the run for the cage
  { id: 11, a: F(43.25), b: F(48.38), light: "day", cInf: 0, sunEl: 80, mine: true, cam: (t) => t < 46.0
      ? mv(C([1.5, M + 2.0, 12], [0.5, M + 1.9, -30], 42), C([1.8, M + 1.9, 10.5], [0.8, M + 1.9, -30], 40), glide((t - 43.25) / 2.75))
      : mv(C([7.5, M + 2.5, 7.0], [13, M + 1.7, -2.5], 46), C([9.0, M + 2.4, 6.8], [15.5, M + 1.7, -3.5], 44), glide((t - 46.0) / 2.38)) },
  // 12 up top: the canal runs backwards into a giant waterfall
  { id: 12, a: F(48.38), b: F(55.08), light: "day", cInf: 0, sunAz: 150, sunEl: 40, fog: 1.8, cam: (t) => mv(C([-160, 14, 58], [-212, -20, 0], 46), C([-168, 8, 48], [-212, -24, 0], 46), glide((t - 49.2) / 5)) },
  // 13 the reveal: cutaway through the lake, the drill punched into the mine roof
  { id: 13, a: F(55.08), b: F(59.62), light: "day", cInf: 0, fog: ["#b8d0ec", 2000, 4000], cam: (t) => mv(C([CUT_X, 30, 250], [CUT_X, 22, 0], 46), C([CUT_X - 7, -28, 150], [CUT_X - 7, -52, 0], 44), glide((t - 56.4) / 2.6)) },
  // 14 every miner and driller got out alive
  { id: 14, a: F(59.62), b: F(63.96), light: "golden", cInf: 12, sunAz: 30, cam: (_t, u) => mv(C([H[0] - 2, H[1] + 2.0, H[2] + 15], [H[0], H[1] + 1.4, H[2] + 2.5], 40), C([H[0] - 1.2, H[1] + 1.7, H[2] + 12], [H[0], H[1] + 1.3, H[2] + 2.5], 38), glide(u)) },
  // 15 days later: the lake has refilled, and the barges shoot back up
  { id: 15, a: F(63.96), b: TOTAL, light: "day", cInf: 0, fog: 1.6, cam: (_t, u) => mv(C([-40, 6, 64], [0, 1.5, 0], 40), C([-35, 4.6, 56], [0, 2, 0], 38), glide(u)) },
];
export const XFADE: Record<number, number> = { 10: 8, 12: 8, 13: 8, 14: 8, 15: 10 };
export const FLASH_AT = F(6.45);
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => {
  for (const s of SHOTS) {
    const x = XFADE[s.id];
    if (x && f >= s.a - x / 2 && f < s.a + x / 2) return [{ id: s.id - 1, alpha: 1 }, { id: s.id, alpha: (f - (s.a - x / 2) + 1) / (x + 1) }];
  }
  return [{ id: shotAt(f).id, alpha: 1 }];
};
/** impact kicks: [frame, strength] */
export const KICKS: [number, number][] = [[F(15.5), 0.06], [F(18.45), 0.12], [F(28.75), 0.2], [F(34.95), 0.15], [F(57.0), 0.1]];
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
