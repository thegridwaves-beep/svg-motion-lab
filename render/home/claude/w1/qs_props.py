"""Quicksand Short props: tidal flats (sky, sea, sand plane), the sinking boy (sand drawn over his legs),
a cut-away of the sand, the incoming tide, the car-lift comparison card, the movie-myth frame."""
import math, random
from wcore import *

L_BEACH = Light("qsDay", amb=(1.0, 0.97, 0.92), sat=1.0, key="#FFE6B0", key_op=0.35, ang=-50, spread=0.8, shade="#3A2A3A", shade_op=0.3, rim="#FFF4D8", rim_op=0.5, rim_w=7)
L_DUSK = Light("qsDusk", amb=(0.95, 0.86, 0.86), sat=0.95, key="#FFB27A", key_op=0.4, ang=-30, spread=0.8, shade="#2A1A3A", shade_op=0.38, rim="#FFD0A0", rim_op=0.55, rim_w=7)
TAU = 2 * math.pi
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


HZ = 228                     # horizon (sea line)
QS_DEFS = (lin("qsSky", [(0, "#7CC0EC"), (0.75, "#D8F0FA"), (1, "#F4F2E0")]) + lin("qsSkyD", [(0, "#5A6AB0"), (0.7, "#F0A27A"), (1, "#FFD8A0")])
           + lin("qsSand", [(0, "#D6C09A"), (0.25, "#CDB284"), (1, "#E2C894")]) + lin("qsSea", [(0, "#4A9AC0"), (1, "#8AD0D8")])
           + rad("qsPool", [(0, "#7E5E34", 1), (0.7, "#93734A", 0.95), (1, "#B89668", 0)]) + lin("qsCut", [(0, "#B8955E"), (1, "#7A5A34")])
           + lin("qsFilm", [(0, "#D8B888"), (1, "#8A6A48")]) + lin("stageQ", [(0, "#2A2050"), (1, "#100A22")]))


def beach_sky(dusk=0.0):
    o = (f'<rect x="-800" y="-1200" width="2560" height="1500" fill="url(#qsSky)"/>'
         + (f'<rect x="-800" y="-1200" width="2560" height="1500" fill="url(#qsSkyD)" opacity="{dusk:.2f}"/>' if dusk > 0 else "")
         + glow(640, 40, 220, "#FFF6D0", 0.55, 30))
    r = random.Random(5)
    for k in range(7):
        x, y, w = r.uniform(-500, 1500), r.uniform(-120, 150), r.uniform(80, 200)
        o += (f'<g opacity="{0.75 - 0.2 * dusk:.2f}"><ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{w:.0f}" ry="{w * 0.18:.0f}" fill="#FFFFFF"/>'
              f'<ellipse cx="{x + w * 0.25:.0f}" cy="{y - w * 0.1:.0f}" rx="{w * 0.45:.0f}" ry="{w * 0.2:.0f}" fill="#FFFFFF"/></g>')
    return o


def headland(x=-120, y=HZ, col="#7A9A9A"):
    return (f'<path d="M{x - 600} {y} L{x - 600} {y - 50} Q{x - 300} {y - 120} {x - 120} {y - 90} Q{x} {y - 70} {x + 90} {y - 30} Q{x + 160} {y - 8} {x + 240} {y} Z" fill="{col}"/>'
            f'<path d="M{x - 300} {y - 112} Q{x - 200} {y - 130} {x - 120} {y - 90}" stroke="#9AB8B4" stroke-width="5" fill="none" opacity="0.6"/>')


def sea(t, y=HZ, depth=26):
    o = f'<rect x="-800" y="{y - 4}" width="2560" height="{depth + 4}" fill="url(#qsSea)"/>'
    for k in range(22):
        x = -700 + 120 * k + 30 * math.sin(t * 0.8 + k)
        o += f'<path d="M{x:.0f} {y + 6 + 7 * (k % 3)} q14 -3 28 0" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="{0.35 + 0.3 * math.sin(t * 2 + k):.2f}"/>'
    return o + f'<rect x="-800" y="{y + depth - 3}" width="2560" height="6" fill="#F4F8F0" opacity="0.7"/>'


def sand_plane(seed=7, y0=HZ + 24):
    """Wet tidal flats in perspective: ripple marks get bigger and further apart toward the viewer, sheen and puddles."""
    r = random.Random(seed)
    o = [f'<rect x="-800" y="{y0}" width="2560" height="1600" fill="url(#qsSand)"/>']
    y, gap = y0 + 4, 4.0
    while y < 1200:
        sc = (y - y0) / 300 + 0.2
        for _ in range(int(14 / max(0.4, sc)) + 4):
            x = r.uniform(-800, 1760); w = r.uniform(30, 90) * sc
            o.append(f'<path d="M{x:.0f} {y:.1f} q{w / 2:.1f} {-3 * sc:.1f} {w:.1f} 0" stroke="#B89A6A" stroke-width="{max(1.0, 2.2 * sc):.1f}" fill="none" opacity="0.55" stroke-linecap="round"/>')
        gap *= 1.16; y += gap
    for _ in range(14):
        x, yy = r.uniform(-700, 1700), r.uniform(y0 + 20, 900); sc = (yy - y0) / 300 + 0.2
        o.append(f'<ellipse cx="{x:.0f}" cy="{yy:.0f}" rx="{r.uniform(40, 120) * sc:.0f}" ry="{r.uniform(5, 12) * sc:.0f}" fill="#BFE0EC" opacity="0.45"/>')
    for _ in range(18):
        x, yy = r.uniform(-700, 1700), r.uniform(y0 + 30, 900); sc = (yy - y0) / 300 + 0.2
        o.append(f'<ellipse cx="{x:.0f}" cy="{yy:.0f}" rx="{5 * sc:.1f}" ry="{3 * sc:.1f}" fill="#F4E8D8"/><ellipse cx="{x - 1:.0f}" cy="{yy - 1:.0f}" rx="{2 * sc:.1f}" ry="{1.2 * sc:.1f}" fill="#FFFFFF" opacity="0.7"/>')
    return "".join(o)


SAND = sand_plane()


def quick_pool(x, y, s=1.0, op=1.0):
    """The patch of quicksand: smoother, darker and glossier than the flats around it."""
    return (f'<g opacity="{op:.2f}"><ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{230 * s:.0f}" ry="{52 * s:.0f}" fill="url(#qsPool)"/>'
            f'<ellipse cx="{x - 40 * s:.0f}" cy="{y - 10 * s:.0f}" rx="{90 * s:.0f}" ry="{9 * s:.0f}" fill="#E8F4F4" opacity="0.35"/>'
            f'<ellipse cx="{x + 70 * s:.0f}" cy="{y + 14 * s:.0f}" rx="{50 * s:.0f}" ry="{5 * s:.0f}" fill="#E8F4F4" opacity="0.25"/></g>')


def beach_back(t, dusk=0.0, pool=None):
    o = beach_sky(dusk) + headland() + sea(t) + SAND
    if pool:
        o += quick_pool(*pool)
    return o


def sand_front(uid, G, x, s, sink, t=0.0, churn=0.0, pool=True):
    """Sand drawn OVER the boy below his entry line G (so whatever has sunk is hidden), with the wet ring where he went in."""
    cid = f"sf_{uid}"
    o = (f'<clipPath id="{cid}"><rect x="-900" y="{G:.1f}" width="2800" height="1600"/></clipPath>'
         f'<g clip-path="url(#{cid})">{SAND}{quick_pool(x, G + 30 * s, s * 1.2) if pool else ""}</g>')
    if sink > 1:
        rw = (58 + 10 * churn * math.sin(t * 9)) * s
        o += (f'<ellipse cx="{x:.1f}" cy="{G:.1f}" rx="{rw + 26 * s:.1f}" ry="{11 * s:.1f}" fill="#8A6A40" opacity="0.55"/>'
              f'<ellipse cx="{x:.1f}" cy="{G - 1:.1f}" rx="{rw:.1f}" ry="{7 * s:.1f}" fill="#6E5232" opacity="0.8"/>'
              f'<path d="M{x - rw:.1f} {G - 2:.1f} Q{x:.1f} {G - 12 * s:.1f} {x + rw:.1f} {G - 2:.1f}" stroke="#E8DCC0" stroke-width="{2.5 * s:.1f}" fill="none" opacity="0.6"/>')
        for k in range(3):                                   # ripples spreading out of the churned sand
            u = (t * 0.7 + k / 3) % 1 if churn > 0 else 0.3 + 0.2 * k
            o += f'<ellipse cx="{x:.1f}" cy="{G + 2:.1f}" rx="{(rw + 20 * s + 90 * s * u):.1f}" ry="{(8 + 16 * u) * s:.1f}" fill="none" stroke="#F0E4C8" stroke-width="{2 * s:.1f}" opacity="{(0.55 * (1 - u)) * (0.4 + 0.6 * churn):.2f}"/>'
    return o


def sand_cut(x0, x1, G, depth, t=0.0, seep=0.0, loose=0.0, seed=3):
    """Cross-section box cut into the ground in front of the boy: packed grains with water between them.
    seep 0..1 = water trickling down around the legs, loose 0..1 = grains pushed apart."""
    r = random.Random(seed)
    o = [f'<rect x="{x0:.0f}" y="{G:.0f}" width="{x1 - x0:.0f}" height="{depth:.0f}" fill="url(#qsCut)" opacity="0.62"/>']
    for _ in range(int((x1 - x0) * depth / 260)):
        gx, gy = r.uniform(x0 + 4, x1 - 4), r.uniform(G + 6, G + depth - 4)
        cx = (x0 + x1) / 2; push = loose * 10 * math.copysign(1, gx - cx) * math.exp(-abs(gx - cx) / 90)
        o.append(f'<circle cx="{gx + push:.1f}" cy="{gy:.1f}" r="{r.uniform(2.2, 4.2):.1f}" fill="{r.choice(["#E8CC98", "#C8A46C", "#F2DCB0", "#A88452"])}" opacity="0.9"/>')
    for k in range(int(26 * (0.3 + seep))):
        gx = r.uniform(x0 + 10, x1 - 10); gy = G + ((r.uniform(0, depth) + t * 60 * seep) % depth)
        o.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="2.4" fill="#7ED4F0" opacity="{0.5 + 0.4 * seep:.2f}"/>')
    o.append(f'<rect x="{x0:.0f}" y="{G:.0f}" width="{x1 - x0:.0f}" height="{depth:.0f}" fill="none" stroke="#FFF4DA" stroke-width="4" stroke-dasharray="14 9" opacity="0.8"/>')
    return "".join(o)


def tide_sheet(t, edge_y, op=0.85):
    """A thin sheet of incoming sea sliding over the flats, foam on its leading edge."""
    wave = " ".join(f"L{x} {edge_y + 6 * math.sin(x * 0.02 + t * 2.4) + 4 * math.sin(x * 0.07 - t * 3):.1f}" for x in range(-800, 1800, 30))
    return (f'<path d="M-800 {HZ} L-800 {edge_y} {wave} L1760 {HZ} Z" fill="#5AAAC8" opacity="{op:.2f}"/>'
            f'<path d="M-800 {edge_y} {wave}" stroke="#F4FBFA" stroke-width="7" fill="none" opacity="0.9" stroke-linecap="round"/>'
            f'<path d="M-800 {edge_y - 10} ' + wave.replace(f"{edge_y}", f"{edge_y - 10}") + '" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.4"/>')


def car(x, y, s=1.0, col="#E8504A"):
    """Simple side-view hatchback, wheels at y."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            f'<path d="M-110 -18 L-110 -46 Q-108 -58 -92 -60 L-58 -62 L-30 -94 Q-24 -100 -12 -100 L52 -100 Q66 -100 74 -90 L98 -62 Q118 -58 120 -42 L120 -18 Z" fill="{col}"/>'
            '<path d="M-48 -64 L-24 -90 L14 -90 L14 -64 Z M22 -64 L22 -90 L58 -90 Q64 -90 68 -84 L84 -64 Z" fill="#CFEFFF"/>'
            '<path d="M-110 -40 L120 -40" stroke="#000000" stroke-width="3" opacity="0.15"/>'
            '<circle cx="-62" cy="-16" r="22" fill="#2A2A3A"/><circle cx="-62" cy="-16" r="10" fill="#B8C0CC"/>'
            '<circle cx="74" cy="-16" r="22" fill="#2A2A3A"/><circle cx="74" cy="-16" r="10" fill="#B8C0CC"/>'
            '<rect x="108" y="-56" width="12" height="9" rx="3" fill="#FFE8A0"/></g>')


def arrow_up(x, y, h, w=44, col="#FFE45A", u=1.0):
    if u <= 0:
        return ""
    h *= eo(min(1, u))
    return (f'<path d="M{x - w * 0.32:.1f} {y:.1f} L{x - w * 0.32:.1f} {y - h + w * 0.7:.1f} L{x - w * 0.7:.1f} {y - h + w * 0.7:.1f} L{x:.1f} {y - h:.1f} L{x + w * 0.7:.1f} {y - h + w * 0.7:.1f} L{x + w * 0.32:.1f} {y - h + w * 0.7:.1f} L{x + w * 0.32:.1f} {y:.1f} Z" '
            f'fill="{col}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')


def friend_arms(hx, hy, s, pull=0.0, t=0.0):
    """Two helpers' arms reaching in from the left edge, hands closed round the boy's wrists at (hx, hy)."""
    o = ""
    for k, dy in enumerate((-10, 12)):
        bx = hx - 300 * s - 40 * pull; by = hy + dy * s + 40 * s * (k - 0.5)
        tx, ty = hx + 2 * s, hy + dy * 0.4 * s
        o += (f'<path d="M{bx:.1f} {by:.1f} Q{(bx + tx) / 2:.1f} {by - 14 * s:.1f} {tx - 20 * s:.1f} {ty:.1f}" stroke="#E07A3A" stroke-width="{34 * s:.1f}" fill="none" stroke-linecap="round"/>'
              f'<path d="M{bx:.1f} {by - 8 * s:.1f} Q{(bx + tx) / 2:.1f} {by - 22 * s:.1f} {tx - 24 * s:.1f} {ty - 8 * s:.1f}" stroke="#F4A060" stroke-width="{6 * s:.1f}" fill="none" opacity="0.5"/>'
              + fist(tx, ty, 0.5 * s, 0, sleeve=10).replace(TP[0], "#E07A3A").replace(TP[1], "#B85A28"))
    return o


def film_frame(cx, cy, w, h, inner, t=0.0):
    """An old movie frame: sepia picture between film-strip edges, flicker and scratches."""
    fl = 0.9 + 0.1 * math.sin(t * 37) * math.sin(t * 11)
    o = (f'<rect x="{cx - w / 2 - 46:.0f}" y="{cy - h / 2 - 20:.0f}" width="{w + 92:.0f}" height="{h + 40:.0f}" rx="10" fill="#1A1420"/>'
         f'<clipPath id="filmc"><rect x="{cx - w / 2:.0f}" y="{cy - h / 2:.0f}" width="{w:.0f}" height="{h:.0f}" rx="6"/></clipPath>'
         f'<g clip-path="url(#filmc)" opacity="{fl:.2f}">{inner}<rect x="{cx - w / 2:.0f}" y="{cy - h / 2:.0f}" width="{w:.0f}" height="{h:.0f}" fill="#B8864A" opacity="0.35"/></g>')
    for side in (-1, 1):
        for k in range(9):
            o += f'<rect x="{cx + side * (w / 2 + 23) - 9:.0f}" y="{cy - h / 2 - 8 + k * (h + 16) / 8.5 - (t * 90) % ((h + 16) / 8.5):.0f}" width="18" height="16" rx="4" fill="#F4ECDC" opacity="0.85"/>'
    r = random.Random(int(t * 12))
    for _ in range(3):
        x = r.uniform(cx - w / 2, cx + w / 2)
        o += f'<path d="M{x:.0f} {cy - h / 2:.0f} l{r.uniform(-6, 6):.0f} {h:.0f}" stroke="#FFF8E8" stroke-width="1.5" opacity="0.35"/>'
    return o


def stamp(x, y, txt, u, col="#FF3A4A", ang=-14, size=64):
    if u <= 0:
        return ""
    k = 1.6 - 0.6 * eo(min(1, u * 2.2))
    w = len(txt) * size * 0.66 + 40
    return (f'<g transform="translate({x} {y}) rotate({ang}) scale({k:.3f})" opacity="{clamp(u * 3):.2f}">'
            f'<rect x="{-w / 2:.0f}" y="{-size * 0.72:.0f}" width="{w:.0f}" height="{size * 1.3:.0f}" rx="12" fill="none" stroke="{col}" stroke-width="9"/>'
            + text(0, size * 0.34, txt, size, col, 700, "middle") + '</g>')
