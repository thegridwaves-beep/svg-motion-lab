"""New coverage: side-profile character with walk/run cycles, POV hands, top-down ground, silhouettes."""
import math, random, sys
sys.path.insert(0, "/home/claude/bible"); sys.path.insert(0, "/home/claude/ant"); sys.path.insert(0, "/home/claude/ant2")
import kit as K
from kit import inside, P, S, E, C, R, U, g
import scene_people as SP
import assets as A
from assets import GREENS
YOU = A.YOU
rim = SP.rimmed
TAU = 2 * math.pi


# ------------------------------------------------------------------ side profile (faces right, feet at y=0)
def _profile_head(expr="neutral", blink=False, p=YOU):
    sk, hr = p.skin, p.hair
    o = []
    back_hair = P("M -58 34 Q -72 -66 4 -74 Q 60 -72 58 -22 Q 34 -44 8 -38 Q -12 -10 -22 36 Z")
    o.append(rim(back_hair, hr[1], hr[1], hr[2], 5))
    face = P("M -38 -2 Q -40 -56 10 -58 Q 52 -56 54 -14 Q 64 -4 66 6 Q 64 14 54 16 Q 52 44 22 54 Q -12 58 -30 34 Q -40 18 -38 -2 Z")
    o.append(rim(face, *sk, 6))
    o.append(rim(E(-10, 6, 10, 13), sk[1], sk[1], sk[2], 3))
    o.append(f'<path d="M-12 0 Q-6 6 -12 12" stroke="{sk[1]}" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.7"/>')
    fringe = P("M -60 4 Q -68 -72 6 -78 Q 62 -74 60 -20 Q 44 -40 26 -42 Q 22 -30 6 -28 Q -20 -30 -30 -6 Q -44 -2 -60 4 Z")
    o.append(rim(fringe, *hr, 5))
    o.append(inside(fringe, f'<path d="M-30 -62 Q4 -76 38 -60 L37 -55 Q4 -70 -29 -57 Z" fill="{hr[2]}" opacity="0.8"/>'))
    o.append(f'<ellipse cx="26" cy="16" rx="11" ry="7" fill="#FF7A8A" opacity="0.35"/>')
    if blink or expr == "sleepy":
        o.append('<path d="M28 -6 Q36 -1 44 -6" stroke="#2A1430" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    else:
        big = expr in ("surprised", "scared")
        o.append(f'<ellipse cx="37" cy="-6" rx="{8 if big else 7}" ry="{11 if big else 9}" fill="#FFFFFF"/>')
        o.append(f'<circle cx="{40 if not big else 39}" cy="-5" r="{5 if big else 5.5}" fill="#2A1430"/><circle cx="42" cy="-8" r="1.6" fill="#FFFFFF"/>')
    by = -26 if expr in ("surprised", "scared") else -21
    o.append(f'<path d="M26 {by} Q36 {by-6} 48 {by-2}" stroke="{hr[0]}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    if expr == "surprised" or expr == "scared":
        o.append('<ellipse cx="46" cy="32" rx="6" ry="8" fill="#5A1E2E"/>')
    elif expr == "happy":
        o.append('<path d="M38 26 Q48 34 56 26" stroke="#5A1E2E" stroke-width="4" fill="none" stroke-linecap="round"/>')
    elif expr == "strain":
        o.append('<path d="M38 30 L56 28" stroke="#5A1E2E" stroke-width="4" stroke-linecap="round"/>')
    else:
        o.append('<path d="M42 30 Q48 32 54 29" stroke="#5A1E2E" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    return "".join(o)


def _leg(hip, knee, foot, p, far):
    col = (p.bottom[1], p.bottom[1], p.bottom[0]) if far else p.bottom
    leg = S(f"M {hip[0]:.1f} {hip[1]:.1f} Q {knee[0]:.1f} {knee[1]:.1f} {foot[0]:.1f} {foot[1] - 14:.1f}", 40)
    fx, fy = foot
    shoe = P(f"M {fx-22:.1f} {fy:.1f} Q {fx-26:.1f} {fy-22:.1f} {fx-6:.1f} {fy-24:.1f} Q {fx+20:.1f} {fy-22:.1f} {fx+38:.1f} {fy-8:.1f} Q {fx+42:.1f} {fy:.1f} {fx+34:.1f} {fy:.1f} Z")
    sc = (p.shoe[1], p.shoe[1], "#FFFFFF") if far else (p.shoe[0], p.shoe[1], "#FFFFFF")
    return rim(leg, *col, 5) + rim(shoe, *sc, 3) + f'<path d="M{fx-22:.1f} {fy-3:.1f} L{fx+38:.1f} {fy-3:.1f}" stroke="#FF4F9A" stroke-width="4" stroke-linecap="round" opacity="0.8"/>'


def _arm(sh, el, hand, p, far):
    col = (p.top[1], p.top[1], p.top[0]) if far else p.top
    sk = (p.skin[1], p.skin[1], p.skin[0]) if far else p.skin
    import rig2, math as _m
    dx, dy = hand[0] - el[0], hand[1] - el[1]
    L = _m.hypot(dx, dy) or 1
    wx, wy = hand[0] - dx / L * 13, hand[1] - dy / L * 13
    sleeve = rig2._limb(sh[0], sh[1], el[0], el[1], wx, wy, 32, 25)
    return rig2._hand(hand[0], hand[1], el[0], el[1], sk, 1) + rim(sleeve, *col, 5)


def side(pose="walk", ph=0.0, expr="neutral", blink=False, lean=None, p=YOU):
    """Profile view facing right. pose: stand, walk, run, reach, crouch, brace, carry, shiver, push."""
    s = math.sin(TAU * ph)
    cz = math.cos(TAU * ph)
    hip = (0.0, -200.0)
    bob = 0.0
    if pose == "walk":
        amp, lift, arm = 46, 20, 40
        bob = -6 * abs(cz)
    elif pose == "run":
        amp, lift, arm = 78, 46, 70
        bob = -14 * abs(cz)
    else:
        amp, lift, arm = 0, 0, 0
    lean_d = lean if lean is not None else {"run": 12, "walk": 3, "push": 16, "brace": -6, "crouch": 8, "shiver": 4, "cower": 10}.get(pose, 0)
    legs = []
    for k, sign in enumerate((1, -1)):
        u = sign * s
        fx = amp * u
        up = max(0.0, sign * cz) * lift
        fy = -up
        kx = fx * 0.5 + 16 + (12 if up > 4 else 0)
        ky = -110 - up * 0.6
        if pose == "crouch":
            fx, fy, kx, ky = (24 if k else -14), 0, (70 if k else 50), -100
        if pose == "push":
            fx, fy, kx, ky = (-70 if k else -10), 0, (-20 if k else 30), -100
        if pose == "brace":
            fx, fy, kx, ky = (-40 if k else 30), 0, (-14 if k else 26), -104
        if pose == "float":
            fx, fy, kx, ky = (-36 if k else 40), (-10 if k else -34), (-6 if k else 50), -110
        if pose == "cower":
            fx, fy, kx, ky = (-30 if k else 30), 0, (20 if k else 60), -110
        legs.append(((hip[0], hip[1] + bob), (kx, ky + bob * 0.5), (fx, fy)))
    sh = (6.0, -342.0 + bob)
    arms = []
    for k, sign in enumerate((-1, 1)):
        u = sign * s
        if pose in ("walk", "run"):
            hx = sh[0] + arm * u
            hy = -215 + (40 if pose == "run" else 0) - abs(u) * 18
            ex = sh[0] - 20 + arm * u * 0.3
            ey = -280 + (10 if pose == "run" else 0)
            if pose == "run":
                hx = sh[0] + 30 + arm * u
                hy = -260 - u * 30
                ex = sh[0] - 30 + arm * u * 0.25
                ey = -270
        elif pose == "reach":
            hx, hy, ex, ey = (sh[0] + 150, -360, sh[0] + 80, -352) if k else (sh[0] + 20, -210, sh[0] - 10, -275)
        elif pose == "push":
            hx, hy, ex, ey = sh[0] + 140, -330 - 30 * k, sh[0] + 70, -322 - 10 * k
        elif pose == "brace":
            hx, hy, ex, ey = sh[0] + 60, -420 + 20 * k, sh[0] + 64, -330
        elif pose == "carry":
            hx, hy, ex, ey = sh[0] + 30, -480 - 10 * k, sh[0] + 60, -420
        elif pose == "shiver":
            hx, hy, ex, ey = sh[0] + 46 + 4 * k, -300, sh[0] + 46, -250
        elif pose == "crouch":
            hx, hy, ex, ey = sh[0] + 70, -230, sh[0] + 40, -270
        elif pose == "float":
            hx, hy, ex, ey = (sh[0] + 90, -470, sh[0] + 70, -400) if k else (sh[0] - 70, -460, sh[0] - 50, -400)
        elif pose == "cower":
            hx, hy, ex, ey = sh[0] + 40, -470 + 10 * k, sh[0] + 70, -400
        else:
            hx, hy, ex, ey = sh[0] + 6 * sign, -214, sh[0] - 6, -280
        arms.append((sh, (ex, ey + bob), (hx, hy + bob)))
    o = []
    o.append(_arm(*arms[0], p, True))
    o.append(_leg(*legs[0], p, True))
    torso = P(f"M -42 {-196 + bob:.1f} Q -50 {-330 + bob:.1f} -8 {-370 + bob:.1f} Q 42 {-378 + bob:.1f} 46 {-316 + bob:.1f} L 44 {-196 + bob:.1f} Q 0 {-186 + bob:.1f} -42 {-196 + bob:.1f} Z")
    o.append(_leg(*legs[1], p, False))
    o.append(rim(R(-10, -394 + bob, 26, 32, 10), p.skin[1], p.skin[1], p.skin[0], 3))
    o.append(rim(torso, *p.top, 8))
    o.append(inside(torso, "".join(f'<rect x="{-44 + i*10}" y="{-222 + bob:.1f}" width="4" height="26" fill="{p.top[1]}" opacity="0.7"/>' for i in range(10))))
    collar = P(f"M -18 {-370 + bob:.1f} Q 2 {-380 + bob:.1f} 22 {-372 + bob:.1f} Q 24 {-362 + bob:.1f} 16 {-358 + bob:.1f} Q 0 {-366 + bob:.1f} -16 {-360 + bob:.1f} Z")
    o.append(rim(collar, p.top[1], p.top[1], p.top[2], 3))
    o.append(g(_profile_head(expr, blink, p), 4, -438 + bob))
    o.append(_arm(*arms[1], p, False))
    body = "".join(o)
    if pose == "crouch":
        body = f'<g transform="translate(0 40) scale(1 0.88)">{body}</g>'
    return f'<g transform="rotate({lean_d:.2f} 0 0)">{body}</g>'


# ------------------------------------------------------------------ first-person POV arms (screen space)
def pov_arm(x, y, ang, right=True, spread=0.4, p=YOU, shake=0.0):
    """Wrist at (x, y), arm direction ang degrees (0 = fingers pointing up), sleeve runs off-frame behind."""
    o = []
    sl = R(-62, 30, 124, 560, 54)
    o.append(rim(sl, *p.top, 10))
    o.append(inside(sl, "".join(f'<rect x="{-60 + i*12}" y="30" width="5" height="44" fill="{p.top[1]}" opacity="0.7"/>' for i in range(11))))
    sk = p.skin
    fingers = []
    for i, L in enumerate((58, 68, 64, 50)):
        fx = -30 + 20 * i
        rot = (i - 1.5) * 7 * spread
        fingers.append(f'<g transform="rotate({rot:.1f} {fx} -70)">' + rim(R(fx - 10, -70 - L, 20, L + 14, 10), *sk, 4) +
                       f'<ellipse cx="{fx}" cy="{-70 - L + 12}" rx="6" ry="5" fill="#F7D0B8" opacity="0.55"/></g>')
    palm = P("M -46 26 Q -56 -50 -40 -78 L 44 -78 Q 56 -50 46 26 Z")
    thumb = f'<g transform="rotate({-48 - 20*spread:.1f} -40 -10)">' + rim(R(-52, -76, 24, 74, 12), *sk, 4) + '</g>'
    o.append(thumb)
    o.append("".join(fingers))
    o.append(rim(palm, *sk, 6))
    o.append(inside(palm, "".join(f'<ellipse cx="{-30 + 20*i}" cy="-66" rx="7" ry="4" fill="{sk[1]}" opacity="0.45"/>' for i in range(4))))
    body = "".join(o)
    sx = 1 if right else -1
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({sx} 1)">{body}</g>'


# ------------------------------------------------------------------ silhouette with warm halo (needs SIL_DEFS)
SIL_DEFS = ('<filter id="sil" x="-30%" y="-30%" width="160%" height="160%">'
            '<feMorphology in="SourceAlpha" operator="dilate" radius="1.6" result="d"/><feGaussianBlur in="d" stdDeviation="3" result="db"/>'
            '<feFlood flood-color="#FFD9A0" flood-opacity="0.95"/><feComposite in2="db" operator="in" result="halo"/>'
            '<feFlood flood-color="#1A0C34"/><feComposite in2="SourceAlpha" operator="in" result="s"/>'
            '<feMerge><feMergeNode in="halo"/><feMergeNode in="s"/></feMerge></filter>')


def silhouette(svg):
    return f'<g filter="url(#sil)">{svg}</g>'


# ------------------------------------------------------------------ top-down ground (camera looking straight down)
SOIL_TOP = {"gold": ("#7A3A78", "#5A2A62"), "storm": ("#3A3470", "#2A2458"), "day": ("#6A4A88", "#4E3570"), "dawn": ("#5A3080", "#3E2266")}


def topdown(seed=1, mood="gold", cx=480, cy=270, n_peb=90, n_bl=34, k=(1.35, 1.75), avoid=(480, 270, 120), x0=-300, x1=1260, y0=-200, y1=740):
    rr = random.Random(seed)
    a, b = SOIL_TOP.get(mood, SOIL_TOP["gold"])
    o = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{a}"/>']
    for _ in range(26):
        o.append(f'<ellipse cx="{rr.uniform(x0, x1):.0f}" cy="{rr.uniform(y0, y1):.0f}" rx="{rr.uniform(60, 180):.0f}" ry="{rr.uniform(40, 120):.0f}" fill="{b}" opacity="0.5" filter="url(#b16)"/>')
    for _ in range(n_peb):
        x, y = rr.uniform(x0, x1), rr.uniform(y0, y1)
        r = rr.uniform(5, 18)
        col = rr.choice([("#8A7AC8", "#5A4A98", "#C8B8FF"), ("#C87AA8", "#94507A", "#FFC0E0"), ("#4AA88A", "#2E7A62", "#9AF0D0"), ("#6A8AD8", "#4A62A8", "#B0C8FF")])
        o.append(f'<ellipse cx="{x + r*0.4:.1f}" cy="{y + r*0.5:.1f}" rx="{r*1.1:.1f}" ry="{r*0.9:.1f}" fill="#140828" opacity="0.4" filter="url(#b2)"/>')
        o.append(g(rim(E(0, 0, r * 1.1, r * 0.85), *col, max(2, r * 0.3)), x, y))
    bl = []
    for _ in range(n_bl * 3):
        if len(bl) >= n_bl:
            break
        x, y = rr.uniform(x0 + 100, x1 - 100), rr.uniform(y0 + 60, y1 - 60)
        if avoid and math.hypot(x - avoid[0], y - avoid[1]) < avoid[2]:
            continue
        bl.append((x, y))
    shadows, blades = [], []
    for (x, y) in bl:
        kk = rr.uniform(*k)
        tx, ty = cx + (x - cx) * kk, cy + (y - cy) * kk
        dx, dy = tx - x, ty - y
        L = math.hypot(dx, dy) + 1e-6
        nx, ny = -dy / L, dx / L
        w = rr.uniform(12, 26)
        col = rr.choice(GREENS)
        def ax(f, side):
            return f"{x + dx*f + nx*w*side:.1f} {y + dy*f + ny*w*side:.1f}"
        pts = (f"M {ax(0, 0.25)} Q {ax(0.45, 1.15)} {ax(0.8, 0.8)} Q {ax(0.96, 0.35)} {tx:.1f} {ty:.1f} "
               f"Q {ax(0.96, -0.35)} {ax(0.8, -0.8)} Q {ax(0.45, -1.15)} {ax(0, -0.25)} Z")
        shadows.append(f'<path d="M {x + nx*w:.1f} {y + ny*w:.1f} L {x + 60 + nx*w*0.3:.1f} {y + 90:.1f} L {x - nx*w:.1f} {y - ny*w:.1f} Z" fill="#120626" opacity="0.35" filter="url(#b8)"/>')
        sh = P(pts)
        half = f"M {x:.1f} {y:.1f} L {tx:.1f} {ty:.1f} L {x - nx*w*2:.1f} {y - ny*w*2:.1f} Z"
        f1, d1 = K.blur_f(3)
        blades.append((L, d1 + sh(col[0] if isinstance(col, tuple) else col) +
                       inside(sh, f'<g{f1}><path d="{half}" fill="#0E3A3A" opacity="0.4"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{w*2.2:.1f}" fill="#0A1E2A" opacity="0.55"/></g>' + f'<circle cx="{x + dx*0.85:.1f}" cy="{y + dy*0.85:.1f}" r="{w*1.1:.1f}" fill="#E8FFD8" opacity="0.3" filter="url(#b8)"/>')))
    blades.sort()
    return "".join(o) + "".join(shadows) + "".join(b for _, b in blades)


def top_contact(x, y, r, op=0.4):
    return f'<ellipse cx="{x + r*0.25:.1f}" cy="{y + r*0.3:.1f}" rx="{r:.1f}" ry="{r*0.85:.1f}" fill="#120626" opacity="{op}" filter="url(#b8)"/>'


# ------------------------------------------------------------------ dutch angle / focus helpers
def dof(svg, b=8):
    return f'<g filter="url(#b{b})">{svg}</g>'
