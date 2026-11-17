"""Props and environments for the v5 storyboard: human-scale kitchen, tabletop macro, ruler, mine shaft, city."""
from board_core import *

# ------------------------------------------------------------------ colours
WALL = ("#5B2DB4", "#3A1A86")
WOOD = ("#E8A06A", "#B86A3A", "#FFD0A0")
MUGC = ("#3FC8E0", "#1E86B0", "#B8F4FF")
CER = ("#FFF6EC", "#D8C8E8", "#FFFFFF")
BREAD = ("#F0A848", "#B86A20", "#FFE0A0")

PROP_DEFS = (
    ''.join(f'<filter id="b{k}" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="{k}"/></filter>' for k in (3, 6, 10, 12, 20)) +
    '<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6A36C8"/><stop offset="1" stop-color="#3A1A86"/></linearGradient>'
    '<linearGradient id="win" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF9AC0"/><stop offset="0.6" stop-color="#FFC890"/><stop offset="1" stop-color="#FFE6B8"/></linearGradient>'
    '<linearGradient id="wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F0AE74"/><stop offset="1" stop-color="#C47640"/></linearGradient>'
    '<linearGradient id="woodplane" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C47A48"/><stop offset="0.35" stop-color="#E29C62"/><stop offset="1" stop-color="#F2B47A"/></linearGradient>'
    '<linearGradient id="mugg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1E86B0"/><stop offset="0.35" stop-color="#5AD8F0"/><stop offset="0.6" stop-color="#3FC8E0"/><stop offset="1" stop-color="#16648A"/></linearGradient>'
    '<linearGradient id="cnt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8A5AE0"/><stop offset="1" stop-color="#5A2EB0"/></linearGradient>'
    '<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE6B8" stop-opacity="0.35"/><stop offset="1" stop-color="#FFE6B8" stop-opacity="0"/></linearGradient>'
    '<linearGradient id="paper" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF4DE"/><stop offset="1" stop-color="#F0DDB8"/></linearGradient>'
    '<linearGradient id="rock" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6A3A9A"/><stop offset="1" stop-color="#2A1450"/></linearGradient>'
    '<linearGradient id="city" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF8AB8"/><stop offset="0.5" stop-color="#9A4AD0"/><stop offset="1" stop-color="#2A1270"/></linearGradient>'
    '<linearGradient id="floorg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A2290"/><stop offset="1" stop-color="#5A3AB8"/></linearGradient>'
    '<radialGradient id="sunwin" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.5" stop-color="#FFF2C8"/><stop offset="1" stop-color="#FFE0A0" stop-opacity="0"/></radialGradient>'
)


def soft_shadow(cx, cy, rx, ry=None, op=0.35):
    ry = ry or rx * 0.22
    return f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="#160838" opacity="{op}" filter="url(#b6)"/>'


def mug(cx, base, s=1.0, steam=True, t=0.0):
    w, h = 120 * s, 132 * s
    x0 = cx - w / 2
    body = f'M{x0:.1f} {base - h:.1f} L{x0 + w:.1f} {base - h:.1f} L{x0 + w - 6*s:.1f} {base - 10*s:.1f} Q{cx:.1f} {base + 6*s:.1f} {x0 + 6*s:.1f} {base - 10*s:.1f} Z'
    o = [soft_shadow(cx + 10 * s, base, w * 0.62, 10 * s)]
    o.append(f'<path d="M{x0 + w - 4*s:.1f} {base - h + 26*s:.1f} q{46*s:.1f} {-6*s:.1f} {44*s:.1f} {38*s:.1f} q{-2*s:.1f} {40*s:.1f} {-48*s:.1f} {40*s:.1f}" stroke="#1E86B0" stroke-width="{16*s:.1f}" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="{body}" fill="url(#mugg)"/>')
    o.append(f'<ellipse cx="{cx:.1f}" cy="{base - h:.1f}" rx="{w/2:.1f}" ry="{12*s:.1f}" fill="#16648A"/>')
    o.append(f'<ellipse cx="{cx:.1f}" cy="{base - h + 3*s:.1f}" rx="{w/2 - 8*s:.1f}" ry="{8*s:.1f}" fill="#6A3A1A"/>')
    o.append(f'<rect x="{x0 + 18*s:.1f}" y="{base - h + 20*s:.1f}" width="{10*s:.1f}" height="{h - 44*s:.1f}" rx="{5*s:.1f}" fill="#FFFFFF" opacity="0.45"/>')
    if steam:
        for k in range(3):
            sx = cx - 26 * s + k * 26 * s
            o.append(f'<path d="M{sx:.1f} {base - h - 14*s:.1f} q{-14*s:.1f} {-22*s:.1f} 0 {-44*s:.1f} q{14*s:.1f} {-22*s:.1f} 0 {-44*s:.1f}" stroke="#FFFFFF" stroke-width="{6*s:.1f}" fill="none" stroke-linecap="round" opacity="0.35" filter="url(#b2)"/>')
    return "".join(o)


def plate(cx, y, s=1.0, toast_=True):
    o = [soft_shadow(cx, y + 6 * s, 150 * s, 18 * s)]
    o.append(f'<ellipse cx="{cx}" cy="{y}" rx="{150*s:.1f}" ry="{26*s:.1f}" fill="#D8C8E8"/>')
    o.append(f'<ellipse cx="{cx}" cy="{y - 4*s:.1f}" rx="{146*s:.1f}" ry="{22*s:.1f}" fill="#FFF6EC"/>')
    o.append(f'<ellipse cx="{cx}" cy="{y - 2*s:.1f}" rx="{100*s:.1f}" ry="{13*s:.1f}" fill="#EDE0F4"/>')
    o.append(f'<ellipse cx="{cx}" cy="{y - 4*s:.1f}" rx="{140*s:.1f}" ry="{20*s:.1f}" fill="none" stroke="#7A8AE0" stroke-width="{3*s:.1f}" opacity="0.6"/>')
    if toast_:
        o.append(toast(cx + 6 * s, y - 8 * s, s * 0.9))
    return "".join(o)


def toast(cx, base, s=1.0, rot=0):
    d = f'M{-60*s:.1f} 0 L{-62*s:.1f} {-70*s:.1f} Q{-74*s:.1f} {-110*s:.1f} {-36*s:.1f} {-116*s:.1f} Q0 {-130*s:.1f} {36*s:.1f} {-116*s:.1f} Q{74*s:.1f} {-110*s:.1f} {62*s:.1f} {-70*s:.1f} L{60*s:.1f} 0 Z'
    inner = f'M{-48*s:.1f} {-8*s:.1f} L{-50*s:.1f} {-70*s:.1f} Q{-58*s:.1f} {-100*s:.1f} {-30*s:.1f} {-104*s:.1f} Q0 {-114*s:.1f} {30*s:.1f} {-104*s:.1f} Q{58*s:.1f} {-100*s:.1f} {50*s:.1f} {-70*s:.1f} L{48*s:.1f} {-8*s:.1f} Z'
    return (f'<g transform="translate({cx:.1f} {base:.1f}) rotate({rot})"><path d="{d}" fill="#B8641E"/><path d="{inner}" fill="#F6C46A"/>'
            f'<ellipse cx="{-14*s:.1f}" cy="{-70*s:.1f}" rx="{22*s:.1f}" ry="{16*s:.1f}" fill="#FFE6A8" opacity="0.7"/></g>')


def toaster(cx, base, s=1.0, pop=0.0):
    w, h = 200 * s, 130 * s
    o = [soft_shadow(cx, base, w * 0.6, 10 * s)]
    for k in (-1, 1):
        o.append(toast(cx + k * 44 * s, base - h + 26 * s - pop * 90 * s, s * 0.62, rot=k * 6 * pop))
    o.append(f'<rect x="{cx - w/2:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{40*s:.1f}" fill="#E8E0F8"/>')
    o.append(f'<rect x="{cx - w/2:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{40*s:.1f}" fill="none" stroke="#B8A8E0" stroke-width="{6*s:.1f}"/>')
    o.append(f'<rect x="{cx - w/2 + 20*s:.1f}" y="{base - h + 16*s:.1f}" width="{30*s:.1f}" height="{h - 40*s:.1f}" rx="{15*s:.1f}" fill="#FFFFFF" opacity="0.7"/>')
    o.append(f'<rect x="{cx + w/2 - 8*s:.1f}" y="{base - h/2 - 10*s + pop*-30*s:.1f}" width="{26*s:.1f}" height="{16*s:.1f}" rx="{6*s:.1f}" fill="#FF6F91"/>')
    for k in (-1, 1):
        o.append(f'<rect x="{cx + k*44*s - 50*s:.1f}" y="{base - h - 4*s:.1f}" width="{100*s:.1f}" height="{12*s:.1f}" rx="{6*s:.1f}" fill="#4A2A8A"/>')
    return "".join(o)


def kettle(cx, base, s=1.0):
    return (soft_shadow(cx, base, 80 * s, 10 * s) +
            f'<path d="M{cx - 70*s:.1f} {base:.1f} Q{cx - 90*s:.1f} {base - 110*s:.1f} {cx:.1f} {base - 130*s:.1f} Q{cx + 90*s:.1f} {base - 110*s:.1f} {cx + 70*s:.1f} {base:.1f} Z" fill="#FF8A6A"/>'
            f'<path d="M{cx + 60*s:.1f} {base - 70*s:.1f} L{cx + 120*s:.1f} {base - 110*s:.1f}" stroke="#FF8A6A" stroke-width="{18*s:.1f}" stroke-linecap="round"/>'
            f'<path d="M{cx - 40*s:.1f} {base - 128*s:.1f} Q{cx:.1f} {base - 190*s:.1f} {cx + 40*s:.1f} {base - 128*s:.1f}" stroke="#4A2A8A" stroke-width="{12*s:.1f}" fill="none"/>'
            f'<ellipse cx="{cx - 30*s:.1f}" cy="{base - 80*s:.1f}" rx="{14*s:.1f}" ry="{36*s:.1f}" fill="#FFFFFF" opacity="0.35"/>')


def plant(cx, base, s=1.0):
    o = [soft_shadow(cx, base, 60 * s, 8 * s)]
    for k, a in enumerate((-60, -30, -5, 20, 50)):
        r = math.radians(a - 90)
        L = (120 + (k % 2) * 30) * s
        ex, ey = cx + L * math.cos(r), base - 70 * s + L * math.sin(r)
        o.append(f'<path d="M{cx:.1f} {base - 70*s:.1f} Q{(cx + ex)/2 + 20*s:.1f} {(base - 70*s + ey)/2:.1f} {ex:.1f} {ey:.1f} Q{(cx + ex)/2 - 20*s:.1f} {(base - 70*s + ey)/2:.1f} {cx:.1f} {base - 70*s:.1f}" fill="{["#2EC880", "#46E08A", "#1EA864"][k % 3]}"/>')
    o.append(f'<path d="M{cx - 50*s:.1f} {base - 80*s:.1f} L{cx + 50*s:.1f} {base - 80*s:.1f} L{cx + 38*s:.1f} {base:.1f} L{cx - 38*s:.1f} {base:.1f} Z" fill="#FF6FA8"/>')
    return "".join(o)


def kitchen_room(t=0.0, table=True, table_top=420, sun=True):
    """Human-scale kitchen, side-on. Back wall, window with morning sun, cabinets, counter with toaster/kettle/plant."""
    o = ['<rect x="-600" y="-600" width="2160" height="1740" fill="url(#wall)"/>']
    # window
    o.append('<rect x="596" y="40" width="300" height="250" rx="16" fill="#FFE8C8"/>')
    o.append('<rect x="612" y="56" width="268" height="218" rx="8" fill="url(#win)"/>')
    if sun:
        o.append('<circle cx="760" cy="150" r="70" fill="url(#sunwin)"/>')
    o.append('<path d="M612 230 Q680 200 740 226 Q800 200 880 222 L880 274 L612 274 Z" fill="#B85AD0" opacity="0.5"/>')
    o.append('<rect x="742" y="56" width="10" height="218" fill="#FFE8C8"/><rect x="612" y="160" width="268" height="8" fill="#FFE8C8"/>')
    o.append('<path d="M612 56 L880 56 L1060 560 L560 560 Z" fill="url(#beam)" opacity="0.6"/>')
    # cabinets
    for k in range(4):
        x = 40 + k * 128
        o.append(f'<rect x="{x}" y="30" width="118" height="130" rx="12" fill="#8A62E8"/><rect x="{x + 8}" y="38" width="102" height="114" rx="8" fill="#7A52D8"/>'
                 f'<rect x="{x + (90 if k % 2 else 18)}" y="120" width="10" height="26" rx="5" fill="#FFD6A8"/>')
    # backsplash tiles
    for i in range(12):
        for j in range(3):
            o.append(f'<rect x="{-20 + i*52}" y="{196 + j*40}" width="48" height="36" rx="6" fill="#7A4ADA" opacity="0.55"/>')
    # counter
    o.append('<rect x="-100" y="318" width="680" height="26" rx="8" fill="#FFE2C0"/><rect x="-100" y="340" width="680" height="240" fill="url(#cnt)"/>')
    for k in range(5):
        o.append(f'<rect x="{-80 + k*128}" y="356" width="116" height="170" rx="10" fill="#6A3AC0"/><rect x="{-80 + k*128 + 50}" y="372" width="16" height="8" rx="4" fill="#FFD6A8"/>')
    o.append(toaster(140, 318, 0.55, pop=0.0) + kettle(300, 318, 0.55) + plant(470, 318, 0.6))
    o.append('<rect x="580" y="300" width="400" height="300" fill="#2A1470" opacity="0.0"/>')
    return "".join(o)


def dining_table(x0, x1, top, s=1.0, legs=True):
    o = []
    th = 26 * s
    if legs:
        for x in (x0 + 40 * s, x1 - 70 * s):
            o.append(f'<rect x="{x:.0f}" y="{top:.0f}" width="{30*s:.0f}" height="{600:.0f}" rx="{8*s:.0f}" fill="#A85E30"/>')
    o.append(f'<rect x="{x0:.0f}" y="{top:.0f}" width="{x1 - x0:.0f}" height="{th:.0f}" rx="{10*s:.0f}" fill="url(#wood)"/>')
    o.append(f'<rect x="{x0:.0f}" y="{top:.0f}" width="{x1 - x0:.0f}" height="{4*s:.0f}" rx="2" fill="#FFD6A8"/>')
    o.append(f'<rect x="{x0:.0f}" y="{top + th - 6*s:.0f}" width="{x1 - x0:.0f}" height="{6*s:.0f}" fill="#8A4A22" opacity="0.5"/>')
    return "".join(o)


def far_kitchen_blur(b=10):
    return f'<g filter="url(#b{b})">{kitchen_room(sun=True)}</g>'


def wood_plane(hz=250, vpx=480, n=22, col="url(#woodplane)", x0=-600, x1=1560):
    """Tabletop seen from ant height: a plane from the horizon down, grain lines converging."""
    o = [f'<rect x="{x0}" y="{hz}" width="{x1 - x0}" height="900" fill="{col}"/>']
    for k in range(n):
        u = (k + 0.5) / n
        bx = -900 + u * 2760
        o.append(f'<path d="M{vpx + (bx - vpx) * 0.02:.0f} {hz} L{bx:.0f} 760" stroke="#B8703E" stroke-width="{1.2 + 2.4*abs(u - 0.5):.1f}" opacity="0.35" fill="none"/>')
    for k in range(7):
        y = hz + (k + 1) ** 2 * 6
        o.append(f'<path d="M-600 {y} Q480 {y + 3} 1560 {y - 2}" stroke="#FFD0A0" stroke-width="1.4" opacity="0.18" fill="none"/>')
    o.append(f'<rect x="{x0}" y="{hz - 3}" width="{x1 - x0}" height="6" fill="#FFE2C0" opacity="0.6"/>')
    return "".join(o)


def giant_mug_base(cx, base, w=820, h=900):
    x0 = cx - w / 2
    return (f'<ellipse cx="{cx}" cy="{base + 6}" rx="{w*0.55:.0f}" ry="30" fill="#160838" opacity="0.4" filter="url(#b10)"/>'
            f'<path d="M{x0:.0f} {base - h} L{x0 + w:.0f} {base - h} L{x0 + w - 10:.0f} {base - 20} Q{cx} {base + 30} {x0 + 10:.0f} {base - 20} Z" fill="url(#mugg)"/>'
            f'<rect x="{x0 + 70:.0f}" y="{base - h}" width="40" height="{h - 60}" rx="20" fill="#FFFFFF" opacity="0.35"/>'
            f'<path d="M{x0 + 10:.0f} {base - 22} Q{cx} {base + 28} {x0 + w - 10:.0f} {base - 22}" stroke="#16648A" stroke-width="10" fill="none" opacity="0.6"/>')


def plate_rim(x0, x1, y, h=34):
    return (f'<path d="M{x0} {y} Q{(x0 + x1)/2} {y - 30} {x1} {y - 6} L{x1} {y - 6 - h} Q{(x0 + x1)/2} {y - 30 - h - 10} {x0} {y - h} Z" fill="#FFF6EC"/>'
            f'<path d="M{x0} {y - h} Q{(x0 + x1)/2} {y - 40 - h} {x1} {y - 6 - h}" stroke="#7A8AE0" stroke-width="5" fill="none" opacity="0.6"/>'
            f'<path d="M{x0} {y} Q{(x0 + x1)/2} {y - 30} {x1} {y - 6}" stroke="#D8C8E8" stroke-width="8" fill="none"/>'
            + soft_shadow((x0 + x1) / 2, y - 4, (x1 - x0) * 0.5, 10, 0.3))


def boulder(cx, base, s, seed=1, col=BREAD):
    return soft_shadow(cx, base, 40 * s, 8 * s, 0.4) + crumb(cx, base - 24 * s, 34 * s, seed)


def tabletop_macro(hz=250, mug_x=860, plate=True, crumbs=True, far=True, seed=3):
    o = []
    if far:
        o.append(f'<g transform="translate(480 {hz}) scale(1.6) translate(-480 -330)" filter="url(#b10)">{kitchen_room()}</g>')
    o.append(wood_plane(hz))
    if plate:
        o.append(plate_rim(-260, 340, hz + 60, 44))
    if mug_x is not None:
        o.append(giant_mug_base(mug_x, hz + 120, 760, 900))
    if crumbs:
        rr = random.Random(seed)
        for (x, y, s) in [(120, hz + 140, 0.8), (700, hz + 230, 1.3), (40, hz + 250, 1.6), (380, hz + 100, 0.5), (900, hz + 280, 1.9)]:
            o.append(boulder(x, y, s, rr.randint(1, 9)))
    return "".join(o)


def table_edge_side(edge_x=700, top=360, floor_y=None):
    """Tabletop from the side, ending at edge_x; beyond it a deep drop to the blurred floor."""
    o = [f'<g filter="url(#b8)"><rect x="-600" y="-600" width="2160" height="1740" fill="url(#floorg)"/>'
         + "".join(f'<rect x="{edge_x + 40 + i*120}" y="{top + 120 + j*90}" width="110" height="80" rx="10" fill="#6444C4" opacity="0.6"/>' for i in range(6) for j in range(5))
         + '</g>']
    o.append(f'<rect x="-600" y="{top}" width="{edge_x + 600}" height="40" fill="url(#wood)"/>')
    o.append(f'<path d="M-600 {top} L{edge_x} {top}" stroke="#FFD6A8" stroke-width="4"/>')
    o.append(f'<rect x="-600" y="{top + 40}" width="{edge_x + 600}" height="600" fill="#8A4A22"/>')
    o.append(f'<rect x="{edge_x - 30}" y="{top}" width="30" height="640" fill="#6A3418" opacity="0.6"/>')
    return "".join(o)
