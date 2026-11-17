"""Crocodile Short props: a 3D saltwater crocodile (any yaw, body roll for the death roll, jaw open, tail sway),
river sets (bank side view, water level, underwater, overhead), the inside of the mouth with the throat flap."""
import math, random
from wcore import *
from botfly_mt import fg_hairs, dust, flare, streaks, hstreaks, flashw
from bear_props import bear3d, walk_J, run_J, kmh_chip, impact_star, GRIZ
from pose2 import back as back_pose

L_RIVER = Light("crDay", amb=(1.0, 0.97, 0.9), sat=1.0, key="#FFE2A8", key_op=0.35, ang=-55, spread=0.8, shade="#13283A", shade_op=0.32, rim="#FFF0C8", rim_op=0.5, rim_w=7)
L_UNDER = Light("crUnder", amb=(0.6, 0.85, 0.9), sat=0.8, key="#9AF0E8", key_op=0.3, ang=-80, spread=0.9, shade="#02141A", shade_op=0.5, rim="#B8FFF4", rim_op=0.5, rim_w=6)
SHADE = "#071008"
TAU = 2 * math.pi
CROC = ("#56693A", "#2F3D22", "#CFCB92", "#3C4C2A")      # top, dark, belly, scutes
WATER_Y = 430


# ------------------------------------------------------------------ 3D crocodile
def croc3d(ox, oy, s=1.0, yaw_deg=0.0, t=0.0, open_=0.0, roll=0.0, sway=0.3, walk=0.0, blink=0.0, persp=0.0, small=False, eye_glow=0.0, sil=None, pitch=0.0, anchor=None):
    """Model: snout at +x, ~370 units snout to tail at s=1, belly on y=0 (oy = belly line), z toward the viewer's left.
    yaw 0 = side view facing right, -90 = head-on toward the camera. open_ = jaw angle 0..1 (~45 deg).
    roll = body roll in degrees around its long axis (the death roll)."""
    yaw = math.radians(yaw_deg); c, si = math.cos(yaw), math.sin(yaw)
    rr = math.radians(roll); cr, sr = math.cos(rr), math.sin(rr)
    top, dark, belly, scute = CROC
    if sil:
        top = dark = belly = scute = sil
    items = []
    AX = -18.0          # roll axis height

    def K(Z):
        return 1.0 / max(0.25, 1 + persp * Z)

    pr = math.radians(pitch); cp, sp = math.cos(pr), math.sin(pr)

    def R(p):
        x, y, z = p
        y0 = y - AX
        x, y, z = x, AX + y0 * cr - z * sr, y0 * sr + z * cr
        if pitch:                                        # head up around a pivot behind the shoulders
            dx, dy = x + 40, y + 10
            x, y = -40 + dx * cp + dy * sp, -10 - dx * sp + dy * cp
        return x, y, z

    if anchor is not None:                               # place the jaw tip exactly on anchor (e.g. the boy's hand)
        tx, ty, tz = R((140, -18, 0))
        ox = anchor[0] - (tx * c - tz * si) * s
        oy = anchor[1] - ty * s

    def P(p):
        x, y, z = R(p)
        Z = x * si + z * c; k = K(Z)
        return ox + (x * c - z * si) * s * k, oy + (-20 + (y + 20) * k) * s, Z

    def dk(Z):
        return 0.0 if sil else max(0.0, min(0.5, Z / 200.0 * 0.45))

    def ell(p, rx, ry, rz, col, hl=0.1, zb=0.0, op=1.0):
        X, Y, Z = P(p); k = K(Z)
        ry2 = math.sqrt((ry * cr) ** 2 + (rz * sr) ** 2); rz2 = math.sqrt((ry * sr) ** 2 + (rz * cr) ** 2)
        prx = math.sqrt((rx * c) ** 2 + (rz2 * si) ** 2) * k * s; pry = ry2 * k * s
        o = f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{prx:.1f}" ry="{pry:.1f}" fill="{mixc(col, SHADE, dk(Z))}" opacity="{op:.2f}"/>'
        if hl > 0 and not sil:
            o += f'<ellipse cx="{X - 0.15 * prx:.1f}" cy="{Y - 0.45 * pry:.1f}" rx="{0.6 * prx:.1f}" ry="{0.25 * pry:.1f}" fill="#F4FFE0" opacity="{hl:.2f}" filter="url(#b3)"/>'
        items.append((Z + zb, o))

    def line(pts, col, w, op=1.0, zb=0.0, cap="round"):
        q = [P(p) for p in pts]; Z = sum(z for *_, z in q) / len(q)
        items.append((Z + zb, f'<path d="M{" L".join(f"{x:.1f} {y:.1f}" for x, y, _ in q)}" stroke="{mixc(col, SHADE, dk(Z))}" stroke-width="{w * s * K(Z):.1f}" fill="none" stroke-linecap="{cap}" stroke-linejoin="round" opacity="{op:.2f}"/>'))

    def poly(pts, col, op=1.0, zb=0.0):
        q = [P(p) for p in pts]; Z = sum(z for *_, z in q) / len(q)
        items.append((Z + zb, f'<path d="M{" L".join(f"{x:.1f} {y:.1f}" for x, y, _ in q)} Z" fill="{mixc(col, SHADE, dk(Z))}" opacity="{op:.2f}"/>'))

    def swz(x):
        """Tail sway: z offset growing toward the tail tip."""
        if x > -40:
            return 0.0
        u = (-40 - x) / 180.0
        return sway * 40 * u * u * math.sin(t * 3.0 - u * 3.0)

    # ---- tail
    n = 11
    for k in range(n):
        u = k / (n - 1)
        x = -40 - 190 * u; r = lerp(25, 4, u)
        ell((x, -18 + 6 * u, swz(x)), 17, r * 1.05, r * 1.15, top, 0.08 if k % 2 == 0 else 0.0)
        if k < n - 1:
            for zz in ((-1, 1) if u < 0.45 else (0,)):
                zo = zz * r * 0.45
                poly([(x - 6, -16 + 4 * u - r * 0.8, swz(x) + zo), (x, -16 + 4 * u - r * 0.8 - (8 - 5 * u), swz(x) + zo), (x + 6, -16 + 4 * u - r * 0.8, swz(x) + zo)], scute, zb=-0.3)
    # ---- body
    for x, rx, ry, rz in ((-30, 36, 27, 42), (0, 38, 28, 44), (30, 34, 26, 40)):
        ell((x, -24, 0), rx, ry, rz, top, 0.12)
        ell((x, -6, 0), rx * 0.9, 9, rz * 0.9, belly, 0.0, zb=0.5)
    for x in range(-50, 50, 12):                           # back armour rows
        for zz in (-12, 0, 12):
            poly([(x - 4, -48, zz), (x, -56, zz), (x + 4, -48, zz)], scute, zb=-0.5)
    # ---- legs
    for front in (True, False):
        for side in (-1, 1):
            hx = 32 if front else -36
            ph = TAU * walk + (0 if front else math.pi) + (0 if side > 0 else math.pi)
            fx = hx + (10 if front else 4) + 18 * math.sin(ph) * (1 if walk else 0)
            lift = max(0.0, math.cos(ph)) * 10 * (1 if walk else 0)
            hip = (hx, -14, side * 26); knee = (hx + 2, -6 - lift * 0.5, side * 46); foot = (fx, -lift, side * 50)
            line([hip, knee], top, 13, zb=1.0); line([knee, foot], top, 10, zb=1.0)
            for k in range(4):
                line([foot, (foot[0] + 8 + 3 * k * (1 if front else -1) * 0.5, foot[1] + 1, foot[2] + side * (k - 1.5) * 4)], dark, 3, zb=0.9)
    # ---- neck + head
    ell((56, -24, 0), 26, 22, 32, top, 0.1)
    ell((78, -26, 0), 24, 17, 28, top, 0.14)
    # eyes on raised bumps
    for side in (-1, 1):
        ell((76, -38, side * 11), 7, 6, 6, top, 0.0, zb=-0.6)
        X, Y, Z = P((79, -42, side * 11)); k = K(Z) * s
        if blink > 0.5:
            items.append((Z - 0.8, f'<path d="M{X - 4.5 * k:.1f} {Y:.1f} L{X + 4.5 * k:.1f} {Y:.1f}" stroke="#1A2410" stroke-width="{2 * k:.1f}"/>'))
        else:
            gl = glow(X, Y, 14 * k, "#FFE04A", 0.5 * eye_glow, 4) if eye_glow > 0 else ""
            items.append((Z - 0.8, gl + f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{4.6 * k:.1f}" ry="{4.2 * k:.1f}" fill="#E8C83A"/>'
                                   f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{1.0 * k:.1f}" ry="{3.6 * k:.1f}" fill="#120A04"/>'
                                   f'<circle cx="{X - 1.5 * k:.1f}" cy="{Y - 1.6 * k:.1f}" r="{1.1 * k:.1f}" fill="#FFFFFF" opacity="0.85"/>'))
    # ---- jaws: rotate around the hinge (64, -16) in the x-y plane
    ang = math.radians(55 * open_)
    hxj, hyj = 64.0, -18.0

    def jaw(p, sgn):
        x, y, z = p
        a = ang * (0.45 if sgn < 0 else 0.75) * sgn       # upper lifts a little, lower drops more
        dx, dy = x - hxj, y - hyj
        return (hxj + dx * math.cos(a) - dy * math.sin(a), hyj + dx * math.sin(a) + dy * math.cos(a), z)

    L_ = 150 if not small else 140
    up = [(92, -24, 22, 9, 18), (116, -23, 20, 8, 13), (138, -22, 14, 7, 10)]
    for x, y, rx, ry, rz in up:
        ell(jaw((x, y, 0), -1), rx, ry, rz, top, 0.12, zb=-0.2)
    ell(jaw((L_, -27, 0), -1), 7, 5, 7, top, 0.0, zb=-0.25)               # nostril knob
    for side in (-1, 1):
        X, Y, Z = P(jaw((L_ + 2, -31, side * 3), -1))
        items.append((Z - 0.3, f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{1.4 * s:.1f}" fill="#1A2010"/>'))
    for x, y, rx, ry, rz in ((92, -12, 21, 6, 17), (116, -12, 19, 5, 12), (138, -13, 13, 5, 9)):
        ell(jaw((x, y, 0), 1), rx, ry, rz, belly if open_ > 0.05 else top, 0.0, zb=-0.15)
    # mouth inside + teeth
    if open_ > 0.03:
        ins = [jaw((66, -17, 0), -1), jaw((146, -18, 0), -1), jaw((146, -16, 0), 1), jaw((66, -15, 0), 1)]
        poly(ins, "#C8586A", zb=0.6)
        poly([jaw((70, -17, 0), -1), jaw((80, -18, 0), -1), jaw((80, -14, 0), 1), jaw((70, -15, 0), 1)], "#7A2A3A", zb=0.55)
    for side in (-1, 1):
        for k in range(10):
            x = 84 + 6.5 * k; w = lerp(16, 8, k / 9)
            a1 = jaw((x, -16, side * w), -1); a2 = jaw((x + 2, -9 + (2 if k % 3 == 0 else 0), side * w), -1)
            line([a1, a2], "#F4F0DC", 2.6, zb=-0.4)
            b1 = jaw((x + 3, -14, side * w * 0.95), 1); b2 = jaw((x + 4, -20 - (2 if k % 3 == 1 else 0), side * w * 0.95), 1)
            line([b1, b2], "#F4F0DC", 2.4, zb=-0.35)
    items.sort(key=lambda it: -it[0])
    out = "".join(v for _, v in items)
    shadow = f'<ellipse cx="{ox:.1f}" cy="{oy + 2:.1f}" rx="{(180 * abs(c) + 60 * abs(si)) * s:.1f}" ry="{12 * s:.1f}" fill="#05030F" opacity="{0.0 if sil else 0.25:.2f}" filter="url(#b6)"/>'
    return shadow + out


# ------------------------------------------------------------------ world
def river_sky(warm=0.0):
    return (f'<rect x="-700" y="-900" width="2360" height="1700" fill="{mixc("#6AB8E8", "#F0A060", warm)}"/>'
            f'<rect x="-700" y="-40" width="2360" height="400" fill="{mixc("#E0F4FF", "#FFE0A8", warm)}" opacity="0.85" filter="url(#b40)"/>'
            + glow(300, -60, 260, "#FFF4C8", 0.6, 30))


def palm(x, y, h, lean=0.0, col="#2E6A3A"):
    tx, ty = x + lean * h * 0.3, y - h
    o = f'<path d="M{x} {y} Q{x + lean * h * 0.1:.1f} {y - h * 0.5:.1f} {tx:.1f} {ty:.1f}" stroke="#7A5A3A" stroke-width="{h * 0.05:.1f}" fill="none" stroke-linecap="round"/>'
    for k in range(7):
        a = -math.pi + k * math.pi / 6
        ex, ey = tx + math.cos(a) * h * 0.4, ty + math.sin(a) * h * 0.2 + h * 0.12
        o += f'<path d="M{tx:.1f} {ty:.1f} Q{(tx + ex) / 2:.1f} {ty - h * 0.14:.1f} {ex:.1f} {ey:.1f}" stroke="{col}" stroke-width="{h * 0.05:.1f}" fill="none" stroke-linecap="round"/>'
    return o


def jungle_row(y, seed, col, n=16, h0=100, h1=180):
    r = random.Random(seed); o = []
    for _ in range(n * 2):
        x = r.uniform(-700, 1660); rad = r.uniform(h0 * 0.35, h1 * 0.45)
        o.append(f'<circle cx="{x:.0f}" cy="{y - rad * 0.6:.0f}" r="{rad:.0f}" fill="{col}"/>')
    for _ in range(n // 3):
        o.append(palm(r.uniform(-600, 1560), y - 10, r.uniform(h0 * 1.2, h1 * 1.3), r.uniform(-0.6, 0.6), mixc(col, "#000000", 0.1)))
    return "".join(o)


def river_back(warm=0.0):
    return (river_sky(warm) + f'<rect x="-700" y="200" width="2360" height="200" fill="#B8D8E0" opacity="0.5" filter="url(#b20)"/>'
            + jungle_row(330, 31, "#4E8A58", 18, 90, 160) + f'<rect x="-700" y="240" width="2360" height="100" fill="#D8F0F0" opacity="0.25" filter="url(#b20)"/>'
            + jungle_row(370, 32, "#2E6A44", 16, 120, 200))


def water_back(y0=WATER_Y):
    """Water body behind/below the croc (far surface + depth gradient)."""
    return (f'<rect x="-700" y="{y0 - 30}" width="2360" height="1000" fill="#3E8A86"/>'
            f'<rect x="-700" y="{y0 - 30}" width="2360" height="40" fill="#8ACAC0" opacity="0.6"/>'
            + "".join(f'<path d="M{-600 + 140 * k} {y0 - 14 + 8 * (k % 3)} q30 -6 60 0" stroke="#D8F4EC" stroke-width="3" fill="none" opacity="0.5"/>' for k in range(17)))


def water_front(t, y0=WATER_Y, op=0.55):
    """Semi-clear water drawn OVER the croc so the part below the surface reads submerged."""
    wave = " ".join(f"L{x} {y0 + 4 * math.sin(x * 0.03 + t * 3):.1f}" for x in range(-700, 1680, 40))
    return (f'<path d="M-700 {y0} {wave} L1660 1400 L-700 1400 Z" fill="#2E7A78" opacity="{op:.2f}"/>'
            f'<path d="M-700 {y0} {wave}" stroke="#E8FFF8" stroke-width="4" fill="none" opacity="0.7"/>')


def bank(x1=520, y0=WATER_Y):
    """Muddy bank on the left, sloping into the water at x1."""
    return (f'<path d="M-700 {y0 - 40} L{x1 - 60} {y0 - 40} Q{x1} {y0 - 30} {x1 + 40} {y0 + 30} L{x1 + 40} 1400 L-700 1400 Z" fill="#8A6A44"/>'
            f'<path d="M-700 {y0 - 40} L{x1 - 60} {y0 - 40} Q{x1} {y0 - 30} {x1 + 40} {y0 + 30}" stroke="#A8865A" stroke-width="8" fill="none"/>'
            + "".join(f'<path d="M{-600 + 70 * k} {y0 - 40} q-4 -18 -10 -26 M{-600 + 70 * k} {y0 - 40} q3 -20 8 -30" stroke="#5A8A3A" stroke-width="4" fill="none" stroke-linecap="round"/>' for k in range(int((x1 + 500) / 70))))


def splash(x, y, u, s=1.0, seed=2):
    if u <= 0:
        return ""
    r = random.Random(seed); o = []
    for k in range(26):
        a = r.uniform(-math.pi * 0.95, -math.pi * 0.05); d = r.uniform(40, 220) * u * s
        px, py = x + math.cos(a) * d, y + math.sin(a) * d + 300 * u * u * s * 0.5
        o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r.uniform(4, 14) * s * (1 - 0.5 * u):.1f}" fill="#E8FFFA" opacity="{0.85 * (1 - u * 0.7):.2f}"/>')
    sheet = f'<path d="M{x - 160 * s} {y} Q{x - 120 * s * u} {y - 200 * s * math.sin(math.pi * min(1, u * 1.4))} {x} {y - 40 * s} Q{x + 120 * s * u} {y - 200 * s * math.sin(math.pi * min(1, u * 1.4))} {x + 160 * s} {y} Z" fill="#CFF4EC" opacity="{0.6 * (1 - u):.2f}"/>'
    return sheet + "".join(o)


def underwater_bg(t):
    o = ['<rect x="-700" y="-900" width="2360" height="2400" fill="#0E3A44"/>',
         '<rect x="-700" y="-900" width="2360" height="900" fill="#3AA0A0" opacity="0.5" filter="url(#b40)"/>']
    for k in range(7):
        x = -200 + 220 * k + 40 * math.sin(t * 0.5 + k)
        o.append(f'<path d="M{x} -400 L{x + 120} -400 L{x + 300} 900 L{x + 220} 900 Z" fill="#9AF0E8" opacity="0.07"/>')
    o.append('<rect x="-700" y="560" width="2360" height="800" fill="#2A2418"/>')
    return "".join(o)


def bubbles2(t, x, y0, n=14, seed=4, spread=120, speed=160):
    r = random.Random(seed); o = []
    for k in range(n):
        ph = (t * speed / 400 + r.random()) % 1
        bx = x + r.uniform(-spread, spread) + 10 * math.sin(t * 3 + k); by = y0 - ph * 500
        o.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{r.uniform(3, 10):.1f}" fill="none" stroke="#DFFFFA" stroke-width="2" opacity="{0.8 * (1 - ph):.2f}"/>')
    return "".join(o)


def topdown_river(t):
    o = ['<rect x="-800" y="-800" width="2560" height="2200" fill="#8A6A44"/>',
         f'<path d="M560 -800 Q520 300 600 1400 L1760 1400 L1760 -800 Z" fill="#3E8A86"/>',
         f'<path d="M560 -800 Q520 300 600 1400" stroke="#CFF4EC" stroke-width="10" fill="none" opacity="0.7"/>']
    o += [f'<path d="M{640 + 60 * k} {-600 + 180 * k} q40 -8 80 0" stroke="#D8F4EC" stroke-width="4" fill="none" opacity="0.5"/>' for k in range(10)]
    r = random.Random(3)
    for _ in range(40):
        x, y = r.uniform(-600, 500), r.uniform(-600, 1300)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(3, 9):.0f}" fill="#6A5034" opacity="0.6"/>')
    return "".join(o)


# ------------------------------------------------------------------ inside the mouth (front view looking down the throat)
def mouth_inside(cx, cy, s=1.0, valve=0.0, glow_v=0.0, flood=0.0, t=0.0):
    """valve 0 = flap sealed against the throat, 1 = pushed down so the throat is open. flood = water rushing in (0..1)."""
    o = [f'<ellipse cx="0" cy="0" rx="300" ry="230" fill="#9A3A4A"/>',
         f'<ellipse cx="0" cy="-30" rx="250" ry="170" fill="#C8586A"/>',
         '<path d="M-200 60 Q0 160 200 60 Q120 200 0 210 Q-120 200 -200 60 Z" fill="#E07A86"/>',       # tongue floor
         '<path d="M-60 -170 Q0 -150 60 -170" stroke="#A8485A" stroke-width="8" fill="none"/>']
    for k in range(9):
        x = -224 + 56 * k; yy = 230 * math.sqrt(max(0.0, 1 - (x / 300) ** 2)) * 0.92
        o.append(f'<path d="M{x - 12:.0f} {-yy:.0f} l12 44 l12 -44 Z" fill="#F4F0DC"/>')
        o.append(f'<path d="M{x - 12:.0f} {yy:.0f} l12 -44 l12 44 Z" fill="#F4F0DC"/>')
    # throat hole + the flap (palatal valve)
    o.append('<ellipse cx="0" cy="-10" rx="70" ry="54" fill="#2A0A12"/>')
    if flood > 0:
        o.append(f'<ellipse cx="0" cy="-10" rx="{70 * flood:.1f}" ry="{54 * flood:.1f}" fill="#4AB8C0" opacity="0.8"/>')
        for k in range(6):
            yy = -200 + ((t * 300 + k * 60) % 220)
            o.append(f'<path d="M{-160 + 64 * k} {yy - 60:.0f} Q{-100 + 50 * k} {yy:.0f} {-30 + 12 * k} {yy + 30:.0f}" stroke="#9AF0F4" stroke-width="10" fill="none" opacity="{0.7 * flood:.2f}" stroke-linecap="round"/>')
    fy = -10 + 60 * valve
    o.append(f'<path d="M-90 {fy - 50:.1f} Q0 {fy - 80 + 40 * valve:.1f} 90 {fy - 50:.1f} Q96 {fy + 10:.1f} 0 {fy + 30 - 20 * valve:.1f} Q-96 {fy + 10:.1f} -90 {fy - 50:.1f} Z" fill="#D86A7A" stroke="#8A2A3A" stroke-width="5"/>')
    if glow_v > 0:
        o.append(f'<path d="M-90 {fy - 50:.1f} Q0 {fy - 80 + 40 * valve:.1f} 90 {fy - 50:.1f} Q96 {fy + 10:.1f} 0 {fy + 30 - 20 * valve:.1f} Q-96 {fy + 10:.1f} -90 {fy - 50:.1f} Z" fill="none" stroke="#FFE45A" stroke-width="10" opacity="{glow_v:.2f}"/>'
                 + glow(0, fy - 20, 140, "#FFE45A", 0.35 * glow_v, 16))
    return f'<g transform="translate({cx:.1f} {cy:.1f}) scale({s:.3f})">{"".join(o)}</g>'


def bottle(x, y, s=1.0, ang=0.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})"><rect x="-14" y="-60" width="28" height="60" rx="8" fill="#5AC8F0" opacity="0.85"/>'
            '<rect x="-8" y="-74" width="16" height="16" rx="3" fill="#2A5AAA"/><rect x="-10" y="-50" width="6" height="40" rx="3" fill="#FFFFFF" opacity="0.5"/></g>')


def crouch_J(reach=0.0, face=None):
    """Side-view crouch at the water's edge, near arm reaching down/forward (reach 0..1)."""
    J = dict(R3.SIDE)
    J.update(hip=(-10, 70), lean=18, k1=(70, -60), f1=(30, 0), k2=(80, -50), f2=(50, 0),
             e1=(30, -270), h1=(70, -230), e2=(60, -280), h2=(lerp(90, 150, reach), lerp(-200, -150, reach)),
             face=face or fc(open=1.0, look=(1, 0.4)))
    return J


def arm_pulled_J(pull=0.0, face=None):
    """Standing, leaning back hard, near arm stretched straight forward (held by the croc)."""
    J = dict(R3.SIDE)
    J.update(lean=lerp(-6, -22, pull), hip=(0, 20), k1=(-10, -100), f1=(-50, 0), k2=(30, -100), f2=(40, 0),
             e2=(80, -290), h2=(165, -215), e1=(40, -300), h1=(110, -320),
             face=face or fc(open=1.4, lift=1.0, knit=0.9, mouth="grit", look=(1, 0)))
    return J
