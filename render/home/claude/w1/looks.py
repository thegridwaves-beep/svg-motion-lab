"""Cinematic look kit for the Shorts (portrait canvas 540x960): golden-hour skies, layered fog, god rays, aerial-perspective
pine forests, depth-of-field, rim light, dust motes, colour grade, vignette. Plus a smooth lofted 3D bear."""
import math, random, os, sys
sys.path[:0] = ["/home/claude/w1", "/home/claude/ep"]
os.environ.setdefault("SHORT", "bear")
from wcore import *
from croc_props import _hull, _sm, croc3d, CROC_DEFS, mouth_inside

CW, CH = 540, 960
TAU = 2 * math.pi


def L_defs():
    o = []
    for n in (1, 2, 3, 4, 6, 8, 12, 18, 26, 40, 60):
        o.append(f'<filter id="g{n}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{n}"/></filter>')
    # rim light: a warm copy of the silhouette offset toward the light, sitting behind the subject
    for nm, col, dx, dy in (("rimW", "#FFD38A", -5, -4), ("rimR", "#FFD38A", 5, -4), ("rimC", "#BFE6FF", -4, -4), ("rimT", "#FFE2A0", 0, -6)):
        o.append(f'<filter id="{nm}" x="-20%" y="-20%" width="140%" height="140%"><feFlood flood-color="{col}"/><feComposite in2="SourceAlpha" operator="in"/>'
                 f'<feOffset dx="{dx}" dy="{dy}"/><feGaussianBlur stdDeviation="1.2"/><feComposite in2="SourceAlpha" operator="out" result="rim"/>'
                 f'<feMerge><feMergeNode in="rim"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    o.append('<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0.08 0"/></filter>')
    o.append('<linearGradient id="bearG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B07A48"/><stop offset="0.45" stop-color="#7A4E2C"/><stop offset="1" stop-color="#3E2614"/></linearGradient>')
    o.append('<linearGradient id="bearB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5E5866"/><stop offset="0.45" stop-color="#34303A"/><stop offset="1" stop-color="#18161C"/></linearGradient>')
    o.append('<linearGradient id="bearBr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C8864E"/><stop offset="0.45" stop-color="#93582C"/><stop offset="1" stop-color="#4E2C14"/></linearGradient>')
    o.append('<linearGradient id="bearD" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5E4A3A"/><stop offset="0.45" stop-color="#332820"/><stop offset="1" stop-color="#18120E"/></linearGradient>')
    o.append('<radialGradient id="vig" cx="0.5" cy="0.45" r="0.75"><stop offset="0.55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.55"/></radialGradient>')
    return "".join(o) + CROC_DEFS


# ------------------------------------------------------------------ atmosphere
def sky(top="#2A3A6A", mid="#E8905A", low="#FFD89A", horizon=520):
    return (f'<linearGradient id="skyG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="0.55" stop-color="{mid}"/><stop offset="1" stop-color="{low}"/></linearGradient>'
            f'<rect x="-200" y="-200" width="940" height="{horizon + 200}" fill="url(#skyG)"/>')


def sun(x, y, r=46, col="#FFF2C8", glow_col="#FFC870"):
    return (f'<circle cx="{x}" cy="{y}" r="{r * 6}" fill="{glow_col}" opacity="0.25" filter="url(#g60)"/>'
            f'<circle cx="{x}" cy="{y}" r="{r * 2.4}" fill="{glow_col}" opacity="0.45" filter="url(#g26)"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/>')


def god_rays(x, y, ang0=60, ang1=120, n=7, ln=1400, op=0.16, col="#FFE6A8", seed=2):
    r = random.Random(seed); o = []
    for k in range(n):
        a = math.radians(lerp(ang0, ang1, (k + r.uniform(-0.3, 0.3)) / max(1, n - 1))); w = math.radians(r.uniform(1.2, 3.5))
        p1 = (x + ln * math.cos(a - w), y + ln * math.sin(a - w)); p2 = (x + ln * math.cos(a + w), y + ln * math.sin(a + w))
        o.append(f'<path d="M{x} {y} L{p1[0]:.0f} {p1[1]:.0f} L{p2[0]:.0f} {p2[1]:.0f} Z" fill="{col}" opacity="{op * r.uniform(0.5, 1.2):.2f}"/>')
    return f'<g filter="url(#g8)" style="mix-blend-mode:screen">{"".join(o)}</g>'


def fog(y, h=120, op=0.55, col="#F6E2C8", blur=26):
    return f'<rect x="-200" y="{y - h / 2}" width="940" height="{h}" fill="{col}" opacity="{op}" filter="url(#g{blur})"/>'


def pine(x, y, h, col):
    w = h * 0.3; o = [f'<path d="M{x - h * 0.02:.1f} {y} L{x - h * 0.02:.1f} {y - h * 0.2:.1f} L{x + h * 0.02:.1f} {y - h * 0.2:.1f} L{x + h * 0.02:.1f} {y} Z" fill="{col}"/>']
    for k in range(5):
        yy = y - h * (0.15 + 0.17 * k); ww = w * (1 - 0.17 * k)
        o.append(f'<path d="M{x - ww:.1f} {yy:.1f} Q{x - ww * 0.4:.1f} {yy - h * 0.12:.1f} {x:.1f} {yy - h * 0.3:.1f} Q{x + ww * 0.4:.1f} {yy - h * 0.12:.1f} {x + ww:.1f} {yy:.1f} Q{x:.1f} {yy - h * 0.04:.1f} {x - ww:.1f} {yy:.1f} Z" fill="{col}"/>')
    return "".join(o)


def pine_layer(y, col, n=12, h0=140, h1=260, seed=1, x0=-120, x1=660, blur=0, base=True):
    r = random.Random(seed)
    o = "".join(pine(r.uniform(x0, x1), y + r.uniform(-6, 6), r.uniform(h0, h1), col) for _ in range(n))
    if base:
        o += f'<rect x="-200" y="{y - 30}" width="940" height="60" fill="{col}" filter="url(#g6)"/>'
    return f'<g filter="url(#g{blur})">{o}</g>' if blur else o


def forest(horizon=560, warm=1.0, seed=3, fogs=True):
    """Golden-hour forest backdrop with aerial perspective (far = pale and warm, near = darker)."""
    cols = [mixc("#D8A890", "#E8B49A", warm), mixc("#A07A7E", "#B88070", warm), mixc("#5E4450", "#6A4440", warm)]
    o = [pine_layer(horizon - 110, cols[0], 22, 80, 140, seed, blur=3)]
    if fogs: o.append(fog(horizon - 100, 110, 0.55))
    o.append(pine_layer(horizon - 50, cols[1], 16, 140, 220, seed + 1, blur=2))
    if fogs: o.append(fog(horizon - 40, 120, 0.5))
    o.append(pine_layer(horizon + 6, cols[2], 9, 220, 330, seed + 2, blur=1))
    if fogs: o.append(fog(horizon + 10, 70, 0.35, "#FFD8A8", 18))
    return "".join(o)


def ground(y, col_top="#B88A50", col_bot="#2E1E12", grass=True, seed=5):
    o = [f'<linearGradient id="grG{seed}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{col_top}"/><stop offset="0.35" stop-color="#7A5430"/><stop offset="1" stop-color="{col_bot}"/></linearGradient>'
         f'<rect x="-200" y="{y}" width="940" height="{CH - y + 300}" fill="url(#grG{seed})"/>'
         f'<rect x="-200" y="{y - 4}" width="940" height="26" fill="#FFD898" opacity="0.35" filter="url(#g8)"/>']
    if grass:
        r = random.Random(seed)
        for _ in range(140):
            x, yy = r.uniform(-40, 580), r.uniform(y + 4, CH + 40); k = 0.4 + (yy - y) / 220
            c = mixc("#D8A860", "#24160A", min(1, (yy - y) / 420))
            o.append(f'<path d="M{x:.0f} {yy:.0f} q{-5 * k:.1f} {-16 * k:.1f} {-12 * k:.1f} {-24 * k:.1f} M{x:.0f} {yy:.0f} q{2 * k:.1f} {-20 * k:.1f} {5 * k:.1f} {-30 * k:.1f} M{x:.0f} {yy:.0f} q{6 * k:.1f} {-12 * k:.1f} {14 * k:.1f} {-20 * k:.1f}" stroke="{c}" stroke-width="{2.2 * k:.1f}" fill="none" stroke-linecap="round"/>')
    return "".join(o)


def trail(y, vx=270, w0=30, w1=700):
    return (f'<path d="M{vx - w0 / 2} {y} L{vx + w0 / 2} {y} L{vx + w1 / 2} {CH + 40} L{vx - w1 / 2} {CH + 40} Z" fill="#9A7448" opacity="0.85"/>'
            f'<path d="M{vx - w0 / 2} {y} L{vx + w0 / 2} {y} L{vx + w1 / 2} {CH + 40} L{vx - w1 / 2} {CH + 40} Z" fill="#FFD08A" opacity="0.12"/>')


def motes(n=40, seed=4, area=(0, 0, 540, 960), col="#FFE8B0", op=0.7):
    r = random.Random(seed)
    return "".join(f'<circle cx="{r.uniform(area[0], area[2]):.0f}" cy="{r.uniform(area[1], area[3]):.0f}" r="{r.uniform(1, 3.5):.1f}" fill="{col}" opacity="{op * r.uniform(0.3, 1):.2f}"/>' for _ in range(n))


def grade(warm=0.25, shadow="#1A1030", vig=1.0):
    return (f'<rect x="0" y="0" width="{CW}" height="{CH}" fill="#FFB060" opacity="{warm * 0.35:.2f}" style="mix-blend-mode:soft-light"/>'
            f'<linearGradient id="shG" x1="0" y1="0" x2="0" y2="1"><stop offset="0.45" stop-color="{shadow}" stop-opacity="0"/><stop offset="1" stop-color="{shadow}" stop-opacity="0.35"/></linearGradient>'
            f'<rect x="0" y="0" width="{CW}" height="{CH}" fill="url(#shG)" style="mix-blend-mode:multiply"/>'
            f'<rect x="0" y="0" width="{CW}" height="{CH}" fill="url(#vig)" opacity="{vig}"/>'
            f'<rect x="0" y="0" width="{CW}" height="{CH}" filter="url(#grain)" opacity="0.6"/>')


def dof(svg, n):
    return f'<g filter="url(#g{n})">{svg}</g>' if n else svg


def rim(svg, side="W"):
    return f'<g filter="url(#rim{side})">{svg}</g>'


def place(svg, x, y, s=1.0, rot=0.0):
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">{svg}</g>'


# ------------------------------------------------------------------ smooth lofted bear
def bear_profile(x, kind):
    """(centre y, half height, half width) along the body; ground y = 0, head at +x."""
    G = kind == "grizzly"
    if x < -112 or x > 152: return None
    def bump(x0, x1):
        u = clamp((x - x0) / (x1 - x0)); return math.sin(math.pi * u) ** 2
    if x < -60:
        u = (x + 112) / 52.0; e = math.sqrt(max(0.0, 1 - (1 - u) ** 2))
        return (-98 if not G else -92), (54 if not G else 50) * e, 44 * e
    if x < 70:
        hump = bump(-5, 70) if G else 0.0
        return -94 - 7 * hump, 50 + 9 * hump, 45
    if x < 100:
        u = _sm(70, 100, x); return lerp(-94, -100, u), lerp(50, 36, u), lerp(45, 32, u)
    if x < 124:
        u = (x - 100) / 24.0
        return -100 + 5 * u, lerp(36, 24, u), lerp(32, 22, u)
    u = (x - 124) / 28.0; tip = math.sqrt(max(0.0, 1 - max(0.0, (u - 0.7) / 0.3) ** 2))
    return -94 + 4 * u, lerp(19, 12, u) * max(tip, 0.3), lerp(18, 11, u) * max(tip, 0.3)


def bearL(ox, oy, s=1.0, yaw=0.0, t=0.0, kind="grizzly", fur=None, gait=0.0, run=0.0, roar=0.0, persp=0.0, hump_glow=0.0, blink=0.0, skid=0.0, head_dx=0.0):
    """Smooth lofted bear. ground point (ox, oy). yaw 0 = side facing right, -90 = head-on to camera."""
    G = kind == "grizzly"
    fill = fur or ("url(#bearG)" if G else "url(#bearB)")
    dark = "#24160C" if G else "#0C0A0E"
    a = math.radians(yaw); c, si = math.cos(a), math.sin(a)
    ph = TAU * gait
    bob = -(9 * run + 2) * abs(math.sin(ph)) if (gait or run) else 0.0

    def K(Z): return 1.0 / max(0.25, 1 + persp * Z)

    def P(p):
        x, y, z = p
        Z = x * si + z * c; k = K(Z)
        return ox + (x * c - z * si) * s * k, oy + (-90 + (y + 90) * k) * s, Z

    def ring(x, cy, h, w, n=14):
        return [P((x, cy + h * math.cos(TAU * q / n) + bob, w * math.sin(TAU * q / n))) for q in range(n)]

    def loft(xs):
        hulls = []; prev = None; zs = []
        for x in xs:
            xx = x + (head_dx if x > 70 else 0)
            pr = bear_profile(xx, kind)
            if pr is None: continue
            r = ring(xx, *pr)
            if prev:
                hp = _hull([(round(q[0], 1), round(q[1], 1)) for q in prev + r])
                hulls.append("M" + " L".join(f"{u:.1f} {v:.1f}" for u, v in hp) + "Z")
            prev = r; zs.append(sum(q[2] for q in r) / len(r))
        return f'<path d="{" ".join(hulls)}" fill="{fill}"/>', sum(zs) / len(zs)
    body, zbody = loft(list(range(-112, 77, 4)))
    headl, zhead = loft(list(range(64, 153, 4)))
    # fur: short strokes along the back and flanks, lighter tips on a grizzly
    rr = random.Random(7); fur_s = []
    for k in range(70):
        x = rr.uniform(-100, 110); pr = bear_profile(x, kind)
        if not pr: continue
        cy, h, w = pr; th = rr.uniform(-2.4, -0.7) if rr.random() < 0.7 else rr.uniform(-0.6, 0.6)
        p0 = P((x, cy + h * math.cos(th) + bob, w * math.sin(th) * (1 if rr.random() < 0.5 else -1)))
        if p0[2] > zbody + 10: continue
        ln = rr.uniform(4, 9) * s
        col = ("#E8C08A" if G else "#6A6270") if rr.random() < 0.5 else dark
        fur_s.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f} l{-ln * 0.4:.1f} {-ln:.1f}" stroke="{col}" stroke-width="{1.4 * s:.1f}" opacity="0.5" stroke-linecap="round"/>')
    # legs: tapered capsules + big thigh masses, gait
    legs_far, legs_near = [], []
    for front in (True, False):
        for side in (-1, 1):
            hx = 44 if front else -72
            if gait or run:
                off = (0.0 if front else math.pi) + (0.25 if side > 0 else 0) * (1 + 2 * run)
                sw = math.sin(ph + off); up = max(0.0, math.cos(ph + off))
                fx = hx + lerp(26, 60, run) * sw; fy = -lerp(8, 30, run) * up
            else:
                fx, fy = hx + (8 if front else -2), 0.0
            if skid and front: fx, fy = hx + 55 * skid, 0
            top = P((hx, -84 + bob, side * 28)); kn = P(((hx + fx) / 2 + (6 if front else 14), -40 + bob * 0.5 + fy * 0.4, side * 30)); ft = P((fx, fy - 6, side * 31))
            th = P((hx, -70 + bob, side * 30))
            k_ = K(th[2])
            o = (f'<ellipse cx="{th[0]:.1f}" cy="{th[1]:.1f}" rx="{(34 if not front else 26) * s * k_:.1f}" ry="{(40 if not front else 32) * s * k_:.1f}" fill="{fill}"/>'
                 f'<path d="M{top[0]:.1f} {top[1]:.1f} L{kn[0]:.1f} {kn[1]:.1f} L{ft[0]:.1f} {ft[1]:.1f}" stroke="{fill}" stroke-width="{(30 if front else 32) * s * k_:.1f}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                 f'<ellipse cx="{ft[0] + 6 * s * c * k_:.1f}" cy="{ft[1] + 3 * s:.1f}" rx="{max(9, 20 * abs(c) + 12 * abs(si)) * s * k_:.1f}" ry="{8 * s * k_:.1f}" fill="{dark}"/>')
            if front:
                cl = 13 if G else 6; ccol = "#EFE4CC" if G else "#3A3438"
                for q in range(4):
                    zz = side * 31 + (q - 1.5) * 5
                    c0 = P((fx + 16, fy - 2, zz)); c1 = P((fx + 16 + cl, fy + 2, zz))
                    o += f'<path d="M{c0[0]:.1f} {c0[1]:.1f} L{c1[0]:.1f} {c1[1]:.1f}" stroke="{ccol}" stroke-width="{3 * s * k_:.1f}" stroke-linecap="round"/>'
            legs_far.append((th[2], o))
    # head details: ears, eyes, nose, mouth
    hx = head_dx
    det = []
    for side in (-1, 1):
        e = P((104 + hx, (-134 if not G else -128), side * (20 if not G else 24)))
        k_ = K(e[2]); er = (11 if not G else 9) * s * k_; eh = (15 if not G else 9) * s * k_
        det.append((e[2], f'<ellipse cx="{e[0]:.1f}" cy="{e[1]:.1f}" rx="{er:.1f}" ry="{eh:.1f}" fill="{fill}"/><ellipse cx="{e[0]:.1f}" cy="{e[1] + 1 * s:.1f}" rx="{er * 0.45:.1f}" ry="{eh * 0.5:.1f}" fill="{dark}" opacity="0.35"/>'))
    eyes_ = [(side, P((122 + hx, -110, side * 14))) for side in (-1, 1)]
    far_z = max(e[2] for _, e in eyes_)
    for side, e in eyes_:
        k_ = K(e[2])
        if e[2] == far_z and abs(si) < 0.42:
            continue                                   # far eye is hidden behind the snout in side-ish views
        if blink > 0.5:
            det.append((e[2] - 30, f'<path d="M{e[0] - 4 * s * k_:.1f} {e[1]:.1f} l{8 * s * k_:.1f} 0" stroke="#0A0606" stroke-width="{2 * s * k_:.1f}"/>'))
        else:
            det.append((e[2] - 30, f'<circle cx="{e[0]:.1f}" cy="{e[1]:.1f}" r="{3.6 * s * k_:.1f}" fill="#0A0606"/><circle cx="{e[0] - 1.2 * s * k_:.1f}" cy="{e[1] - 1.3 * s * k_:.1f}" r="{1.3 * s * k_:.1f}" fill="#FFF4D8"/>'))
    n_ = P((152 + hx, -94, 0)); k_ = K(n_[2])
    det.append((n_[2] - 40, f'<ellipse cx="{n_[0]:.1f}" cy="{n_[1]:.1f}" rx="{8 * s * k_ * max(0.6, abs(si) + 0.4):.1f}" ry="{6 * s * k_:.1f}" fill="#120A08"/><ellipse cx="{n_[0] - 2 * s:.1f}" cy="{n_[1] - 2 * s:.1f}" rx="{2.5 * s * k_:.1f}" ry="{1.4 * s * k_:.1f}" fill="#FFFFFF" opacity="0.5"/>'))
    muz = P((140 + hx, -90, 0)); k_ = K(muz[2])
    if not G:
        det.insert(0, (muz[2] - 20, f'<ellipse cx="{muz[0]:.1f}" cy="{muz[1]:.1f}" rx="{(16 * abs(c) + 11 * abs(si)) * s * k_:.1f}" ry="{10 * s * k_:.1f}" fill="#B88E5E"/>'))
    if roar > 0:
        m = P((142 + hx, -82, 0)); k_ = K(m[2])
        det.append((m[2] - 35, f'<ellipse cx="{m[0]:.1f}" cy="{m[1] + 6 * roar * s:.1f}" rx="{(12 * abs(c) + 10 * abs(si)) * s * k_:.1f}" ry="{(3 + 10 * roar) * s * k_:.1f}" fill="#5A0E1A"/>'
                                 + "".join(f'<path d="M{m[0] + (q - 1.5) * 6 * s * k_:.1f} {m[1] - (2 + 4 * roar) * s:.1f} l{2 * s:.1f} {6 * s * k_:.1f} l{2 * s:.1f} {-6 * s * k_:.1f} Z" fill="#FFF6E0"/>' for q in range(4))))
    det.sort(key=lambda q: -q[0])
    hump = ""
    if hump_glow > 0 and G:
        hp = P((32, -150 + bob, 0))
        hump = (f'<ellipse cx="{hp[0]:.1f}" cy="{hp[1]:.1f}" rx="{48 * s:.1f}" ry="{24 * s:.1f}" fill="none" stroke="#FFE070" stroke-width="{4 * s:.1f}" opacity="{hump_glow:.2f}"/>'
                + f'<ellipse cx="{hp[0]:.1f}" cy="{hp[1]:.1f}" rx="{70 * s:.1f}" ry="{40 * s:.1f}" fill="#FFD050" opacity="{0.25 * hump_glow:.2f}" filter="url(#g18)"/>')
    shadow = f'<ellipse cx="{ox:.1f}" cy="{oy + 3:.1f}" rx="{(150 * abs(c) + 70 * abs(si)) * s:.1f}" ry="{16 * s:.1f}" fill="#0A0604" opacity="0.45" filter="url(#g8)"/>'
    dets = "".join(v for _, v in det)
    items = [(z, o) for z, o in legs_far] + [(zbody, body + "".join(fur_s)), (zhead - 1, headl + dets)]
    items.sort(key=lambda q: -q[0])
    return shadow + "".join(o for _, o in items) + hump
