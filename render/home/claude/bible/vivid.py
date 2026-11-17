"""Sandbox explainer frames: vivid range (space, data, labs, cities, micro, food, people).
Original designs. Drawn on a 960x540 grid, rendered at 1920x1080.
Rule: every highlight/shadow is a clipped shape (tt / inside). Strokes only for real lines."""
import math, random
import kit as K
from kit import tt, inside, P, S, E, C, R, U, g, text
import scene_people as SP

W, H = 960, 540
I = 0.866
T = 0.0                 # current time in seconds (animation); 0 for stills
CAM = None              # (scale, cx, cy) camera push, None for stills
ANIM = False            # True while rendering motion
BARE = False            # True: no vignette/grain (sequence adds them once)


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def pop(t0, dur=0.5):
    """Scale for a pop-in starting at t0 with a little overshoot (back ease). 1 for stills."""
    if not (ANIM or CAM):
        return 1.0
    x = (T - t0) / dur
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    c = 2.2
    x -= 1
    return 1 + (c + 1) * x ** 3 + c * x ** 2


def popg(content, x, y, t0, dur=0.5):
    k = pop(t0, dur)
    if k <= 0.001:
        return ""
    return f'<g transform="translate({x} {y}) scale({k:.3f}) translate({-x} {-y})">{content}</g>'


# ------------------------------------------------------------------ helpers
def defs():
    return ("".join(f'<filter id="b{k}" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="{k}"/></filter>' for k in (2, 4, 8, 16, 30))
            + '<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="4"/>'
              '<feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.9 -0.4"/></filter>'
            + '<radialGradient id="vig" cx="0.5" cy="0.5" r="0.75"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#0A0420" stop-opacity="0.4"/></radialGradient>')


def lin(id_, stops, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rad(id_, stops, cx=0.5, cy=0.5, r=0.5):
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    return f'<radialGradient id="{id_}" cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient>'


def svg(body, extra=""):
    if CAM:
        k, cx, cy = CAM
        body = f'<g transform="translate({cx} {cy}) scale({k:.4f}) translate({-cx} {-cy})">{body}</g>'
    if BARE:
        return f'<svg x="0" y="0" width="{W}" height="{H}" viewBox="0 0 {W} {H}" overflow="hidden"><defs>{defs()}{extra}</defs>{body}</svg>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 {W} {H}"><defs>{defs()}{extra}</defs>{body}'
            f'<rect width="{W}" height="{H}" fill="url(#vig)"/><rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.06" style="mix-blend-mode:overlay"/></svg>')


def ball(cx, cy, r, base, shade, rim=None):
    return tt(C(cx, cy, r), base, shade, rim or shade, k=r / 40)


def sh(fn, base, shade, rim=None, k=1.0):
    return tt(fn, base, shade, rim or shade, k=k)


def term(shape, dx, dy, col, op=0.35, soft=8):
    """Shadow crescent: the shape minus itself shifted (dx, dy), with a soft terminator.
    The blur lives on the mask's cut-out only, so the silhouette edge stays fully shaded."""
    mid = K.uid("tm")
    return inside(shape, f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-5000" y="-5000" width="10000" height="10000">'
                         f'<rect x="-5000" y="-5000" width="10000" height="10000" fill="#fff"/><g transform="translate({dx} {dy})" filter="url(#b{soft})">{shape("#000")}</g></mask>'
                         f'<g mask="url(#{mid})" opacity="{op}"><rect x="-5000" y="-5000" width="10000" height="10000" fill="{col}"/></g>')


def glow(cx, cy, r, col, op=0.5, b=16):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}" opacity="{op}" filter="url(#b{b})"/>'


def sparkle(x, y, r, col, op=1.0):
    return (f'<path d="M{x} {y-r} Q{x} {y} {x+r} {y} Q{x} {y} {x} {y+r} Q{x} {y} {x-r} {y} Q{x} {y} {x} {y-r} Z" '
            f'fill="{col}" opacity="{op}"/>')


def stars(rnd, n, y0=0, y1=H, col="#FFFFFF", x0=0, x1=W):
    o = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if rnd.random() < 0.12:
            o.append(sparkle(round(x), round(y), rnd.uniform(3, 6), col, 0.9))
        else:
            op_ = rnd.uniform(0.4, 0.9) * (0.65 + 0.35 * math.sin(T * rnd.uniform(2, 5) + rnd.uniform(0, 6.28)))
            o.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rnd.uniform(0.5, 1.4):.1f}" fill="{col}" opacity="{op_:.2f}"/>')
    return "".join(o)


def chip(x, y, s, bg, fg="#FFFFFF", size=13, anchor="middle"):
    w = len(s) * size * 0.6 + 20
    h = size + 12
    x0 = x - w / 2 if anchor == "middle" else x
    return (f'<rect x="{x0:.2f}" y="{y - h/2 + 3:.2f}" width="{w:.2f}" height="{h}" rx="6" fill="#0A0420" opacity="0.25"/>'
            f'<rect x="{x0:.2f}" y="{y - h/2:.2f}" width="{w:.2f}" height="{h}" rx="6" fill="{bg}"/>'
            + text(f"{x0 + w/2:.2f}", f"{y + size*0.36:.2f}", s, size, fg, 700, "middle"))


def leader(x1, y1, x2, y2, col="#FFFFFF"):
    return (f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{col}" stroke-width="1.6" opacity="0.8"/>'
            f'<circle cx="{x1}" cy="{y1}" r="3" fill="{col}"/>')


def poly(pts, col, op=1.0):
    return f'<path d="M{" L".join(f"{x:.1f} {y:.1f}" for x, y in pts)} Z" fill="{col}" opacity="{op}"/>'


def iso_box(cx, cy, a, b, h, top, left, right):
    """Front-bottom corner at (cx, cy). Right face runs a along (I,-.5); left face b along (-I,-.5)."""
    A = (cx + I * a, cy - 0.5 * a)
    B = (cx - I * b, cy - 0.5 * b)
    return (poly([(cx, cy), B, (B[0], B[1] - h), (cx, cy - h)], left) +
            poly([(cx, cy), A, (A[0], A[1] - h), (cx, cy - h)], right) +
            poly([(cx, cy - h), (A[0], A[1] - h), (A[0] - I * b, A[1] - 0.5 * b - h), (B[0], B[1] - h)], top))


def iso_windows(cx, cy, a, b, h, rnd, lit="#FFE27A", dim="#2A1A6A", side="both", rows=None, ww=5, wh=7, gap=4):
    o = []
    rows = rows or max(1, int((h - 10) // (wh + gap)))
    for face, length, sgn in (("r", a, 1), ("l", b, -1)):
        if side not in ("both", face):
            continue
        cols = max(1, int((length - 6) // (ww + gap)))
        for i in range(rows):
            for j in range(cols):
                u, v = 5 + j * (ww + gap), 6 + i * (wh + gap)
                if v + wh > h - 4:
                    continue
                c = lit if rnd.random() < 0.45 else dim
                pts = [(u, v), (u + ww, v), (u + ww, v + wh), (u, v + wh)]
                o.append(poly([(cx + sgn * I * pu, cy - 0.5 * pu - h + pv) for pu, pv in pts], c, 0.95 if c == lit else 0.55))
    return "".join(o)


PAL = {  # iso faces: top, left (lit), right (shade)
    "pink": ("#FFB3DC", "#FF6FB5", "#C9408A"),
    "violet": ("#B9A2FF", "#7A5CF0", "#5236C0"),
    "blue": ("#A8D8FF", "#4A9CFF", "#2E64D0"),
    "cyan": ("#B8FFF4", "#38E0D0", "#1EA6A8"),
    "yellow": ("#FFF0A0", "#FFD23A", "#E09A1A"),
    "orange": ("#FFC79A", "#FF8A3A", "#D25A1E"),
    "mint": ("#C2FFD8", "#46E08A", "#1EA864"),
    "cream": ("#FFF6E6", "#F2DEC4", "#C9AE92"),
    "night": ("#5A4AA0", "#3A2A80", "#241866"),
}


def face(x, y, k=1.0, mood="smile", col="#2A1030"):
    o = (f'<circle cx="{x - 9*k:.1f}" cy="{y:.1f}" r="{3.2*k:.1f}" fill="{col}"/><circle cx="{x + 9*k:.1f}" cy="{y:.1f}" r="{3.2*k:.1f}" fill="{col}"/>'
         f'<ellipse cx="{x - 15*k:.1f}" cy="{y + 7*k:.1f}" rx="{4.5*k:.1f}" ry="{2.6*k:.1f}" fill="#FF6F8E" opacity="0.6"/>'
         f'<ellipse cx="{x + 15*k:.1f}" cy="{y + 7*k:.1f}" rx="{4.5*k:.1f}" ry="{2.6*k:.1f}" fill="#FF6F8E" opacity="0.6"/>')
    if mood == "smile":
        o += f'<path d="M{x - 5*k:.1f} {y + 6*k:.1f} q{5*k:.1f} {5*k:.1f} {10*k:.1f} 0" stroke="{col}" stroke-width="{2.4*k:.1f}" fill="none" stroke-linecap="round"/>'
    else:
        o += f'<path d="M{x - 6*k:.1f} {y + 5*k:.1f} q{6*k:.1f} {9*k:.1f} {12*k:.1f} 0 Z" fill="{col}"/>'
    return o


# ------------------------------------------------------------------ 1. space
def f_space():
    rnd = random.Random(1)
    ex = rad("sp", [(0, "#3A1A9A", 1), (0.6, "#1A0A5A", 1), (1, "#0A0428", 1)], 0.62, 0.5, 0.75)
    b = [f'<rect width="{W}" height="{H}" fill="url(#sp)"/>', stars(rnd, 160)]
    b.append(glow(600, 280, 260, "#FF5FA8", 0.25, 30))
    for (x, y, r_, c, o) in [(140, 90, 120, "#5A3AF0", 0.35), (220, 150, 90, "#FF4FA0", 0.18), (880, 80, 110, "#2EC8F0", 0.18)]:
        b.append(glow(x, y, r_, c, o, 30))
    tail = P("M820 120 L930 60 L936 70 Z")
    hx, hy = 860 - 70 * T, 100 + 36 * T
    b.append(f'<path d="M{hx:.1f} {hy:.1f} L{hx+170:.1f} {hy-92:.1f} L{hx+174:.1f} {hy-84:.1f} Z" fill="#BFF4FF" opacity="0.5"/>' + ball(hx, hy, 6, "#FFFFFF", "#9AE8FF") + glow(hx, hy, 12, "#9AE8FF", 0.8, 4))
    cx, cy, r = 600, 280, 160
    ring = lambda c: f'<path d="M{cx-300} {cy} A300 70 0 1 0 {cx+300} {cy} A300 70 0 1 0 {cx-300} {cy} Z M{cx-220} {cy} A220 44 0 1 1 {cx+220} {cy} A220 44 0 1 1 {cx-220} {cy} Z" fill="{c}" fill-rule="evenodd" transform="rotate(-14 {cx} {cy})"/>'
    ring_back = lambda c: f'<g clip-path="url(#rtop)">{ring(c)}</g>'
    b.append(f'<clipPath id="rtop"><rect x="0" y="0" width="{W}" height="{cy}" transform="rotate(-14 {cx} {cy})"/></clipPath>')
    b.append(f'<clipPath id="rbot"><rect x="-200" y="{cy}" width="{W+400}" height="{H}" transform="rotate(-14 {cx} {cy})"/></clipPath>')
    b.append(sh(ring, "#FFC27A", "#E08A5A", "#FFE6B0", 2))
    bands = "".join(f'<path d="M{cx-200} {cy-160+i*34} Q{cx} {cy-150+i*34+(12 if i%2 else -8)+5*math.sin(T*1.6+i):.1f} {cx+200} {cy-160+i*34} L{cx+200} {cy-146+i*34} Q{cx} {cy-136+i*34} {cx-200} {cy-146+i*34} Z" fill="{["#FF8A5A", "#E8508A", "#FFB070"][i%3]}" opacity="0.7"/>' for i in range(10))
    pl = C(cx, cy, r)
    b.append(pl("#FF7A9A") + inside(pl, f'<g transform="rotate(-14 {cx} {cy})">{bands}'
                    f'<ellipse cx="{cx-50}" cy="{cy+56}" rx="26" ry="12" fill="#C8306A"/></g>'))
    b.append(term(pl, -46, -40, "#4A0E6A", 0.45) + term(pl, -14, -12, "#4A0E6A", 0.25))
    b.append(inside(pl, f'<g transform="rotate(-14 {cx} {cy})"><ellipse cx="{cx}" cy="{cy+44}" rx="260" ry="26" fill="#3A0A5A" opacity="0.35"/></g>'))
    b.append(f'<g clip-path="url(#rbot)">{sh(ring, "#FFC27A", "#E08A5A", "#FFE6B0", 2)}</g>')
    # ring shadow on planet
    # moons
    for j, (x, y, rr, c) in enumerate([(250, 140, 22, ("#9FE8FF", "#4AA8E0", "#E0F8FF")), (860, 420, 30, ("#C8B8FF", "#7A62D8", "#ECE4FF")), (330, 430, 12, ("#FFE27A", "#D8A030", "#FFF4C0"))]):
        x, y = x + 10 * math.sin(T * 0.6 + j * 2), y + 6 * math.cos(T * 0.6 + j * 2)
        b.append(ball(x, y, rr, *c))
        b.append(inside(C(x, y, rr), f'<circle cx="{x-rr*0.3}" cy="{y+rr*0.2}" r="{rr*0.22}" fill="{c[1]}"/><circle cx="{x+rr*0.2}" cy="{y-rr*0.35}" r="{rr*0.14}" fill="{c[1]}"/>'))
    # tiny earth for scale
    b.append(ball(150, 300, 9, "#3AA8FF", "#1E64C0", "#BFE8FF") + inside(C(150, 300, 9), '<circle cx="147" cy="297" r="4" fill="#46E08A"/><circle cx="153" cy="304" r="3" fill="#46E08A"/>'))
    if not (ANIM and T > 2.45):
        b.append(popg(leader(150, 312, 150, 352) + chip(150, 366, "Earth", "#3A8CFF"), 150, 330, 1.5))
    b.append(popg(chip(600, 500, "764 Earths fit inside", "#FF4F9A", size=15), 600, 500, 1.0))
    # rocket with a dotted path
    b.append(f'<path d="M70 500 C 160 470 200 380 260 330" stroke="#FFFFFF" stroke-width="2.4" stroke-dasharray="1 8" stroke-dashoffset="{-T*18:.1f}" stroke-linecap="round" fill="none" opacity="0.7"/>')
    rk = (sh(P("M0 -34 Q14 -18 12 14 L-12 14 Q-14 -18 0 -34 Z"), "#F4F0FF", "#B8A8E0", "#FFFFFF", 0.6) +
          inside(P("M0 -34 Q14 -18 12 14 L-12 14 Q-14 -18 0 -34 Z"), '<rect x="-20" y="-40" width="40" height="14" fill="#FF4F7A"/>') +
          ball(0, -6, 5, "#5ACCFF", "#2A7AD0", "#DFF6FF") +
          sh(P("M-12 2 L-22 18 L-12 14 Z"), "#FF4F7A", "#C02A5A") + sh(P("M12 2 L22 18 L12 14 Z"), "#FF4F7A", "#C02A5A") +
          glow(0, 26, 12, "#FFB040", 0.9, 4) + sh(P(f"M-7 14 Q0 {40 + 8*math.sin(T*40):.1f} 7 14 Z"), "#FFE27A", "#FF8A3A"))
    u = 0.55 + 0.45 * ease(T / 5) if (CAM or ANIM) else 1.0
    bz = lambda u_, a_, b_, c_, d_: (1-u_)**3*a_ + 3*(1-u_)**2*u_*b_ + 3*(1-u_)*u_**2*c_ + u_**3*d_
    rx_, ry_ = bz(u, 70, 160, 200, 260) + 40 * max(0, u - 1), bz(u, 500, 470, 380, 330)
    b.append(g(rk, rx_ + 8, ry_ - 8, 1.0, 40 + 1.2 * math.sin(T * 2)))
    return svg("".join(b), ex)


# ------------------------------------------------------------------ 2. stat cards
def f_stats():
    ex = lin("st", [(0, "#7A3CF0"), (1, "#4A1AB8")])
    b = [f'<rect width="{W}" height="{H}" fill="url(#st)"/>']
    for i in range(14):
        b.append(f'<circle cx="{(i*137)%W}" cy="{(i*89)%H}" r="{40 + (i*23)%60}" fill="#FFFFFF" opacity="0.035"/>')
    b.append(chip(480, 48, "A DAY IN NUMBERS", "#FFD23A", "#3A1470", 18))
    cards = [("Sleep", "7h 12m", "#3AC8FF", 0.62), ("Screens", "4h 37m", "#FF4F9A", 0.48), ("Steps", "5,100", "#46E08A", 0.51)]
    for i, (lab, num, col, frac) in enumerate(cards):
        x = 96 + i * 270
        card = R(x, 92, 228, 400, 18)
        b.append(f'<rect x="{x}" y="100" width="228" height="400" rx="18" fill="#1A0650" opacity="0.35"/>')
        b.append(sh(card, "#5A2AD0", "#4A1EB0", "#8A62FF", 0.8))
        b.append(inside(card, f'<rect x="{x}" y="92" width="228" height="48" fill="{col}"/><rect x="{x}" y="132" width="228" height="8" fill="#000" opacity="0.12"/>'))
        b.append(text(x + 114, 124, lab, 20, "#FFFFFF", 700, "middle"))
        cx, cy = x + 114, 250
        b.append(glow(cx, cy, 70, col, 0.35, 16))
        if i == 0:      # moon on a pillow
            b.append(sh(P(f"M{cx-70} {cy+40} Q{cx-80} {cy+10} {cx-50} {cy+6} L{cx+50} {cy+6} Q{cx+80} {cy+10} {cx+70} {cy+40} Q{cx} {cy+56} {cx-70} {cy+40} Z"), "#F4F0FF", "#BCB0E8", "#FFFFFF"))
            moon = P(f"M{cx+8} {cy-70} A48 48 0 1 0 {cx+44} {cy+4} A38 38 0 1 1 {cx+8} {cy-70} Z")
            b.append(sh(moon, "#FFE27A", "#E0A030", "#FFF6C8"))
            b.append(f'<path d="M{cx-14} {cy-22} q7 6 14 0" stroke="#7A4A10" stroke-width="3" fill="none" stroke-linecap="round"/>')
            b.append(text(cx + 46, cy - 50, "z", 22, "#FFFFFF") + text(cx + 64, cy - 72, "z", 16, "#FFFFFF", op=0.7))
        if i == 1:      # phone with notifications
            ph = R(cx - 40, cy - 74, 80, 140, 14)
            b.append(sh(ph, "#2A1A5A", "#1A0E40", "#6A5AB0"))
            b.append(inside(R(cx - 33, cy - 64, 66, 120, 8), f'<rect x="{cx-40}" y="{cy-74}" width="80" height="140" fill="#FF7AB8"/>'
                            f'<circle cx="{cx+30}" cy="{cy-70}" r="60" fill="#FFB0D8" opacity="0.6"/>'))
            for k, c in enumerate(["#FFFFFF", "#FFE27A", "#FFFFFF"]):
                b.append(f'<rect x="{cx-27}" y="{cy-50+k*30}" width="54" height="20" rx="6" fill="{c}"/><circle cx="{cx-18}" cy="{cy-40+k*30}" r="5" fill="{col}"/>'
                         f'<rect x="{cx-8}" y="{cy-44+k*30}" width="26" height="4" rx="2" fill="#C9B8E0"/>')
            b.append(ball(cx + 40, cy - 72, 14, "#FF3A5A", "#C02040", "#FF9AA8") + text(cx + 40, cy - 67, "9+", 13, "#FFFFFF", 700, "middle"))
        if i == 2:      # sneaker
            shoe = P(f"M{cx-70} {cy+30} Q{cx-74} {cy-10} {cx-50} {cy-34} L{cx-10} {cy-40} Q{cx+10} {cy-6} {cx+50} {cy} Q{cx+76} {cy+6} {cx+74} {cy+30} Z")
            b.append(sh(shoe, "#46E08A", "#1EA864", "#C2FFD8"))
            b.append(inside(shoe, f'<rect x="{cx-80}" y="{cy+16}" width="160" height="20" fill="#FFFFFF"/><path d="M{cx-60} {cy-10} q20 -6 40 6 l-4 10 q-18 -10 -36 -4 Z" fill="#FFFFFF" opacity="0.9"/>'))
            b.append(inside(shoe, "".join(f'<rect x="{cx-38+k*13}" y="{cy-36+k*3}" width="9" height="16" rx="3" fill="#FFFFFF" transform="rotate(-30 {cx-34+k*13} {cy-28+k*3})"/>' for k in range(3))))
        b.append(text(x + 114, 392, num, 40, "#FFFFFF", 700, "middle"))
        bar = R(x + 24, 430, 180, 16, 8)
        b.append(f'<rect x="{x+24}" y="430" width="180" height="16" rx="8" fill="#2A0E80"/>')
        b.append(inside(bar, f'<rect x="{x+24}" y="430" width="{180*frac:.2f}" height="16" rx="8" fill="{col}"/><rect x="{x+24}" y="430" width="{180*frac:.2f}" height="5" fill="#FFFFFF" opacity="0.35"/>'))
        b.append(text(x + 114, 472, f"{int(frac*100)}% of goal", 13, "#D8C8FF", 600, "middle", "Inter"))
    return svg("".join(b), ex)


# ------------------------------------------------------------------ 3. floating iso island city
def f_island():
    rnd = random.Random(3)
    ex = lin("sk3", [(0, "#4A2AE0"), (0.55, "#36B8F0"), (1, "#FFB0E0")])
    b = [f'<rect width="{W}" height="{H}" fill="url(#sk3)"/>']
    b.append(glow(760, 110, 70, "#FFF6C0", 0.8, 16) + ball(760, 110, 34, "#FFF6D0", "#FFE08A", "#FFFFFF"))
    for (x, y, s) in [(120, 120, 1.0), (840, 300, 0.8), (90, 380, 0.7), (700, 470, 1.1)]:
        x = x + T * 9 * s
        cl = U(C(x, y, 22*s), C(x + 26*s, y - 10*s, 28*s), C(x + 56*s, y, 20*s), R(x - 22*s, y, 98*s, 20*s, 10*s))
        b.append(sh(cl, "#FFFFFF", "#D8C8FF", "#FFFFFF", s))
    ox, oy, s = 480, 330 + 3 * math.sin(2 * math.pi * T / 6), 21
    def ip(gx, gy):
        return (ox + (gx - gy) * I * s, oy + (gx + gy) * 0.5 * s - 105)
    # island top slab + underside
    F = ip(9, 9); Rr = ip(9, 0); L = ip(0, 9); Bk = ip(0, 0)
    under = P(f"M{L[0]:.2f} {L[1]+16:.2f} L{F[0]:.2f} {F[1]+16:.2f} L{Rr[0]:.2f} {Rr[1]+16:.2f} L{F[0]+40:.2f} {F[1]+120:.2f} L{F[0]-10:.2f} {F[1]+190:.2f} L{F[0]-60:.2f} {F[1]+110:.2f} Z")
    b.append(sh(under, "#9A4ABE", "#5A2490", "#D08AE8", 2))
    b.append(inside(under, "".join(f'<path d="M{L[0]-20} {F[1]+30+i*28} Q{F[0]} {F[1]+50+i*28} {Rr[0]+20} {F[1]+20+i*28} L{Rr[0]+20} {F[1]+30+i*28} Q{F[0]} {F[1]+60+i*28} {L[0]-20} {F[1]+40+i*28} Z" fill="#3A1470" opacity="0.35"/>' for i in range(6))))
    for (x, y) in [(F[0] - 30, F[1] + 80), (F[0] + 26, F[1] + 60)]:
        b.append(ball(x, y, 9, "#46E0D0", "#1EA6A8", "#C8FFF8") + glow(x, y, 12, "#46E0D0", 0.6, 4))
    b.append(iso_box(F[0], F[1], 9 * s, 9 * s, 16, "#5AEA8A", "#A0583A", "#7A3A2A"))
    # river across the island + waterfall off the edge
    rv = [ip(0, 3.6), ip(9, 3.6), ip(9, 5), ip(0, 5)]
    rv = [(x, y - 16) for x, y in rv]
    b.append(poly(rv, "#3AC8FF") + poly([rv[0], rv[1], (rv[1][0], rv[1][1] + 5), (rv[0][0], rv[0][1] + 5)], "#B8F0FF", 0.7))
    wf = P(f"M{rv[1][0]:.2f} {rv[1][1]:.2f} L{rv[2][0]:.2f} {rv[2][1]:.2f} L{rv[2][0]+4:.2f} {rv[2][1]+150:.2f} L{rv[1][0]+4:.2f} {rv[1][1]+150:.2f} Z")
    b.append(sh(wf, "#9AE8FF", "#4AB8F0", "#FFFFFF", 0.6) + inside(wf, "".join(f'<rect x="{rv[1][0]+4+k*7:.2f}" y="{rv[1][1] - 60 + (rnd.uniform(0,150) + T*120) % 210:.1f}" width="2.5" height="{rnd.uniform(20,60):.2f}" rx="1.2" fill="#FFFFFF" opacity="0.8"/>' for k in range(8))))
    b.append(glow((rv[1][0] + rv[2][0]) / 2, rv[2][1] + 150, 26, "#FFFFFF", 0.7, 8))
    # road
    rd = [ip(6.2, 0), ip(7.1, 0), ip(7.1, 3.6), ip(6.2, 3.6)]
    b.append(poly([(x, y - 16) for x, y in rd], "#5A4A8A"))
    # buildings back-to-front
    blds = [(0.5, 0.5, 2, 2, 120, "violet"), (3, 0.4, 1.6, 1.6, 170, "pink"), (0.6, 2.4, 1.4, 1.0, 70, "yellow"), (4.6, 0.6, 1.4, 1.4, 90, "blue"),
            (2.6, 2.3, 1.2, 1.2, 60, "orange"), (7.6, 0.6, 1.2, 1.4, 130, "cyan"), (7.6, 2.2, 1.2, 1.2, 60, "pink"),
            (1, 5.8, 1.6, 1.6, 100, "blue"), (3.2, 5.6, 1.4, 1.2, 150, "violet"), (5.2, 5.8, 1.4, 1.4, 80, "yellow"), (7.4, 6, 1.4, 1.4, 110, "pink"),
            (2.2, 7.6, 1.2, 1.2, 46, "cream"), (5, 7.6, 1.6, 1.0, 60, "mint")]
    items = []
    for gx, gy, a, bb, hh, pal in blds:
        F2 = ip(gx + a, gy + bb)
        F2 = (F2[0], F2[1] - 16)
        t, l, r_ = PAL[pal]
        items.append((gx + gy + a + bb, iso_box(F2[0], F2[1], bb * s, a * s, hh, t, l, r_) +
                      iso_windows(F2[0], F2[1], bb * s, a * s, hh, random.Random(int(gx * 100 + gy * 10)))))
    for gx, gy in [(2.4, 1.0), (6.0, 2.6), (0.4, 7.5), (8.3, 8.2), (4.4, 2.6), (1.6, 3.0), (8.6, 5.3), (6.6, 8.4)]:
        x, y = ip(gx, gy); y -= 16
        items.append((gx + gy + 0.5, f'<rect x="{x-2}" y="{y-14}" width="4" height="14" fill="#6A3A2A"/>' + ball(x, y - 22, 12, "#46E08A", "#1EA864", "#C2FFD8")))
    # crane
    cx_, cy_ = ip(4.7, 4.6); cy_ -= 16
    hk = 18 * math.sin(T * 1.3)
    items.append((10, f'<path d="M{cx_} {cy_} L{cx_} {cy_-170} M{cx_-30} {cy_-160} L{cx_+80} {cy_-160} M{cx_+70} {cy_-160} L{cx_+70} {cy_-110+hk:.1f}" stroke="#FFD23A" stroke-width="4" fill="none"/>'
                      f'<rect x="{cx_+62}" y="{cy_-110+hk:.1f}" width="16" height="12" rx="2" fill="#FF4F9A"/>'))
    for _, it in sorted(items, key=lambda t: t[0]):
        b.append(it)
    # cars on road
    for t_ in ((0.8 + T * 0.5) % 3.6, (2.6 + T * 0.7) % 3.6):
        x, y = ip(6.6, t_); y -= 20
        b.append(f'<rect x="{x-6}" y="{y-5}" width="12" height="8" rx="3" fill="#FF4F5A"/>')
    for j, (x, y) in enumerate([(200, 200), (230, 214), (260, 196)]):
        x, y = x + T * 22, y - T * 4
        w_ = 6 * math.sin(T * 9 + j * 1.7)
        b.append(f'<path d="M{x-8:.1f} {y:.1f} q4 {w_:.1f} 8 -1 q4 {w_:.1f} 8 1" stroke="#2A1470" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    b.append(popg(chip(150, 490, "Sandbox", "#FF4F9A", size=18), 150, 490, 1.2))
    return svg("".join(b), ex)


# ------------------------------------------------------------------ 4. lab
def f_lab():
    rnd = random.Random(4)
    ex = lin("lb", [(0, "#2A7AF0"), (1, "#1A3AB0")]) + lin("lq", [(0, "#8AFFE8"), (1, "#2AC8B0")])
    b = [f'<rect width="{W}" height="{H}" fill="url(#lb)"/>']
    for i in range(6):
        x = 20 + i * 160
        b.append(f'<rect x="{x}" y="30" width="140" height="330" rx="10" fill="#3A8AFF" opacity="0.35"/>')
        b.append(f'<circle cx="{x+12}" cy="42" r="3" fill="#1A3AB0"/><circle cx="{x+128}" cy="42" r="3" fill="#1A3AB0"/>')
    b.append(f'<rect x="0" y="380" width="{W}" height="160" fill="#14288A"/><rect x="0" y="380" width="{W}" height="6" fill="#4A9CFF"/>')
    for i in range(12):
        b.append(f'<path d="M{i*90-40} 540 L{i*90+30} 386" stroke="#1A3AA0" stroke-width="2"/>')
    # pipes
    b.append(sh(S("M300 140 Q300 80 400 80 L480 80", 18), "#9AA8D8", "#6A78B0", "#DDE4FF"))
    b.append(sh(S("M660 160 Q660 80 560 80 L480 80", 18), "#9AA8D8", "#6A78B0", "#DDE4FF"))
    # machines
    for (x, w, col) in [(150, 200, "#5A62C8"), (610, 200, "#5A62C8")]:
        m = R(x, 140, w, 250, 14)
        b.append(sh(m, "#7080E0", "#4A58B8", "#A8B4FF"))
        scr = R(x + 18, 160, w - 36, 110, 8)
        b.append(inside(scr, f'<rect x="{x}" y="150" width="{w}" height="130" fill="#0E1A5A"/>'
                             f'<circle cx="{x+w/2}" cy="215" r="70" fill="#2A4AD0" opacity="0.6" filter="url(#b16)"/>'
                             + "".join(f'<rect x="{x+18}" y="{172+k*22}" width="{w-36}" height="1.5" fill="#2A3A9A"/>' for k in range(5))))
        for k, c in enumerate(["#FF4F9A", "#FFD23A", "#46E08A"]):
            b.append(ball(x + 30 + k * 26, 300, 8, c, "#2A2A80"))
        b.append(f'<rect x="{x+20}" y="330" width="{w-40}" height="10" rx="5" fill="#3A46A0"/><rect x="{x+20}" y="350" width="{(w-40)*0.6:.2f}" height="10" rx="5" fill="#3A46A0"/>')
    # left screen: growth chart; right screen: readout
    pts = [(184 + i * 13, 252 - (i ** 1.7) * 1.6 - rnd.uniform(0, 5)) for i in range(11)]
    b.append(poly(pts + [(pts[-1][0], 262), (pts[0][0], 262)], "#46E0D0", 0.18))
    b.append(f'<path d="M{" L".join(f"{x:.2f} {y:.2f}" for x, y in pts)}" stroke="#46E0D0" stroke-width="3" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
    b.append(f'<circle cx="{pts[-1][0]:.2f}" cy="{pts[-1][1]:.2f}" r="5" fill="#FFFFFF"/>' + glow(pts[-1][0], pts[-1][1], 9, "#46E0D0", 0.8, 4))
    b.append(text(720, 205, "GROWTH", 15, "#8AA8FF", 700, "middle") + text(720, 245, "+212%", 34, "#46E0D0", 700, "middle"))
    # central capsule
    b.append(glow(480, 250, 150, "#46E0D0", 0.35, 30))
    base = U(R(390, 380, 180, 46, 12), E(480, 380, 90, 20))
    b.append(sh(base, "#6A78C8", "#3A48A0", "#B8C4FF"))
    b.append(sh(R(380, 70, 200, 40, 14), "#6A78C8", "#3A48A0", "#B8C4FF"))
    tube = R(404, 110, 152, 270, 6)
    b.append(inside(tube, f'<rect x="400" y="100" width="160" height="290" fill="url(#lq)" opacity="0.9"/>'
                          f'<rect x="400" y="100" width="160" height="40" fill="#C8FFF4" opacity="0.5"/>'
                          + "".join(f'<circle cx="{rnd.uniform(414,546):.2f}" cy="{rnd.uniform(140,370):.2f}" r="{rnd.uniform(2,6):.1f}" fill="#FFFFFF" opacity="0.6"/>' for _ in range(26))
                          + '<rect x="416" y="110" width="14" height="270" fill="#FFFFFF" opacity="0.35"/><rect x="438" y="110" width="5" height="270" fill="#FFFFFF" opacity="0.25"/>'
                          + '<rect x="532" y="110" width="24" height="270" fill="#0A6A70" opacity="0.25"/>'))
    # the specimen: a glowing sprout in a seed
    b.append(glow(480, 250, 50, "#FFF6A0", 0.8, 8))
    b.append(ball(480, 268, 30, "#FFC94A", "#D88A1A", "#FFF0B0"))
    b.append(sh(P("M480 240 Q470 200 480 180 Q490 200 480 240 Z"), "#46E08A", "#1EA864", "#C2FFD8", 0.5))
    b.append(sh(P("M480 196 Q450 170 430 186 Q452 206 480 196 Z"), "#46E08A", "#1EA864", "#C2FFD8", 0.5))
    b.append(sh(P("M480 190 Q510 160 532 174 Q510 198 480 190 Z"), "#46E08A", "#1EA864", "#C2FFD8", 0.5))
    # table with flasks
    b.append(sh(R(40, 420, 300, 22, 8), "#E8ECFF", "#A8B0E0", "#FFFFFF"))
    b.append(f'<rect x="60" y="442" width="16" height="98" fill="#0E1E6A"/><rect x="300" y="442" width="16" height="98" fill="#0E1E6A"/>')
    for (x, liq, hgt) in [(110, "#FF4F9A", 70), (190, "#FFD23A", 50), (262, "#46E0D0", 60)]:
        fl = P(f"M{x-8} {420-hgt} L{x+8} {420-hgt} L{x+8} {420-hgt+22} L{x+30} 418 Q{x} 424 {x-30} 418 L{x-8} {420-hgt+22} Z")
        b.append(sh(fl, "#DDE8FF", "#9AA8E0", "#FFFFFF", 0.6))
        b.append(inside(fl, f'<rect x="{x-40}" y="{420-hgt*0.45:.2f}" width="80" height="60" fill="{liq}"/>'
                            f'<rect x="{x-40}" y="{420-hgt*0.45:.2f}" width="80" height="4" fill="#FFFFFF" opacity="0.5"/>'
                            f'<rect x="{x-6}" y="{420-hgt}" width="4" height="{hgt}" fill="#FFFFFF" opacity="0.5"/>'))
        b.append(glow(x, 405, 22, liq, 0.4, 8))
    # stool + clipboard on the right, small drone helper
    b.append(sh(R(842, 400, 90, 16, 8), "#FF8A3A", "#D25A1E", "#FFC79A") + '<rect x="852" y="416" width="10" height="124" fill="#0E1E6A"/><rect x="912" y="416" width="10" height="124" fill="#0E1E6A"/>')
    cb = R(856, 340, 56, 62, 6)
    b.append(sh(cb, "#FFF6E6", "#D8C8B0", "#FFFFFF", 0.6) + inside(cb, "".join(f'<rect x="864" y="{356+k*10}" width="{40-k*6}" height="4" rx="2" fill="#B8A890"/>' for k in range(4))))
    b.append(sh(R(872, 334, 24, 10, 4), "#5A62C8", "#3A48A0"))
    dx_, dy_ = 820, 120
    b.append(glow(dx_, dy_ + 30, 26, "#FF4F9A", 0.4, 8))
    b.append(sh(E(dx_, dy_, 30, 16), "#F4F0FF", "#B8B0E0", "#FFFFFF", 0.7) + inside(E(dx_, dy_, 30, 16), f'<rect x="{dx_-30}" y="{dy_+4}" width="60" height="14" fill="#C8C0F0"/>'))
    b.append(ball(dx_, dy_ - 2, 8, "#2A1A5A", "#14103A", "#5A4AA0") + f'<circle cx="{dx_+2}" cy="{dy_-4}" r="3" fill="#FF4F9A"/>')
    for sx_ in (-36, 36):
        b.append(f'<rect x="{dx_+sx_-18}" y="{dy_-14}" width="36" height="5" rx="2.5" fill="#9AA8D8" opacity="0.8"/><rect x="{dx_+sx_-2}" y="{dy_-12}" width="4" height="12" fill="#5A62C8"/>')
    return svg("".join(b), ex)



# ------------------------------------------------------------------ 5. whale
def f_whale():
    rnd = random.Random(5)
    ex = lin("oc", [(0, "#1E7AF0"), (0.45, "#1240B8"), (1, "#0A1050")])
    b = [f'<rect width="{W}" height="{H}" fill="url(#oc)"/>']
    for k in range(7):
        x = 80 + k * 140 + rnd.uniform(-30, 30)
        b.append(f'<path d="M{x-14} 0 L{x+14} 0 L{x+120} {H} L{x+40} {H} Z" fill="#BFF0FF" opacity="0.06"/>')
    b.append(f'<path d="M0 0 L{W} 0 L{W} 22 Q{W*0.75} 34 {W/2} 22 Q{W*0.25} 10 0 22 Z" fill="#7FD8FF" opacity="0.35"/>')
    for _ in range(90):
        x, y = rnd.uniform(0, W), rnd.uniform(40, H - 40)
        b.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rnd.uniform(0.6, 1.8):.1f}" fill="#9AF4FF" opacity="{rnd.uniform(0.3, 0.8):.2f}"/>')
    # seabed
    bed = P(f"M0 470 Q120 440 240 466 Q380 490 520 460 Q700 430 {W} 468 L{W} {H} L0 {H} Z")
    b.append(bed("#0A1446"))
    for (x, hgt, c) in [(80, 120, "#2EC8A0"), (110, 90, "#1EA88A"), (840, 140, "#2EC8A0"), (880, 100, "#1EA88A"), (610, 70, "#FF4F9A")]:
        kelp = P(f"M{x-6} 480 Q{x-20} {480-hgt*0.5} {x} {480-hgt} Q{x+20} {480-hgt*0.5} {x+6} 480 Z")
        b.append(sh(kelp, c, "#127060", None, 0.6))
    for (x, y, r_) in [(300, 478, 30), (340, 484, 20), (700, 470, 26)]:
        b.append(sh(E(x, y, r_ * 1.4, r_), "#2A3A8A", "#1A2466", "#5A6AC8", 0.8))
    # whale
    body = P("M250 300 C300 210 520 190 690 236 C770 258 812 300 800 330 C780 372 640 394 470 390 C360 388 290 362 250 332 Z")
    stock = P("M276 296 Q210 296 170 280 L176 336 Q216 336 276 340 Z")
    fluke = P("M180 300 Q130 248 84 246 Q118 284 150 308 Q112 336 80 372 Q140 368 184 322 Z")
    fin = P("M520 356 Q560 420 510 468 Q500 420 470 376 Z")
    b.append(sh(fluke, "#4A62D8", "#2E3EA8", "#9AB8FF"))
    b.append(sh(stock, "#4A62D8", "#2E3EA8", "#9AB8FF"))
    b.append(sh(body, "#5A72E8", "#3546B8", "#A8C4FF", 1.6))
    belly = E(560, 392, 260, 56)
    b.append(inside(body, belly("#D8E4FF") + "".join(f'<path d="M{430+k*40} 352 Q{520+k*40} 368 {600+k*40} 360 L{600+k*40} 364 Q{520+k*40} 373 {430+k*40} 357 Z" fill="#A8B8F0"/>' for k in range(6))
                    + f'<ellipse cx="470" cy="250" rx="300" ry="50" fill="#7A92FF" opacity="0.45"/>'
                    + "".join(f'<circle cx="{rnd.uniform(330,680):.2f}" cy="{rnd.uniform(230,300):.2f}" r="{rnd.uniform(3,7):.1f}" fill="#3A4AB8" opacity="0.5"/>' for _ in range(16))))
    b.append(sh(fin, "#4A62D8", "#2E3EA8", "#9AB8FF"))
    b.append(ball(712, 300, 6, "#141040", "#0A0828") + '<circle cx="714" cy="298" r="2" fill="#FFFFFF"/>')
    b.append(f'<path d="M712 324 Q760 330 796 318" stroke="#2A2A80" stroke-width="3" fill="none" stroke-linecap="round"/>')
    # fish school in an arc
    for k in range(48):
        t = k / 47
        x = 560 + 330 * math.cos(math.pi * (0.85 + 0.9 * t)) + rnd.uniform(-20, 20)
        y = 300 + 220 * math.sin(math.pi * (0.85 + 0.9 * t)) * 0.75 + rnd.uniform(-14, 14) - 30
        if 230 < y < 400 and 240 < x < 800:
            continue
        c = rnd.choice(["#FFD23A", "#FF8A3A", "#FFE27A"])
        fs = rnd.uniform(0.7, 1.1)
        fish = f'<ellipse cx="0" cy="0" rx="9" ry="5" fill="{c}"/><path d="M-7 0 L-15 -5 L-15 5 Z" fill="{c}"/><circle cx="4" cy="-1" r="1.4" fill="#2A1030"/>'
        b.append(g(fish, x, y, fs, rnd.uniform(-20, 20)))
    for _ in range(14):
        x, y = rnd.uniform(560, 820), rnd.uniform(60, 240)
        r_ = rnd.uniform(3, 9)
        b.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r_:.1f}" fill="#BFF4FF" opacity="0.35"/>'
                 + inside(C(x, y, r_), f'<circle cx="{x - r_*0.35:.1f}" cy="{y - r_*0.35:.1f}" r="{r_*0.35:.1f}" fill="#FFFFFF" opacity="0.8"/>'))
    b.append(chip(170, 70, "Blue whale", "#FFD23A", "#14286A", 16) + chip(170, 104, "30 m long", "#2EC8F0", "#0A1446", 13))
    return svg("".join(b), ex)


# ------------------------------------------------------------------ 6. cell
def f_cell():
    rnd = random.Random(6)
    ex = rad("ce", [(0, "#C23AD0", 1), (1, "#4A0E8A", 1)], 0.5, 0.5, 0.7)
    b = [f'<rect width="{W}" height="{H}" fill="url(#ce)"/>']
    for _ in range(40):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        b.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rnd.uniform(2, 6):.1f}" fill="#FFB0F0" opacity="0.25"/>')
    cx, cy = 470, 280
    pts = []
    for k in range(18):
        a = 2 * math.pi * k / 18
        rr = 220 + 14 * math.sin(3 * a) + 8 * math.cos(5 * a)
        pts.append((cx + rr * math.cos(a) * 1.15, cy + rr * math.sin(a) * 0.98))
    d = f"M{pts[0][0]:.2f} {pts[0][1]:.2f} " + " ".join(
        f"Q{pts[k][0]:.2f} {pts[k][1]:.2f} {(pts[k][0]+pts[(k+1)%18][0])/2:.2f} {(pts[k][1]+pts[(k+1)%18][1])/2:.2f}" for k in range(18)) + " Z"
    cell = P(d)
    b.append(glow(cx, cy, 250, "#FF6FD0", 0.3, 30))
    b.append(sh(cell, "#FF7AC8", "#C2408E", "#FFC4EA", 3))
    inner = P(d.replace("M", "M").strip())
    b.append(inside(cell, f'<g transform="translate({cx} {cy}) scale(0.93) translate({-cx} {-cy})">{cell("#FFC0E4")}</g>'
                          f'<g transform="translate({cx} {cy}) scale(0.93) translate({-cx} {-cy})">' + term(cell, -40, -36, "#E080C0", 0.6) + '</g>'
                          + "".join(f'<circle cx="{rnd.uniform(270,680):.2f}" cy="{rnd.uniform(90,470):.2f}" r="{rnd.uniform(1.5,3.5):.1f}" fill="#B8408A" opacity="0.6"/>' for _ in range(90))))
    # ER bands around nucleus
    for k in range(3):
        b.append(sh(S(f"M{430-k*16} {150-k*18} Q{360-k*20} {230} {420-k*14} {350+k*16}", 9), "#E86AB8", "#B8408A", "#FFB0DC"))
    # nucleus
    b.append(ball(520, 250, 82, "#8A5AF0", "#5A30C0", "#C8B0FF"))
    b.append(inside(C(520, 250, 82), "".join(f'<circle cx="{rnd.uniform(450,600):.2f}" cy="{rnd.uniform(180,320):.2f}" r="{rnd.uniform(3,7):.1f}" fill="#6A40D0" opacity="0.7"/>' for _ in range(22))))
    b.append(ball(536, 240, 24, "#4A1AA8", "#300E80", "#8A6AE8"))
    # mitochondria
    for (x, y, rot) in [(340, 380, 20), (640, 400, -18), (680, 170, 30), (330, 200, -30)]:
        m = E(0, 0, 46, 24)
        cr = "".join(f'<path d="M{-36+k*14} -16 Q{-30+k*14} 0 {-36+k*14} 16" stroke="#C8501E" stroke-width="5" fill="none" stroke-linecap="round"/>' for k in range(6))
        b.append(g(sh(m, "#FFB040", "#E0701E", "#FFE0A0") + inside(m, f'<ellipse cx="0" cy="0" rx="38" ry="16" fill="#FFD27A"/>' + cr), x, y, 1.0, rot))
    for (x, y, r_) in [(420, 440, 14), (600, 330, 10), (390, 300, 12), (720, 280, 16), (560, 450, 9)]:
        b.append(ball(x, y, r_, "#46E0D0", "#1EA6A8", "#C8FFF8"))
    # viruses outside
    for (x, y, r_) in [(110, 120, 26), (860, 110, 22), (870, 430, 30), (90, 450, 18)]:
        for k in range(10):
            a = 2 * math.pi * k / 10
            x2, y2 = x + (r_ + 10) * math.cos(a), y + (r_ + 10) * math.sin(a)
            b.append(f'<path d="M{x:.2f} {y:.2f} L{x2:.2f} {y2:.2f}" stroke="#46E08A" stroke-width="3.4"/>' + ball(x2, y2, 4.5, "#C2FFD8", "#46E08A"))
        b.append(ball(x, y, r_, "#46E08A", "#1EA864", "#C2FFD8"))
        b.append(inside(C(x, y, r_), f'<circle cx="{x+r_*0.3}" cy="{y+r_*0.2}" r="{r_*0.25}" fill="#1EA864"/><circle cx="{x-r_*0.3}" cy="{y-r_*0.3}" r="{r_*0.15}" fill="#1EA864"/>'))
    b.append(leader(560, 200, 640, 80) + chip(640, 66, "nucleus", "#8A5AF0"))
    b.append(leader(660, 404, 770, 486) + chip(780, 500, "mitochondria", "#FF8A3A"))
    b.append(leader(870, 430, 900, 340) + chip(900, 326, "virus", "#1EA864"))
    return svg("".join(b), ex)


# ------------------------------------------------------------------ 7. timeline
def f_timeline():
    ex = lin("tl", [(0, "#FFF2DE"), (1, "#FFE0C0")])
    b = [f'<rect width="{W}" height="{H}" fill="url(#tl)"/>']
    for i in range(20):
        b.append(f'<circle cx="{(i*173)%W}" cy="{(i*97)%H}" r="{20 + (i*31)%40}" fill="#FFB27A" opacity="0.08"/>')
    b.append(chip(140, 60, "BIG LEAPS", "#5A2AD0", size=20))
    y0 = 380
    seg = [("#FF4F9A", 60), ("#FF8A3A", 260), ("#FFD23A", 470), ("#46E08A", 650), ("#3A8CFF", 800)]
    b.append(f'<rect x="60" y="{y0+4}" width="840" height="34" rx="17" fill="#C9A08A" opacity="0.4"/>')
    bar = R(60, y0, 840, 34, 17)
    b.append(sh(bar, "#5A2AD0", "#3A1A98", "#8A62FF", 0.7))
    b.append(inside(bar, "".join(f'<rect x="{x}" y="{y0}" width="{(seg[i+1][1] if i < 4 else 900) - x}" height="34" fill="{c}"/>'
                                 f'<rect x="{x}" y="{y0}" width="{(seg[i+1][1] if i < 4 else 900) - x}" height="9" fill="#FFFFFF" opacity="0.3"/>'
                                 f'<rect x="{x}" y="{y0+25}" width="{(seg[i+1][1] if i < 4 else 900) - x}" height="9" fill="#000" opacity="0.12"/>'
                                 for i, (c, x) in enumerate(seg))))
    years = ["3500 BC", "1440", "1879", "1969", "2007"]
    labs = ["wheel", "printing", "light bulb", "moon", "smartphone"]
    xs = [130, 340, 540, 700, 840]
    for i, (x, yr, lab) in enumerate(zip(xs, years, labs)):
        b.append(f'<path d="M{x} {y0-6} L{x} {y0-40}" stroke="#5A2AD0" stroke-width="3"/><circle cx="{x}" cy="{y0+17}" r="7" fill="#FFFFFF"/>')
        b.append(chip(x, y0 + 70, yr, "#2A1470", size=15) + text(x, y0 + 106, lab, 14, "#7A5A8A", 600, "middle", "Inter"))
        cy = 250
        b.append(f'<ellipse cx="{x}" cy="{cy+80}" rx="46" ry="8" fill="#C9A08A" opacity="0.35"/>')
        if i == 0:
            wh = C(x, cy + 10, 56)
            b.append(sh(wh, "#B8784A", "#8A5230", "#E8A878", 1.2))
            b.append(inside(wh, f'<circle cx="{x}" cy="{cy+10}" r="40" fill="#E8C8A0"/>' + "".join(f'<rect x="{x-4}" y="{cy-34}" width="8" height="88" fill="#B8784A" transform="rotate({k*45} {x} {cy+10})"/>' for k in range(4))))
            b.append(ball(x, cy + 10, 12, "#8A5230", "#5A3018", "#C8885A"))
        if i == 1:
            pr = R(x - 60, cy - 40, 120, 90, 10)
            b.append(sh(pr, "#9A6A4A", "#6A4228", "#D8A078"))
            b.append(sh(R(x - 46, cy - 70, 92, 30, 6), "#6A4228", "#4A2A18"))
            b.append(sh(P(f"M{x-40} {cy+50} L{x+40} {cy+50} L{x+52} {cy+80} L{x-52} {cy+80} Z"), "#FFF6E6", "#D8C8B0", "#FFFFFF"))
            b.append("".join(f'<rect x="{x-36+k*8}" y="{cy+58}" width="5" height="3" fill="#2A1470"/>' for k in range(9)))
            b.append(ball(x, cy - 10, 16, "#C9A040", "#8A6A20", "#FFE08A"))
        if i == 2:
            b.append(glow(x, cy - 10, 70, "#FFE27A", 0.7, 16))
            bulb = U(C(x, cy - 16, 46), R(x - 22, cy + 14, 44, 30, 6))
            b.append(sh(bulb, "#FFF6B0", "#FFD23A", "#FFFFFF", 1.0))
            b.append(f'<path d="M{x-12} {cy+12} L{x-12} {cy-20} q12 -16 24 0 L{x+12} {cy+12}" stroke="#E08A1A" stroke-width="3" fill="none"/>')
            b.append(sh(R(x - 20, cy + 40, 40, 34, 6), "#9AA8D8", "#6A78B0", "#DDE4FF") + "".join(f'<rect x="{x-20}" y="{cy+46+k*9}" width="40" height="4" fill="#6A78B0"/>' for k in range(3)))
        if i == 3:
            b.append(ball(x, cy, 58, "#E8E4F4", "#B0A8CC", "#FFFFFF"))
            b.append(inside(C(x, cy, 58), "".join(f'<circle cx="{x+dx}" cy="{cy+dy}" r="{rr}" fill="#B8B0D8"/>' for dx, dy, rr in [(-20, -18, 12), (18, 10, 16), (-10, 30, 8), (26, -28, 7)])))
            b.append(f'<path d="M{x+6} {cy-56} L{x+6} {cy-96}" stroke="#7A5A8A" stroke-width="3"/>' + sh(P(f"M{x+6} {cy-96} L{x+44} {cy-88} L{x+6} {cy-78} Z"), "#FF4F5A", "#C02A3A"))
        if i == 4:
            ph = R(x - 34, cy - 66, 68, 130, 12)
            b.append(sh(ph, "#2A1A5A", "#14103A", "#6A5AB0"))
            b.append(inside(R(x - 28, cy - 58, 56, 112, 7), f'<rect x="{x-40}" y="{cy-70}" width="80" height="140" fill="#3A8CFF"/>'
                            + "".join(f'<rect x="{x-22+(k%3)*16}" y="{cy-48+(k//3)*18}" width="12" height="12" rx="3" fill="{["#FFD23A", "#FF4F9A", "#46E08A", "#FFFFFF", "#FF8A3A", "#B9A2FF"][k%6]}"/>' for k in range(12))))
    return svg("".join(b), ex)


# ------------------------------------------------------------------ 8. food friends
def f_food():
    rnd = random.Random(8)
    ex = rad("fd", [(0, "#FFE680", 1), (1, "#FFB82A", 1)], 0.5, 0.55, 0.75)
    b = [f'<rect width="{W}" height="{H}" fill="url(#fd)"/>']
    for k in range(18):
        a0 = 2 * math.pi * k / 18
        b.append(poly([(480, 300), (480 + 900 * math.cos(a0), 300 + 900 * math.sin(a0)), (480 + 900 * math.cos(a0 + 0.17), 300 + 900 * math.sin(a0 + 0.17))], "#FFFFFF", 0.13))
    b.append(f'<path d="M0 430 Q480 400 {W} 430 L{W} {H} L0 {H} Z" fill="#38C8B8"/><path d="M0 430 Q480 400 {W} 430 L{W} 440 Q480 410 0 440 Z" fill="#8AF0E0"/>')
    # avocado
    ax, ay = 160, 300
    av = P(f"M{ax} {ay-120} Q{ax+40} {ay-120} {ax+56} {ay-40} Q{ax+100} {ay+40} {ax+70} {ay+100} Q{ax} {ay+150} {ax-70} {ay+100} Q{ax-100} {ay+40} {ax-56} {ay-40} Q{ax-40} {ay-120} {ax} {ay-120} Z")
    b.append(f'<ellipse cx="{ax}" cy="{ay+130}" rx="90" ry="12" fill="#1E8A80" opacity="0.5"/>')
    b.append(sh(av, "#3A8A2A", "#22601E", "#8AD06A", 1.2))
    b.append(inside(av, f'<g transform="translate({ax} {ay}) scale(0.86) translate({-ax} {-ay-4})">{av("#C8F07A")}</g>'))
    b.append(ball(ax, ay + 40, 38, "#B8703A", "#7A4220", "#E8A878"))
    b.append(face(ax, ay - 40, 1.3))
    # strawberry
    sx, sy = 380, 330
    st = P(f"M{sx} {sy+100} Q{sx-90} {sy+20} {sx-80} {sy-40} Q{sx-60} {sy-80} {sx} {sy-70} Q{sx+60} {sy-80} {sx+80} {sy-40} Q{sx+90} {sy+20} {sx} {sy+100} Z")
    b.append(f'<ellipse cx="{sx}" cy="{sy+106}" rx="70" ry="10" fill="#1E8A80" opacity="0.5"/>')
    b.append(sh(st, "#FF3A5A", "#C01E40", "#FF9AA8", 1.2))
    b.append(inside(st, "".join(f'<ellipse cx="{sx-60+(k%6)*24+(k//6%2)*12}" cy="{sy-30+(k//6)*28}" rx="3" ry="5" fill="#FFE27A"/>' for k in range(30))))
    lv = P(f"M{sx} {sy-64} L{sx-50} {sy-84} L{sx-20} {sy-90} L{sx} {sy-116} L{sx+20} {sy-90} L{sx+50} {sy-84} Z")
    b.append(sh(lv, "#46E08A", "#1EA864", "#C2FFD8"))
    b.append(face(sx, sy - 10, 1.3, "open"))
    # toast
    tx, ty = 600, 320
    toast = P(f"M{tx-80} {ty+100} L{tx-80} {ty-40} Q{tx-110} {ty-70} {tx-80} {ty-100} Q{tx} {ty-140} {tx+80} {ty-100} Q{tx+110} {ty-70} {tx+80} {ty-40} L{tx+80} {ty+100} Z")
    b.append(f'<ellipse cx="{tx}" cy="{ty+106}" rx="96" ry="10" fill="#1E8A80" opacity="0.5"/>')
    b.append(sh(toast, "#D88A3A", "#A85A1E", "#FFC27A", 1.2))
    b.append(inside(toast, f'<g transform="translate({tx} {ty}) scale(0.84) translate({-tx} {-ty+4})">{toast("#FFE0A8")}</g>'))
    but = R(tx - 30, ty + 10, 60, 40, 8)
    b.append(sh(but, "#FFF2A0", "#FFD23A", "#FFFFFF", 0.7))
    b.append(face(tx, ty - 34, 1.3))
    # donut
    dx, dy = 810, 360
    dn = P(f"M{dx-90} {dy} A90 72 0 1 0 {dx+90} {dy} A90 72 0 1 0 {dx-90} {dy} Z M{dx-26} {dy-4} A26 18 0 1 1 {dx+26} {dy-4} A26 18 0 1 1 {dx-26} {dy-4} Z")
    dnf = lambda c: dn(c).replace("<path", '<path fill-rule="evenodd"')
    b.append(f'<ellipse cx="{dx}" cy="{dy+70}" rx="90" ry="10" fill="#1E8A80" opacity="0.5"/>')
    b.append(sh(dnf, "#D88A3A", "#A85A1E", "#FFC27A", 1.2))
    icing = P(f"M{dx-80} {dy-6} Q{dx-84} {dy-60} {dx} {dy-64} Q{dx+84} {dy-60} {dx+80} {dy-6} Q{dx+70} {dy+20} {dx+50} {dy+8} Q{dx+30} {dy+36} {dx+6} {dy+20} Q{dx-24} {dy+40} {dx-40} {dy+14} Q{dx-66} {dy+30} {dx-80} {dy-6} Z M{dx-26} {dy-4} A26 18 0 1 0 {dx+26} {dy-4} A26 18 0 1 0 {dx-26} {dy-4} Z")
    icf = lambda c: icing(c).replace("<path", '<path fill-rule="evenodd"')
    b.append(sh(icf, "#FF6FB5", "#D0408A", "#FFC4E4", 0.9))
    b.append(inside(icf, "".join(f'<rect x="{rnd.uniform(dx-70, dx+64):.2f}" y="{rnd.uniform(dy-56, dy+10):.2f}" width="10" height="4" rx="2" fill="{rnd.choice(["#FFFFFF", "#FFD23A", "#3A8CFF", "#46E08A"])}" transform="rotate({rnd.uniform(0,180):.2f} {dx} {dy})"/>' for _ in range(0))
                     + "".join((lambda x_, y_, c_: f'<rect x="{x_-5:.2f}" y="{y_-2:.2f}" width="10" height="4" rx="2" fill="{c_}" transform="rotate({rnd.uniform(0,180):.2f} {x_:.2f} {y_:.2f})"/>')(rnd.uniform(dx-70, dx+70), rnd.uniform(dy-56, dy+14), rnd.choice(["#FFFFFF", "#FFD23A", "#3A8CFF", "#46E08A"])) for _ in range(40))))
    b.append(face(dx, dy - 40, 1.0))
    for (x, y, r_) in [(270, 160, 10), (500, 140, 8), (720, 180, 12), (900, 240, 7), (60, 200, 8)]:
        b.append(sparkle(x, y, r_, "#FFFFFF"))
    return svg("".join(b), ex)


# ------------------------------------------------------------------ 9. atom
def f_atom():
    rnd = random.Random(9)
    ex = rad("at", [(0, "#4A22C8", 1), (0.6, "#24107A", 1), (1, "#0E0636", 1)], 0.5, 0.5, 0.7)
    b = [f'<rect width="{W}" height="{H}" fill="url(#at)"/>', stars(rnd, 70)]
    # perspective grid floor
    for k in range(-12, 13):
        b.append(f'<path d="M{480+k*20} 330 L{480+k*120} {H}" stroke="#6A4AF0" stroke-width="1.2" opacity="0.35"/>')
    for k in range(8):
        y = 330 + (k ** 1.8) * 4.6
        b.append(f'<path d="M0 {y:.2f} L{W} {y:.2f}" stroke="#6A4AF0" stroke-width="1.2" opacity="{0.15+k*0.04:.2f}"/>')
    b.append(f'<rect x="0" y="0" width="{W}" height="330" fill="url(#at)" opacity="0"/>')
    cx, cy = 480, 250
    b.append(glow(cx, cy, 90, "#FF5FA8", 0.45, 16))
    for (rot, col) in [(0, "#46E0FF"), (60, "#FF7AC8"), (-60, "#FFD23A")]:
        b.append(f'<ellipse cx="{cx}" cy="{cy}" rx="250" ry="78" fill="none" stroke="{col}" stroke-width="2.4" opacity="0.65" transform="rotate({rot} {cx} {cy})"/>')
    nuc = [(0, 0), (-22, -8), (20, -12), (-8, 20), (14, 18), (-26, 16), (28, 8), (2, -26), (-14, -26), (24, -30), (-34, -6), (8, 34)]
    for i, (dx, dy) in sorted(enumerate(nuc), key=lambda t: t[1][1]):
        c = ("#FF4F7A", "#C0204A", "#FFA8B8") if i % 2 == 0 else ("#4A8CFF", "#2A54C8", "#B8D4FF")
        b.append(ball(cx + dx, cy + dy, 18, *c))
    for (rot, t, col) in [(0, 0.15, "#46E0FF"), (60, 0.62, "#FF7AC8"), (-60, 0.35, "#FFD23A")]:
        a = 2 * math.pi * t
        x0, y0 = 250 * math.cos(a), 78 * math.sin(a)
        r_ = math.radians(rot)
        x, y = cx + x0 * math.cos(r_) - y0 * math.sin(r_), cy + x0 * math.sin(r_) + y0 * math.cos(r_)
        b.append(glow(x, y, 20, col, 0.8, 8) + ball(x, y, 11, "#FFFFFF", col))
        if rot == 0:
            ex_, ey_ = x, y
    b.append(leader(cx + 24, cy - 30, 660, 120) + chip(680, 106, "proton", "#FF4F7A"))
    b.append(leader(cx - 30, cy + 12, 300, 300) + chip(260, 314, "neutron", "#4A8CFF"))
    b.append(leader(round(ex_ + 12), round(ey_ + 6), 820, 360) + chip(840, 374, "electron", "#1EA6C8"))
    return svg("".join(b), ex)



# ------------------------------------------------------------------ 10. June and the phone
def phone_prop():
    ph = R(-34, -62, 68, 116, 12)
    return (sh(ph, "#2A1A5A", "#14103A", "#6A5AB0") +
            inside(R(-28, -54, 56, 100, 7), '<rect x="-40" y="-70" width="80" height="140" fill="#7AD8FF"/><circle cx="20" cy="-40" r="50" fill="#C8F0FF" opacity="0.6"/>'
                   '<rect x="-20" y="-40" width="40" height="22" rx="6" fill="#FFFFFF"/><rect x="-20" y="-10" width="40" height="22" rx="6" fill="#FFFFFF"/><rect x="-20" y="20" width="26" height="16" rx="6" fill="#FFFFFF"/>'))


def bubble(x, y, kind, col):
    bub = U(R(x - 30, y - 24, 60, 48, 16), P(f"M{x-10} {y+20} L{x-22} {y+38} L{x+6} {y+22} Z"))
    o = glow(x, y, 30, col, 0.35, 8) + sh(bub, "#FFFFFF", "#E0D0F0", "#FFFFFF", 0.6)
    if kind == "heart":
        o += sh(P(f"M{x} {y+12} Q{x-22} {y-2} {x-14} {y-12} Q{x-6} {y-18} {x} {y-8} Q{x+6} {y-18} {x+14} {y-12} Q{x+22} {y-2} {x} {y+12} Z"), col, "#C0204A")
    elif kind == "chat":
        o += "".join(ball(x - 14 + k * 14, y, 5, col, "#2A54C8") for k in range(3))
    else:
        o += sh(P(f"M{x-12} {y+8} Q{x-12} {y-14} {x} {y-14} Q{x+12} {y-14} {x+12} {y+8} Z"), col, "#C08A1A") + ball(x, y + 12, 4, col, "#C08A1A")
    return o


def f_june():
    rnd = random.Random(10)
    ex = lin("jn", [(0, "#FF5FA8"), (1, "#FF8A4A")], 1, 1)
    b = [f'<rect width="{W}" height="{H}" fill="url(#jn)"/>']
    for k in range(5):
        b.append(f'<circle cx="480" cy="300" r="{120 + k*80}" fill="none" stroke="#FFFFFF" stroke-width="22" opacity="{0.07 - k*0.01:.2f}"/>')
    b.append(glow(480, 300, 160, "#FFE0F0", 0.5, 30))
    june = SP.person(SP.JUNE, "hold", "happy")
    b.append(g(june + g(phone_prop(), 0, -300, 0.95), 480, 830, 1.25))
    for (x, y, kind, col, sc) in [(250, 150, "heart", "#FF3A6A", 1.2), (720, 120, "chat", "#3A8CFF", 1.1), (760, 300, "bell", "#FFC93A", 1.0), (190, 330, "chat", "#3A8CFF", 0.9), (640, 430, "heart", "#FF3A6A", 0.8)]:
        b.append(g(bubble(0, 0, kind, col), x, y, sc))
    for _ in range(10):
        b.append(sparkle(round(rnd.uniform(60, 900)), round(rnd.uniform(40, 500)), rnd.uniform(4, 8), "#FFFFFF", 0.8))
    b.append(chip(150, 470, "4h 37m a day", "#2A1470", size=18))
    return svg("".join(b), ex)


# ------------------------------------------------------------------ 11. Mira looks up
def f_ava():
    rnd = random.Random(11)
    ex = rad("av", [(0, "#4A2AD0", 1), (1, "#160A50", 1)], 0.3, 0.3, 0.9)
    b = [f'<rect width="{W}" height="{H}" fill="url(#av)"/>', stars(rnd, 140)]
    b.append(glow(250, 170, 160, "#FF5FD0", 0.25, 30) + glow(330, 120, 120, "#46C8FF", 0.2, 30))
    # galaxy swirl
    for k in range(160):
        t = k / 160 * 4 * math.pi + T * 0.5
        r_ = 6 + t * 10
        for arm in (0, math.pi):
            x, y = 250 + r_ * math.cos(t + arm), 170 + r_ * math.sin(t + arm) * 0.5
            b.append(f'<circle cx="{x + rnd.uniform(-6,6):.2f}" cy="{y + rnd.uniform(-4,4):.2f}" r="{rnd.uniform(0.8, 2.2):.1f}" fill="{rnd.choice(["#FFFFFF", "#FFB0F0", "#9AE8FF"])}" opacity="{0.9 - k/220:.2f}"/>')
    b.append(glow(250, 170, 22, "#FFF6E0", 0.9, 8))
    b.append(ball(110, 380, 30, "#FFD23A", "#E08A1A", "#FFF0B0") + inside(C(110, 380, 30), '<rect x="70" y="372" width="80" height="8" fill="#FF8A3A" opacity="0.7"/><rect x="70" y="388" width="80" height="5" fill="#FF8A3A" opacity="0.6"/>'))
    b.append(ball(470, 90, 16, "#46E0D0", "#1EA6A8", "#C8FFF8"))
    b.append(f'<path d="M560 60 L420 150 L424 156 Z" fill="#BFF4FF" opacity="0.5"/>' + ball(420, 152, 5, "#FFFFFF", "#9AE8FF") + glow(420, 152, 10, "#9AE8FF", 0.8, 4))
    # Mira, big, three quarter crop; the cosmos light on her
    b.append(glow(680, 330, 220, "#7A5AFF", 0.4, 30))
    b.append(g(SP.person(SP.MIRA, "stand", "surprised"), 650, 1430, 2.3))
    b.append(popg(text(70, 490, "What's out there?", 28, "#FFFFFF"), 180, 480, 0.7))
    return svg("".join(b), ex)


# ------------------------------------------------------------------ 12. Earth in orbit
def f_earth():
    rnd = random.Random(12)
    ex = rad("ea", [(0, "#1A1060", 1), (1, "#06041E", 1)], 0.5, 0.5, 0.75)
    b = [f'<rect width="{W}" height="{H}" fill="url(#ea)"/>', stars(rnd, 150)]
    cx, cy, r = 480, 290, 150
    b.append(glow(cx, cy, r + 30, "#3AC8FF", 0.45, 16))
    # orbit back half
    orbit = f'<ellipse cx="{cx}" cy="{cy}" rx="300" ry="86" fill="none" stroke="#9AE8FF" stroke-width="1.6" stroke-dasharray="4 7" opacity="0.6" transform="rotate(-12 {cx} {cy})"/>'
    b.append(f'<clipPath id="oback"><rect x="0" y="0" width="{W}" height="{cy}" transform="rotate(-12 {cx} {cy})"/></clipPath><clipPath id="ofront"><rect x="-200" y="{cy}" width="{W+400}" height="{H}" transform="rotate(-12 {cx} {cy})"/></clipPath>')
    debris = []
    for k in range(240):
        a = rnd.uniform(0, 2 * math.pi) + T * 0.35
        rr = rnd.uniform(0.92, 1.12)
        x0, y0 = 300 * rr * math.cos(a), 86 * rr * math.sin(a)
        rt = math.radians(-12)
        x, y = cx + x0 * math.cos(rt) - y0 * math.sin(rt), cy + x0 * math.sin(rt) + y0 * math.cos(rt)
        debris.append((math.sin(a) > 0, f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rnd.uniform(0.8, 2.2):.1f}" fill="{rnd.choice(["#FF7AC8", "#FFD23A", "#9AE8FF", "#FFFFFF"])}" opacity="0.85"/>'))
    b.append(f'<g clip-path="url(#oback)">{orbit}</g>' + "".join(d for f_, d in debris if not f_))
    earth = C(cx, cy, r)
    lands = "".join(f'<circle cx="{cx+dx+T*5:.1f}" cy="{cy+dy}" r="{rr}" fill="#46E08A"/>' for dx, dy, rr in
                    [(-60, -60, 44), (-30, -90, 30), (-90, -20, 30), (-20, -30, 26), (60, 40, 50), (90, 10, 30), (40, 90, 30), (-80, 80, 22), (110, -70, 20), (10, -120, 18)])
    clouds = "".join(f'<rect x="{cx+dx+T*9:.1f}" y="{cy+dy}" width="{w_}" height="12" rx="6" fill="#FFFFFF" opacity="0.85"/>' for dx, dy, w_ in
                     [(-120, -40, 80), (-10, -10, 90), (20, 120, 70), (-90, 60, 60), (40, -100, 70)])
    b.append(earth("#2E8CFF") + inside(earth, lands + f'<g opacity="0.5">{lands.replace("#46E08A", "#1EA864")}</g>'.replace('cx="', 'cx="').replace("<g", "<g transform=\"translate(8 8)\"") + lands + clouds))
    b.append(term(earth, -60, -50, "#0A0A4A", 0.55) + term(earth, -16, -14, "#0A0A4A", 0.25))
    b.append(inside(earth, "".join(f'<circle cx="{rnd.uniform(cx+40, cx+150):.2f}" cy="{rnd.uniform(cy+20, cy+150):.2f}" r="1.6" fill="#FFE27A"/>' for _ in range(40))))
    b.append(f'<g clip-path="url(#ofront)">{orbit}</g>' + "".join(d for f_, d in debris if f_))
    # satellites
    for j, (x, y, rot, s_) in enumerate([(210, 230, -20, 1.0), (770, 330, 14, 0.9), (640, 160, 30, 0.7)]):
        x, y = x + T * (16 if j != 1 else -14), y + T * (-4 if j != 1 else 3)
        sat = (sh(R(-10, -8, 20, 16, 3), "#E8ECFF", "#A8B0E0", "#FFFFFF", 0.4) +
               inside(R(-38, -7, 24, 14, 2), '<rect x="-40" y="-10" width="30" height="20" fill="#3A5AE0"/>' + "".join(f'<rect x="{-37+k*6}" y="-7" width="1.5" height="14" fill="#8AA8FF"/>' for k in range(4))) +
               inside(R(14, -7, 24, 14, 2), '<rect x="10" y="-10" width="30" height="20" fill="#3A5AE0"/>' + "".join(f'<rect x="{15+k*6}" y="-7" width="1.5" height="14" fill="#8AA8FF"/>' for k in range(4))) +
               '<circle cx="0" cy="-12" r="3" fill="#FF4F7A"/>')
        b.append(g(sat, x, y, s_ * 1.3, rot))
    b.append(ball(820, 90, 26, "#E8E4F4", "#A8A0C8", "#FFFFFF") + inside(C(820, 90, 26), '<circle cx="812" cy="84" r="6" fill="#C0B8DC"/><circle cx="830" cy="100" r="4" fill="#C0B8DC"/>'))
    b.append(chip(180, 470, "Low Earth orbit", "#FF4F9A", size=16))
    return svg("".join(b), ex)


# ------------------------------------------------------------------ 13. volcano
def f_volcano():
    rnd = random.Random(13)
    ex = lin("vo", [(0, "#2A0A5A"), (0.55, "#B82A7A"), (1, "#FF7A3A")])
    b = [f'<rect width="{W}" height="{H}" fill="url(#vo)"/>', stars(rnd, 40, 0, 160)]
    b.append(f'<path d="M0 400 L120 330 L230 380 L330 320 L420 390 L{W} 380 L{W} {H} L0 {H} Z" fill="#7A2A7A" opacity="0.7"/>')
    # plume
    b.append(glow(480, 170, 200, "#FF8A3A", 0.45, 30))
    plume = [(480, 190, 60), (430, 150, 58), (530, 140, 62), (470, 100, 64), (400, 90, 48), (560, 80, 52), (500, 50, 56), (420, 40, 40), (590, 30, 40), (360, 120, 40), (610, 130, 44)]
    pl = U(*[C(x, y, r_) for x, y, r_ in plume])
    b.append(pl("#6A3A8A") + inside(pl, U(*[C(x - 12, y - 14, r_) for x, y, r_ in plume])("#8A5AAA")
                                    + f'<ellipse cx="480" cy="230" rx="200" ry="90" fill="#FF7A3A" opacity="0.75"/><ellipse cx="480" cy="250" rx="120" ry="60" fill="#FFC23A" opacity="0.7"/>'))
    b.append(poly([(470, 70), (490, 110), (474, 112), (496, 160), (462, 116), (478, 114)], "#FFF2A0"))
    # cone
    cone = P("M180 470 L420 230 Q480 214 540 230 L790 470 Z")
    b.append(sh(cone, "#5A2A6E", "#3A1650", "#B85A8A", 2))
    b.append(inside(cone, '<path d="M480 230 L540 230 L790 470 L640 470 Z" fill="#2A0E40" opacity="0.4"/>'))
    b.append(glow(480, 228, 60, "#FFC23A", 0.9, 8))
    b.append(sh(E(480, 230, 64, 14), "#FFE27A", "#FF8A3A"))
    lava = P("M450 232 Q440 300 470 340 Q500 380 450 430 Q430 460 470 480 L520 480 Q490 450 510 420 Q540 370 510 330 Q490 290 510 232 Z")
    b.append(glow(480, 360, 60, "#FF6A2A", 0.6, 16))
    b.append(sh(lava, "#FFB03A", "#FF5A1E", "#FFF2A0", 0.8))
    b.append(inside(lava, "".join(f'<ellipse cx="{rnd.uniform(450, 510):.2f}" cy="{rnd.uniform(240, 470):.2f}" rx="8" ry="3" fill="#FFF2A0" opacity="0.8"/>' for _ in range(12))))
    # lava bombs with trails
    for (x, y, tx_, ty_) in [(330, 120, 440, 210), (650, 90, 520, 210), (720, 200, 540, 230), (260, 230, 430, 230)]:
        b.append(f'<path d="M{tx_} {ty_} Q{(x+tx_)/2} {min(y,ty_)-60} {x} {y}" stroke="#FFD27A" stroke-width="2.4" stroke-dasharray="2 7" stroke-linecap="round" fill="none" opacity="0.7"/>')
        b.append(glow(x, y, 12, "#FF8A3A", 0.9, 4) + ball(x, y, 7, "#FFE27A", "#FF5A1E"))
    # foreground ground + pine silhouettes
    b.append(f'<path d="M0 460 Q480 430 {W} 460 L{W} {H} L0 {H} Z" fill="#2A0A3A"/>')
    b.append(f'<path d="M0 460 Q480 430 {W} 460 L{W} 466 Q480 436 0 466 Z" fill="#FF7A3A" opacity="0.6"/>')
    for (x, hgt) in [(40, 150), (90, 110), (130, 170), (820, 160), (870, 120), (920, 180), (760, 100)]:
        b.append(poly([(x, 540 - hgt - 20), (x + 26, 520), (x - 26, 520)], "#1A0628"))
        b.append(poly([(x, 540 - hgt - 20), (x + 26, 520), (x + 6, 520)], "#FF6A3A", 0.25))
    b.append(chip(480, 506, "Pressure finds a way out", "#FFD23A", "#3A0A3A", 16))
    return svg("".join(b), ex)


# ------------------------------------------------------------------ 14. dot crowd
def f_crowd():
    rnd = random.Random(14)
    ex = lin("cr", [(0, "#1E0E5A"), (1, "#3A1A8A")])
    b = [f'<rect width="{W}" height="{H}" fill="url(#cr)"/>']
    cols = ["#FF4F9A", "#FFD23A", "#46E0D0", "#3A8CFF", "#FF8A3A", "#B9A2FF", "#46E08A"]
    hi = (17, 6)
    for i in range(32):
        for j in range(12):
            x, y = 50 + i * 28, 120 + j * 32
            c = rnd.choice(cols)
            if (i, j) == hi:
                continue
            op = 0.55 + 0.45 * rnd.random()
            b.append(f'<g opacity="{op:.2f}"><circle cx="{x}" cy="{y-8}" r="6" fill="{c}"/><rect x="{x-8}" y="{y}" width="16" height="12" rx="6" fill="{c}"/></g>')
    x, y = 50 + hi[0] * 28, 120 + hi[1] * 32
    b.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#0A0420" opacity="0.35"/>')
    b.append(glow(x, y, 40, "#FFFFFF", 0.6, 8))
    b.append(f'<circle cx="{x}" cy="{y-2}" r="26" fill="none" stroke="#FFFFFF" stroke-width="3"/>')
    b.append(ball(x, y - 10, 8, "#FFFFFF", "#D0C8F0") + sh(R(x - 10, y - 1, 20, 15, 7), "#FFFFFF", "#D0C8F0"))
    b.append(leader(x + 20, y - 20, x + 80, y - 80) + chip(x + 100, y - 92, "you", "#FF4F9A", size=16))
    b.append(text(50, 74, "8 billion of us", 34, "#FFFFFF") + text(52, 100, "each dot is about 21 million people", 15, "#C8B8FF", 600, family="Inter"))
    return svg("".join(b), ex)


# ------------------------------------------------------------------ 15. iso room at night
def f_room():
    rnd = random.Random(15)
    ex = lin("rm", [(0, "#2A1A7A"), (1, "#140A40")])
    b = [f'<rect width="{W}" height="{H}" fill="url(#rm)"/>', stars(rnd, 80)]
    Fx, Fy, L, Hh = 480, 500, 300, 230
    def fl(u, v):
        return (Fx + I * u - I * v, Fy - 0.5 * u - 0.5 * v)
    Rr, Lc, Bk = fl(L, 0), fl(0, L), fl(L, L)
    # walls
    b.append(poly([Lc, Bk, (Bk[0], Bk[1] - Hh), (Lc[0], Lc[1] - Hh)], "#7A5AE0"))
    b.append(poly([Bk, Rr, (Rr[0], Rr[1] - Hh), (Bk[0], Bk[1] - Hh)], "#5A3AC0"))
    b.append(poly([Lc, (Lc[0], Lc[1] - Hh), (Lc[0] - 12, Lc[1] - Hh - 6), (Lc[0] - 12, Lc[1] + 6 - 6)], "#4A2AA0"))
    b.append(poly([Rr, (Rr[0], Rr[1] - Hh), (Rr[0] + 12, Rr[1] - Hh - 6), (Rr[0] + 12, Rr[1] - 6)], "#3A1E88"))
    # floor slab
    b.append(iso_box(Fx, Fy, L, L, 14, "#FFC79A", "#C9705A", "#9A4A4A"))
    b.append(inside(P(f"M{Fx} {Fy-14} L{Rr[0]} {Rr[1]-14} L{Bk[0]} {Bk[1]-14} L{Lc[0]} {Lc[1]-14} Z"),
                    "".join(f'<path d="M{fl(k*30,0)[0]:.2f} {fl(k*30,0)[1]-14:.2f} L{fl(k*30,L)[0]:.2f} {fl(k*30,L)[1]-14:.2f}" stroke="#E8A07A" stroke-width="2"/>' for k in range(1, 10))))
    # window on right wall with moon
    wu0, wu1 = 120, 220
    wp = lambda u, h: (Bk[0] + I * (L - u) * 0 + (Rr[0] - Bk[0]) * u / L, Bk[1] + (Rr[1] - Bk[1]) * u / L - h)
    win = [wp(wu0, 80), wp(wu1, 80), wp(wu1, 190), wp(wu0, 190)]
    b.append(poly(win, "#1A1060"))
    b.append(poly([wp(wu0 + 20, 140), wp(wu0 + 50, 140), wp(wu0 + 50, 170), wp(wu0 + 20, 170)], "#FFF2C0"))
    b.append(glow(*wp(wu0 + 35, 155), 24, "#FFF2C0", 0.6, 8))
    b.append(f'<path d="M{win[0][0]:.2f} {win[0][1]:.2f} L{win[1][0]:.2f} {win[1][1]:.2f} L{win[2][0]:.2f} {win[2][1]:.2f} L{win[3][0]:.2f} {win[3][1]:.2f} Z M{(win[0][0]+win[1][0])/2:.2f} {(win[0][1]+win[1][1])/2:.2f} L{(win[2][0]+win[3][0])/2:.2f} {(win[2][1]+win[3][1])/2:.2f}" stroke="#FFC79A" stroke-width="5" fill="none"/>')
    # shelf with books on left wall
    lw = lambda v, h: (Lc[0] + (Bk[0] - Lc[0]) * v / L, Lc[1] + (Bk[1] - Lc[1]) * v / L - h)
    b.append(poly([lw(60, 150), lw(200, 150), lw(200, 142), lw(60, 142)], "#FF8A3A"))
    for k in range(9):
        v = 70 + k * 14
        hgt = 26 + (k * 7) % 12
        b.append(poly([lw(v, 150), lw(v + 10, 150), lw(v + 10, 150 + hgt), lw(v, 150 + hgt)], ["#FF4F9A", "#46E0D0", "#FFD23A", "#3A8CFF", "#46E08A"][k % 5]))
    b.append(poly([lw(220, 70), lw(280, 70), lw(280, 120), lw(220, 120)], "#FFD23A", 0.9))
    # rug
    b.append(poly([fl(90, 80), fl(210, 80), fl(210, 200), fl(90, 200)], "#FF6FB5"))
    b.append(poly([fl(100, 90), fl(200, 90), fl(200, 190), fl(100, 190)], "#FF9AD0"))
    # bed (left, along left wall)
    bed_f = fl(0, 150); bed_f = (bed_f[0], bed_f[1] - 14)
    b.append(iso_box(*bed_f, 100, 140, 34, *PAL["blue"]))
    b.append(iso_box(bed_f[0], bed_f[1] - 34, 100, 90, 12, "#FFF6E6", "#F2DEC4", "#C9AE92"))
    pil = fl(10, 250)
    b.append(iso_box(pil[0], pil[1] - 46 - 14, 60, 30, 14, "#FFFFFF", "#E8E0F0", "#C8C0E0"))
    # cat on the bed
    b.append(g(f'<ellipse cx="0" cy="0" rx="22" ry="12" fill="#FF9A4A"/><circle cx="16" cy="-6" r="10" fill="#FFAA5A"/>'
               f'<path d="M10 -14 L12 -22 L18 -15 Z M18 -15 L24 -22 L25 -12 Z" fill="#FFAA5A"/><path d="M12 -6 q3 2 6 0" stroke="#5A2A1A" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
               + inside(E(0, 0, 22, 12), '<rect x="-14" y="-14" width="5" height="28" fill="#E8742A"/><rect x="-4" y="-14" width="5" height="28" fill="#E8742A"/>'),
               *fl(60, 210)[:1], fl(60, 210)[1] - 60))
    # desk + laptop + lamp (right)
    dk = fl(150, 10); dk = (dk[0], dk[1] - 14)
    for (u, v) in [(264, 64), (150, 64), (264, 12), (152, 12)]:
        p_ = fl(u, v)
        b.append(f'<rect x="{p_[0]-3:.2f}" y="{p_[1]-76:.2f}" width="6" height="62" fill="#5A2A6E"/>')
    b.append(iso_box(dk[0], dk[1] - 60, 120, 60, 9, "#FF8AC8", "#E0559E", "#B83C82"))
    lp = fl(196, 34)
    b.append(glow(lp[0], lp[1] - 100, 50, "#7AD8FF", 0.6, 8))
    b.append(poly([(lp[0], lp[1] - 82), (lp[0] + 30, lp[1] - 97), (lp[0] + 30, lp[1] - 137), (lp[0], lp[1] - 122)], "#7AD8FF"))
    b.append(poly([(lp[0], lp[1] - 82), (lp[0] + 30, lp[1] - 97), (lp[0] + 10, lp[1] - 107), (lp[0] - 20, lp[1] - 92)], "#C8C0E0"))
    lm = fl(250, 60)
    b.append(glow(lm[0], lm[1] - 120, 60, "#FFE27A", 0.55, 16))
    b.append(f'<rect x="{lm[0]-2:.2f}" y="{lm[1]-120:.2f}" width="4" height="40" fill="#2A1A5A"/>' + sh(P(f"M{lm[0]-16:.2f} {lm[1]-112:.2f} L{lm[0]+16:.2f} {lm[1]-112:.2f} L{lm[0]+8:.2f} {lm[1]-136:.2f} L{lm[0]-8:.2f} {lm[1]-136:.2f} Z"), "#FFE27A", "#E0A01A", "#FFF6C0", 0.5))
    # plant
    pp = fl(290, 260)
    b.append(sh(P(f"M{pp[0]-16:.2f} {pp[1]-14:.2f} L{pp[0]+16:.2f} {pp[1]-14:.2f} L{pp[0]+12:.2f} {pp[1]+8:.2f} L{pp[0]-12:.2f} {pp[1]+8:.2f} Z"), "#FF6FB5", "#C9408A"))
    for (dx, dy, rot) in [(-12, -40, -30), (10, -46, 25), (0, -56, 0), (-18, -26, -60), (16, -30, 60)]:
        b.append(g(sh(E(0, 0, 8, 20), "#46E08A", "#1EA864", "#C2FFD8", 0.4), pp[0] + dx, pp[1] + dy, 1, rot))
    b.append(chip(150, 470, "Why do we need sleep?", "#FFD23A", "#2A1470", 16))
    return svg("".join(b), ex)


# ------------------------------------------------------------------ 16. iso bar chart
def f_bars():
    rnd = random.Random(16)
    ex = lin("br", [(0, "#6A2AE0"), (1, "#2A0E8A")])
    b = [f'<rect width="{W}" height="{H}" fill="url(#br)"/>']
    b.append(text(60, 80, "Where the energy goes", 32, "#FFFFFF"))
    Fx, Fy = 400, 500
    b.append(iso_box(Fx, Fy, 520, 200, 18, "#8A62FF", "#5236C0", "#3A1E98"))
    bars = [("Industry", "pink", 250), ("Transport", "yellow", 190), ("Homes", "cyan", 140), ("Other", "mint", 90)]
    for i, (lab, pal, hgt) in enumerate(bars):
        u = 40 + i * 120
        x, y = Fx + I * u - I * 70, Fy - 0.5 * u - 0.5 * 70 - 18
        b.append(iso_box(x, y, 60, 60, hgt, *PAL[pal]))
        b.append(iso_windows(x, y, 60, 60, hgt, rnd, PAL[pal][0], PAL[pal][2], side="r", ww=6, wh=6, gap=6))
        top = (x, y - 30 - hgt)
        b.append(chip(round(top[0]), round(top[1] - 40), lab, "#2A1470", size=13))
    b.append(sparkle(860, 110, 10, "#FFFFFF") + sparkle(120, 300, 7, "#FFD23A"))
    return svg("".join(b), ex)


FRAMES = {k: v for k, v in list(globals().items()) if k.startswith("f_") and callable(v)}

if __name__ == "__main__":
    import sys, render
    names = sys.argv[1:] or list(FRAMES)
    render.render([("v" + n[1:], FRAMES[n]()) for n in names])
