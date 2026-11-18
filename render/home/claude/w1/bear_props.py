"""Bear Short props: a 3D bear (grizzly or black bear, any yaw, gallop/walk/skid, roar), forest trail sets,
bear spray, the spray cloud, a stick, the boy's run/walk cycles and backpack."""
import math, random
from wcore import *
from botfly_mt import fg_hairs, dust, flare, streaks, hstreaks, flashw
from pose2 import back as back_pose

L_FOREST = Light("brDay", amb=(1.0, 0.97, 0.9), sat=1.0, key="#FFE6B0", key_op=0.16, ang=-55, spread=0.8, shade="#1A2A3A", shade_op=0.32, rim="#FFF4D0", rim_op=0.5, rim_w=7)
L_SHADE = Light("brShade", amb=(0.82, 0.88, 0.95), sat=0.9, key="#FFD890", key_op=0.3, ang=-40, spread=0.8, shade="#0A1A2A", shade_op=0.45, rim="#FFE8B0", rim_op=0.6, rim_w=7)
SHADE = "#0A0610"

# fur palettes: (body, dark, light tips, muzzle)
GRIZ = ("#8A5A32", "#5A381E", "#D8AE72", "#7A5030")
GRIZ_DARK = ("#2E241E", "#1A1410", "#7A6A58", "#3A2E24")
BLACK = ("#232028", "#141218", "#4A4452", "#B88E5E")
BLACK_BROWN = ("#8A5430", "#5E361C", "#B8804A", "#C8A070")


# ------------------------------------------------------------------ 3D bear
def _bear3d_old(ox, oy, s=1.0, yaw_deg=0.0, t=0.0, kind="grizzly", fur=None, gait=0.0, run=0.0, roar=0.0,
           head_dy=0.0, head_dx=0.0, skid=0.0, glow_hump=0.0, blink=0.0, lean=0.0, sil=None, persp=0.0):
    """Model: head at +x, ~300 units nose to tail at s=1, ground at y=0 under the body (oy is the ground point),
    z toward the viewer's left. yaw 0 = side view facing right, -90 = charging head-on at the camera, 90 = walking away.
    gait = phase (0..1 loops), run 0 = walk, 1 = gallop. kind 'grizzly' has the shoulder hump, short round ears,
    dished face and long pale claws; 'black' has a straight face, tall ears, no hump, rump higher than shoulders.
    sil = a single colour for a flat silhouette (hump comparison)."""
    yaw = math.radians(yaw_deg); c, si = math.cos(yaw), math.sin(yaw)
    G = kind == "grizzly"
    body, dark, tip, muz = fur or (GRIZ if G else BLACK)
    if sil:
        body = dark = tip = muz = sil
    items = []
    TAU = 2 * math.pi
    ph = TAU * gait
    bob = -(10 * run + 3) * abs(math.sin(ph)) if (run or gait) else 0.0
    pitch = 6 * run * math.sin(ph) * 0.0

    def K(Z):
        return 1.0 / max(0.25, 1 + persp * Z)

    def P(p):
        x, y, z = p
        Z = x * si + z * c; k = K(Z)
        return ox + (x * c - z * si) * s * k, oy + (-90 + (y + 90) * k) * s, Z

    def dk(Z):
        return 0.0 if sil else max(0.0, min(0.5, Z / 160.0 * 0.4))

    def ell(p, rx, ry, rz, col, hl=0.12, op=1.0, zb=0.0, hcol="#FFF4E0"):
        X, Y, Z = P(p); k = K(Z); prx = math.sqrt((rx * c) ** 2 + (rz * si) ** 2) * k; ry = ry * k
        o = f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{prx * s:.1f}" ry="{ry * s:.1f}" fill="{mixc(col, SHADE, dk(Z))}" opacity="{op:.2f}"/>'
        if hl > 0 and not sil:
            o += f'<ellipse cx="{X - 0.2 * prx * s:.1f}" cy="{Y - 0.5 * ry * s:.1f}" rx="{0.55 * prx * s:.1f}" ry="{0.28 * ry * s:.1f}" fill="{hcol}" opacity="{hl:.2f}" filter="url(#b3)"/>'
        items.append((Z + zb, o))

    def line(pts, col, w, op=1.0, zb=0.0, cap="round"):
        q = [P(p) for p in pts]; Z = sum(z for *_, z in q) / len(q)
        items.append((Z + zb, f'<path d="M{" L".join(f"{x:.1f} {y:.1f}" for x, y, _ in q)}" stroke="{mixc(col, SHADE, dk(Z))}" stroke-width="{w * s * K(Z):.1f}" fill="none" stroke-linecap="{cap}" stroke-linejoin="round" opacity="{op:.2f}"/>'))

    def poly(pts, col, op=1.0, zb=0.0):
        q = [P(p) for p in pts]; Z = sum(z for *_, z in q) / len(q)
        items.append((Z + zb, f'<path d="M{" L".join(f"{x:.1f} {y:.1f}" for x, y, _ in q)} Z" fill="{mixc(col, SHADE, dk(Z))}" opacity="{op:.2f}"/>'))

    by = bob
    hd = (head_dx, head_dy)
    # ---- legs (drawn as thick tapered strokes, two segments). Gallop: fronts together, hinds together, offset.
    legs = []
    for front in (True, False):
        for side in (-1, 1):
            hx = 52 if front else -62
            hz = side * 24
            if run > 0 or gait > 0:
                off = (0.0 if front else math.pi) + (0.18 if side > 0 else 0) * (1 + 2 * run)
                sw = math.sin(ph + off); up = max(0.0, math.cos(ph + off))
                stride = lerp(28, 62, run)
                fx = hx + stride * sw; fy = -lerp(10, 34, run) * up
            else:
                fx, fy = hx + (6 if front else -4), 0.0
            if skid > 0 and front:
                fx = hx + 60 * skid; fy = 0
            if skid > 0 and not front:
                fx = hx - 10 * skid
            top = (hx, -70 + by, hz)
            if front:
                knee = ((hx + fx) / 2 + 4, -36 + by * 0.5 + fy * 0.4, hz * 1.02)
            else:
                knee = ((hx + fx) / 2 + 14, -40 + by * 0.5 + fy * 0.4, hz * 1.02)
            foot = (fx, fy - 6, hz * 1.04)
            legs.append((front, side, top, knee, foot))
    for front, side, top, knee, foot in legs:
        line([top, knee], body, 40 if front else 46, zb=2)
        line([knee, foot], body, 30 if front else 30, zb=2)
        # paw + claws
        px, py, pz = foot
        ell((px + 6, py + 2, pz), 18, 9, 13, dark, hl=0, zb=1)
        if front:
            cl = 14 if G else 6
            ccol = "#EDE2C8" if G else "#3A3438"
            for k in range(4):
                zz = pz + (k - 1.5) * 5
                line([(px + 18, py + 2, zz), (px + 18 + cl, py + 6 + cl * 0.25, zz)], ccol, 3.2, zb=-1)
    # ---- body
    rump_y = -100 if not G else -92
    ell((-62, rump_y + 10 + by, 0), 52, 50, 46, body, 0.10)                     # rump / haunch
    ell((-10, -92 + by, 0), 78, 46, 46, body, 0.14)                            # barrel
    ell((44, -96 + by, 0), 50, 50, 44, body, 0.12)                             # chest + shoulders
    ell((20, -66 + by, 0), 66, 22, 36, dark, 0.0, 0.55, zb=-1)                # belly shadow
    if G:
        hk = 1.0
        ell((34, -126 + by, 0), 46, 30 * hk, 34, body, 0.0)                   # the hump
        ell((30, -140 + by, 0), 30, 12, 22, tip, 0.0, 0.35, zb=-0.5)
        if glow_hump > 0:
            X, Y, Z = P((40, -142 + by, 0))
            items.append((-999, f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{48 * s:.1f}" ry="{30 * s:.1f}" fill="none" stroke="#FFE45A" stroke-width="{6 * s:.1f}" opacity="{glow_hump:.2f}"/>'
                                + glow(X, Y, 70 * s, "#FFE45A", 0.45 * glow_hump, 10)))
    # grizzled tips along the back
    if not sil:
        for k in range(9):
            x = -90 + 20 * k
            yb = (-136 if G and 20 < x < 64 else (-128 if not G and x < -40 else -134)) + by + (8 if not G else 0)
            line([(x, yb + 12, 0), (x - 6, yb + 5, 0)], tip if G else mixc(body, "#FFFFFF", 0.12), 4, 0.4, zb=-0.6)
    # tail
    ell((-112, rump_y - 8 + by, 0), 10, 8, 8, body, 0.0)
    # ---- neck + head
    hy = -96 + by + hd[1]; hx0 = 92 + hd[0]
    ell((70 + hd[0] * 0.5, -100 + by + hd[1] * 0.5, 0), 34, 36, 32, body, 0.08)
    ell((hx0, hy, 0), 32, 30, 30, body, 0.16)                                   # skull
    # ears
    for side in (-1, 1):
        if G:
            ell((hx0 - 10, hy - 30, side * 20), 9, 9, 6, body, 0.0, zb=0.5)
            ell((hx0 - 9, hy - 30, side * 20.5), 5, 5, 3, dark, 0.0, zb=0.3)
        else:
            ell((hx0 - 6, hy - 34, side * 17), 9, 14, 6, body, 0.0, zb=0.5)
            ell((hx0 - 5, hy - 34, side * 17.5), 5, 9, 3, dark, 0.0, zb=0.3)
    # snout: grizzly = dished (brow bump then lower snout), black = straight Roman profile
    sy = hy + (10 if G else 4)
    if G:
        ell((hx0 + 8, hy - 20, 0), 20, 10, 22, body, 0.12, zb=0.2)            # brow ridge
    ell((hx0 + 34, sy, 0), 24, 15, 15, muz, 0.12, zb=-0.5)
    # jaw / mouth
    if roar > 0:
        X, Y, Z = P((hx0 + 34, sy + 10, 0))
        jaw_drop = 16 * roar
        ell((hx0 + 28, sy + 12 + jaw_drop, 0), 22, 7, 13, muz, 0.0, zb=-0.4)
        mx, my, mz = P((hx0 + 38, sy + 8 + jaw_drop * 0.5, 0))
        prx = max(5, abs(16 * c) + abs(10 * si))
        items.append((mz - 0.45, f'<ellipse cx="{mx:.1f}" cy="{my:.1f}" rx="{prx * s:.1f}" ry="{(4 + 7 * roar) * s:.1f}" fill="#7A1A2A"/>'
                                 f'<ellipse cx="{mx:.1f}" cy="{my + 3 * roar * s:.1f}" rx="{prx * 0.6 * s:.1f}" ry="{3 * roar * s:.1f}" fill="#D85A6A"/>'
                                 + "".join(f'<path d="M{mx + (k - 1.5) * prx * 0.5 * s:.1f} {my - (3 + 6 * roar) * s:.1f} l{2 * s:.1f} {5 * s:.1f} l{2 * s:.1f} {-5 * s:.1f} Z" fill="#FFF8E8"/>' for k in range(4) if roar > 0.3)))
    else:
        line([(hx0 + 44, sy + 10, -6), (hx0 + 30, sy + 12, 0), (hx0 + 44, sy + 10, 6)], dark, 2.4, zb=-0.6)
    ell((hx0 + 56, sy - 3, 0), 7, 6, 8, "#120C10", 0.3, zb=-0.8)               # nose
    # eyes
    for side in (-1, 1):
        X, Y, Z = P((hx0 + 20, hy - 8, side * 15))
        rr = 3.6 * s * K(Z)
        if blink > 0.5:
            items.append((Z - 0.7, f'<path d="M{X - rr:.1f} {Y:.1f} L{X + rr:.1f} {Y:.1f}" stroke="#0A0608" stroke-width="{1.6 * s:.1f}"/>'))
        else:
            items.append((Z - 0.7, f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{rr:.1f}" fill="#0A0608"/><circle cx="{X - 1.2 * s:.1f}" cy="{Y - 1.2 * s:.1f}" r="{1.1 * s:.1f}" fill="#FFFFFF" opacity="0.85"/>'))
    items.sort(key=lambda it: -it[0])
    out = "".join(v for _, v in items)
    shadow = f'<ellipse cx="{ox + 10 * c * s:.1f}" cy="{oy + 2:.1f}" rx="{(150 * abs(c) + 70 * abs(si)) * s:.1f}" ry="{18 * s:.1f}" fill="#05030F" opacity="{0.0 if sil else 0.3:.2f}" filter="url(#b6)"/>'
    if lean:
        out = f'<g transform="rotate({lean:.1f} {ox:.1f} {oy:.1f})">{out}</g>'
    return shadow + out


# ------------------------------------------------------------------ the boy: walk / run cycles, backpack
def walk_J(ph, run=False, **kw):
    s_, cz = math.sin(TAU * ph), math.cos(TAU * ph)
    amp, lift, arm = (78, 46, 70) if run else (46, 20, 40)
    bob = -(14 if run else 6) * abs(cz)
    J = dict(R3.SIDE)
    for k, sign in ((1, 1), (2, -1)):
        u = sign * s_
        fx = amp * u; up = max(0.0, sign * cz) * lift
        J[f"f{k}"] = (fx, -up)
        J[f"k{k}"] = (fx * 0.5 + 16 + (12 if up > 4 else 0), -110 - up * 0.6 + bob * 0.5)
    for k, sign in ((1, -1), (2, 1)):
        u = sign * s_
        J[f"h{k}"] = (6 + arm * u, -215 - abs(u) * 18); J[f"e{k}"] = (-14 + arm * u * 0.3, -280)
    J["hip"] = (0, bob); J["lean"] = 3
    for k, v in kw.items():
        J[k] = (J["face"] | v) if k == "face" else v
    return J


def run_J(ph, lean=20, panic=1.0, **kw):
    s_, c_ = math.sin(TAU * ph), math.cos(TAU * ph)
    J = dict(R3.SIDE)
    for k, sign in ((1, 1), (2, -1)):
        u = sign * s_; up = max(0.0, sign * c_)
        J[f"f{k}"] = (105 * u - 10, -70 * up)
        J[f"k{k}"] = (60 * u + 46 + 26 * up, -112 - 50 * up)
    for k, sign in ((1, -1), (2, 1)):
        u = sign * s_
        J[f"h{k}"] = (50 + 95 * u, -262 - 55 * u)
        J[f"e{k}"] = (-6 + 40 * u, -300 + 6 * u)
    J["hip"] = (0, -22 * abs(s_) + 10); J["lean"] = lean; J["head"] = (6, 4, -4)
    J["face"] = fc(open=1.3, lift=0.9, knit=0.7 * panic, mouth="scream" if panic > 0.6 else "grit", mo=0.3, look=(1, 0))
    for k, v in kw.items():
        J[k] = (J["face"] | v) if k == "face" else v
    return J


def pack_side(x, y, s, flip=False, bob=0.0, lean=0.0):
    """Hiking backpack seen from the side (boy faces right): snug against his back, tilts with his torso lean."""
    f = -1 if flip else 1
    return (f'<g transform="translate({x:.1f} {y + bob * s:.1f}) scale({f * s:.4f} {s:.4f}) rotate({lean * 0.55:.2f} -10 -200)">'
            '<rect x="-90" y="-374" width="64" height="178" rx="22" fill="#2E7A5A"/><rect x="-84" y="-302" width="40" height="60" rx="12" fill="#246448"/>'
            '<rect x="-90" y="-374" width="12" height="178" rx="6" fill="#1E5A40" opacity="0.6"/>'
            '<rect x="-94" y="-392" width="70" height="30" rx="14" fill="#E8703A"/><rect x="-92" y="-198" width="70" height="20" rx="10" fill="#3A3A4A"/>'
            '<path d="M-30 -230 Q-18 -226 -8 -214" stroke="#1E4A36" stroke-width="9" fill="none" stroke-linecap="round"/></g>')


def pack_strap(x, y, s, flip=False, bob=0.0, lean=0.0):
    """Shoulder strap over the top of his shoulder (drawn over the body)."""
    f = -1 if flip else 1
    return (f'<g transform="translate({x:.1f} {y + bob * s:.1f}) scale({f * s:.4f} {s:.4f}) rotate({lean * 0.55:.2f} -10 -200)">'
            '<path d="M-30 -368 Q-10 -384 8 -372 Q16 -360 14 -336" stroke="#1E4A36" stroke-width="11" fill="none" stroke-linecap="round"/></g>')


def kid_side(J, uid, x, y, s, Lt, flip=False):
    """Side-view boy wearing the backpack: pack behind, body, strap on top. Pack follows hip bob and torso lean."""
    b, ln = J.get("hip", (0, 0))[1], J.get("lean", 0.0)
    return pack_side(x, y, s, flip, b, ln) + boy(J, uid, x, y, s, Lt, side=True, flip=flip) + pack_strap(x, y, s, flip, b, ln)


def hiker(t, x, y, s, Lt, uid, ph=None, flip=False, run=False, face=None):
    ph = (t * (1.6 if run else 0.9)) % 1 if ph is None else ph
    J = (run_J(ph) if run else walk_J(ph, face=face or fc(open=1.0, mouth="smile", look=(1, 0))))
    return kid_side(J, uid, x, y, s, Lt, flip)


def prone(uid, x, y, s, Lt, rot=-90, spread=1.0):
    """The boy lying face down, hands laced behind his neck, legs spread (seen from straight above = his back)."""
    J = R3.FRONT | dict(el=(-96, -420), hl=(-26, -470), er=(96, -420), hr=(26, -470),
                        kl=(-40 - 30 * spread, -100), fl=(-50 - 50 * spread, 0), kr=(40 + 30 * spread, -100), fr=(50 + 50 * spread, 0),
                        face=fc(open=0.2))
    body = back_pose(J)
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">' + lit(body, uid, 0, 0, s, Lt)
            + f'<g transform="scale({s:.4f})">{PACK_BACK}</g></g>')


# ------------------------------------------------------------------ forest world
def forest_sky(t, warm=0.0):
    top = mixc("#5AA8E8", "#F0A060", warm); bot = mixc("#D8F0FF", "#FFE0A8", warm)
    return (f'<rect x="-700" y="-900" width="2360" height="1700" fill="{top}"/>'
            f'<rect x="-700" y="-60" width="2360" height="420" fill="{bot}" opacity="0.85" filter="url(#b40)"/>'
            + glow(760, -40, 260, "#FFF4C8", 0.6, 30))


def mountains(y0=250, col="#8AA8C8", seed=2):
    r = random.Random(seed)
    pts = [(-700, y0)]
    x = -700
    while x < 1700:
        x += r.uniform(90, 180); pts.append((x, y0 - r.uniform(80, 240)))
    pts.append((1700, y0))
    d = "M" + " L".join(f"{a:.0f} {b:.0f}" for a, b in pts) + " L1700 900 L-700 900 Z"
    snow = "".join(f'<path d="M{a - 26:.0f} {b + 34:.0f} L{a:.0f} {b:.0f} L{a + 26:.0f} {b + 34:.0f} Z" fill="#F4F8FF" opacity="0.85"/>' for a, b in pts[1:-1] if b < y0 - 170)
    return f'<path d="{d}" fill="{col}"/>' + snow


def pine(x, y, h, col, col2=None):
    col2 = col2 or mixc(col, "#000000", 0.2)
    w = h * 0.36
    o = f'<rect x="{x - h * 0.03:.1f}" y="{y - h * 0.18:.1f}" width="{h * 0.06:.1f}" height="{h * 0.2:.1f}" fill="#4A3020"/>'
    for k in range(4):
        yy = y - h * (0.12 + 0.22 * k); ww = w * (1 - 0.2 * k)
        o += f'<path d="M{x - ww:.1f} {yy:.1f} L{x:.1f} {yy - h * 0.36:.1f} L{x + ww:.1f} {yy:.1f} Q{x:.1f} {yy + h * 0.05:.1f} {x - ww:.1f} {yy:.1f} Z" fill="{col}"/>'
        o += f'<path d="M{x:.1f} {yy - h * 0.36:.1f} L{x + ww:.1f} {yy:.1f} Q{x + ww * 0.5:.1f} {yy + h * 0.03:.1f} {x:.1f} {yy + h * 0.02:.1f} Z" fill="{col2}"/>'
    return o


def pine_row(y, seed, col, n=18, h0=160, h1=260, x0=-700, x1=1660):
    r = random.Random(seed)
    xs = sorted(r.uniform(x0, x1) for _ in range(n))
    return "".join(pine(x, y + r.uniform(-8, 8), r.uniform(h0, h1), col) for x in xs)


def grass_tufts(y0, y1, seed=3, n=50, col="#5A8A3A", x0=-600, x1=1560):
    r = random.Random(seed); o = []
    for _ in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1); k = 0.6 + (y - y0) / max(1, y1 - y0)
        o.append(f'<path d="M{x:.0f} {y:.0f} q{-4 * k:.1f} {-14 * k:.1f} {-10 * k:.1f} {-20 * k:.1f} M{x:.0f} {y:.0f} q{1 * k:.1f} {-16 * k:.1f} {4 * k:.1f} {-24 * k:.1f} M{x:.0f} {y:.0f} q{5 * k:.1f} {-10 * k:.1f} {12 * k:.1f} {-16 * k:.1f}" stroke="{col}" stroke-width="{2.6 * k:.1f}" fill="none" stroke-linecap="round"/>')
    return "".join(o)


def rocks(y0, y1, seed=4, n=10, x0=-600, x1=1560):
    r = random.Random(seed); o = []
    for _ in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1); w = r.uniform(10, 26) * (0.6 + (y - y0) / max(1, y1 - y0))
        o.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{w:.1f}" ry="{w * 0.55:.1f}" fill="#8A8A90"/><ellipse cx="{x - w * 0.2:.0f}" cy="{y - w * 0.2:.0f}" rx="{w * 0.5:.1f}" ry="{w * 0.25:.1f}" fill="#B8B8C0"/>')
    return "".join(o)


def forest_back(t=0.0, warm=0.0):
    """Static far layers: sky, mountains, two hazy pine rows."""
    return (forest_sky(t, warm) + mountains(250) + f'<rect x="-700" y="180" width="2360" height="120" fill="#C8E0F0" opacity="0.4" filter="url(#b20)"/>'
            + pine_row(300, 11, "#3E6A6A", 30, 120, 190) + f'<rect x="-700" y="200" width="2360" height="120" fill="#D8ECF4" opacity="0.25" filter="url(#b20)"/>'
            + pine_row(330, 12, "#2E5A48", 22, 170, 260))


def trail_side(y0=380):
    """Side-view ground: meadow band with a dirt trail running left-right at y0..y0+60."""
    return (f'<rect x="-700" y="{y0 - 50}" width="2360" height="900" fill="#6A9A48"/>'
            + grass_tufts(y0 - 46, y0 - 6, 5, 70, "#4E7E36")
            + f'<path d="M-700 {y0} Q480 {y0 - 10} 1660 {y0} L1660 {y0 + 64} Q480 {y0 + 74} -700 {y0 + 64} Z" fill="#C8A070"/>'
            + f'<path d="M-700 {y0 + 20} Q480 {y0 + 14} 1660 {y0 + 22}" stroke="#B08A5A" stroke-width="6" fill="none" opacity="0.6"/>'
            + rocks(y0 + 10, y0 + 56, 6, 14) + f'<rect x="-700" y="{y0 + 64}" width="2360" height="900" fill="#5A8A3E"/>'
            + grass_tufts(y0 + 70, y0 + 300, 7, 120, "#3E6E2E"))


def trail_persp(vy=300, w0=40, w1=900):
    """Front view: the dirt trail narrowing to the vanishing point (480, vy)."""
    return (f'<rect x="-700" y="{vy - 20}" width="2360" height="1000" fill="#6A9A48"/>'
            f'<path d="M{480 - w0 / 2} {vy} L{480 + w0 / 2} {vy} L{480 + w1 / 2} 760 L{480 - w1 / 2} 760 Z" fill="#C8A070"/>'
            f'<path d="M{480 - w0 / 4} {vy} L{480 - w1 / 4} 760" stroke="#B08A5A" stroke-width="8" opacity="0.5"/>'
            + grass_tufts(vy, 760, 9, 140, "#3E6E2E") + rocks(vy + 40, 700, 10, 12, 300, 660))


def fg_pines(t, xs=(180, 820), y=640, h=700):
    return "".join(pine(x, y, h, "#163A2C") for x in xs)


# ------------------------------------------------------------------ gear
def spray_can(x, y, s=1.0, ang=0.0, safety=1.0):
    """Bear spray canister, nozzle up. safety 1 = clip on, 0 = clip off."""
    o = ('<rect x="-26" y="-110" width="52" height="130" rx="12" fill="#E8602A"/><rect x="-26" y="-60" width="52" height="34" fill="#1A1A22"/>'
         + text(0, -38, "SPRAY", 13, "#FFFFFF", 700, "middle")
         + '<rect x="-14" y="-138" width="28" height="30" rx="6" fill="#1A1A22"/><rect x="-6" y="-150" width="22" height="14" rx="4" fill="#2A2A32"/>'
         '<rect x="-20" y="-104" width="10" height="110" rx="5" fill="#FFFFFF" opacity="0.25"/>')
    if safety > 0:
        o += f'<g transform="translate({30 * (1 - safety):.1f} {-40 * (1 - safety):.1f}) rotate({60 * (1 - safety):.1f} 0 -124)"><rect x="-22" y="-130" width="44" height="12" rx="5" fill="#FFD23A" stroke="{INK}" stroke-width="2"/></g>'
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})">{o}</g>'


def spray_cloud(x, y, u, t, dirx=1, s=1.0, seed=3, col="#FF7A3A"):
    """An expanding orange pepper cloud blasting along dirx from (x, y). u 0..1 = growth."""
    if u <= 0:
        return ""
    r = random.Random(seed); o = []
    for k in range(26):
        d = r.uniform(0.1, 1.0) * u
        px = x + dirx * (40 + 420 * d) * s; py = y + (r.uniform(-1, 1) * 90 * d - 20 * d) * s
        rr = (20 + 90 * d) * s * r.uniform(0.7, 1.2)
        cc = mixc(col, "#FFC8A0", r.uniform(0, 0.5))
        o.append(f'<circle cx="{px + 6 * math.sin(t * 3 + k):.1f}" cy="{py:.1f}" r="{rr:.1f}" fill="{cc}" opacity="{0.42 * (1 - 0.4 * d):.2f}"/>')
    jet = f'<path d="M{x:.1f} {y:.1f} L{x + dirx * 300 * u * s:.1f} {y - 30 * s:.1f} L{x + dirx * 300 * u * s:.1f} {y + 30 * s:.1f} Z" fill="{col}" opacity="0.6" filter="url(#b6)"/>'
    return f'<g filter="url(#b4)">{jet}{"".join(o)}</g>'


def stick(x, y, s=1.0, ang=0.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})"><path d="M0 0 L200 -6" stroke="#6A4428" stroke-width="16" stroke-linecap="round"/>'
            '<path d="M110 -4 L140 -30" stroke="#6A4428" stroke-width="8" stroke-linecap="round"/><path d="M20 -2 L180 -8" stroke="#8A6040" stroke-width="4" opacity="0.6"/></g>')


def impact_star(x, y, u, s=1.0, col="#FFE45A"):
    if u <= 0:
        return ""
    k = s * (0.6 + 0.6 * eo(u))
    pts = []
    for i in range(16):
        r = (110 if i % 2 == 0 else 46) * k
        a = TAU * i / 16 + 0.2
        pts.append(f"{x + r * math.cos(a):.1f} {y + r * math.sin(a):.1f}")
    return (f'<path d="M{" L".join(pts)} Z" fill="{col}" stroke="{INK}" stroke-width="6" stroke-linejoin="round" opacity="{clamp((1 - u) * 3):.2f}"/>'
            f'<circle cx="{x}" cy="{y}" r="{40 * k:.1f}" fill="#FFFFFF" opacity="{clamp((1 - u) * 3):.2f}"/>')


def kmh_chip(x, y, val, label_, u, col="#FFFFFF", bg=INK, edge=PINK):
    if u <= 0:
        return ""
    k = 0.7 + 0.3 * eo(min(1, u * 2))
    return (f'<g transform="translate({x} {y}) scale({k:.3f})" opacity="{clamp(u * 3):.2f}"><rect x="-120" y="-50" width="240" height="100" rx="26" fill="{bg}" opacity="0.92" stroke="{edge}" stroke-width="4"/>'
            + text(0, 6, val, 42, col, 700, "middle") + text(0, 36, label_, 18, "#CFC8E8", 600, "middle") + '</g>')


TAU = 2 * math.pi


# ------------------------------------------------------------------ v2: the smooth lofted bear everywhere (keeps the old call signature)
R3.YOU.hair = ("#2B1B14", "#1A100B", "#5A4030")          # dark brown fringe in every shot (was reading grey-lavender in daylight)
_FILL = {GRIZ_DARK: "url(#bearD)", BLACK_BROWN: "url(#bearBr)", GRIZ: None, BLACK: None}


def bear3d(ox, oy, s=1.0, yaw_deg=0.0, t=0.0, kind="grizzly", fur=None, gait=0.0, run=0.0, roar=0.0,
           head_dy=0.0, head_dx=0.0, skid=0.0, glow_hump=0.0, blink=0.0, lean=0.0, sil=None, persp=0.0):
    import looks as LK
    if sil:
        return _bear3d_old(ox, oy, s, yaw_deg, t, kind, fur, gait, run, roar, head_dy, head_dx, skid, glow_hump, blink, lean, sil, persp)
    o = LK.bearL(ox, oy, s, yaw_deg, t, kind, _FILL.get(fur), gait, run, roar, persp, glow_hump, blink, skid, head_dx)
    if head_dy:
        o = f'<g transform="translate(0 {head_dy * s * 0.3:.1f})">{o}</g>'
    return o


def bear_face(x, y, s=1.0, t=0.0, blink=0.0, angry=0.0, look=(0.0, 0.0), nose=0.0):
    """Head-on grizzly portrait for close-ups: dished face, round ears, brow, pale muzzle, wet nose, small hard eyes."""
    lx, ly = look
    br = 8 * angry
    fur = "".join(f'<path d="M{math.cos(a) * 170:.1f} {math.sin(a) * 160 + 10:.1f} l{math.cos(a + 0.3) * 26:.1f} {math.sin(a + 0.3) * 26:.1f}" stroke="{c}" stroke-width="5" stroke-linecap="round" opacity="0.55"/>'
                  for a, c in [(1.2 + k * 0.33, "#C89A62" if k % 2 else "#4A2C16") for k in range(-16, 3)])
    eyes = ""
    for sd in (-1, 1):
        ex, ey = sd * 62, -32
        eyes += (f'<ellipse cx="{ex}" cy="{ey + 4}" rx="30" ry="20" fill="#3A2212" opacity="0.7" filter="url(#b3)"/>'
                 + (f'<path d="M{ex - 18} {ey} Q{ex} {ey + 6} {ex + 18} {ey}" stroke="#120A06" stroke-width="5" fill="none" stroke-linecap="round"/>' if blink > 0.5 else
                    f'<circle cx="{ex + lx * 5}" cy="{ey + ly * 4}" r="14" fill="#1A0E08"/><circle cx="{ex + lx * 5}" cy="{ey + ly * 4}" r="9" fill="#5A2E14"/>'
                    f'<circle cx="{ex + lx * 5}" cy="{ey + ly * 4}" r="5.5" fill="#080404"/><circle cx="{ex + lx * 5 - 4}" cy="{ey + ly * 4 - 5}" r="4" fill="#FFF6E6"/>')
                 + f'<path d="M{ex - 34 * sd * -1 - 0} {ey - 22 + br * (1 if sd < 0 else 1)} Q{ex} {ey - 34 - br * 0.3} {ex + 34 * sd} {ey - 24 - br}" stroke="#3A2210" stroke-width="12" fill="none" stroke-linecap="round" opacity="0.8"/>')
    ears = "".join(f'<g transform="translate({sd * 128} -118)"><circle r="52" fill="url(#bearG)"/><circle r="30" cy="6" fill="#3A2414"/><circle r="20" cy="10" fill="#5A3A24" opacity="0.6"/></g>' for sd in (-1, 1))
    tw = 3 * math.sin(t * 11) * nose
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            f'<ellipse cx="0" cy="250" rx="300" ry="140" fill="#6E4628"/>'                                  # chest/shoulders
            f'{ears}'
            f'<path d="M-175 -40 Q-190 -150 -90 -175 Q0 -195 90 -175 Q190 -150 175 -40 Q185 70 120 140 Q60 190 0 192 Q-60 190 -120 140 Q-185 70 -175 -40 Z" fill="url(#bearG)"/>'
            f'<path d="M-150 -60 Q-160 -140 -70 -160 Q0 -175 70 -160 Q160 -140 150 -60" fill="#C08A54" opacity="0.35" filter="url(#b8)"/>'   # sunlit crown
            f'{fur}'
            f'<path d="M-40 -110 Q0 -60 40 -110" stroke="#5A3A20" stroke-width="10" fill="none" opacity="0.5" filter="url(#b3)"/>'        # dished brow
            f'{eyes}'
            f'<ellipse cx="0" cy="70" rx="98" ry="78" fill="#C99A64"/><ellipse cx="0" cy="54" rx="80" ry="50" fill="#DDB27A" opacity="0.7" filter="url(#b8)"/>'
            f'<g transform="translate({tw:.1f} {tw * 0.4:.1f})"><path d="M-46 22 Q-48 -6 0 -8 Q48 -6 46 22 Q40 52 0 58 Q-40 52 -46 22 Z" fill="#1A100C"/>'
            f'<ellipse cx="-14" cy="6" rx="15" ry="7" fill="#FFFFFF" opacity="0.45"/><ellipse cx="-17" cy="34" rx="8" ry="6" fill="#000"/><ellipse cx="17" cy="34" rx="8" ry="6" fill="#000"/></g>'
            f'<path d="M0 58 L0 92 M-40 104 Q0 92 40 104" stroke="#3A2214" stroke-width="7" fill="none" stroke-linecap="round"/>'
            '</g>')


def spray_in_hand(x, y, s=1.0, ang=0.0, safety=1.0):
    """The can gripped in the boy's fist from the side: palm behind, can, four fingers wrapped in front below the label, sleeve."""
    sk, sk2 = R3.YOU.skin[0], R3.YOU.skin[1]
    sleeve = (f'<path d="M-46 36 L46 36 L58 330 L-58 330 Z" fill="{TP[0]}"/><path d="M-46 36 L46 36 L48 70 L-48 70 Z" fill="{TP[1]}"/>'
              + "".join(f'<path d="M{-42 + 12 * k} 40 L{-44 + 12 * k} 68" stroke="{TP[0]}" stroke-width="3" opacity="0.7"/>' for k in range(8)))
    palm = f'<ellipse cx="-6" cy="8" rx="46" ry="40" fill="{sk2}"/>'
    fingers = "".join(f'<rect x="-32" y="{-22 + 15 * k}" width="{60 - 4 * k}" height="15" rx="7.5" fill="{sk}" stroke="{sk2}" stroke-width="2"/>' for k in range(4))
    thumb = f'<path d="M-34 0 Q-44 -26 -14 -30 Q0 -30 2 -22 Q-10 -18 -18 -4 Z" fill="{sk}" stroke="{sk2}" stroke-width="2"/>'
    can = spray_can(0, 0, 1.0, 0.0, safety)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})">{sleeve}{palm}{can}{fingers}{thumb}</g>'


def paw(x, y, s=1.0, ang=0.0, col="#6A4426"):
    """Grizzly paw seen from below: furry foot, dark leathery pad and toe beans, long curved pale claws."""
    claws = "".join(f'<path d="M{-36 + 18 * k} -50 Q{-40 + 18 * k} -96 {-24 + 18 * k} -122 Q{-28 + 18 * k} -92 {-26 + 18 * k} -50 Z" fill="#EFE4CC" stroke="#B8A888" stroke-width="2"/>' for k in range(5))
    fur = "".join(f'<path d="M{70 * math.cos(a):.1f} {56 * math.sin(a):.1f} l{12 * math.cos(a):.1f} {12 * math.sin(a):.1f}" stroke="#4A2C16" stroke-width="5" stroke-linecap="round" opacity="0.6"/>' for a in [k * 0.4 for k in range(16)])
    beans = "".join(f'<ellipse cx="{-36 + 18 * k}" cy="{-34 + 4 * abs(k - 2)}" rx="10" ry="13" fill="#2A1A12"/>' for k in range(5))
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})">{claws}'
            f'<ellipse cx="0" cy="4" rx="74" ry="62" fill="url(#bearG)"/>{fur}'
            f'<path d="M-40 10 Q-44 -14 0 -16 Q44 -14 40 10 Q36 40 0 44 Q-36 40 -40 10 Z" fill="#2A1A12"/>'
            f'<ellipse cx="-10" cy="4" rx="14" ry="6" fill="#FFFFFF" opacity="0.12"/>{beans}</g>')


def claw_swipe(x, y, u, s=1.0):
    """Three fresh claw slashes torn across the frame."""
    if u <= 0:
        return ""
    o = ""
    for k in range(3):
        L = 380 * min(1, u * 3)
        x0, y0 = -190 + 62 * (k - 1), -150 - 88 * (k - 1)
        d = f'M{x0} {y0} q{L * 0.5:.0f} {L * 0.42:.0f} {L:.0f} {L * 0.7:.0f}'
        o += (f'<path d="{d}" stroke="#1A0608" stroke-width="34" fill="none" stroke-linecap="round" opacity="0.6"/>'
              f'<path d="{d}" stroke="#E8303A" stroke-width="16" fill="none" stroke-linecap="round"/>'
              f'<path d="{d}" stroke="#FFFFFF" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.85"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})" opacity="{clamp(2 - u * 2):.2f}">{o}</g>'


PACK_BACK = ('<rect x="-60" y="-388" width="120" height="190" rx="28" fill="#2E7A5A"/>'
             '<rect x="-60" y="-388" width="120" height="190" rx="28" fill="url(#vig)" opacity="0"/>'
             '<rect x="-44" y="-300" width="88" height="70" rx="16" fill="#246448"/><path d="M-44 -282 L44 -282" stroke="#1E5A40" stroke-width="4"/>'
             '<rect x="-66" y="-404" width="132" height="40" rx="18" fill="#E8703A"/><rect x="-10" y="-372" width="20" height="26" rx="5" fill="#3A3A4A"/>'
             '<rect x="-62" y="-206" width="124" height="22" rx="11" fill="#3A3A4A"/>'
             '<path d="M-52 -380 Q-60 -300 -50 -210" stroke="#FFFFFF" stroke-width="6" opacity="0.12" fill="none"/>')
PACK_FRONT = ('<path d="M-44 -364 Q-40 -310 -40 -250" stroke="#1E4A36" stroke-width="10" fill="none" stroke-linecap="round"/>'
              '<path d="M44 -364 Q40 -310 40 -250" stroke="#1E4A36" stroke-width="10" fill="none" stroke-linecap="round"/>'
              '<rect x="-42" y="-312" width="84" height="8" rx="4" fill="#1E4A36"/><rect x="-8" y="-317" width="16" height="18" rx="4" fill="#3A3A4A"/>')


def kid_front(J, uid, x, y, s, Lt, **kw):
    """Front-view boy with the backpack straps over his sweater."""
    return boy(J, uid, x, y, s, Lt, **kw) + f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f})">{PACK_FRONT}</g>'


def kid_back(J, uid, x, y, s, Lt, **kw):
    """Back-view boy (over-the-shoulder shots) with the pack on his back."""
    return boy(J, uid, x, y, s, Lt, backv=True, **kw) + f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f})">{PACK_BACK}</g>'
