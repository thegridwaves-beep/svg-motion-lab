"""Reusable drawn things for episode 1, in the Sandbox style (soft clipped shading, no loose highlight strokes)."""
import math, random, sys
sys.path.insert(0, "/home/claude/bible")
import kit as K
from kit import inside, P, S, E, C, R, U, g, text
import vivid as V
import scene_people as SP
from vivid import ball, sh, glow, sparkle, chip, leader, poly, term

YOU = SP.Person(name="You", skin=("#C98B62", "#A86E48", "#F0B890"), hair=("#2A1E3A", "#1A1228", "#5A4A8A"), hairstyle="bob",
                glasses=False, top=("#2EA6C8", "#1E7A9A", "#A8F0FF"), top_style="sweater", bottom=("#3A2A6E", "#2A1E52", "#6A5AB0"),
                shoe=("#FFFFFF", "#C9BFD8"), accent=None)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ramp(t, a, b):
    """0 before a, 1 after b, smooth in between."""
    if b <= a:
        return 1.0 if t >= a else 0.0
    return V.ease((t - a) / (b - a))


def out_back(x):
    x = clamp(x)
    c = 1.7
    x -= 1
    return 1 + (c + 1) * x ** 3 + c * x ** 2


POPLOG = None


def popin(content, x, y, t, t0, dur=0.45):
    """Scale-in with a small overshoot, centred on (x, y)."""
    if POPLOG is not None:
        POPLOG.add(round(t0, 3))
    if t < t0:
        return ""
    k = out_back((t - t0) / dur)
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.4f}) translate({-x:.2f} {-y:.2f})">{content}</g>'


def fade(content, op):
    if op <= 0.001:
        return ""
    return content if op >= 0.999 else f'<g opacity="{op:.3f}">{content}</g>'


# ------------------------------------------------------------------ the tiny human
def you(pose="stand", expr="neutral", prop=None, t=0.0, breathe=True):
    """Feet at (0,0), about 520 units tall at k=1."""
    k = 1 + (0.006 * math.sin(t * 2.2) if breathe else 0)
    return f'<g transform="scale(1 {k:.4f})">{SP.person(YOU, pose, expr, prop)}</g>'


# ------------------------------------------------------------------ plants
GREENS = [("#3FD68A", "#1E9A6A", "#B8FFD8"), ("#2EC8A8", "#178A80", "#A8FFF0"), ("#5AE07A", "#2AA05A", "#D0FFB8"),
          ("#22B890", "#127A6A", "#90F0D0"), ("#7AE860", "#3AA83A", "#E0FFB0")]


def blade(x, y, h, w, bend, col, sway=0.0):
    """Tapered grass blade from base (x, y) to a tip bent sideways by bend (+sway)."""
    b = bend + sway
    tipx, tipy = x + b, y - h
    d = (f"M{x - w/2:.2f} {y:.2f} Q{x - w*0.35 + b*0.25:.2f} {y - h*0.55:.2f} {tipx:.2f} {tipy:.2f} "
         f"Q{x + w*0.4 + b*0.35:.2f} {y - h*0.5:.2f} {x + w/2:.2f} {y:.2f} Z")
    shape = P(d)
    vein = f'<path d="M{x:.2f} {y:.2f} Q{x + b*0.3:.2f} {y - h*0.55:.2f} {tipx:.2f} {tipy:.2f}" stroke="{col[1]}" stroke-width="{w*0.08:.2f}" fill="none" opacity="0.35"/>'
    return sh(shape, col[0], col[1], col[2], max(0.3, w / 26)) + inside(shape, vein)


def grass_field(rnd, x0, x1, y, hmin, hmax, wmin, wmax, n, t, cols=GREENS, wind=1.0, haze=None):
    out = []
    for i in range(n):
        x = rnd.uniform(x0, x1)
        h = rnd.uniform(hmin, hmax)
        w = rnd.uniform(wmin, wmax)
        bend = rnd.uniform(-0.25, 0.25) * h
        ph = rnd.uniform(0, 6.28)
        sway = wind * h * 0.025 * math.sin(t * 1.1 + ph)
        out.append(blade(x, y + rnd.uniform(0, 6), h, w, bend, rnd.choice(cols), sway))
    s = "".join(out)
    return f'<g opacity="{haze}">{s}</g>' if haze else s


def leaf(cx, cy, L, Wd, rot, col=("#46E08A", "#1EA864", "#C2FFD8")):
    shape = P(f"M{-L/2:.1f} 0 Q{-L*0.1:.1f} {-Wd:.1f} {L/2:.1f} 0 Q{-L*0.1:.1f} {Wd:.1f} {-L/2:.1f} 0 Z")
    veins = (f'<path d="M{-L/2:.1f} 0 L{L/2:.1f} 0" stroke="{col[1]}" stroke-width="{L*0.012:.2f}" opacity="0.6"/>' +
             "".join(f'<path d="M{-L*0.35 + i*L*0.14:.1f} 0 Q{-L*0.3 + i*L*0.14:.1f} {s*Wd*0.4:.1f} {-L*0.22 + i*L*0.14:.1f} {s*Wd*0.72:.1f}" stroke="{col[1]}" stroke-width="{L*0.007:.2f}" fill="none" opacity="0.45"/>'
                     for i in range(6) for s in (-1, 1)))
    return g(sh(shape, *col, L / 160) + inside(shape, veins), cx, cy, 1, rot)


def pebble(cx, cy, rx, ry, col=("#B8A8E0", "#7A6AB0", "#E8E0FF")):
    return sh(E(cx, cy, rx, ry), *col, rx / 40)


# ------------------------------------------------------------------ water
def drop(cx, cy, r, t=0.0, wobble=0.0):
    """A water sphere with refraction and a crisp specular glint, all clipped inside."""
    sx = 1 + wobble * math.sin(t * 9)
    shape = E(cx, cy, r * sx, r / sx)
    inner = (f'<ellipse cx="{cx:.1f}" cy="{cy + r*0.45:.1f}" rx="{r*0.75:.1f}" ry="{r*0.45:.1f}" fill="#DFFBFF" opacity="0.55"/>'
             f'<ellipse cx="{cx + r*0.15:.1f}" cy="{cy + r*0.25:.1f}" rx="{r*0.55:.1f}" ry="{r*0.25:.1f}" fill="#2A8ACB" opacity="0.25"/>'
             f'<ellipse cx="{cx - r*0.38:.1f}" cy="{cy - r*0.42:.1f}" rx="{r*0.22:.1f}" ry="{r*0.13:.1f}" fill="#FFFFFF" opacity="0.95" transform="rotate(-35 {cx - r*0.38:.1f} {cy - r*0.42:.1f})"/>'
             f'<circle cx="{cx + r*0.35:.1f}" cy="{cy + r*0.38:.1f}" r="{r*0.06:.1f}" fill="#FFFFFF" opacity="0.8"/>')
    return (f'<ellipse cx="{cx:.1f}" cy="{cy + r*0.96:.1f}" rx="{r*0.7:.1f}" ry="{r*0.12:.1f}" fill="#0E4A6A" opacity="0.25"/>' +
            sh(shape, "#8EE6FF", "#3AA8E0", "#E8FDFF", r / 40) + inside(shape, inner))


def raindrop(cx, cy, r, op=1.0):
    shape = P(f"M{cx:.1f} {cy - r*2.2:.1f} Q{cx + r*0.35:.1f} {cy - r*1.1:.1f} {cx + r:.1f} {cy:.1f} A{r:.1f} {r:.1f} 0 1 1 {cx - r:.1f} {cy:.1f} Q{cx - r*0.35:.1f} {cy - r*1.1:.1f} {cx:.1f} {cy - r*2.2:.1f} Z")
    return fade(sh(shape, "#9AE8FF", "#4AA8E0", "#EFFFFF", r / 30) +
                inside(shape, f'<ellipse cx="{cx - r*0.35:.1f}" cy="{cy - r*0.3:.1f}" rx="{r*0.18:.1f}" ry="{r*0.4:.1f}" fill="#FFFFFF" opacity="0.85"/>'), op)


def splash(cx, cy, s, u):
    """Crown splash, u from 0 to 1."""
    if u <= 0 or u >= 1:
        return ""
    o = []
    for i in range(7):
        a = math.pi * (0.1 + 0.8 * i / 6)
        d = s * (0.4 + 1.2 * u)
        x, y = cx - math.cos(a) * d, cy - math.sin(a) * d * (1.3 - u) + s * u * u * 0.8
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s*0.12*(1-u):.2f}" fill="#BFF4FF"/>')
    o.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{s*(0.5+1.4*u):.1f}" ry="{s*(0.12+0.25*u):.1f}" fill="none" stroke="#BFF4FF" stroke-width="{2.5*(1-u):.2f}"/>')
    return f'<g opacity="{1 - u*0.6:.2f}">{"".join(o)}</g>'


# ------------------------------------------------------------------ the ant (side view, facing right, feet on y=0)
ANT = ("#5A2846", "#341430", "#FF8AA0")


def ant(t=0.0, walk=1.0, col=ANT, carry=None, antenna=0.0):
    o = []
    gait = t * 9 * walk
    hips = [(-2, -24), (8, -25), (18, -25)]
    legs_back, legs_front = [], []
    for i, (hx, hy) in enumerate(hips):
        for side in (0, 1):
            ph = gait + (math.pi if (i + side) % 2 else 0)
            reach = 18 + i * 4
            swing = 9 * math.sin(ph) * walk
            lift = max(0, math.cos(ph)) * 4 * walk
            fx = hx + (i - 1) * 14 + swing
            kx, ky = hx + (fx - hx) * 0.45 + (i - 1) * 6, hy - 12 - lift * 0.5
            leg = f'<path d="M{hx} {hy} L{kx:.1f} {ky:.1f} L{fx:.1f} {-lift:.1f}" stroke="{col[1] if side else col[0]}" stroke-width="{3.4 if side else 3.0}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            (legs_front if side else legs_back).append(leg)
    o += legs_back
    gaster = E(-40, -30, 27, 18)
    o.append(g(sh(gaster, col[0], col[1], col[2], 0.7), 0, 0, 1, 0) +
             inside(gaster, "".join(f'<ellipse cx="{-58 + k*12}" cy="-30" rx="2" ry="18" fill="{col[1]}" opacity="0.5"/>' for k in range(4))))
    o.append(ball(-12, -27, 5.5, col[0], col[1], col[2]))
    o.append(sh(E(8, -29, 19, 9), col[0], col[1], col[2], 0.6))
    o += legs_front
    o.append(sh(E(38, -37, 15, 12.5), col[0], col[1], col[2], 0.55))
    o.append(f'<ellipse cx="42" cy="-40" rx="4" ry="3.2" fill="#140A18"/><circle cx="43" cy="-41" r="1.1" fill="#FFFFFF" opacity="0.85"/>')
    a = antenna + 3 * math.sin(t * 3.1)
    o.append(f'<path d="M40 -48 Q46 {-64 + a:.1f} 50 {-68 + a:.1f} Q62 {-64 + a:.1f} 72 {-58 + a:.1f}" stroke="{col[0]}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    o.append(sh(P("M50 -32 Q60 -32 62 -25 Q56 -26 50 -27 Z"), col[0], col[1]))
    if carry:
        o.append(carry)
    return "".join(o)


def crumb(cx, cy, s, seed=1):
    rr = random.Random(seed)
    pts = []
    for i in range(9):
        a = 2 * math.pi * i / 9
        r = s * rr.uniform(0.75, 1.05)
        pts.append((cx + r * math.cos(a) * 1.25, cy + r * math.sin(a) * 0.85))
    shape = P("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z")
    holes = "".join(f'<ellipse cx="{cx + rr.uniform(-s*0.7, s*0.7):.1f}" cy="{cy + rr.uniform(-s*0.4, s*0.5):.1f}" rx="{s*rr.uniform(0.06, 0.12):.1f}" ry="{s*rr.uniform(0.04, 0.08):.1f}" fill="#C88A4A"/>' for _ in range(10))
    return sh(shape, "#FFD89A", "#E0A060", "#FFF0C8", s / 40) + inside(shape, holes)


def sugar(cx, cy, s):
    return (V.iso_box(cx, cy, s, s, s * 0.9, "#FFFFFF", "#E8E4F8", "#C8C0E8") +
            glow(cx, cy - s, s * 0.6, "#FFFFFF", 0.4, 4))


# ------------------------------------------------------------------ critters
def spider(t=0.0, col=("#3A1E5A", "#1E0E36", "#B88AFF")):
    """Side-ish view, facing right. Jointed legs: hip -> high knee -> foot on the ground (y = 30)."""
    o = []
    for side in (0, 1):
        for i in range(4):
            hx = 6 + i * 6
            reach = (-70, -40, 30, 70)[i]
            sway = 4 * math.sin(t * 6 + i * 1.3 + side)
            fx = hx + reach + (8 if side else -8) + sway
            kx, ky = hx + reach * 0.55, -46 - (4 - abs(i - 1.5)) * 6
            c = col[1] if side == 0 else col[0]
            o.append(f'<path d="M{hx} -2 L{kx:.1f} {ky:.1f} L{fx:.1f} 30" stroke="{c}" stroke-width="{5.5 if side else 4.5}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        if side == 0:
            ab = E(-30, -8, 34, 27)
            o.append(sh(ab, *col, 0.9) + inside(ab, '<path d="M-52 -14 Q-30 -26 -8 -14 L-10 -8 Q-30 -18 -50 -8 Z" fill="#FF4F9A" opacity="0.8"/>'
                                               '<path d="M-48 2 Q-30 -8 -12 2 L-14 7 Q-30 -2 -46 7 Z" fill="#FF4F9A" opacity="0.6"/>'))
            o.append(sh(E(18, -4, 20, 16), *col, 0.6))
    for (x, y, r) in [(30, -12, 3.6), (36, -7, 3.0), (24, -16, 2.4), (33, -17, 2.2), (38, -1, 2.0)]:
        o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FF2A5A"/><circle cx="{x-0.8}" cy="{y-0.8}" r="{r*0.35:.1f}" fill="#FFFFFF"/>')
    o.append(f'<path d="M34 6 Q38 14 32 18 M28 6 Q30 14 25 17" stroke="{col[1]}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    return "".join(o)


def mosquito(t=0.0):
    w = 6 * math.sin(t * 60)
    return (f'<ellipse cx="-6" cy="{-14 + w:.1f}" rx="16" ry="5" fill="#E8F6FF" opacity="0.7" transform="rotate(-25 -6 -14)"/>'
            f'<path d="M-4 0 L-26 18 M2 0 L-6 22 M6 0 L16 20" stroke="#2A1E3A" stroke-width="1.6" fill="none"/>' +
            sh(E(-14, -2, 14, 4.5), "#4A3A5A", "#2A1E3A") + ball(4, -3, 6, "#4A3A5A", "#2A1E3A") +
            '<path d="M9 -2 L24 4" stroke="#2A1E3A" stroke-width="1.4"/>')


def shrew(t=0.0):
    body = P("M-90 0 Q-100 -60 -20 -66 Q60 -70 96 -30 L130 -18 Q100 -4 70 0 Z")
    o = [f'<path d="M-88 -10 Q-150 -20 -190 10" stroke="#B89AA0" stroke-width="7" fill="none" stroke-linecap="round"/>',
         sh(body, "#9A7A8E", "#6A4E66", "#E0C8D8", 2),
         inside(body, '<path d="M-100 -10 Q0 -2 140 -14 L140 10 L-100 10 Z" fill="#D8C0CC"/>'),
         sh(E(40, -60, 13, 15), "#B8949E", "#7A5A70"),
         '<circle cx="78" cy="-42" r="5" fill="#140A18"/><circle cx="77" cy="-43.5" r="1.6" fill="#FFF"/>',
         ball(130, -18, 6, "#FF8AA0", "#C05070")]
    for x in (-50, 50):
        o.append(f'<path d="M{x} -6 L{x+4} 4" stroke="#6A4E66" stroke-width="7" stroke-linecap="round"/>')
    return "".join(o)


def bird_shadow(op=0.35):
    return (f'<path d="M0 0 Q-60 -26 -150 -6 Q-80 4 -30 18 Q-10 30 0 60 Q10 30 30 18 Q80 4 150 -6 Q60 -26 0 0 Z" fill="#1A0A30" opacity="{op}"/>')


# ------------------------------------------------------------------ neurons
def neuron(cx, cy, s, seed, col="#FF7AC8", glow_op=0.5):
    rr = random.Random(seed)
    o = []
    for _ in range(6):
        a = rr.uniform(0, 2 * math.pi)
        L = s * rr.uniform(1.8, 3.4)
        mx, my = cx + math.cos(a) * L * 0.5 + rr.uniform(-s, s) * 0.4, cy + math.sin(a) * L * 0.5 + rr.uniform(-s, s) * 0.4
        ex, ey = cx + math.cos(a) * L, cy + math.sin(a) * L
        o.append(f'<path d="M{cx:.1f} {cy:.1f} Q{mx:.1f} {my:.1f} {ex:.1f} {ey:.1f}" stroke="{col}" stroke-width="{s*0.12:.2f}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    return glow(cx, cy, s * 1.4, col, glow_op, 4) + "".join(o) + ball(cx, cy, s * 0.42, "#FFD0EE", col)


# ------------------------------------------------------------------ labels
def label(x, y, s, bg="#2A1470", fg="#FFFFFF", size=13):
    return chip(round(x), round(y), s, bg, fg, size)


def caption_big(x, y, s, size=34, col="#FFFFFF", anchor="middle"):
    return (text(x, y + 2, s, size, "#0A0420", 700, anchor, op=0.25) + text(x, y, s, size, col, 700, anchor))
