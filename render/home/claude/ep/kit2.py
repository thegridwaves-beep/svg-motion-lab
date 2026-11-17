"""Angle kit: perspective grounds, converging/diverging grass, skies, and extra character views (back, top, close)."""
import math, random, sys
sys.path.insert(0, "/home/claude/bible"); sys.path.insert(0, "/home/claude/ant"); sys.path.insert(0, "/home/claude/ant2")
import vivid as V
from kit import inside, P, S, E, C, R, U, g, text
import kit as K
import assets as A
from assets import drop, ant, glow, ball, sh, GREENS, pebble, sparkle, raindrop, crumb, spider, leaf, label
import rig
import scene_people as SP

W, H = 960, 540
YOU = A.YOU

SKIES = {
    "dawn": [(0, "#2A1680"), (0.5, "#7A34C0"), (0.82, "#FF7AB0"), (1, "#FFC79A")],
    "day": [(0, "#3A2AD0"), (0.5, "#5A8AF0"), (0.85, "#B8A8FF"), (1, "#FFD0E0")],
    "gold": [(0, "#4A1E9A"), (0.45, "#C84A9A"), (0.8, "#FF9A6A"), (1, "#FFE0A0")],
    "cold": [(0, "#1E2A7A"), (0.5, "#3A5AC0"), (0.85, "#8AB0E8"), (1, "#D8E8FF")],
    "storm": [(0, "#14123A"), (0.5, "#2A2A6A"), (0.85, "#4A4A8A"), (1, "#7A6AA8")],
    "night": [(0, "#0E0A30"), (0.6, "#2A1A6A"), (1, "#5A2A8A")],
}
SOILS = {
    "dawn": [(0, "#8A4AA8"), (0.35, "#4A1E7A"), (1, "#1E0E46")],
    "day": [(0, "#7A5AC8"), (0.35, "#4A2A9A"), (1, "#24125E")],
    "gold": [(0, "#B85A8A"), (0.35, "#6A2A7A"), (1, "#2A0E4A")],
    "cold": [(0, "#6A7AC8"), (0.35, "#3A3A8A"), (1, "#18184A")],
    "storm": [(0, "#4A4A7A"), (0.35, "#2A2A5A"), (1, "#100E2A")],
    "night": [(0, "#3A2A6A"), (1, "#0E0828")],
}
SUNS = {"dawn": ("#FFE6C8", "#FFF6E0"), "day": ("#FFF6E0", "#FFFFFF"), "gold": ("#FFD8A0", "#FFF2D0"), "cold": ("#D8E8FF", "#FFFFFF"),
        "storm": ("#8A8AC8", "#B8B8E8"), "night": ("#C8C0FF", "#FFFFFF")}
PEBS = [("#9A7AD8", "#6A4AA8", "#D8C8FF"), ("#C88AB8", "#8A4A80", "#FFD0EE"), ("#7A8AE0", "#4A5AB0", "#C8D8FF")]


def sky_defs(mood):
    return V.lin(f"sky_{mood}", SKIES[mood]) + V.lin(f"soil_{mood}", SOILS[mood])


def sky(mood, sun=(700, 120), rays=True, stars=0, seed=1):
    o = [f'<rect x="-300" y="-300" width="1560" height="1140" fill="url(#sky_{mood})"/>']
    rr = random.Random(seed)
    for _ in range(stars):
        x, y = rr.uniform(-200, 1160), rr.uniform(-200, 300)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr.uniform(0.6, 1.6):.1f}" fill="#FFFFFF" opacity="{rr.uniform(0.3, 0.9):.2f}"/>')
    if sun:
        a, b = SUNS[mood]
        o.append(glow(sun[0], sun[1], 260, a, 0.5, 30) + glow(sun[0], sun[1], 70, b, 0.9, 16))
        if rays:
            for k in range(9):
                an = math.radians(80 + k * 13)
                o.append(f'<path d="M{sun[0]} {sun[1]} L{sun[0] + 1700*math.cos(an-0.022):.0f} {sun[1] + 1700*math.sin(an-0.022):.0f} '
                         f'L{sun[0] + 1700*math.cos(an+0.022):.0f} {sun[1] + 1700*math.sin(an+0.022):.0f} Z" fill="{b}" opacity="0.05"/>')
    return "".join(o)


class Cam:
    """A 2D perspective camera: horizon line + vertical vanishing point.
    vp_y < 0: looking up (verticals converge upward). vp_y > H: looking down (verticals spread upward).
    """
    def __init__(self, hz=400, vp=(480, -2200), near=600):
        self.hz, self.vp, self.near = hz, vp, near

    def gy(self, d):
        """ground y at depth d (0 = horizon, 1 = at the lens)."""
        return self.hz + (self.near - self.hz) * d ** 1.7

    def gx(self, u, d):
        """ground x for lateral position u (-1..1) at depth d."""
        return 480 + u * (220 + 1100 * d)

    def scale(self, d):
        """apparent size of a ground object at depth d, 1.0 at roughly the main subject distance"""
        return max(0.04, (self.gy(d) - self.hz) / (self.near - self.hz) * 2.6)


def ground(cam, mood, seed=3, n=140, x0=-300, x1=1260):
    rr = random.Random(seed)
    o = [f'<path d="M{x0} {cam.hz} L{x1} {cam.hz} L{x1} 900 L{x0} 900 Z" fill="url(#soil_{mood})"/>',
         f'<rect x="{x0}" y="{cam.hz - 3}" width="{x1 - x0}" height="7" fill="#FFC8D8" opacity="0.35" filter="url(#b2)"/>']
    items = []
    for _ in range(n):
        d = rr.random() ** 0.75
        y = cam.gy(d)
        s_ = 0.8 + 16 * d ** 1.6
        x = cam.gx(rr.uniform(-1.1, 1.1), d)
        items.append((d, pebble(x, y, s_ * 1.5, s_ * 0.55, rr.choice(PEBS))))
    # little moss tufts
    for _ in range(int(n * 0.6)):
        d = rr.random() ** 0.75
        y = cam.gy(d); x = cam.gx(rr.uniform(-1.1, 1.1), d); s_ = 2 + 14 * d ** 1.5
        c = rr.choice(GREENS)
        items.append((d, f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{s_*1.6:.1f}" ry="{s_*0.45:.1f}" fill="{c[1]}" opacity="0.8"/>'
                         f'<ellipse cx="{x - s_*0.3:.1f}" cy="{y - s_*0.12:.1f}" rx="{s_*0.9:.1f}" ry="{s_*0.25:.1f}" fill="{c[0]}" opacity="0.8"/>'))
    items.sort(key=lambda a: a[0])
    o += [s for _, s in items]
    return "".join(o)


def pblade(cam, bx, by, h, w, col, lean=0.0, sway=0.0, shadow=True):
    """A blade rooted at (bx, by), aimed at the camera's vertical vanishing point (or away from it when looking down)."""
    vx, vy = cam.vp
    dx, dy = vx - bx, vy - by
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    if vy > by:          # looking down: verticals point away from the vanishing point
        ux, uy = -ux, -uy
    lx = (lean + sway) * h
    tx, ty = bx + ux * h + lx, by + uy * h
    nx, ny = -uy, ux
    d = (f"M{bx - nx*w/2:.1f} {by - ny*w/2:.1f} Q{bx + ux*h*0.55 - nx*w*0.35 + lx*0.3:.1f} {by + uy*h*0.55 - ny*w*0.35:.1f} {tx:.1f} {ty:.1f} "
         f"Q{bx + ux*h*0.5 + nx*w*0.4 + lx*0.25:.1f} {by + uy*h*0.5 + ny*w*0.4:.1f} {bx + nx*w/2:.1f} {by + ny*w/2:.1f} Z")
    out = ""
    if shadow:
        out += f'<ellipse cx="{bx:.1f}" cy="{by + 1:.1f}" rx="{w*0.9:.1f}" ry="{w*0.2:.1f}" fill="#120830" opacity="0.4"/>'
    return out + sh(P(d), col[0], col[1], col[2], max(0.3, w / 26))


def blades(cam, seed, n, dmin, dmax, hmin, hmax, wmul=1.0, avoid=None, umin=-1.1, umax=1.1, t=0.0, sway=0.0, cols=GREENS):
    rr = random.Random(seed)
    items = []
    for k in range(n):
        d = rr.uniform(dmin, dmax)
        u = rr.uniform(umin, umax)
        x, y = cam.gx(u, d), cam.gy(d)
        if avoid and avoid[0] < x < avoid[1] and d > avoid[2]:
            continue
        sc = cam.scale(d)
        h = rr.uniform(hmin, hmax) * sc
        w = h * rr.uniform(0.07, 0.12) * wmul
        items.append((d, pblade(cam, x, y, h, w, rr.choice(cols), rr.uniform(-0.1, 0.1), sway * math.sin(t * 1.1 + k))))
    items.sort(key=lambda a: a[0])
    return "".join(s for _, s in items)


def forest(cam, seed, n=60, haze=0.55, mood_col=None):
    """Hazy wall of tall blades near the horizon, the 'jungle' backdrop."""
    s = blades(cam, seed, n, 0.0, 0.12, 2200, 4200, 1.0)
    return f'<g opacity="{haze}">{s}</g>'


def contact(x, y, rx, op=0.45):
    return f'<ellipse cx="{x:.1f}" cy="{y + 1:.1f}" rx="{rx:.1f}" ry="{rx*0.17:.1f}" fill="#120830" opacity="{op}"/>'


# ------------------------------------------------------------------ character views
def front(arms="stand", legs="stand", expr="neutral", tilt=0, blink=False, prop=None):
    a = rig.ARMS[arms] if isinstance(arms, str) else arms
    l = rig.LEGS[legs] if isinstance(legs, str) else legs
    return rig.person(YOU, a, l, expr, tilt, blink, prop)


def back(arms="stand", legs="stand", tilt=0):
    """Seen from behind: same body, head is all hair."""
    a = rig.ARMS[arms] if isinstance(arms, str) else arms
    l = rig.LEGS[legs] if isinstance(legs, str) else legs
    p = YOU
    o = []
    for i, (hx, hy, fx, fy) in enumerate(l):
        col = (p.bottom[0], p.bottom[1], p.bottom[0]) if i == 1 else (p.bottom[1], p.bottom[1], p.bottom[2])
        o.append(SP.rimmed(P(f"M {hx-22:.1f} {hy:.1f} L {hx+22:.1f} {hy:.1f} L {fx+16:.1f} {fy:.1f} Q {fx:.1f} {fy+6:.1f} {fx-16:.1f} {fy:.1f} Z"), *col, 5))
        o.append(SP.rimmed(P(f"M {fx-24:.1f} {fy+16:.1f} Q {fx-24:.1f} {fy-4:.1f} {fx:.1f} {fy-6:.1f} Q {fx+24:.1f} {fy-4:.1f} {fx+24:.1f} {fy+16:.1f} Z"), p.shoe[0], p.shoe[1], "#FFFFFF", 3))
    torso = P("M -64 -196 Q -70 -330 -10 -372 Q 62 -372 66 -300 L 62 -196 Q 0 -186 -64 -196 Z")
    o.append(SP.rimmed(torso, *p.top, 8))
    o.append(inside(torso, "".join(f'<rect x="{-62+i*10}" y="-222" width="4" height="26" fill="{p.top[1]}" opacity="0.7"/>' for i in range(13))
                    + f'<path d="M0 -360 L0 -200" stroke="{p.top[1]}" stroke-width="3" opacity="0.35"/>'))
    for j, (sx, sy, ex, ey, hx, hy) in enumerate(a):
        o.append(SP.rimmed(S(f"M {sx:.1f} {sy:.1f} Q {ex:.1f} {ey:.1f} {hx:.1f} {hy:.1f}", 30), *p.top, 5) + SP.rimmed(C(hx, hy, 15), *p.skin, 3))
    hair = P("M -56 -400 Q -66 -500 0 -506 Q 66 -500 56 -400 Q 50 -380 30 -378 L -30 -378 Q -50 -380 -56 -400 Z")
    o.append(f'<g transform="rotate({tilt} 0 -440)">' + SP.rimmed(E(-50, -440, 9, 13), *p.skin, 3) + SP.rimmed(E(50, -440, 9, 13), *p.skin, 3) +
             SP.rimmed(hair, *p.hair, 6) + inside(hair, '<path d="M-30 -490 Q4 -502 36 -486 L34 -480 Q4 -494 -28 -484 Z" fill="#5A4A8A"/>') + '</g>')
    return "".join(o)


def top(arms_out=0.0, curl=0.0):
    """Seen from straight above: hair disc, shoulders, arms, feet poking out."""
    p = YOU
    o = []
    for sx in (-1, 1):
        o.append(SP.rimmed(E(sx * 20, 70, 14, 22), p.shoe[0], p.shoe[1], "#FFFFFF", 3))
    o.append(SP.rimmed(E(0, 10, 66 - 20 * curl, 44), *p.top, 8))
    for sx in (-1, 1):
        ax = sx * (70 + 50 * arms_out - 30 * curl)
        o.append(SP.rimmed(S(f"M {sx*52} 0 Q {sx*80} {20 - 40*curl:.1f} {ax:.1f} {40 - 30*curl:.1f}", 26), *p.top, 5))
        o.append(SP.rimmed(C(ax, 40 - 30 * curl, 13), *p.skin, 3))
    o.append(SP.rimmed(C(0, -18, 44), *p.hair, 6))
    o.append(inside(C(0, -18, 44), '<path d="M-30 -40 Q0 -60 30 -40 L28 -34 Q0 -52 -28 -34 Z" fill="#5A4A8A"/>'))
    return "".join(o)


def face_close(expr="neutral", tilt=0, blink=False):
    return SP.head(YOU, "sleepy" if blink else expr, tilt)


# ------------------------------------------------------------------ text and UI
def kinetic(word, x, y, t, t0, size=64, col="#FFFFFF", out_t=None, shadow="#0A0420"):
    if t < t0 or (out_t is not None and t > out_t + 0.35):
        return ""
    u = 1 - (1 - min(1, (t - t0) / 0.32)) ** 3
    dy = (1 - u) * size * 1.1
    if out_t is not None and t > out_t:
        dy = -((t - out_t) / 0.3) ** 3 * size * 1.1
    w = len(word) * size * 0.62 + 60
    mid = K.uid("kc")
    return (f'<clipPath id="{mid}"><rect x="{x - w/2:.1f}" y="{y - size*1.05:.1f}" width="{w:.1f}" height="{size*1.4:.1f}"/></clipPath>'
            f'<g clip-path="url(#{mid})"><g transform="translate(0 {dy:.2f})">'
            + text(x, y + 3, word, size, shadow, 700, "middle", op=0.35) + text(x, y, word, size, col, 700, "middle") + '</g></g>')


def chip(x, y, s, t, t0, bg="#2A1470", fg="#FFFFFF", size=16):
    return A.popin(label(x, y, s, bg, fg, size), x, y, t, t0)


def panel(x, y, w, h, op=0.82):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="26" fill="#140A3A" opacity="{op}"/><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="26" fill="none" stroke="#FFFFFF" stroke-opacity="0.08" stroke-width="2"/>'
