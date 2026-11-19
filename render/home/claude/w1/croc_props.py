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
CROC_DEFS = ('<linearGradient id="crocG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#86995A"/><stop offset="0.35" stop-color="#66793E"/>'
             '<stop offset="0.62" stop-color="#4E6230"/><stop offset="0.74" stop-color="#5E6E3A"/><stop offset="0.8" stop-color="#C9C38C"/><stop offset="1" stop-color="#B2AA74"/></linearGradient>')
CROC = ("#56693A", "#2F3D22", "#CFCB92", "#3C4C2A")      # top, dark, belly, scutes
WATER_Y = 430


# ------------------------------------------------------------------ 3D crocodile
def _hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts
    def cr(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def _sm(a, b, x):
    u = clamp((x - a) / (b - a)); return u * u * (3 - 2 * u)


def croc_profile(x):
    """Cross-section at x: (centre y, half height, half width). Snout +x, belly on y=0."""
    if x < -40:                                            # tail: tall and flattened sideways
        u = (-40 - x) / 190.0
        return -21 + 6 * u, lerp(21, 4, u ** 0.8), lerp(26, 2.5, u ** 0.7)
    if x < 44:                                             # body: wide, low, armoured
        b = 1 - 0.18 * (1 - _sm(-40, -10, x)) - 0.22 * _sm(20, 44, x)
        return -26, 25 * b, 46 * b
    if x < 66:                                             # neck
        return -27, lerp(20, 17, _sm(44, 66, x)), lerp(36, 31, _sm(44, 66, x))
    if x < 96:                                             # skull, broad and flat
        return -28, lerp(17, 13, _sm(66, 96, x)), lerp(31, 24, _sm(66, 96, x))
    u = (x - 96) / 56.0                                    # snout tapering to a rounded tip
    tip = max(0.0, 1 - max(0.0, (u - 0.85) / 0.15) ** 2) ** 0.5
    return -26 + 2 * u, lerp(13, 8, u) * max(tip, 0.25), lerp(24, 11, u) * max(tip, 0.2)


LAST = {}


def croc3d(ox, oy, s=1.0, yaw_deg=0.0, t=0.0, open_=0.0, roll=0.0, sway=0.3, walk=0.0, blink=0.0, persp=0.0, small=False, eye_glow=0.0, sil=None, pitch=0.0, anchor=None, inner="", tip_in=0.0):
    """Saltwater crocodile as one smooth lofted body (cross-sections joined by hulls), seen from any yaw.
    Snout at +x, ~380 units long at s=1, belly on y=0 (oy), z toward the viewer's left. yaw 0 = side view facing right,
    -90 = head-on. open_ 0..1 jaw gape, roll = death-roll angle (deg), pitch = head-up tilt (deg), anchor = put the jaw tip there."""
    yaw = math.radians(yaw_deg); c, si = math.cos(yaw), math.sin(yaw)
    rr = math.radians(roll); cr_, sr_ = math.cos(rr), math.sin(rr)
    pr = math.radians(pitch); cp, sp = math.cos(pr), math.sin(pr)
    TOP, DARK, BELLY, SCUTE = CROC
    LITE = "#73884A"
    if sil:
        TOP = DARK = BELLY = SCUTE = LITE = sil
    AX = -26.0
    ga = math.radians(42 * open_)

    def swz(x):
        if x > -40: return 0.0
        u = (-40 - x) / 190.0
        return sway * 46 * u * u * math.sin(t * 3.0 - u * 3.2)

    def jaw(p, part):
        """part +1 = upper jaw (lifts), -1 = lower jaw (drops); hinge at (66, AX)."""
        x, y, z = p
        if part == 0 or x < 66: return p
        a = -ga * 0.35 if part > 0 else ga * 0.8
        dx, dy = x - 66, y - AX
        return (66 + dx * math.cos(a) - dy * math.sin(a), AX + dx * math.sin(a) + dy * math.cos(a), z)

    def R(p):
        x, y, z = p
        y0 = y - AX
        x, y, z = x, AX + y0 * cr_ - z * sr_, y0 * sr_ + z * cr_
        if pitch:
            dx, dy = x + 40, y + 10
            x, y = -40 + dx * cp + dy * sp, -10 - dx * sp + dy * cp
        return x, y, z

    def K(Z): return 1.0 / max(0.25, 1 + persp * Z)

    if anchor is not None:
        tx, ty, tz = R((148 - tip_in, -26, 0))
        ox = anchor[0] - (tx * c - tz * si) * s
        oy = anchor[1] - ty * s

    def P(p):
        x, y, z = R(p)
        Z = x * si + z * c; k = K(Z)
        return (ox + (x * c - z * si) * s * k, oy + (-20 + (y + 20) * k) * s, Z)

    def ring(x, cy, h, w, zc, part=0, n=14):
        out = []
        for k in range(n):
            th = TAU * k / n
            out.append(P(jaw((x, cy + h * math.cos(th), zc + w * math.sin(th)), part)))
        return out

    def loft(xs, col, f=lambda x: croc_profile(x), part=0):
        o = []; prev = None; zs = []
        for x in xs:
            cy, h, w = f(x)
            r = ring(x, cy, h, w, swz(x), part)
            if prev:
                hp = _hull([(round(a, 1), round(b, 1)) for a, b, _ in prev + r])
                o.append("M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in hp) + "Z")
            prev = r; zs.append(sum(z for *_, z in r) / len(r))
        return f'<path d="{" ".join(o)}" fill="{col}"/>', sum(zs) / max(1, len(zs))

    def seg(p0, p1, w, col):
        a, b = P(p0), P(p1)
        return f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="{col}" stroke-width="{w * s:.1f}" stroke-linecap="round"/>', (a[2] + b[2]) / 2

    xs_body = [x for x in range(-230, 67, 5)]
    xs_head = [66 + 3 * k for k in range(29)]               # 66..150
    layers = []                                              # (depth, svg)
    # legs (thick capsules); far ones go behind the body, near ones in front
    for front in (True, False):
        for side in (-1, 1):
            hx = 30 if front else -32
            ph = TAU * walk + (0 if front else math.pi) + (0 if side > 0 else math.pi)
            fx = hx + (12 if front else 2) + (16 * math.sin(ph) if walk else 0)
            lift = max(0.0, math.cos(ph)) * 10 if walk else 0
            hip = (hx, -20, side * 34); knee = (hx + 2, -10 - lift * 0.5, side * 56); foot = (fx, -lift, side * 60)
            a, za = seg(hip, knee, 20 if not front else 17, TOP)
            b, zb = seg(knee, foot, 15 if not front else 13, TOP)
            toes = "".join(seg(foot, (foot[0] + (9 if front else -9) * math.cos(q), foot[1] + 1, foot[2] + side * 9 * math.sin(q) + side * 2), 4, DARK)[0] for q in (-0.6, 0, 0.6, 1.2))
            layers.append((za, a + b + toes))
    # body: base, lit top band, pale belly
    FILL = TOP if sil else "url(#crocG)"
    closed = open_ <= 0.03
    if closed:
        base, zb_ = loft(xs_body + xs_head[1:], FILL)
    else:
        tp = lambda x: (lambda cy, h, w: (cy, h * (1 - 0.75 * _sm(62, 80, x)), w * (1 - 0.6 * _sm(62, 80, x))))(*croc_profile(x))
        base, zb_ = loft(xs_body + [68, 71, 74, 77, 80], FILL, tp)
    body = base
    # armour: two rows of raised scutes down the back, one crest down the tail
    sc = []
    for x in range(-200, 50, 9):
        cy, h, w = croc_profile(x)
        rows = (-0.32, 0.32) if x > -110 else (0.0,)
        for rz in rows:
            zc = swz(x) + rz * w
            p0, p1, p2 = P((x - 3.5, cy - h * 0.92, zc)), P((x, cy - h - (6 if x > -110 else 5), zc)), P((x + 3.5, cy - h * 0.92, zc))
            sc.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f} L{p1[0]:.1f} {p1[1]:.1f} L{p2[0]:.1f} {p2[1]:.1f} Z" fill="{SCUTE}"/>')
    body += "".join(sc)
    # head: closed = one loft; open = upper + lower jaw lofts with the pink mouth between
    if open_ > 0.03:
        up_f = lambda x: (lambda cy, h, w: (cy - 0.45 * h, 0.6 * h, w))(*croc_profile(x))
        lo_f = lambda x: (lambda cy, h, w: (cy + 0.55 * h, 0.45 * h, 0.94 * w))(*croc_profile(x))
        mouth = [P(jaw((66, AX, 0), 1)), P(jaw((146, AX - 2, 0), 1)), P(jaw((146, AX + 2, 0), -1)), P(jaw((66, AX, 0), -1))]
        inside = f'<path d="M{" L".join(f"{a:.1f} {b:.1f}" for a, b, _ in mouth)} Z" fill="#6A1E2C"/>'
        U0, U1, L1, L0 = [m[:2] for m in mouth]
        mix = lambda A, B, k: (A[0] + (B[0] - A[0]) * k, A[1] + (B[1] - A[1]) * k)
        pts = lambda ps: "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in ps) + " Z"
        # palate: upper 55% of the gape, ridged; tongue: a rounded pad on the lower jaw
        pal = [mix(U0, L0, 0.12), mix(U1, L1, 0.06), mix(U1, L1, 0.5), mix(U0, L0, 0.5)]
        tng = [mix(U0, L0, 0.62), mix(mix(U1, L1, 0.7), mix(U0, L0, 0.7), 0.25), mix(L1, L0, 0.3), mix(U0, L0, 0.92)]
        inside += f'<path d="{pts(pal)}" fill="#B24E60"/>'
        for k in (0.3, 0.5, 0.7):
            r0, r1 = mix(mix(U0, L0, 0.15), mix(U1, L1, 0.08), k), mix(mix(U0, L0, 0.45), mix(U1, L1, 0.45), k)
            inside += f'<path d="M{r0[0]:.1f} {r0[1]:.1f} L{r1[0]:.1f} {r1[1]:.1f}" stroke="#94374A" stroke-width="{2.2 * s:.1f}" stroke-linecap="round"/>'
        inside += f'<path d="{pts(tng)}" fill="#D0707E" stroke="#B85464" stroke-width="{1.2 * s:.1f}" stroke-linejoin="round"/>'
        ma, mb = mix(U0, L0, 0.5), mix(U1, L1, 0.5)
        inside += f'<path d="M{ma[0]:.1f} {ma[1]:.1f} L{mix(ma, mb, 0.85)[0]:.1f} {mix(ma, mb, 0.85)[1]:.1f}" stroke="#7A2436" stroke-width="{1.6 * s:.1f}" opacity="0.6"/>'
        thr = P((68, AX, 0)); inside += f'<ellipse cx="{thr[0]:.1f}" cy="{thr[1]:.1f}" rx="{10 * s:.1f}" ry="{14 * s * max(0.3, open_):.1f}" fill="#4A1220" opacity="0.7"/><ellipse cx="{thr[0]:.1f}" cy="{thr[1]:.1f}" rx="{5 * s:.1f}" ry="{9 * s * max(0.3, open_):.1f}" fill="#2A0810"/>'
        # far-side teeth (smaller, in shade), seen through the open mouth
        for x in range(76, 146, 6):
            cy_, h_, w_ = croc_profile(x)
            for prt, dy0, dy1 in ((1, 1, 5), (-1, 3, -2)):
                q0 = P(jaw((x, cy_ + dy0, 0), prt)); q1 = P(jaw((x + 1.5, cy_ + dy1, 0), prt))
                inside += f'<path d="M{q0[0] - 1.2 * s:.1f} {q0[1]:.1f} L{q1[0]:.1f} {q1[1]:.1f} L{q0[0] + 1.2 * s:.1f} {q0[1]:.1f} Z" fill="#D6CFB4"/>'
        inside += inner
        lo, _ = loft(xs_head, BELLY if not sil else TOP, lo_f, -1); upj, _ = loft(xs_head, FILL, up_f, 1)
        lower_side, _ = loft(xs_head, FILL, lambda x: (lambda cy, h, w: (cy + 0.35 * h, 0.4 * h, 0.97 * w))(*croc_profile(x)), -1)
        head = lo + lower_side + inside + upj
    else:
        head = ""
    # teeth and the jaw line on the side facing the camera
    near = 1 if (c * 0 + (-si) * 0 + 1) and (math.cos(yaw) * 0 + math.sin(yaw) * 0) == 0 else 1
    zside = 1 if (0 * si + 1 * c) < 0 else -1               # z side nearer the camera
    if roll and abs(((roll + 90) % 360) - 180) < 90:
        zside = -zside
    det = []
    if open_ > 0.03:
        for prt, dy in ((1, 2), (-1, -1)):
            gl = [P(jaw((x, croc_profile(x)[0] + dy, zside * croc_profile(x)[2] * 0.93), prt)) for x in range(70, 146, 4)]
            det.append(f'<path d="M{" L".join(f"{a:.1f} {b:.1f}" for a, b, _ in gl)}" stroke="#D8707E" stroke-width="{4.2 * s:.1f}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    jl = []
    for x in range(68, 148, 3):
        cy, h, w = croc_profile(x)
        jl.append(P(jaw((x, cy + 1, zside * w * 0.97), 1 if open_ > 0.03 else 0)))
    det.append(f'<path d="M{" L".join(f"{a:.1f} {b:.1f}" for a, b, _ in jl)}" stroke="{DARK}" stroke-width="{2.2 * s:.1f}" fill="none" stroke-linecap="round"/>')
    for k, x in enumerate(range(74, 146, 6)):
        cy, h, w = croc_profile(x)
        z0 = zside * w * 0.96
        if open_ > 0.03:
            a0 = P(jaw((x, cy + 1, z0), 1)); a1 = P(jaw((x + 1.5, cy + 6, z0), 1))
            b0 = P(jaw((x + 3, cy + 3, z0 * 0.95), -1)); b1 = P(jaw((x + 4, cy - 3, z0 * 0.95), -1))
            for q0, q1 in ((a0, a1), (b0, b1)):
                det.append(f'<path d="M{q0[0] - 1.6 * s:.1f} {q0[1]:.1f} L{q1[0]:.1f} {q1[1]:.1f} L{q0[0] + 1.6 * s:.1f} {q0[1]:.1f} Z" fill="#F6F2DE"/>')
        else:
            dn = 1 if k % 2 == 0 else -1
            q0 = P((x, cy + 1, z0)); q1 = P((x + 1, cy + 1 + dn * 4.5, z0))
            det.append(f'<path d="M{q0[0] - 1.5 * s:.1f} {q0[1]:.1f} L{q1[0]:.1f} {q1[1]:.1f} L{q0[0] + 1.5 * s:.1f} {q0[1]:.1f} Z" fill="#F6F2DE"/>')
    # nostril knob, eyes on raised bumps
    part = 1 if open_ > 0.03 else 0
    nk = P(jaw((143, -33, 0), part))
    det.append(f'<ellipse cx="{nk[0]:.1f}" cy="{nk[1]:.1f}" rx="{7 * s:.1f}" ry="{4 * s:.1f}" fill="{TOP}"/><circle cx="{nk[0] - 2 * s:.1f}" cy="{nk[1] - 1 * s:.1f}" r="{1.3 * s:.1f}" fill="#1A2010"/><circle cx="{nk[0] + 2 * s:.1f}" cy="{nk[1] - 1 * s:.1f}" r="{1.3 * s:.1f}" fill="#1A2010"/>')
    eyes = []
    for side in (-1, 1):
        bump = P(jaw((80, -42, side * 12), part)); e = P(jaw((82, -46, side * 12), part))
        k = s * K(e[2])
        o = f'<ellipse cx="{bump[0]:.1f}" cy="{bump[1]:.1f}" rx="{8.5 * k:.1f}" ry="{6.5 * k:.1f}" fill="{TOP}"/>'
        if blink > 0.5:
            o += f'<path d="M{e[0] - 5 * k:.1f} {e[1]:.1f} L{e[0] + 5 * k:.1f} {e[1]:.1f}" stroke="#1A2410" stroke-width="{2 * k:.1f}"/>'
        else:
            o += (glow(e[0], e[1], 14 * k, "#FFE04A", 0.5 * eye_glow, 4) if eye_glow > 0 else "")
            o += (f'<ellipse cx="{e[0]:.1f}" cy="{e[1]:.1f}" rx="{5 * k:.1f}" ry="{4.4 * k:.1f}" fill="#E8C83A"/>'
                  f'<ellipse cx="{e[0]:.1f}" cy="{e[1]:.1f}" rx="{1.1 * k:.1f}" ry="{3.9 * k:.1f}" fill="#120A04"/>'
                  f'<circle cx="{e[0] - 1.6 * k:.1f}" cy="{e[1] - 1.7 * k:.1f}" r="{1.2 * k:.1f}" fill="#FFFFFF" opacity="0.85"/>')
        eyes.append((e[2], o))
    eyes.sort(key=lambda q: -q[0])
    LAST.clear()
    LAST.update(tip=P(jaw((146, AX, 0), 0))[:2], eye=P(jaw((82, -46, 12 * zside), part))[:2], hinge=P((66, AX, 0))[:2],
                snout=P(jaw((120, -34, 0), part))[:2], lowtip=P(jaw((146, AX + 2, 0), -1))[:2])
    far = "".join(v for z, v in sorted(layers, key=lambda q: -q[0]) if z > zb_)
    nearl = "".join(v for z, v in sorted(layers, key=lambda q: -q[0]) if z <= zb_)
    shadow = f'<ellipse cx="{ox:.1f}" cy="{oy + 2:.1f}" rx="{(190 * abs(c) + 70 * abs(si)) * s:.1f}" ry="{12 * s:.1f}" fill="#05030F" opacity="{0.0 if sil else 0.25:.2f}" filter="url(#b6)"/>'
    # head in front when it points at the camera, behind the body when it points away
    hz = P((110, -26, 0))[2]
    if hz <= zb_ or closed:
        return shadow + far + body + nearl + head + "".join(det) + "".join(v for _, v in eyes)
    return shadow + far + head + "".join(det) + "".join(v for _, v in eyes) + body + nearl


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
             e2=(75, -270), h2=(150, -170), e1=(40, -300), h1=(110, -320),
             face=face or fc(open=1.4, lift=1.0, knit=0.9, mouth="grit", look=(1, 0)))
    return J


# ------------------------------------------------------------------ hands (v2: rounded, with sleeve and knuckles)
def fist(x, y, s=1.0, ang=0.0, thumb_out=False, sleeve=170):
    """Side-view fist at (x, y) pointing along +x (rotate with ang), forearm + sleeve trailing back along -x."""
    sk, sk2, sk3 = R3.YOU.skin
    arm = (f'<path d="M{-sleeve} -20 L-30 -18 L-30 18 L{-sleeve} 22 Z" fill="{TP[0]}"/>'
           f'<rect x="-46" y="-21" width="18" height="42" rx="6" fill="{TP[1]}"/>'
           + "".join(f'<path d="M{-44 + 4 * k} -18 L{-44 + 4 * k} 18" stroke="{TP[0]}" stroke-width="1.6" opacity="0.6"/>' for k in range(4))
           + f'<path d="M-30 -14 L-8 -16 L-8 16 L-30 14 Z" fill="{sk2}"/>')
    hand = (f'<path d="M-12 -26 Q20 -30 30 -14 Q36 0 30 16 Q20 30 -12 26 Q-20 0 -12 -26 Z" fill="{sk}"/>'
            + "".join(f'<path d="M{18 + 4 * abs(k - 1.5):.0f} {-19 + 12 * k} q8 3 0 10" stroke="{sk2}" stroke-width="2.4" fill="none" stroke-linecap="round"/>' for k in range(4))
            + f'<ellipse cx="6" cy="-16" rx="10" ry="5" fill="{sk3}" opacity="0.45"/>')
    th = (f'<path d="M-6 -22 Q14 -40 46 -36 Q52 -32 46 -28 Q20 -26 4 -12 Z" fill="{sk}" stroke="{sk2}" stroke-width="2"/>' if thumb_out else
          f'<path d="M-8 -20 Q8 -30 20 -24 Q24 -18 16 -14 Q4 -14 -4 -8 Z" fill="{sk}" stroke="{sk2}" stroke-width="2"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})">{arm}{hand}{th}</g>'


def hands_on_snout(x, y, s=1.0, t=0.0, depth=26.0, gap=34.0):
    """Two hands clamping a snout whose top edge runs through (x, y): arms come down from the upper left,
    the back of each hand rests on top, the fingers wrap down the near side (depth = snout height in px)."""
    sk, sk2, sk3 = R3.YOU.skin
    o = ""
    for k, dx in enumerate((-gap, 0.0)):
        hx = x + dx * s
        sq = 1.5 * math.sin(t * 9 + k)                 # squeeze tremor
        ax0, ay0 = hx - 150 * s, y - 210 * s           # forearm start (off toward the boy)
        o += (f'<path d="M{ax0:.1f} {ay0:.1f} Q{hx - 60 * s:.1f} {y - 120 * s:.1f} {hx - 14 * s:.1f} {y - 26 * s:.1f}" stroke="{TP[0]}" stroke-width="{40 * s:.1f}" fill="none" stroke-linecap="round"/>'
              f'<path d="M{ax0 + 8 * s:.1f} {ay0 - 6 * s:.1f} Q{hx - 56 * s:.1f} {y - 128 * s:.1f} {hx - 18 * s:.1f} {y - 36 * s:.1f}" stroke="{TP[2]}" stroke-width="{6 * s:.1f}" fill="none" opacity="0.35"/>'
              f'<path d="M{hx - 34 * s:.1f} {y - 48 * s:.1f} L{hx - 2 * s:.1f} {y - 26 * s:.1f}" stroke="{TP[1]}" stroke-width="{16 * s:.1f}" stroke-linecap="round"/>')
        # back of the hand lying across the top of the snout
        o += (f'<path d="M{hx - 22 * s:.1f} {y - 22 * s:.1f} Q{hx + 4 * s:.1f} {y - 30 * s:.1f} {hx + 30 * s:.1f} {y - 8 * s:.1f} '
              f'L{hx + 30 * s:.1f} {y + 2:.1f} L{hx - 24 * s:.1f} {y + 2:.1f} Z" fill="{sk}" stroke="{sk2}" stroke-width="{2 * s:.1f}"/>')
        # four fingers curling down over the near side
        for f in range(4):
            fx = hx - 16 * s + f * 13 * s
            L = depth * (0.72 + 0.12 * math.sin(f * 1.7)) + sq
            o += (f'<path d="M{fx:.1f} {y - 6 * s:.1f} L{fx:.1f} {y + L:.1f}" stroke="{sk2}" stroke-width="{12.5 * s:.1f}" stroke-linecap="round"/>'
                  f'<path d="M{fx:.1f} {y - 6 * s:.1f} L{fx:.1f} {y + L - 1:.1f}" stroke="{sk}" stroke-width="{10 * s:.1f}" stroke-linecap="round"/>'
                  f'<path d="M{fx - 3 * s:.1f} {y + L * 0.45:.1f} q{3 * s:.1f} {2 * s:.1f} {6 * s:.1f} 0" stroke="{sk2}" stroke-width="{1.4 * s:.1f}" fill="none"/>')
        # thumb pressing on top
        o += f'<path d="M{hx - 20 * s:.1f} {y - 18 * s:.1f} Q{hx - 8 * s:.1f} {y - 36 * s:.1f} {hx + 16 * s:.1f} {y - 30 * s:.1f}" stroke="{sk2}" stroke-width="{12 * s:.1f}" stroke-linecap="round" fill="none"/>'
        o += f'<path d="M{hx - 20 * s:.1f} {y - 18 * s:.1f} Q{hx - 8 * s:.1f} {y - 36 * s:.1f} {hx + 16 * s:.1f} {y - 30 * s:.1f}" stroke="{sk}" stroke-width="{9.5 * s:.1f}" stroke-linecap="round" fill="none"/>'
    return o
