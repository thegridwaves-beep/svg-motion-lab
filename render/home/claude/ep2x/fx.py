"""Ep2 effects and shape helpers: organic blobs, billowing plumes, fire, embers, ash/snow with depth, dust puffs,
ejecta trails, water surfaces, rock silhouettes. Everything is seeded and a pure function of time."""
import math, random

TAU = 2 * math.pi


def clamp(u, a=0.0, b=1.0):
    return max(a, min(b, u))


def ramp(t, a, b):
    return clamp((t - a) / max(1e-6, b - a))


def eo(u):
    u = clamp(u); return 1 - (1 - u) ** 3


def ei(u):
    u = clamp(u); return u ** 3


def eio(u):
    u = clamp(u); return u * u * (3 - 2 * u)


def lerp(a, b, u):
    return a + (b - a) * u


def hexc(c):
    c = c.lstrip("#"); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mixc(a, b, u):
    A, B = hexc(a), hexc(b); u = clamp(u)
    return "#" + "".join(f"{int(round(x + (y - x) * u)):02X}" for x, y in zip(A, B))


def smooth_path(pts, closed=True):
    """Quadratic-midpoint smooth path through points."""
    n = len(pts)
    if n < 3:
        return ""
    mids = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    if closed:
        d = f"M{mids[-1][0]:.1f} {mids[-1][1]:.1f}"
        for i in range(n):
            d += f" Q{pts[i][0]:.1f} {pts[i][1]:.1f} {mids[i][0]:.1f} {mids[i][1]:.1f}"
        return d + "Z"
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(1, n - 1):
        d += f" Q{pts[i][0]:.1f} {pts[i][1]:.1f} {mids[i][0]:.1f} {mids[i][1]:.1f}"
    return d + f" L{pts[-1][0]:.1f} {pts[-1][1]:.1f}"


def blob_pts(cx, cy, r, seed=1, irr=0.22, n=11, t=0.0, wob=0.0, sx=1.0, sy=1.0):
    rr = random.Random(seed)
    ph = [rr.uniform(0, TAU) for _ in range(n)]
    amp = [rr.uniform(-irr, irr) for _ in range(n)]
    pts = []
    for i in range(n):
        a = TAU * i / n + rr.uniform(-0.15, 0.15)
        k = 1 + amp[i] + wob * math.sin(t * 1.3 + ph[i])
        pts.append((cx + math.cos(a) * r * k * sx, cy + math.sin(a) * r * k * sy))
    return pts


def blob(cx, cy, r, seed=1, irr=0.22, n=11, t=0.0, wob=0.0, sx=1.0, sy=1.0):
    return smooth_path(blob_pts(cx, cy, r, seed, irr, n, t, wob, sx, sy))


def ridge(x0, x1, base, amp, seed=1, n=18, jag=0.5, y_floor=900):
    """Mountain / ridge silhouette polygon from x0 to x1 above `base`."""
    rr = random.Random(seed)
    pts = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        h = amp * (0.35 + 0.65 * abs(math.sin(i * 0.7 + seed))) * (1 - jag + jag * rr.random())
        pts.append((x, base - h))
    d = f"M{x0:.0f} {y_floor} L" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + f" L{x1:.0f} {y_floor}Z"
    return d


def soft_ridge(x0, x1, base, amp, seed=1, n=10, y_floor=900):
    rr = random.Random(seed)
    pts = [(x0, y_floor)]
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        pts.append((x, base - amp * (0.4 + 0.6 * rr.random())))
    pts.append((x1, y_floor))
    return smooth_path(pts, closed=False) + "Z"


# ------------------------------------------------------------------ billowing plume (volcanic / impact / steam)
def plume(x, y, t, seed=3, h=380, w=120, rise=1.0, spread=1.0, n=26, cols=("#8A8088", "#4A4048", "#2A2228"),
          light=(-1, -1), hi="#D8CCD0", hi_op=0.55, glow_col=None, top_spread=0.0, lean=0.0):
    """Billowing column rising from (x, y) as ONE evolving silhouette (no stacked circles): churning bulging edges,
    a cauliflower top, an optional umbrella spread, lit billows on the light side and darker folds in shadow."""
    rr = random.Random(seed)
    lx, ly = light
    m = math.hypot(lx, ly) or 1; lx, ly = lx / m, ly / m
    H = h * clamp(rise, 0.02, 1.0)
    N = 14
    ph = [rr.uniform(0, TAU) for _ in range(40)]
    def cx_at(f):
        return x + lean * f * H + 0.12 * w * math.sin(f * 5 + t * 0.7 + ph[0])
    def w_at(f):
        um = ei(clamp((f - 0.62) / 0.38)) * top_spread
        return w * spread * (0.38 + 2.1 * f ** 0.75 + 2.6 * um)
    left, right = [], []
    for i in range(N + 1):
        f = i / N
        yy = y - f * H
        bul = 1 + 0.16 * math.sin(f * 11 + t * 1.1 + ph[1]) + 0.1 * math.sin(f * 23 - t * 1.7 + ph[2])
        bur = 1 + 0.16 * math.sin(f * 13 - t * 1.0 + ph[3]) + 0.1 * math.sin(f * 19 + t * 1.5 + ph[4])
        c, ww = cx_at(f), w_at(f)
        left.append((c - ww * bul, yy)); right.append((c + ww * bur, yy))
    # cauliflower cap: bulges across the top
    c, ww = cx_at(1.0), w_at(1.0)
    cap = []
    nb = 7
    for j in range(nb + 1):
        a = math.pi + math.pi * j / nb
        rad_ = ww * (0.9 + 0.22 * math.sin(j * 2.3 + t * 0.9 + ph[5]))
        cap.append((c + math.cos(a) * rad_, y - H + math.sin(a) * rad_ * (0.55 + 0.25 * (1 - top_spread))))
    pts = left + cap + right[::-1]
    d = smooth_path(pts)
    cid = f"pl{seed}_{int(x)}_{int(y)}"
    o = [f'<path d="{d}" fill="{cols[2]}"/>']
    # lit body: the silhouette pushed toward the light
    o.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})">')
    o.append(f'<path d="{d}" fill="{cols[1]}" transform="translate({lx * w * 0.35:.1f} {ly * w * 0.25:.1f})" filter="url(#b6)"/>')
    o.append(f'<path d="{d}" fill="{cols[0]}" transform="translate({lx * w * 0.75:.1f} {ly * w * 0.5:.1f})" opacity="0.85" filter="url(#b10)"/>')
    # billows: overlapping irregular lobes along the lit edge, drifting upward with time
    for i in range(n):
        f = ((i / n) + t * 0.035 * (1 + rr.random() * 0.3)) % 1.0
        if f * h > H:
            continue
        cc, ww_ = cx_at(f), w_at(f)
        side = rr.uniform(-0.7, 0.9)
        bx = cc + ww_ * side * (1 if lx < 0 else -1) * -1
        by = y - f * H
        br = ww_ * rr.uniform(0.35, 0.6)
        o.append(f'<path d="{blob(bx + lx * br * 0.3, by + ly * br * 0.3, br, rr.randint(1, 9999), 0.25, 9, t, 0.05)}" fill="{hi}" opacity="{hi_op * rr.uniform(0.35, 0.8):.2f}"/>')
        o.append(f'<path d="{blob(bx - lx * br * 0.55, by - ly * br * 0.4, br * 0.7, rr.randint(1, 9999), 0.25, 9, t, 0.05)}" fill="{cols[2]}" opacity="0.22"/>')
    if glow_col:
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{w * 1.2:.1f}" ry="{H * 0.25:.1f}" fill="{glow_col}" opacity="0.55" filter="url(#b8)"/>')
    o.append("</g>")
    return "".join(o)


# ------------------------------------------------------------------ fire with fuel
def flame(x, y, s, t, seed=1, cols=("#FFF4C0", "#FFB43A", "#FF5A1E")):
    rr = random.Random(seed)
    o = []
    for k, (col, sc) in enumerate(zip(reversed(cols), (1.0, 0.72, 0.42))):
        pts = []
        h = 120 * s * sc * (0.9 + 0.12 * math.sin(t * 9 + seed + k))
        wv = 34 * s * sc
        sway = 10 * s * math.sin(t * 6.5 + seed * 2 + k)
        for i in range(9):
            a = i / 8
            yy = y - h * a
            ww = wv * math.sin(math.pi * (1 - a) ** 0.8 + 0.25) * (1 - a * 0.7)
            pts.append((x + ww + sway * a * a, yy))
        right = pts
        left = [(x - (px - x) + sway * ((y - py) / h) ** 2 * 1.4, py) for px, py in reversed(pts)]
        tip = (x + sway * 1.6, y - h * 1.12)
        d = smooth_path(right + [tip] + left)
        o.append(f'<path d="{d}" fill="{col}"/>')
    return "".join(o)


def campfire(x, y, s, t, seed=2):
    o = [f'<ellipse cx="{x}" cy="{y + 4 * s}" rx="{70 * s}" ry="{14 * s}" fill="#1A1010" opacity="0.6"/>']
    for k, (dx, dy, r) in enumerate(((-60, 2, 15), (-30, 8, 17), (5, 10, 16), (40, 7, 15), (66, 2, 13))):
        o.append(f'<ellipse cx="{x + dx * s}" cy="{y + dy * s}" rx="{r * s}" ry="{r * 0.7 * s}" fill="#5A5058"/><ellipse cx="{x + dx * s - 3 * s}" cy="{y + dy * s - 4 * s}" rx="{r * 0.6 * s}" ry="{r * 0.35 * s}" fill="#8A7E86"/>')
    for a, ln in ((-24, 110), (20, 104), (-6, 96)):
        o.append(f'<g transform="translate({x} {y - 6 * s}) rotate({a})"><rect x="{-ln / 2 * s}" y="{-7 * s}" width="{ln * s}" height="{14 * s}" rx="{7 * s}" fill="#5A341E"/>'
                 f'<rect x="{-ln / 2 * s}" y="{-7 * s}" width="{ln * s}" height="{5 * s}" rx="{3 * s}" fill="#8A5A34"/>'
                 f'<circle cx="{ln / 2 * s}" cy="0" r="{7 * s}" fill="#C8905A"/></g>')
    o.append(f'<ellipse cx="{x}" cy="{y - 8 * s}" rx="{40 * s}" ry="{10 * s}" fill="#FF7A2A" opacity="{0.75 + 0.2 * math.sin(t * 11):.2f}"/>')
    for k, (dx, sc) in enumerate(((-16, 0.75), (14, 0.85), (0, 1.15))):
        o.append(flame(x + dx * s, y - 4 * s, s * sc, t + k * 0.37, seed + k))
    o.append(embers(x, y - 40 * s, t, s, seed))
    return "".join(o)


def embers(x, y, t, s=1.0, seed=1, n=10, h=260):
    rr = random.Random(seed)
    o = []
    for i in range(n):
        ph = rr.random(); sp = rr.uniform(0.35, 0.7)
        u = (t * sp + ph) % 1.0
        ex = x + rr.uniform(-30, 30) * s + 26 * s * math.sin(t * 2 + i) * u
        ey = y - u * h * s
        o.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{(2.2 - 1.6 * u) * s:.2f}" fill="#FFC060" opacity="{(1 - u) * 0.9:.2f}"/>')
    return "".join(o)


# ------------------------------------------------------------------ falling particles with depth (ash, snow, debris)
def flakes(t, seed=5, n=90, box=(-60, -60, 1080, 660), wind=(60, 120), col="#D8D2CC", size=(1.2, 4.0), op=0.85, depth=True, tumble=True):
    x0, y0, w, h = box
    rr = random.Random(seed)
    o = []
    for i in range(n):
        z = rr.random() if depth else 0.5
        sp = 0.5 + z
        px, py = rr.uniform(0, w), rr.uniform(0, h)
        x = x0 + (px + wind[0] * sp * t + 12 * math.sin(t * 1.7 + i)) % w
        y = y0 + (py + wind[1] * sp * t) % h
        r = size[0] + (size[1] - size[0]) * z
        if tumble:
            o.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.2f}" ry="{r * (0.55 + 0.45 * abs(math.sin(t * 3 + i))):.2f}" fill="{col}" opacity="{op * (0.45 + 0.55 * z):.2f}"/>')
        else:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{col}" opacity="{op * (0.45 + 0.55 * z):.2f}"/>')
    return "".join(o)


def streaks(t, seed=6, n=40, box=(-100, -200, 1160, 800), vel=(260, 520), L=0.12, col="#FFD08A", w=2.2, op=0.9, head="#FFFFFF"):
    """Fast falling glowing streaks (re-entering ejecta, meteors)."""
    x0, y0, bw, bh = box
    rr = random.Random(seed)
    o = []
    for i in range(n):
        z = rr.random(); sp = 0.6 + 0.8 * z
        px, py = rr.uniform(0, bw), rr.uniform(0, bh)
        x = x0 + (px + vel[0] * sp * t) % bw
        y = y0 + (py + vel[1] * sp * t) % bh
        tx, ty = x - vel[0] * sp * L, y - vel[1] * sp * L
        o.append(f'<path d="M{tx:.1f} {ty:.1f} L{x:.1f} {y:.1f}" stroke="{col}" stroke-width="{w * (0.5 + z):.2f}" stroke-linecap="round" opacity="{op * (0.4 + 0.6 * z):.2f}"/>'
                 f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{w * (0.6 + z):.2f}" fill="{head}" opacity="{op:.2f}"/>')
    return "".join(o)


def dust_puff(x, y, t, t0, s=1.0, seed=3, col="#8A7A70", n=6, life=0.9, spread=60):
    if t < t0 or t > t0 + life:
        return ""
    u = (t - t0) / life
    rr = random.Random(seed)
    o = []
    for i in range(n):
        a = rr.uniform(math.pi * 1.05, math.pi * 1.95)
        d = spread * s * eo(u) * rr.uniform(0.5, 1.1)
        r = (8 + 18 * eo(u)) * s * rr.uniform(0.6, 1.2)
        o.append(f'<path d="{blob(x + math.cos(a) * d, y + math.sin(a) * d * 0.5, r, seed + i, 0.25, 9)}" fill="{col}" opacity="{0.6 * (1 - u):.2f}"/>')
    return "".join(o)


def chips(x, y, t, t0, s=1.0, seed=4, col="#3A2A2A", n=7, life=0.7, v=180, g=600):
    """Small fragments kicked out by a contact, ballistic."""
    if t < t0 or t > t0 + life:
        return ""
    tt = t - t0
    rr = random.Random(seed)
    o = []
    for i in range(n):
        a = rr.uniform(-2.7, -0.45); sp = v * rr.uniform(0.5, 1.1) * s
        px, py = x + math.cos(a) * sp * tt, y + math.sin(a) * sp * tt + 0.5 * g * s * tt * tt
        if py > y + 4:
            continue
        r = rr.uniform(1.5, 3.5) * s
        o.append(f'<rect x="{px - r:.1f}" y="{py - r:.1f}" width="{2 * r:.1f}" height="{1.4 * r:.1f}" fill="{col}" transform="rotate({tt * 600 + i * 40:.0f} {px:.1f} {py:.1f})"/>')
    return "".join(o)


# ------------------------------------------------------------------ water
def waves(x0, x1, y, t, amp=4, wl=90, speed=40, col="#FFFFFF", op=0.5, w=2.0, seed=1, rows=1, dy=14, persp=0.6):
    o = []
    rr = random.Random(seed)
    for r in range(rows):
        yy = y + r * dy
        a = amp * (1 + r * persp * 0.6)
        L = wl * (1 + r * persp)
        ph = rr.uniform(0, TAU)
        d = []
        x = x0
        while x <= x1:
            d.append(f"{x:.0f} {yy + a * math.sin((x + speed * t) / L * TAU + ph):.1f}")
            x += 14
        o.append(f'<path d="M{" L".join(d)}" stroke="{col}" stroke-width="{w * (1 + r * 0.3):.1f}" fill="none" opacity="{op:.2f}" stroke-linecap="round"/>')
    return "".join(o)


def glints(x0, x1, y0, y1, t, seed=2, n=22, col="#FFFFFF", op=0.8):
    rr = random.Random(seed)
    o = []
    for i in range(n):
        x, y = rr.uniform(x0, x1), rr.uniform(y0, y1)
        k = max(0.0, math.sin(t * rr.uniform(1.5, 3.5) + rr.uniform(0, TAU)))
        L = (6 + 18 * (y - y0) / max(1, y1 - y0)) * k
        if L > 1:
            o.append(f'<path d="M{x - L:.1f} {y:.1f} L{x + L:.1f} {y:.1f}" stroke="{col}" stroke-width="2" stroke-linecap="round" opacity="{op * k:.2f}"/>')
    return "".join(o)


# ------------------------------------------------------------------ misc
def stars(seed=1, n=120, x0=-400, x1=1360, y0=-300, y1=840, op=1.0, tw=0.0, t=0.0):
    rr = random.Random(seed)
    o = []
    for i in range(n):
        x, y = rr.uniform(x0, x1), rr.uniform(y0, y1)
        r = rr.choice((0.7, 1.0, 1.0, 1.4, 2.0))
        a = op * rr.uniform(0.35, 1) * (1 - tw * 0.5 * (1 + math.sin(t * 3 + i)))
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#FFFFFF" opacity="{a:.2f}"/>')
    return "".join(o)


def glow(cx, cy, r, col, op=0.5, b=16):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}" opacity="{op:.3f}" filter="url(#b{b})"/>'


def rays(cx, cy, r0, r1, n, t=0.0, col="#FFFFFF", op=0.2, w=0.06, seed=1, rot=0.0):
    rr = random.Random(seed)
    o = []
    for i in range(n):
        a = TAU * i / n + rr.uniform(-0.1, 0.1) + rot
        da = w * rr.uniform(0.6, 1.4)
        o.append(f'<path d="M{cx + r0 * math.cos(a - da):.1f} {cy + r0 * math.sin(a - da):.1f} L{cx + r1 * math.cos(a):.1f} {cy + r1 * math.sin(a):.1f} '
                 f'L{cx + r0 * math.cos(a + da):.1f} {cy + r0 * math.sin(a + da):.1f}Z" fill="{col}" opacity="{op * rr.uniform(0.5, 1):.2f}"/>')
    return "".join(o)


def blurf(*ks):
    return "".join(f'<filter id="b{k}" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="{k}"/></filter>' for k in ks)


def lin(id_, stops, x1=0, y1=0, x2=0, y2=1, units=None):
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' if len(st) == 3 else f'<stop offset="{o}" stop-color="{c}"/>'
                for st in stops for (o, c, *rest) in [st] for a in [rest[0] if rest else 1])
    u = f' gradientUnits="{units}"' if units else ""
    return f'<linearGradient id="{id_}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>{s}</linearGradient>'


def rad(id_, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None, units=None):
    s = "".join(f'<stop offset="{st[0]}" stop-color="{st[1]}" stop-opacity="{st[2] if len(st) > 2 else 1}"/>' for st in stops)
    f = (f' fx="{fx}" fy="{fy}"' if fx is not None else "")
    u = f' gradientUnits="{units}"' if units else ""
    return f'<radialGradient id="{id_}" cx="{cx}" cy="{cy}" r="{r}"{f}{u}>{s}</radialGradient>'
