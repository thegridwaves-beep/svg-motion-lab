"""Episode 1 scenes. Each scene: fn(t, D, cues) -> dict(world, defs, cam=(z, fx, fy), overlay)."""
import math, random, json, sys
sys.path.insert(0, "/home/claude/bible")
import vivid as V
from kit import inside, P, S, E, C, R, U, g, text
from assets import *
from seq import cam_at

W, H = 960, 540
TL = {s["name"]: s for s in json.load(open("/home/claude/ant/timeline.json"))}


MODE = "all"            # "all" = everything inline, "frame" = skip cached layers, "collect" = gather cached layers
COLLECT = {"bg": [], "fg": []}


def ST(s):
    """Static background content: cached as an image when rendering motion."""
    if MODE == "all":
        return s
    if MODE == "collect":
        COLLECT["bg"].append(s)
    return ""


def FG(s):
    """Static foreground content (drawn above the action), cached separately."""
    if MODE == "all":
        return s
    if MODE == "collect":
        COLLECT["fg"].append(s)
    return ""


def cue(cues, i):
    return cues[i]["t"] if i < len(cues) else 1e9


def sky(id_, stops):
    return V.lin(id_, stops)


# ------------------------------------------------------------------ shared garden world
def garden_bg(t, seed=11, ground=432, sun=(760, 120), warm=1.0):
    rnd = random.Random(seed)
    o = [f'<rect x="-400" y="-400" width="1760" height="1340" fill="url(#gsky)"/>']
    o.append(glow(sun[0], sun[1], 220, "#FFD9A8", 0.45 * warm, 30) + glow(sun[0], sun[1], 70, "#FFF4D8", 0.8 * warm, 16))
    for k in range(7):
        a = math.radians(100 + k * 12)
        o.append(poly([sun, (sun[0] + 1400 * math.cos(a - 0.03), sun[1] + 1400 * math.sin(a - 0.03)),
                       (sun[0] + 1400 * math.cos(a + 0.03), sun[1] + 1400 * math.sin(a + 0.03))], "#FFE6C0", 0.05 * warm))
    o.append(f'<g filter="url(#b4)">{grass_field(rnd, -300, 1260, ground + 4, 260, 560, 26, 60, 30, t, wind=0.6, haze=0.45)}</g>')
    o.append(f'<path d="M-400 {ground} Q480 {ground - 14} 1360 {ground} L1360 940 L-400 940 Z" fill="url(#gsoil)"/>')
    o.append(f'<path d="M-400 {ground} Q480 {ground - 14} 1360 {ground} L1360 {ground + 5} Q480 {ground - 9} -400 {ground + 5} Z" fill="#FFB89A" opacity="0.55"/>')
    for _ in range(26):
        x, y = rnd.uniform(-300, 1260), rnd.uniform(ground + 10, ground + 110)
        r = rnd.uniform(4, 14)
        o.append(pebble(x, y, r * 1.4, r, rnd.choice([("#9A7AD8", "#6A4AA8", "#D8C8FF"), ("#C88AB8", "#8A4A80", "#FFD0EE"), ("#7A8AE0", "#4A5AB0", "#C8D8FF")])))
    return ST("".join(o))


GARDEN_DEFS = (sky("gsky", [(0, "#2A1680"), (0.45, "#7A34C0"), (0.8, "#FF7AB0"), (1, "#FFC79A")]) +
               V.lin("gsoil", [(0, "#4A1E7A"), (1, "#22104A")]))


def fg_blades(t, seed=5, ground=540, n=8, blur=True):
    rnd = random.Random(seed)
    s = grass_field(rnd, -200, 1160, ground + 60, 200, 380, 40, 80, n, 0.0, wind=0.8)
    return FG(f'<g filter="url(#b8)" opacity="0.95">{s}</g>' if blur else s)


def title_panel(t, t0, s, size=40):
    if t < t0:
        return ""
    w = len(s) * size * 0.56 + 60
    panel = (f'<rect x="{480 - w/2:.0f}" y="54" width="{w:.0f}" height="{size + 34}" rx="22" fill="#1A0A4A" opacity="0.55"/>' +
             text(480, 54 + size + 6, s, size, "#FFFFFF", 700, "middle"))
    return popin(panel, 480, 80, t, t0, 0.5)


def danger_icons(t, t0):
    o = ""
    icons = [(300, 190, "cold"), (480, 205, "water"), (660, 190, "bite")]
    for i, (x, y, kind) in enumerate(icons):
        if kind == "cold":
            ic = ball(x, y, 26, "#9AE8FF", "#3A8CC8", "#EFFFFF") + "".join(
                f'<path d="M{x} {y} L{x + 16*math.cos(a):.1f} {y + 16*math.sin(a):.1f}" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>' for a in [k * math.pi / 3 for k in range(6)])
        elif kind == "water":
            ic = raindrop(x, y + 10, 16)
        else:
            ic = g(spider(t), x, y + 6, 0.32)
        o += popin(ic, x, y, t, t0 + 0.9 + i * 0.25, 0.4)
    return o


# ------------------------------------------------------------------ 1. hook
def sc_hook(t, D, cues):
    c0, c1, c2, c3 = (cue(cues, i) for i in range(4))
    gr = 432
    w = [garden_bg(t, ground=gr)]
    rnd = random.Random(21)
    # clearing: mid blades left and right, with dew
    w.append(ST(grass_field(rnd, 120, 380, gr + 6, 160, 300, 18, 34, 9, 0.0)))
    w.append(ST(grass_field(rnd, 600, 900, gr + 6, 160, 320, 18, 34, 9, 0.0)))
    # the giant blade next to you, with the ghost building
    w.append(ST(blade(560, gr + 4, 372, 40, -30, GREENS[0], 0.0)))
    w.append(ST(drop(392, 300, 9) + drop(705, 270, 12) + drop(560 - 18, 140, 7)))
    bld = ramp(t, c2 + 0.5, c2 + 1.4)
    if bld > 0:
        x0, top = 600, gr - 372
        floors = "".join(f'<path d="M{x0} {gr - (k+1)*372/15:.1f} L{x0+70} {gr - (k+1)*372/15:.1f}" stroke="#FFFFFF" stroke-width="1.2" opacity="0.5"/>' for k in range(14))
        w.append(fade(f'<rect x="{x0}" y="{top}" width="70" height="372" fill="#FFFFFF" fill-opacity="0.08" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="6 6"/>' + floors, bld))
        if t < c3 + 0.4:
            w.append(popin(label(635, top - 22, "15 floors", "#FF4F9A"), 635, top - 22, t, c2 + 1.2))
    # you
    expr = "sleepy" if t < c0 + 1.6 else ("surprised" if t < c1 + 2.5 else "neutral")
    look_up = t > c2 + 0.3 and t < c3
    w.append(f'<ellipse cx="480" cy="{gr + 2}" rx="16" ry="3" fill="#140830" opacity="0.4"/>')
    w.append(g(you("stand", "surprised" if look_up else expr, t=t), 480, gr, 0.16))
    # the ant walks in and stops beside you
    ax = 760 - 230 * ramp(t, c1 - 0.2, c1 + 2.4)
    walking = c1 - 0.2 < t < c1 + 2.4
    w.append(f'<ellipse cx="{ax:.1f}" cy="{gr + 2}" rx="38" ry="4" fill="#140830" opacity="0.35"/>')
    w.append(g(ant(t, 1.0 if walking else 0.0), ax, gr + 1, 0.78, 0, flip=True))
    # size bracket
    br = ramp(t, c1 + 1.0, c1 + 1.6) * (1 - ramp(t, c2 - 0.2, c2 + 0.3))
    if br > 0:
        w.append(fade(f'<path d="M455 {gr} L449 {gr} L449 {gr - 84} L455 {gr - 84}" stroke="#FFFFFF" stroke-width="2" fill="none"/>', br))
        w.append(popin(label(412, gr - 42, "3.4 mm", "#2A1470"), 412, gr - 42, t, c1 + 1.2))
    w.append(fg_blades(t, 7, 560, 7))
    cam = cam_at([(0, 3.4, 478, 372), (c0 + 3.5, 3.0, 480, 380), (c1 + 0.3, 3.0, 480, 380), (c1 + 2.6, 1.6, 540, 395),
                  (c2 + 0.2, 1.6, 540, 395), (c2 + 2.2, 1.0, 480, 270), (D, 1.0, 480, 270)], t)
    ov = title_panel(t, c3 + 0.6, "What would kill you first?") + danger_icons(t, c3 + 0.6)
    return dict(world="".join(w), defs=GARDEN_DEFS, cam=cam, overlay=ov)


# ------------------------------------------------------------------ 2. the kitchen table
KITCHEN_DEFS = (sky("ksky", [(0, "#3A1E9A"), (0.55, "#6A34C8"), (1, "#B85AD0")]) + V.lin("wood", [(0, "#E8A06A"), (1, "#B86A3A")]) +
                V.lin("ktop", [(0, "#C9804E"), (1, "#F2B47A")]) + V.lin("kfloor", [(0, "#3A2290"), (1, "#24125E")]) +
                V.lin("beam", [(0, "#FFE6B8"), (1, "#FFE6B8")]) +
                '<radialGradient id="ushade" cx="0.5" cy="0" r="0.9"><stop offset="0" stop-color="#0A0420" stop-opacity="0.55"/><stop offset="1" stop-color="#0A0420" stop-opacity="0"/></radialGradient>')


def kitchen_bg(t, seed=4):
    """Wall, window light, blurred far counter with objects, bokeh and floating dust. Covers x -400..1400, y -300..900."""
    rr = random.Random(seed)
    o = [f'<rect x="-600" y="-600" width="2400" height="2000" fill="url(#ksky)"/>']
    far = []
    far.append(f'<rect x="640" y="-120" width="420" height="330" rx="18" fill="#FFE2B0" opacity="0.8"/>')
    far.append(f'<rect x="655" y="-105" width="190" height="300" fill="#FFF4DC" opacity="0.7"/><rect x="855" y="-105" width="190" height="300" fill="#FFF4DC" opacity="0.7"/>')
    for i in range(16):
        for j in range(4):
            far.append(f'<rect x="{-300 + i*90}" y="{40 + j*60}" width="82" height="52" rx="8" fill="#8A6AE8" opacity="0.35"/>')
    far.append(f'<rect x="-400" y="250" width="1800" height="30" fill="#4A2AA0"/>')
    # far counter objects
    far.append(f'<rect x="80" y="40" width="110" height="210" rx="40" fill="#5AD8E8" opacity="0.85"/><rect x="95" y="20" width="80" height="34" rx="10" fill="#2EA6C8"/>')
    for (x, y, r, c) in [(330, 210, 46, "#FF8A3A"), (400, 200, 52, "#FFB03A"), (370, 160, 44, "#FF6F61")]:
        far.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>')
    far.append(f'<path d="M280 250 Q300 270 470 250 L460 230 L290 230 Z" fill="#E8E4FF"/>')
    for k in range(5):
        a = math.radians(-120 + k * 18)
        far.append(f'<ellipse cx="{560 + 70*math.cos(a):.0f}" cy="{150 + 90*math.sin(a):.0f}" rx="22" ry="60" fill="#3FD68A" transform="rotate({math.degrees(a)+90:.0f} {560 + 70*math.cos(a):.0f} {150 + 90*math.sin(a):.0f})"/>')
    far.append(f'<path d="M520 170 L600 170 L590 250 L530 250 Z" fill="#FF6FB5"/>')
    o.append(f'<g filter="url(#b8)">{"".join(far)}</g>')
    # window light beam and dust in it
    o.append(poly([(700, -120), (1040, -120), (620, 900), (180, 900)], "#FFE6B8", 0.07))
    for _ in range(10):
        o.append(f'<circle cx="{rr.uniform(-200, 1200):.0f}" cy="{rr.uniform(-200, 300):.0f}" r="{rr.uniform(20, 50):.0f}" fill="#FFD0F0" opacity="0.12" filter="url(#b8)"/>')
    return ST("".join(o)) + dust(t, seed)


def dust(t, seed=4):
    rr = random.Random(seed + 100)
    o = []
    for _ in range(36):
        x0, y0 = rr.uniform(250, 950), rr.uniform(-80, 800)
        x = x0 + 12 * math.sin(t * 0.4 + y0)
        y = (y0 - t * 6) % 880 - 80
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr.uniform(0.8, 2.2):.1f}" fill="#FFF2D8" opacity="{rr.uniform(0.3, 0.8):.2f}"/>')
    return "".join(o)


def table_top(x0=-600, x1=640, top=300):
    surf = P(f"M{x0} {top - 70} L{x1 - 40} {top - 70} L{x1} {top} L{x0} {top} Z")
    o = [surf("url(#ktop)")]
    o.append(inside(surf, "".join(f'<path d="M{x0} {top - 64 + k*13} Q{(x0 + x1)/2} {top - 60 + k*13 + (5 if k % 2 else -4)} {x1} {top - 64 + k*13}" stroke="#B8703E" stroke-width="1.6" fill="none" opacity="0.45"/>' for k in range(6))))
    edge = R(x0, top, x1 - x0, 40, 8)
    o.append(sh(edge, "#D8905A", "#A85E30", "#FFC890", 1.6))
    o.append(f'<rect x="{x0}" y="{top - 2}" width="{x1 - x0}" height="4" fill="#FFD6A8" opacity="0.7"/>')
    return ST("".join(o))


def sc_fall(t, D, cues):
    c0, c1, c2 = (cue(cues, i) for i in range(3))
    top = 300
    w = [kitchen_bg(t), table_top(top=top)]
    w.append(ST("".join(crumb(x, top - 20 - s_ * 0.6, s_, sd) for (x, s_, sd) in [(430, 9, 3), (340, 6, 4), (250, 7, 5)]) +
                sugar(470, top - 30, 7) + sugar(380, top - 46, 6)))
    spoon = P("M150 520 Q300 380 520 360 Q560 362 560 380 Q540 400 320 470 Q220 520 180 560 Z")
    w.append(FG(f'<g filter="url(#b8)">{sh(spoon, "#D8DCF8", "#9AA0D0", "#FFFFFF", 3)}</g>'))
    # you walk to the edge, slip at c0+2.2, then freeze mid-air at c1
    slip = c0 + 2.2
    if t < slip:
        x = 520 + 90 * ramp(t, 0.2, slip)
        w.append(f'<ellipse cx="{x:.1f}" cy="{top - 6:.1f}" rx="10" ry="2" fill="#7A3A1E" opacity="0.4"/>')
        w.append(g(you("walk" if t < slip - 0.1 else "stand", "happy", t=t), x, top - 6, 0.12))
    else:
        u = min(t, c1) - slip
        x = 610 + 40 * u + (6 * math.sin(t * 2) if t > c1 else 0)
        y = top + 0.5 * 90 * u * u
        rot = 30 * u + (8 * math.sin(t * 1.5) if t > c1 else 0)
        expr = "surprised"
        w.append(g(g(you("cheer", expr, breathe=False), 0, 260, 1, 0), x, y - 30, 0.12, rot))
    cam = cam_at([(0, 2.4, 560, 270), (slip, 2.6, 610, 285), (c1, 2.2, 650, 330), (D, 2.0, 650, 335)], t)
    # comparison panel during c1..c2
    pnl = ramp(t, c1 + 0.2, c1 + 0.9) * (1 - ramp(t, c2 - 0.4, c2 + 0.2))
    ov = ""
    if pnl > 0:
        p = [f'<rect x="96" y="70" width="768" height="400" rx="26" fill="#140A3A" opacity="0.72"/>']
        # left: table and tiny you
        p.append(sh(R(170, 220, 230, 18, 6), "#E8A06A", "#B86A3A", "#FFD0A0"))
        p.append(f'<rect x="185" y="238" width="12" height="150" fill="#B86A3A"/><rect x="373" y="238" width="12" height="150" fill="#B86A3A"/>')
        p.append(f'<rect x="150" y="388" width="270" height="4" rx="2" fill="#8A7AD8"/>')
        p.append(f'<circle cx="390" cy="217" r="2.2" fill="#2EA6C8"/>' + label(392, 192, "you", "#2EA6C8"))
        p.append(label(285, 428, "table: 75 cm", "#FF8A3A") + text(285, 112, "Your fall", 24, "#FFFFFF", 700, "middle"))
        # right: skyscraper and normal human
        p.append(V.iso_box(660, 388, 40, 40, 230, "#B9A2FF", "#7A5CF0", "#5236C0"))
        p.append(V.iso_windows(660, 388, 40, 40, 230, random.Random(3), "#FFE27A", "#2A1A6A"))
        p.append(f'<rect x="530" y="388" width="270" height="4" rx="2" fill="#8A7AD8"/>')
        p.append(f'<circle cx="660" cy="130" r="3" fill="#FFD23A"/>')
        p.append(label(660, 428, "skyscraper: 375 m", "#FF4F9A") + text(660, 112, "Same fall, at human size", 24, "#FFFFFF", 700, "middle"))
        ov = fade("".join(p), pnl)
    return dict(world="".join(w), defs=KITCHEN_DEFS, cam=cam, overlay=ov)


# ------------------------------------------------------------------ 3. square cube law
def sc_cube(t, D, cues):
    c0, c1 = cue(cues, 0), cue(cues, 1)
    o = [ST(f'<rect x="-200" y="-200" width="1360" height="940" fill="url(#cbg)"/>' + "".join(
        f'<path d="M{k*40} 0 L{k*40 - 300} 540" stroke="#FFFFFF" stroke-width="1" opacity="0.04"/>' for k in range(-10, 30)))]
    # cube on the left that shrinks
    s = 150 * (1 - 0.82 * ramp(t, c1 + 0.4, c1 + 3.0))
    cx, cy = 250, 400
    o.append(f'<ellipse cx="{cx}" cy="{cy + 4}" rx="{s*1.1:.1f}" ry="{s*0.28:.1f}" fill="#0A0420" opacity="0.3"/>')
    o.append(V.iso_box(cx, cy, s, s, s, "#9AF0FF", "#2EA6C8", "#1E7A9A"))
    o.append(popin(label(cx, 120, "shrink 500×", "#FF4F9A", size=16), cx, 120, t, c1 + 0.2))
    # two meters on the right
    rows = [("Surface", "÷ 250,000", "#46E0D0", 0.45, c0 + 0.6), ("Weight", "÷ 125,000,000", "#FFD23A", 0.86, c0 + 1.2)]
    for i, (name, val, col, frac, t0) in enumerate(rows):
        y = 210 + i * 130
        o.append(popin(text(500, y, name, 28, "#FFFFFF", 700, "start"), 560, y - 10, t, t0))
        if t > t0:
            bar = R(500, y + 20, 380, 30, 15)
            o.append(f'<rect x="500" y="{y + 20}" width="380" height="30" rx="15" fill="#2A0E80"/>')
            shrink = ramp(t, c1 + 0.6 + i * 1.2, c1 + 2.8 + i * 1.2)
            wd = 380 * (1 - frac * shrink)
            o.append(inside(bar, f'<rect x="500" y="{y + 20}" width="{wd:.1f}" height="30" rx="15" fill="{col}"/><rect x="500" y="{y + 20}" width="{wd:.1f}" height="9" fill="#FFFFFF" opacity="0.35"/>'))
            o.append(popin(label(820, y - 8, val, "#1A0A4A", col, 16), 820, y - 8, t, c1 + 1.4 + i * 1.2))
    return dict(world="".join(o), defs=V.lin("cbg", [(0, "#4A20C0"), (1, "#22107A")]), cam=(1.0, 480, 270), overlay="")


# ------------------------------------------------------------------ 4. the slow fall, and the ant
def sc_fall2(t, D, cues):
    c0, c1 = cue(cues, 0), cue(cues, 1)
    land = 4.4
    floor_y = 470
    # world scrolls up while you drift; camera follows you, then settles
    fall_u = ramp(t, 0, land)
    yy = 120 + (floor_y - 120) * fall_u
    o = [kitchen_bg(t)]
    st = [f'<rect x="-600" y="{floor_y}" width="2400" height="500" fill="url(#kfloor)"/>']
    for k in range(-8, 18):
        st.append(f'<path d="M{k*120} {floor_y} L{k*120 + (k*120 - 480)*0.6:.0f} {floor_y + 300}" stroke="#5A3AC0" stroke-width="2" opacity="0.6"/>')
    st.append(f'<rect x="-600" y="{floor_y}" width="2400" height="3" fill="#9A7AF8" opacity="0.6"/>')
    o.append(ST("".join(st)))
    leg = R(330, -600, 70, floor_y + 600, 8)
    o.append(ST(f'<rect x="-600" y="-600" width="2400" height="{floor_y + 600}" fill="url(#ushade)"/>' +
                f'<ellipse cx="365" cy="{floor_y + 4}" rx="70" ry="8" fill="#0A0420" opacity="0.4"/>' + sh(leg, "#E8A06A", "#B86A3A", "#FFD0A0", 2)))
    o.append(FG(f'<g filter="url(#b8)">{sh(R(760, -600, 60, floor_y + 640, 10), "#FF8AC8", "#C9408A", "#FFC0E0", 2)}</g>'))
    # air streaks while falling
    if t < land:
        rr = random.Random(5)
        for k in range(10):
            x = 480 + rr.uniform(-60, 60)
            y0 = (rr.uniform(0, 300) - t * 260) % 300
            y = yy - 150 + y0
            o.append(f'<path d="M{x:.1f} {y:.1f} l0 {-24:.1f}" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.45"/>')
    # you
    if t < land:
        rot = 18 * math.sin(t * 1.6)
        o.append(g(g(you("cheer", "happy", breathe=False), 0, 260, 1, 0), 480, yy - 22, 0.12, rot))
    else:
        o.append(f'<ellipse cx="480" cy="{floor_y + 1}" rx="12" ry="2.5" fill="#140830" opacity="0.4"/>')
        o.append(g(you("stand" if t < land + 1.2 else "wave", "happy", t=t), 480, floor_y, 0.12))
        u = clamp((t - land) / 0.8)
        if u < 1:
            for k in range(6):
                a = math.pi * k / 5
                o.append(f'<circle cx="{480 + math.cos(a)*22*u:.1f}" cy="{floor_y - math.sin(a)*8*u:.1f}" r="{3*(1-u):.2f}" fill="#B8A8FF" opacity="{0.8*(1-u):.2f}"/>')
    # the ant falls next to you and walks off
    a0 = c1 + 0.6
    if t > a0:
        u = t - a0
        ay = min(floor_y, 60 + 0.5 * 400 * u * u)
        landed = ay >= floor_y
        tl = (u - math.sqrt(2 * (floor_y - 60) / 400)) if landed else 0
        ax = 600 + 60 * max(0, tl - 0.6)
        rot = 0 if landed else 40 * u
        bounce = -6 * math.sin(min(tl, 0.4) / 0.4 * math.pi) if landed and tl < 0.4 else 0
        o.append(g(ant(t, 1.0 if tl > 0.6 else 0.0), ax, ay + bounce, 0.6, rot))
    cam = cam_at([(0, 2.4, 480, 120), (land, 2.2, 480, floor_y - 60), (c1, 2.2, 480, floor_y - 60), (c1 + 1.2, 1.7, 540, floor_y - 90), (D, 1.6, 560, floor_y - 90)], t)
    ov = popin(label(480, 470, "about 9 km/h, a slow jog", "#2A1470", size=16), 480, 470, t, 1.4) if t < land + 0.6 else ""
    return dict(world="".join(o), defs=KITCHEN_DEFS, cam=cam, overlay=ov)



# ------------------------------------------------------------------ helpers for garden-floor scenes
def garden_stage(t, gr=432, seed=21, warm=1.0, sun=(760, 120)):
    rnd = random.Random(seed)
    o = [garden_bg(t, ground=gr, warm=warm, sun=sun)]
    o.append(ST(grass_field(rnd, 60, 360, gr + 6, 150, 300, 18, 34, 8, 0.0)))
    o.append(ST(grass_field(rnd, 640, 960, gr + 6, 150, 320, 18, 34, 8, 0.0)))
    return "".join(o)


def shadow(x, y, rx):
    return f'<ellipse cx="{x:.1f}" cy="{y + 1:.1f}" rx="{rx:.1f}" ry="{rx*0.2:.1f}" fill="#140830" opacity="0.4"/>'


def stage_bg(id_="stg", c1="#4A20C0", c2="#1E0E6A"):
    return ST(f'<rect x="-400" y="-400" width="1760" height="1340" fill="url(#{id_})"/>'), V.lin(id_, [(0, c1), (1, c2)])


# ------------------------------------------------------------------ 5. strong
def sc_strong(t, D, cues):
    c0, c1 = cue(cues, 0), cue(cues, 1)
    gr = 432
    w = [garden_stage(t, gr)]
    cx = 560
    lift = ramp(t, c1 + 0.4, c1 + 1.4)
    yx = 440 + 100 * ramp(t, 0.3, 2.6)
    if lift <= 0:
        w.append(crumb(cx + 20, gr - 22, 26, 7))
        w.append(shadow(yx, gr, 12) + g(you("walk" if 0.3 < t < 2.6 else "stand", "neutral" if t < c1 else "happy", t=t), yx, gr, 0.16))
    else:
        hy = gr - 0.16 * 470
        cy = (gr - 22) + (hy - 26 - (gr - 22)) * lift
        w.append(shadow(yx, gr, 12) + g(you("cheer", "happy", t=t), yx, gr, 0.16))
        w.append(crumb(yx + 20 * (1 - lift), cy, 26, 7))
    # an ant carrying a leaf bit walks past behind
    ax = 980 - 70 * t
    carry = g(leaf(0, 0, 70, 18, -20, ("#7AE860", "#3AA83A", "#E0FFB0")), 10, -64, 1)
    w.append(shadow(ax, gr - 6, 30) + g(ant(t, 1.0, carry=carry), ax, gr - 6, 0.62, 0, flip=True))
    w.append(fg_blades(t, 9, 560, 6))
    ov = (popin(label(300, 70, "strength ÷ 250,000", "#46E0D0", "#0A0420", 16), 300, 70, t, c0 + 2.0) +
          popin(label(660, 70, "weight ÷ 125,000,000", "#FFD23A", "#0A0420", 16), 660, 70, t, c0 + 3.4) +
          popin(label(480, 470, "10× your weight", "#FF4F9A", size=18), 480, 470, t, c1 + 2.4))
    cam = cam_at([(0, 2.0, 520, 360), (c1, 2.3, 530, 365), (D, 2.4, 535, 360)], t)
    return dict(world="".join(w), defs=GARDEN_DEFS, cam=cam, overlay=ov)


# ------------------------------------------------------------------ 6. cold
def heat_aura(t, cx, cy, strength, cold, rate=1.0, seed=3):
    rr = random.Random(seed)
    o = [glow(cx, cy, 70 * strength, "#FF8A3A", 0.35 * strength, 16), glow(cx, cy, 34 * strength, "#FFC27A", 0.35 * strength, 8)]
    for k in range(int(40 * rate)):
        a = rr.uniform(0, 2 * math.pi)
        sp = rr.uniform(22, 40)
        life = 2.2
        u = ((t * rate * 0.6 + rr.random()) % 1.0)
        d = 14 + u * sp * life
        x, y = cx + math.cos(a) * d * 0.8, cy + math.sin(a) * d - u * 18
        col = "#FFB060" if cold < 0.5 else "#9AD8FF"
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{2.6*(1-u)+0.6:.2f}" fill="{col}" opacity="{0.8*(1-u):.2f}"/>')
    return "".join(o)


def sc_cold(t, D, cues):
    c0, c1, c2 = (cue(cues, i) for i in range(3))
    gr = 432
    w = [garden_stage(t, gr, warm=0.6, sun=(840, 200))]
    rate = 1.0 + 2.0 * ramp(t, c2, c2 + 2)
    w.append(heat_aura(t, 480, gr - 42, 1.0, 0.0, rate))
    w.append(shadow(480, gr, 12) + g(you("stand", "neutral", t=t), 480, gr, 0.16))
    pulse = 0.5 + 0.5 * math.sin(t * 3)
    if t > c1:
        w.append(fade(glow(480, gr - 50, 9 + 2 * pulse, "#FFD27A", 0.9, 4), ramp(t, c1, c1 + 0.6)))
    w.append(fg_blades(t, 12, 560, 6))
    ov = (popin(label(480, 76, "37 °C inside", "#FF8A3A", size=18), 480, 76, t, c1 + 1.0) +
          popin(label(480, 470, "500× more skin for every bit of you", "#2A1470", size=16), 480, 470, t, c2 + 0.8))
    cam = cam_at([(0, 3.0, 480, 380), (c2, 2.6, 480, 385), (D, 2.8, 480, 383)], t)
    return dict(world="".join(w), defs=GARDEN_DEFS, cam=cam, overlay=ov)


# ------------------------------------------------------------------ 7. shrew vs you
def sc_shrew(t, D, cues):
    c0, c1 = cue(cues, 0), cue(cues, 1)
    bg, bd = stage_bg("shb", "#5A24C8", "#22107A")
    o = [bg]
    o.append(ST("".join(f'<circle cx="{(k*173) % 960}" cy="{(k*97) % 540}" r="{40 + (k*31) % 50}" fill="#FFFFFF" opacity="0.04"/>' for k in range(12))))
    # scale platform + shrew
    o.append(sh(R(90, 380, 360, 26, 13), "#E8ECFF", "#A8B0E0", "#FFFFFF"))
    o.append(sh(R(220, 406, 100, 60, 8), "#9AA8D8", "#6A78B0"))
    o.append(g(shrew(t), 270, 380, 1.0))
    o.append(popin(label(270, 440, "2 g", "#FF8A3A", size=18), 270, 440, t, c0 + 2.2))
    # food pile grows: twice its weight a day
    fp = ramp(t, c0 + 4.5, c0 + 7.5)
    if fp > 0:
        rr = random.Random(4)
        for k in range(int(26 * fp)):
            x, y = 500 + rr.uniform(-60, 60), 400 - rr.uniform(0, 50) * (k / 26)
            o.append(ball(x, y, rr.uniform(9, 13), rr.choice(["#FFB03A", "#FF8A3A", "#FFD27A"]), "#C0601E"))
        o.append(popin(label(500, 300, "2× its weight, every day", "#FFD23A", "#2A1470", 15), 500, 300, t, c0 + 6.0))
    # tiny you and a grain of sugar
    if t > c1:
        o.append(sh(R(700, 380, 160, 14, 7), "#E8ECFF", "#A8B0E0", "#FFFFFF"))
        o.append(popin(g(you("wave", "happy", t=t), 755, 380, 0.08) + sugar(805, 380, 12), 780, 370, t, c1 + 0.3))
        o.append(popin(label(780, 420, "0.5 mg", "#2EA6C8", size=18), 780, 420, t, c1 + 1.2))
        o.append(popin(label(780, 300, "≈ a grain of sugar", "#FFFFFF", "#2A1470", 15), 780, 300, t, c1 + 2.2))
        o.append(popin(label(480, 488, "thousands of times lighter than the shrew", "#FF4F9A", size=15), 480, 488, t, c1 + 3.6))
    return dict(world="".join(o), defs=bd, cam=cam_at([(0, 1.06, 470, 280), (D, 1.0, 480, 270)], t), overlay="")


# ------------------------------------------------------------------ 8. losing to the cold
def sc_cold2(t, D, cues):
    gr = 432
    w = [garden_stage(t, gr, warm=0.35, sun=(860, 260))]
    fr = ramp(t, 0.5, 5.0)
    w.append(heat_aura(t, 480, gr - 42, 1.0 - 0.7 * fr, fr, 2.5))
    jit = 0.8 * fr * math.sin(t * 47)
    w.append(shadow(480, gr, 12) + g(you("hold", "sad", t=t), 480 + jit, gr, 0.16))
    w.append(f'<rect x="-400" y="-400" width="1760" height="1340" fill="#4A8AE0" opacity="{0.18*fr:.2f}"/>')
    w.append(fg_blades(t, 13, 560, 6))
    # frost creeping in from the frame edges (screen space)
    rr = random.Random(9)
    frost = []
    for _ in range(90):
        side = rr.choice(["l", "r", "t", "b"])
        d = rr.uniform(0, 90) * fr
        if side == "l": x, y = d, rr.uniform(0, 540)
        elif side == "r": x, y = 960 - d, rr.uniform(0, 540)
        elif side == "t": x, y = rr.uniform(0, 960), d
        else: x, y = rr.uniform(0, 960), 540 - d
        frost.append(sparkle(round(x), round(y), rr.uniform(3, 9) * fr + 0.5, "#E8F8FF", 0.75))
    ov = (f'<g filter="url(#b2)">{"".join(frost)}</g>' +
          f'<rect width="960" height="540" fill="none" stroke="#DFF4FF" stroke-width="{60*fr:.1f}" opacity="0.25" filter="url(#b16)"/>')
    cam = cam_at([(0, 2.8, 480, 383), (D, 3.1, 480, 380)], t)
    return dict(world="".join(w), defs=GARDEN_DEFS, cam=cam, overlay=ov)


# ------------------------------------------------------------------ 9-10. the dewdrop
def leaf_world(t, top=420):
    o = [garden_bg(t, ground=560, seed=31, warm=0.9)]
    surf = P(f"M-400 {top + 30} Q480 {top - 30} 1360 {top + 30} L1360 900 L-400 900 Z")
    o.append(sh(surf, "#46E08A", "#1EA864", "#C2FFD8", 4))
    o.append(inside(surf, "".join(f'<path d="M{-200 + k*170} 900 Q{-100 + k*170} {top + 60} {40 + k*170} {top - 10}" stroke="#2EB872" stroke-width="5" fill="none" opacity="0.5"/>' for k in range(10)) +
                    f'<path d="M-400 {top + 50} Q480 {top - 10} 1360 {top + 50}" stroke="#2AA060" stroke-width="10" fill="none" opacity="0.6"/>'))
    rr = random.Random(5)
    for _ in range(30):
        x = rr.uniform(-300, 1260)
        o.append(f'<circle cx="{x:.0f}" cy="{top + 10 + rr.uniform(0, 60) + (x - 480)**2 / 9000:.0f}" r="{rr.uniform(1.5, 3):.1f}" fill="#E0FFE8" opacity="0.6"/>')
    return ST("".join(o))


def sc_dew(t, D, cues):
    c0, c1 = cue(cues, 0), cue(cues, 1)
    top = 420
    w = [leaf_world(t, top)]
    dx, dr = 590, 44
    w.append(drop(dx, top - dr + 4, dr, t, 0.01))
    w.append(glow(dx - 18, top - dr - 18, 10, "#FFFFFF", 0.6 + 0.3 * math.sin(t * 4), 4))
    stop = c1 - 0.2
    yx = 360 + 165 * ramp(t, 0.6, stop)
    pose = "walk" if 0.6 < t < stop else ("point" if t > c1 else "stand")
    expr = "surprised" if t > c1 else "happy"
    w.append(shadow(yx, top - 2, 11) + g(you(pose, expr, t=t), yx, top - 2, 0.15))
    w.append(FG(f'<g filter="url(#b8)">{drop(260, 500, 70)}{blade(880, 620, 300, 70, -60, GREENS[1])}</g>'))
    cam = cam_at([(0, 1.8, 470, 330), (c1, 2.3, 560, 350), (D, 2.4, 565, 352)], t)
    return dict(world="".join(w), defs=GARDEN_DEFS, cam=cam, overlay="")


def sc_dew2(t, D, cues):
    c0, c1, c2 = (cue(cues, i) for i in range(3))
    top = 420
    w = [leaf_world(t, top)]
    dx, dr = 590, 44
    dcy = top - dr + 4
    w.append(drop(dx, dcy, dr, t, 0.01))
    # surface tension arrows around the skin of the drop
    st = ramp(t, c0 + 2.5, c0 + 3.4) * (1 - ramp(t, c1 - 0.6, c1))
    if st > 0:
        arr = []
        for k in range(12):
            a = 2 * math.pi * k / 12
            x0, y0 = dx + math.cos(a) * (dr + 14), dcy + math.sin(a) * (dr + 14)
            x1, y1 = dx + math.cos(a) * (dr - 6), dcy + math.sin(a) * (dr - 6)
            arr.append(f'<path d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round"/>'
                       f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="2.6" fill="#FFFFFF"/>')
        w.append(fade("".join(arr), st))
    yx = 525
    touch = ramp(t, c1 + 0.4, c1 + 2.4)
    expr = "surprised" if t > c1 + 0.6 else "neutral"
    w.append(shadow(yx, top - 2, 11) + g(you("point", expr, t=t), yx, top - 2, 0.15))
    if touch > 0:
        pts = [(dx - dr + 6, dcy - 6), (yx + 28, top - 64), (yx + 9, top - 54), (yx + 4, top - 30)]
        segs = touch * 3
        path = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
        for i in range(3):
            if segs <= 0:
                break
            f_ = min(1, segs)
            (xa, ya), (xb, yb) = pts[i], pts[i + 1]
            path += f" L{xa + (xb - xa)*f_:.1f} {ya + (yb - ya)*f_:.1f}"
            segs -= 1
        w.append(f'<g opacity="0.8">{sh(S(path, 9), "#8EE6FF", "#3AA8E0", "#E8FDFF", 0.3)}</g>')
    w.append(FG(f'<g filter="url(#b8)">{drop(260, 500, 70)}{blade(880, 620, 300, 70, -60, GREENS[1])}</g>'))
    ov = popin(label(480, 470, "≈ 100× your weight", "#2A1470", size=18), 480, 470, t, c0 + 5.0) if t < c1 + 0.3 else ""
    # insects: waxy legs with beads sitting on top
    if t > c2:
        p = [f'<rect x="220" y="120" width="520" height="300" rx="24" fill="#140A3A" opacity="0.94"/>']
        legs = P("M260 330 Q480 300 700 330 L700 352 Q480 322 260 352 Z")
        p.append(sh(legs, ANT[0], ANT[1], ANT[2], 1))
        for k in range(14):
            p.append(f'<path d="M{275 + k*30} {330 - 2*math.sin(k)} l-4 -9" stroke="{ANT[1]}" stroke-width="2"/>')
        for k, (x, r) in enumerate([(330, 16), (430, 22), (540, 18), (640, 14)]):
            bob = 2 * math.sin(t * 3 + k)
            p.append(drop(x, 318 - r + bob, r, t))
        p.append(text(480, 170, "Waxy, water repelling", 26, "#FFFFFF", 700, "middle"))
        ov += popin("".join(p), 480, 270, t, c2 + 0.2, 0.5)
    cam = cam_at([(0, 2.4, 565, 352), (c1, 2.6, 560, 360), (D, 2.6, 560, 360)], t)
    return dict(world="".join(w), defs=GARDEN_DEFS, cam=cam, overlay=ov)


# ------------------------------------------------------------------ 11. rain
def sc_rain(t, D, cues):
    c0, c1, c2 = (cue(cues, i) for i in range(3))
    gr = 432
    w = [garden_stage(t, gr, warm=0.25, sun=(820, 60))]
    w.append(ST(f'<rect x="-400" y="-400" width="1760" height="1340" fill="#2A3A8A" opacity="0.35"/>'))
    # puddle
    pud = E(640, gr + 30, 120, 16)
    w.append(ST(sh(pud, "#5A8AE8", "#3A5AC0", "#BFE0FF", 1)) + inside(pud, "".join(
        f'<ellipse cx="640" cy="{gr + 30}" rx="{(((t*0.7 + k/3) % 1) * 110):.1f}" ry="{(((t*0.7 + k/3) % 1) * 14):.1f}" fill="none" stroke="#DFF4FF" stroke-width="1.5" opacity="{1 - ((t*0.7 + k/3) % 1):.2f}"/>' for k in range(3))))
    rr = random.Random(12)
    intensity = ramp(t, 0.3, 2.5)
    for k in range(int(60 * intensity)):
        x = rr.uniform(-100, 1060)
        sp = rr.uniform(300, 380)
        ph = rr.uniform(0, 3)
        period = (gr + 260) / sp
        u = ((t + ph) % period) / period
        y = -260 + u * (gr + 260)
        if y > gr:
            continue
        r = rr.uniform(8, 15)
        if abs(x - 480) < 30:
            continue
        w.append(raindrop(x, y, r, 0.9))
        su = ((t + ph) % period) / period
        tail = (t + ph) % period
        if su < 0.12 and t > period:
            w.append(splash(x, gr, r * 1.6, su / 0.12))
    w.append(shadow(480, gr, 12) + g(you("hold", "surprised" if t > c0 + 1 else "neutral", t=t), 480, gr, 0.16))
    # mosquito riding a drop, then slipping off
    if t > c2:
        u = t - c2
        my = -120 + 300 * u
        if u < 1.5:
            w.append(raindrop(300, my, 12) + g(mosquito(t), 300, my - 6, 0.8))
        else:
            fy = -120 + 450 - 40 * (u - 1.5)
            w.append(raindrop(300, -120 + 300 * u, 12))
            w.append(g(mosquito(t), 300 + 60 * (u - 1.5), fy, 0.8))
    ov = (popin(label(300, 76, "up to 100× your weight", "#2EA6C8", size=16), 300, 76, t, c1 + 1.4) +
          popin(label(660, 76, "≈ 30 km/h", "#FF4F9A", size=16), 660, 76, t, c1 + 3.0))
    cam = cam_at([(0, 1.5, 480, 330), (c2, 1.4, 430, 300), (c2 + 4, 1.6, 480, 360), (D, 1.6, 480, 360)], t)
    return dict(world="".join(w), defs=GARDEN_DEFS, cam=cam, overlay=ov)


# ------------------------------------------------------------------ 12. voice
def sc_voice(t, D, cues):
    c0, c1 = cue(cues, 0), cue(cues, 1)
    gr = 432
    w = [garden_stage(t, gr)]
    # a giant shoe nearby, unbothered
    shoe = P("M640 440 Q640 300 760 300 L1100 300 L1100 440 Z")
    w.append(ST(sh(shoe, "#FFFFFF", "#C9C0E8", "#FFFFFF", 4)) + ST(inside(shoe, '<rect x="600" y="400" width="520" height="40" fill="#FF4F9A"/><rect x="600" y="300" width="520" height="30" fill="#E8E4F8"/>')))
    shout = t > c1 + 1.0
    w.append(shadow(480, gr, 12) + g(you("wave" if not shout else "cheer", "laugh" if shout else "surprised", t=t), 480, gr, 0.16))
    if shout:
        for k in range(5):
            u = ((t - c1) * 0.8 + k / 5) % 1
            r = 12 + u * 120
            w.append(f'<path d="M{480 + r*0.2:.1f} {gr - 76 - r*0.6:.1f} A{r:.1f} {r:.1f} 0 0 1 {480 + r*0.2:.1f} {gr - 76 + r*0.6:.1f}" stroke="#FFFFFF" stroke-width="2.4" fill="none" opacity="{0.8*(1-u):.2f}" transform="rotate(-10 480 {gr - 76})"/>')
    ov = ""
    sp = ramp(t, c1 + 2.5, c1 + 3.2)
    if sp > 0:
        p = [f'<rect x="120" y="40" width="720" height="130" rx="22" fill="#140A3A" opacity="0.8"/>']
        x0, x1 = 160, 800
        lg = lambda hz: x0 + (x1 - x0) * (math.log10(hz) - 1) / (math.log10(200000) - 1)
        p.append(f'<rect x="{x0}" y="110" width="{x1 - x0}" height="12" rx="6" fill="#3A2A8A"/>')
        p.append(f'<rect x="{lg(20):.1f}" y="110" width="{lg(20000) - lg(20):.1f}" height="12" rx="6" fill="#46E0D0"/>')
        p.append(text((lg(20) + lg(20000)) / 2, 96, "what humans can hear", 15, "#46E0D0", 700, "middle"))
        vx = lg(50000) + (lg(100000) - lg(50000)) * 0.5
        p.append(f'<rect x="{lg(50000):.1f}" y="106" width="{lg(100000) - lg(50000):.1f}" height="20" rx="10" fill="#FF4F9A"/>')
        p.append(text(vx, 152, "your voice", 15, "#FF8AC0", 700, "middle"))
        for hz, s_ in [(20, "20 Hz"), (20000, "20 kHz"), (100000, "100 kHz")]:
            p.append(text(lg(hz), 152 if hz != 100000 else 70, s_, 12, "#C8B8FF", 600, "middle", "Inter"))
        ov = fade("".join(p), sp)
    cam = cam_at([(0, 2.2, 520, 360), (D, 2.0, 540, 340)], t)
    return dict(world="".join(w), defs=GARDEN_DEFS, cam=cam, overlay=ov)


# ------------------------------------------------------------------ 13. eye
def sc_eye(t, D, cues):
    bg, bd = stage_bg("eyb", "#FF9AC8", "#7A3AC8")
    o = [bg]
    # what you'd see: a giant, very blurred person
    blur = ramp(t, 0.5, 3.0)
    face = (f'<circle cx="480" cy="230" r="230" fill="#E8B08A"/><circle cx="400" cy="200" r="28" fill="#2A1A3A"/><circle cx="560" cy="200" r="28" fill="#2A1A3A"/>'
            f'<path d="M380 60 Q480 -40 600 60 L620 120 Q480 40 340 120 Z" fill="#3A2A5A"/><ellipse cx="480" cy="330" rx="70" ry="20" fill="#C8605A"/>'
            f'<rect x="300" y="430" width="360" height="200" rx="80" fill="#FF6F61"/>')
    o.append(f'<g filter="url(#b{30 if blur > 0.5 else 16})" opacity="{0.6 + 0.4*blur:.2f}">{face}</g>')
    # inset: hair vs pupil
    ins = ramp(t, 3.4, 4.2)
    if ins > 0:
        p = [f'<rect x="560" y="300" width="360" height="200" rx="20" fill="#140A3A" opacity="0.85"/>']
        hair = R(590, 380, 300, 34, 17)
        p.append(sh(hair, "#7A4A2A", "#4A2A1A", "#C8885A", 0.8))
        p.append(text(740, 362, "a human hair, 70 µm", 15, "#FFD8B0", 700, "middle"))
        p.append(glow(740, 397, 6, "#FFFFFF", 0.8, 2) + '<circle cx="740" cy="397" r="3.6" fill="#FFFFFF"/>')
        p.append(text(740, 456, "your pupil, 8 µm", 15, "#FFFFFF", 700, "middle") + '<path d="M740 404 L740 438" stroke="#FFFFFF" stroke-width="1.5"/>')
        o.append(fade("".join(p), ins))
    return dict(world="".join(o), defs=bd, cam=cam_at([(0, 1.0, 480, 270), (D, 1.04, 480, 270)], t), overlay="")


# ------------------------------------------------------------------ 14. the locals
def sc_locals(t, D, cues):
    gr = 432
    w = [garden_stage(t, gr, warm=0.8)]
    # spider dropping on a thread
    sy = 90 + 170 * ramp(t, 0.4, 2.6) + 4 * math.sin(t * 2)
    w.append(f'<path d="M300 -400 L300 {sy - 30:.1f}" stroke="#E8E0FF" stroke-width="1.2" opacity="0.8"/>' + g(spider(t), 300, sy, 0.6, 90))
    # ants marching in from the right
    for k in range(4):
        ax = 1000 + k * 90 - 70 * max(0, t - 2.4)
        w.append(shadow(ax, gr - 4, 26) + g(ant(t + k * 0.3, 1.0), ax, gr - 4, 0.55, 0, flip=True))
    look = "surprised"
    turn = t > 2.2
    w.append(shadow(480, gr, 12) + g(you("stand", look, t=t), 480, gr, 0.16, 0, flip=turn))
    # bird shadow sweeping across the ground
    bx = -300 + 280 * max(0, t - 3.4)
    if t > 3.4:
        w.append(g(bird_shadow(0.3), bx, gr + 20, 1.4))
    w.append(fg_blades(t, 15, 560, 6))
    cam = cam_at([(0, 1.6, 420, 330), (D, 1.45, 480, 330)], t)
    return dict(world="".join(w), defs=GARDEN_DEFS, cam=cam, overlay="")


# ------------------------------------------------------------------ 15. the twist
def sc_twist(t, D, cues):
    c0, c1 = cue(cues, 0), cue(cues, 1)
    gr = 432
    dim = ramp(t, c1, c1 + 1.0)
    w = [garden_stage(t, gr, warm=0.7)]
    w.append(f'<rect x="-400" y="-400" width="1760" height="1340" fill="#0A0420" opacity="{0.55*dim:.2f}"/>')
    w.append(glow(480, gr - 40, 60, "#FFF0D0", 0.35 * dim, 16))
    w.append(shadow(480, gr, 12) + g(you("think", "think", t=t), 480, gr, 0.16))
    icons = [(-1, "cold"), (0, "water"), (1, "bite")]
    for i, (dxk, kind) in enumerate(icons):
        a = t * 0.6 + i * 2.09
        x, y = 480 + 70 * math.cos(a), gr - 50 + 26 * math.sin(a)
        if kind == "cold":
            ic = ball(x, y, 9, "#9AE8FF", "#3A8CC8", "#EFFFFF")
        elif kind == "water":
            ic = raindrop(x, y + 4, 6)
        else:
            ic = g(spider(t), x, y, 0.12)
        w.append(fade(popin(ic, x, y, t, 0.4 + i * 0.6), 1 - dim))
    cam = cam_at([(0, 2.6, 480, 385), (D, 3.0, 480, 385)], t)
    return dict(world="".join(w), defs=GARDEN_DEFS, cam=cam, overlay="")


# ------------------------------------------------------------------ 16. cells and neurons
def silhouette(kind, x, y, s):
    if kind == "mouse":
        return g('<ellipse cx="0" cy="-20" rx="40" ry="22" fill="#FFFFFF"/><circle cx="34" cy="-30" r="14" fill="#FFFFFF"/><circle cx="28" cy="-46" r="8" fill="#FFFFFF"/><path d="M-38 -16 Q-70 -10 -80 10" stroke="#FFFFFF" stroke-width="4" fill="none"/>', x, y, s)
    if kind == "human":
        return g('<circle cx="0" cy="-150" r="22" fill="#FFFFFF"/><rect x="-26" y="-124" width="52" height="80" rx="20" fill="#FFFFFF"/><rect x="-22" y="-50" width="18" height="50" rx="8" fill="#FFFFFF"/><rect x="4" y="-50" width="18" height="50" rx="8" fill="#FFFFFF"/>', x, y, s)
    return g('<path d="M-150 -40 Q-90 -100 20 -90 Q110 -84 140 -40 Q150 -10 110 0 Q20 10 -90 -10 Q-120 -14 -140 -26 Z" fill="#FFFFFF"/>'
             '<path d="M-140 -30 L-190 -70 Q-180 -40 -200 -10 Z" fill="#FFFFFF"/><path d="M10 -6 Q30 20 0 34 Q-6 14 -10 -8 Z" fill="#FFFFFF"/>', x, y, s)


def sc_cells(t, D, cues):
    c0, c1, c2 = (cue(cues, i) for i in range(3))
    bg, bd = stage_bg("clb", "#3A1AA8", "#14084A")
    o = [bg]
    a1 = 1 - ramp(t, c1 - 0.6, c1)
    if a1 > 0:
        part = []
        for i, (kind, x, s) in enumerate([("mouse", 190, 1.3), ("human", 480, 1.0), ("whale", 770, 0.9)]):
            part.append(popin(f'<g opacity="0.85">{silhouette(kind, x, 260, s)}</g>', x, 220, t, 0.4 + i * 0.8))
            cx, cy = x, 380
            part.append(popin(f'<circle cx="{cx}" cy="{cy}" r="58" fill="#1A0A5A" stroke="#FFFFFF" stroke-width="3"/>' +
                              inside(C(cx, cy, 56), "".join(f'<circle cx="{cx - 60 + (k % 5)*30 + (15 if (k//5) % 2 else 0)}" cy="{cy - 60 + (k//5)*30}" r="13" fill="#FF7AC8" opacity="0.85"/><circle cx="{cx - 60 + (k % 5)*30 + (15 if (k//5) % 2 else 0)}" cy="{cy - 60 + (k//5)*30}" r="4.5" fill="#8A2A8A"/>' for k in range(25))),
                              cx, cy, t, 2.6 + i * 0.5))
        part.append(popin(label(480, 480, "same size cells", "#FF4F9A", size=16), 480, 480, t, 5.0))
        o.append(fade("".join(part), a1))
    # brain: many neurons, then very few
    b1 = ramp(t, c1, c1 + 0.8) * (1 - ramp(t, c2 - 0.5, c2))
    if b1 > 0:
        rr = random.Random(7)
        thin = ramp(t, c1 + 3.4, c1 + 5.2)
        part = [f'<ellipse cx="480" cy="270" rx="300" ry="200" fill="#2A1478" opacity="0.6"/>']
        n = 70
        for k in range(n):
            x, y = 480 + rr.uniform(-270, 270), 270 + rr.uniform(-170, 170)
            if ((x - 480) / 290) ** 2 + ((y - 270) / 190) ** 2 > 1:
                continue
            keep = (k % 9 == 0)
            op = 1.0 if keep else 1 - thin
            if op > 0.02:
                part.append(fade(neuron(x, y, 9, k), op))
        o.append(fade("".join(part), b1))
        o.append(fade(label(480, 60, "86,000,000,000 neurons", "#FF7AC8", "#14084A", 18), b1 * (1 - thin)))
        o.append(fade(label(480, 60, "fewer than 1,000", "#FFD23A", "#14084A", 18), b1 * thin))
    # an actual ant's brain
    b2 = ramp(t, c2, c2 + 0.8)
    if b2 > 0:
        o.append(fade(g(ant(t, 0.0), 480, 400, 3.2) + glow(480 + 38 * 3.2, 400 - 37 * 3.2, 30, "#FF7AC8", 0.8, 8) +
                      label(480, 90, "an ant: about 250,000 neurons", "#FF7AC8", "#14084A", 18), b2))
    return dict(world="".join(o), defs=bd, cam=(1.0, 480, 270), overlay="")


def sc_cells2(t, D, cues):
    gr = 432
    w = [garden_stage(t, gr, warm=0.6)]
    w.append(f'<rect x="-400" y="-400" width="1760" height="1340" fill="#0A0420" opacity="0.45"/>')
    dis = ramp(t, 2.6, 6.2)
    w.append(fade(shadow(480, gr, 12) + g(you("stand", "neutral", t=t), 480, gr, 0.16), 1 - dis))
    if dis > 0:
        rr = random.Random(2)
        for k in range(80):
            x0, y0 = 480 + rr.uniform(-12, 12), gr - rr.uniform(0, 84)
            u = clamp(dis * 1.4 - rr.uniform(0, 0.4))
            x, y = x0 + rr.uniform(-40, 40) * u, y0 - 70 * u
            w.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.6*(1-u)+0.3:.2f}" fill="{rr.choice(["#2EA6C8", "#C98B62", "#FFFFFF"])}" opacity="{(1-u)*min(1, dis*4):.2f}"/>')
    cam = cam_at([(0, 2.8, 480, 385), (D, 3.1, 480, 382)], t)
    return dict(world="".join(w), defs=GARDEN_DEFS, cam=cam, overlay="")


# ------------------------------------------------------------------ 17. what nature does instead
def sc_ant(t, D, cues):
    c0, c1 = cue(cues, 0), cue(cues, 1)
    bg, bd = stage_bg("anb", "#5A24C8", "#1E0E6A")
    o = [bg]
    o.append(ST("".join(f'<circle cx="{(k*173) % 960}" cy="{(k*97) % 540}" r="{30 + (k*31) % 60}" fill="#FFFFFF" opacity="0.035"/>' for k in range(16))))
    K_ = 4.2
    ax, ay = 470, 420
    o.append(f'<ellipse cx="{ax}" cy="{ay + 6}" rx="300" ry="26" fill="#0A0420" opacity="0.35"/>')
    o.append(g(ant(t, 0.0, antenna=0), ax, ay, K_))
    pts = [  # (label, anchor in ant coords, label pos, time offset)
        ("armor, not skin", (-40, -44), (190, 120), 0.2),
        ("tubes, not lungs", (8, -30), (470, 470), 1.9),
        ("thousands of tiny eyes", (42, -40), (790, 140), 3.6),
        ("a densely packed brain", (34, -32), (790, 300), 5.9),
    ]
    for i, (s_, (px, py), (lx, ly), dt) in enumerate(pts):
        t0 = c1 + dt
        if t < t0:
            continue
        X, Y = ax + px * K_, ay + py * K_
        if i == 1:
            o.append(fade(f'<path d="M{ax - 120} {ay - 120} Q{ax} {ay - 150} {ax + 110} {ay - 120}" stroke="#9AF0FF" stroke-width="3" fill="none" stroke-dasharray="6 6"/>', ramp(t, t0, t0 + 0.5)))
        if i == 2:
            o.append(fade("".join(f'<circle cx="{X - 10 + (k % 4)*6 + (3 if (k//4) % 2 else 0):.1f}" cy="{Y - 8 + (k//4)*5:.1f}" r="2.2" fill="#9AF0FF" opacity="0.9"/>' for k in range(16)), ramp(t, t0, t0 + 0.5)))
        if i == 3:
            o.append(fade(glow(X, Y, 26, "#FF7AC8", 0.9, 8), ramp(t, t0, t0 + 0.5)))
        o.append(fade(f'<path d="M{X:.1f} {Y:.1f} L{lx} {ly}" stroke="#FFFFFF" stroke-width="1.6" opacity="0.8"/><circle cx="{X:.1f}" cy="{Y:.1f}" r="4" fill="#FFFFFF"/>', ramp(t, t0, t0 + 0.4)))
        o.append(popin(label(lx, ly, s_, ["#FF8A3A", "#2EA6C8", "#46E0D0", "#FF4F9A"][i], size=16), lx, ly, t, t0 + 0.1))
    return dict(world="".join(o), defs=bd, cam=cam_at([(0, 1.08, 480, 280), (D, 1.0, 480, 270)], t), overlay="")


# ------------------------------------------------------------------ 18. end
def sc_end(t, D, cues):
    c0 = cue(cues, 0)
    gr = 432
    w = [garden_stage(t, gr, warm=1.0, sun=(700, 300))]
    m = ramp(t, c0 + 4.0, c0 + 5.2)
    w.append(fade(shadow(480, gr, 12) + g(you("stand", "happy", t=t), 480, gr, 0.16), 1 - m))
    w.append(fade(shadow(480, gr, 30) + g(ant(t, 0.0), 480, gr, 0.62), m))
    w.append(fg_blades(t, 17, 560, 6))
    cam = cam_at([(0, 2.6, 480, 385), (c0 + 5.5, 2.2, 480, 375), (D, 1.4, 480, 330)], t)
    endc = ramp(t, D - 2.6, D - 1.6)
    ov = ""
    if endc > 0:
        ov = fade(f'<rect width="960" height="540" fill="#14084A" opacity="0.65"/>' +
                  text(480, 260, "Sandbox", 64, "#FFFFFF", 700, "middle") +
                  text(480, 300, "big questions, small worlds", 18, "#C8B8FF", 600, "middle", "Inter"), endc)
    return dict(world="".join(w), defs=GARDEN_DEFS, cam=cam, overlay=ov)


SCENES = {"hook": sc_hook, "fall": sc_fall, "cube": sc_cube, "fall2": sc_fall2, "strong": sc_strong, "cold": sc_cold, "shrew": sc_shrew,
          "cold2": sc_cold2, "dew": sc_dew, "dew2": sc_dew2, "rain": sc_rain, "voice": sc_voice, "eye": sc_eye, "locals": sc_locals,
          "twist": sc_twist, "cells": sc_cells, "cells2": sc_cells2, "ant": sc_ant, "end": sc_end}


def frame_svg(name, t):
    s = TL[name]
    out = SCENES[name](t, s["dur"], s["cues"])
    z, fx, fy = out["cam"]
    world = (f'<g transform="translate({W/2} {H/2}) scale({z:.4f}) translate({-fx:.2f} {-fy:.2f})">{out["world"]}</g>')
    return V.svg(world + out.get("overlay", ""), out.get("defs", ""))
