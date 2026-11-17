"""Cold open + second 1 (the fall)."""
import math, random, sys
sys.path.insert(0, "/home/claude/ant"); sys.path.insert(0, "/home/claude/ant2")
from engine import shot, W, H
import vivid as V
from kit import inside, P, S, E, C, R, U, g, text
import assets as A
from assets import drop, ant, glow, ball, sh, GREENS, pebble, sparkle, raindrop, crumb, spider, leaf, label, sugar
from kit2 import *
import kit2
import hook  # the approved motion-test shots
import ep1

ease = V.ease
ramp = A.ramp


def eo(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def ei(x):
    x = max(0.0, min(1.0, x)); return x ** 3


def single(body_defs):
    body, defs = body_defs
    return dict(layers=[("all", 0, body, False, None)], defs=defs, cam=(0, 0, 1.0))


# better micro world for the shrink dive: grounded perspective, eye level
EYE = Cam(hz=392, vp=(480, -40000), near=560)


def micro_world(t):
    cam = EYE
    return (sky("dawn", (720, 150)) + forest(cam, 40) + ground(cam, "dawn", seed=4) +
            blades(cam, 11, 40, 0.02, 0.45, 260, 520, 0.9, avoid=(380, 600, 0.3), t=t) +
            pblade(cam, 590, 436, 380, 34, GREENS[0], -0.08) + drop(392, 300, 9, t) + drop(705, 270, 12, t) +
            contact(640, 433, 40) + g(ant(t, 1.0), 640 - 22 * max(0, t - 2.4), 433, 0.78, 0, flip=True) +
            blades(cam, 12, 8, 0.6, 0.75, 200, 300, 1.0, avoid=(300, 660, 0.0), t=t))


hook.micro_world = micro_world
hook.MACRO_DEFS = hook.MACRO_DEFS + sky_defs("dawn")


@shot("o_shrink")
def _(t, D, c):
    b, d = hook.s1(t)
    return single((b, d + sky_defs("dawn")))


@shot("o_flat")
def _(t, D, c):
    return single(hook.s2(t))


@shot("o_fall")
def _(t, D, c):
    return single(hook.s3(t))


# ---------------------------------------------------------------- montage: new angles
LOW = Cam(hz=440, vp=(480, -1800), near=640)


@shot("o_spider")
def _(t, D, c):
    """Low angle: a spider rears up over you, filling the top of frame."""
    cam = LOW
    L = [("sky", 0.1, sky("dusk" if False else "gold", (760, 140)), True, None),
         ("far", 0.3, blades(cam, 3, 40, 0.02, 0.2, 400, 900, t=0), True, 2),
         ("gnd", 0.6, ground(cam, "gold", seed=7) + blades(cam, 4, 18, 0.2, 0.5, 400, 800, avoid=(300, 660, 0.25)), True, None)]
    yy = cam.gy(0.55)
    you = contact(450, yy, 60) + g(front("brace", "stand", "surprised", -6, False), 450, yy, 0.42)
    sx = 900 - 200 * eo(t / 0.7)
    sp = g(spider(t), sx, yy - 40, 3.2, -18)
    L.append(("act", 0.9, you + sp, False, None))
    L.append(("fg", 1.4, pblade(cam, -40, 620, 1300, 140, GREENS[3], 0.1), True, 8))
    ov = kinetic("SPIDERS", 480, 110, t, 0.12, 72)
    return dict(layers=L, defs=sky_defs("gold"), cam=(12 * t, 0, 1 + 0.04 * t), overlay=ov)


@shot("o_cold")
def _(t, D, c):
    """Overhead: you curled up, frost growing in a ring around you."""
    o = [f'<rect x="-300" y="-300" width="1560" height="1140" fill="url(#ovr)"/>']
    rr = random.Random(5)
    for _ in range(90):
        x, y = rr.uniform(-100, 1060), rr.uniform(-100, 640)
        s_ = rr.uniform(6, 22)
        o.append(pebble(x, y, s_, s_ * 0.8, rr.choice(kit2.PEBS)))
    for _ in range(40):
        x, y = rr.uniform(-100, 1060), rr.uniform(-100, 640)
        if abs(x - 480) < 130 and abs(y - 270) < 110:
            continue
        a = rr.uniform(0, 6.28)
        o.append(g(leaf(0, 0, rr.uniform(60, 120), rr.uniform(14, 26), 0, rr.choice(GREENS)), x, y, 1, math.degrees(a)))
    st = "".join(o)
    fr = eo(t / 1.0)
    frost = []
    rr = random.Random(9)
    for k in range(80):
        a = rr.uniform(0, 6.28)
        r0 = 420 - 260 * fr * rr.uniform(0.6, 1.0)
        frost.append(sparkle(round(480 + math.cos(a) * r0 * 1.3), round(270 + math.sin(a) * r0 * 0.8), rr.uniform(5, 14) * fr + 1, "#E8F8FF", 0.85))
    jit = 1.5 * math.sin(t * 45)
    act = (f'<ellipse cx="480" cy="282" rx="96" ry="70" fill="#120830" opacity="0.35" filter="url(#b8)"/>' +
           g(top(0.0, 0.8), 480 + jit, 270, 1.4))
    L = [("bg", 1.0, st, True, None), ("act", 1.0, act, False, None),
         ("frost", 1.0, "".join(frost) + f'<rect width="{W}" height="{H}" fill="#9AC8FF" opacity="{0.25*fr:.2f}"/>', False, None)]
    ov = kinetic("COLD", 480, 110, t, 0.08, 72, "#E8F8FF")
    return dict(layers=L, defs=V.lin("ovr", [(0, "#3A3A8A"), (1, "#1E1A5A")]), cam=(0, 0, 1.06 - 0.06 * t), overlay=ov)


WORM = Cam(hz=560, vp=(480, 170), near=700)


@shot("o_rain")
def _(t, D, c):
    """Worm's eye, looking straight up: blades converge to the sky, a raindrop drops at the lens."""
    o = [sky("storm", (480, 170), False)]
    rr = random.Random(3)
    for k in range(18):
        a = math.radians(-180 + k * 20 + rr.uniform(-6, 6))
        bx, by = 480 + math.cos(a) * 900, 270 + math.sin(a) * 700
        o.append(pblade(Cam(vp=(480, 230)), bx, by, rr.uniform(500, 800), rr.uniform(70, 140), rr.choice(GREENS), 0, 0, shadow=False))
    st = "".join(o)
    u = ramp(t, 0.0, 0.85)
    r = 14 + 330 * ei(u)
    act = raindrop(480, 230 + 120 * ei(u), r)
    if t > 0.82:
        v = ramp(t, 0.82, 1.1)
        act += f'<rect width="{W}" height="{H}" fill="#DFF6FF" opacity="{0.9*(1-abs(2*v-1)):.2f}"/>'
    L = [("bg", 1.0, st, True, None), ("act", 1.0, act, False, None)]
    ov = kinetic("RAIN", 480, 470, t, 0.06, 72, "#FFFFFF")
    return dict(layers=L, defs=sky_defs("storm"), cam=(0, 0, 1 + 0.08 * t), overlay=ov)


HIGH = Cam(hz=60, vp=(480, 2600), near=600)


@shot("o_all")
def _(t, D, c):
    """High angle looking down: you small in the middle, everything closing in."""
    cam = HIGH
    st = (f'<rect x="-300" y="-300" width="1560" height="1140" fill="url(#soil_storm)"/>' + ground(cam, "storm", seed=12, n=180) +
          blades(cam, 21, 40, 0.0, 1.0, 120, 260, 1.0, avoid=(330, 630, 0.35)))
    yy = cam.gy(0.6)
    act = contact(480, yy, 30) + g(front("brace", "stand", "surprised", 0, (t % 1.7) < 0.1), 480, yy, 0.2)
    sy = 120 + 120 * eo(t / 1.6)
    act += f'<path d="M330 -300 L330 {sy:.1f}" stroke="#E8E0FF" stroke-width="1.4"/>' + g(spider(t), 330, sy + 20, 0.7, 90)
    for k in range(3):
        ax = 800 + k * 70 - 45 * t
        ay = cam.gy(0.66 + 0.04 * k)
        act += contact(ax, ay, 30) + g(ant(t + k * 0.4, 1.0), ax, ay, 0.55, 0, flip=True)
    rr = random.Random(2)
    rain = "".join(raindrop(rr.uniform(-100, 1060), (rr.uniform(-300, 600) + t * 380) % 840 - 300, rr.uniform(6, 11), 0.75) for _ in range(34))
    L = [("bg", 1.0, st, True, None), ("act", 1.0, act, False, None), ("rain", 1.1, rain, False, None)]
    ov = f'<rect width="{W}" height="{H}" fill="none" stroke="#DFF4FF" stroke-width="80" opacity="0.18" filter="url(#b16)"/>'
    return dict(layers=L, defs=sky_defs("storm"), cam=(0, -10 * t, 1.25 - 0.12 * ease(t / D)), overlay=ov)


@shot("o_head")
def _(t, D, c):
    return single(hook.s5(t))


@shot("o_clock")
def _(t, D, c):
    out = single(hook.s6(t))
    out["clock"] = False
    return out


# ================================================================ SECOND 1: the fall
KDEFS = ep1.KITCHEN_DEFS


def kitchen_far():
    o = [f'<rect x="-400" y="-400" width="1760" height="1340" fill="url(#ksky)"/>']
    far = []
    far.append(f'<rect x="600" y="-80" width="440" height="330" rx="18" fill="#FFE2B0" opacity="0.85"/>')
    far.append(f'<rect x="616" y="-64" width="200" height="300" fill="#FFF4DC" opacity="0.7"/><rect x="826" y="-64" width="200" height="300" fill="#FFF4DC" opacity="0.7"/>')
    for i in range(16):
        for j in range(4):
            far.append(f'<rect x="{-300 + i*90}" y="{60 + j*60}" width="82" height="52" rx="8" fill="#8A6AE8" opacity="0.35"/>')
    far.append(f'<rect x="80" y="40" width="110" height="230" rx="40" fill="#5AD8E8"/><rect x="95" y="20" width="80" height="34" rx="10" fill="#2EA6C8"/>')
    for (x, y, r, col) in [(330, 230, 46, "#FF8A3A"), (400, 220, 52, "#FFB03A"), (370, 180, 44, "#FF6F61")]:
        far.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/>')
    for k in range(5):
        a = math.radians(-120 + k * 18)
        far.append(f'<ellipse cx="{540 + 70*math.cos(a):.0f}" cy="{170 + 90*math.sin(a):.0f}" rx="22" ry="60" fill="#3FD68A" transform="rotate({math.degrees(a)+90:.0f} {540 + 70*math.cos(a):.0f} {170 + 90*math.sin(a):.0f})"/>')
    far.append(f'<path d="M500 190 L580 190 L570 270 L510 270 Z" fill="#FF6FB5"/>')
    o.append(f'<g filter="url(#b8)">{"".join(far)}</g>')
    o.append(poly_beam())
    return "".join(o)


def poly_beam():
    return V.poly([(660, -120), (1040, -120), (620, 900), (160, 900)], "#FFE6B8", 0.07)


def table_persp(edge_y=380, x_edge=760):
    """Table top seen at a low angle: wood planks receding toward the horizon."""
    top = P(f"M-400 {edge_y - 120} L{x_edge - 40} {edge_y - 120} L{x_edge} {edge_y} L-400 {edge_y} Z")
    o = [top("url(#ktop)"), inside(top, "".join(
        f'<path d="M-400 {edge_y - 116 + k*20} L{x_edge - 40 + k*8} {edge_y - 116 + k*20}" stroke="#B8703E" stroke-width="{1 + k*0.4:.1f}" opacity="0.5"/>' for k in range(6)))]
    edge = R(-400, edge_y, x_edge + 400, 50, 10)
    o.append(sh(edge, "#D8905A", "#A85E30", "#FFC890", 1.8))
    o.append(f'<rect x="-400" y="{edge_y - 3}" width="{x_edge + 400}" height="5" fill="#FFD6A8" opacity="0.7"/>')
    return "".join(o)


@shot("f_table")
def _(t, D, c):
    """Wide establishing: you on the vast table, the kitchen towering behind."""
    st_far = kitchen_far()
    tab = table_persp(380, 760)
    rr = random.Random(4)
    props = "".join(crumb(rr.uniform(-100, 500), rr.uniform(285, 360), rr.uniform(6, 14), k) for k in range(6)) + sugar(520, 330, 10) + sugar(300, 300, 8)
    x = 600 + 40 * ramp(t, 0.6, 3.2)
    act = contact(x, 372, 16) + g(front("walk" if 0.6 < t < 3.2 else "stand", "stand", "neutral", 0, (t % 2.6) < 0.1), x, 372, 0.15)
    dust = "".join(f'<circle cx="{(k*97 + 30*math.sin(t*0.4 + k)) % 1000:.1f}" cy="{(k*53 - t*8) % 560:.1f}" r="{1 + (k % 3)*0.6:.1f}" fill="#FFF2D8" opacity="0.6"/>' for k in range(40))
    L = [("far", 0.2, st_far, True, None), ("tab", 0.8, tab + props, True, None), ("act", 0.85, act, False, None), ("dust", 1.0, dust, False, None)]
    return dict(layers=L, defs=KDEFS, cam=(-30 + 25 * ease(t / D), 0, 1.05 + 0.05 * ease(t / D)), overlay="")


@shot("f_slip")
def _(t, D, c):
    """Extreme close-up on your shoes at the very edge: one slides off."""
    st = kitchen_far()
    edge_y = 330
    tab = (sh(R(-400, edge_y, 1100, 90, 16), "#D8905A", "#A85E30", "#FFC890", 4) +
           f'<path d="M-400 {edge_y - 160} L640 {edge_y - 160} L700 {edge_y} L-400 {edge_y} Z" fill="url(#ktop)"/>')
    tab += crumb(220, edge_y - 40, 28, 3)
    u = ramp(t, 0.4, 1.3)
    shoe = A.YOU.shoe
    left = sh(P("M520 330 Q518 290 560 286 Q620 284 640 316 Q640 334 620 334 L536 334 Q520 334 520 330 Z"), shoe[0], shoe[1], "#FFFFFF", 1.6)
    right = g(sh(P("M0 0 Q-2 -40 40 -44 Q100 -46 120 -14 Q120 4 100 4 L16 4 Q0 4 0 0 Z"), shoe[0], shoe[1], "#FFFFFF", 1.6), 610 + 90 * eo(u), 330 + 260 * ei(ramp(t, 0.9, 1.8)), 1, 40 * ramp(t, 0.7, 1.6))
    rx = 600 + 90 * eo(u); ry = 330 + 260 * ei(ramp(t, 0.9, 1.8))
    bt = A.YOU.bottom
    legs = (sh(P(f"M548 -80 L612 -80 L606 300 L556 300 Z"), bt[1], bt[1], bt[2], 1.5) +
            sh(P(f"M640 -80 L704 -80 L{rx + 76:.1f} {ry - 30:.1f} L{rx + 26:.1f} {ry - 30:.1f} Z"), bt[0], bt[1], bt[2], 1.5))
    left = sh(P("M520 330 Q518 290 560 286 Q620 284 640 316 Q640 334 620 334 L536 334 Q520 334 520 330 Z"), shoe[0], shoe[1], "#FFFFFF", 1.6)
    act = legs + left + right
    L = [("far", 0.3, st, True, 4), ("tab", 1.0, tab, True, None), ("act", 1.0, act, False, None)]
    return dict(layers=L, defs=KDEFS, cam=(0, 0, 1.0 + 0.05 * t), overlay="")


@shot("f_scale")
def _(t, D, c):
    """Infographic: your drop vs. the same drop at human size."""
    o = [f'<rect x="-300" y="-300" width="1560" height="1140" fill="url(#ifg)"/>']
    for k in range(14):
        o.append(f'<circle cx="{(k*173) % 960}" cy="{(k*97) % 540}" r="{40 + (k*31) % 60}" fill="#FFFFFF" opacity="0.035"/>')
    st = "".join(o)
    a = []
    # left: table with tiny you
    a.append(A.popin(sh(R(150, 250, 230, 18, 6), "#E8A06A", "#B86A3A", "#FFD0A0") + sh(R(165, 268, 12, 160, 4), "#B86A3A", "#8A4A2A") + sh(R(353, 268, 12, 160, 4), "#B86A3A", "#8A4A2A") +
                     '<rect x="120" y="428" width="300" height="4" rx="2" fill="#8A7AD8"/>', 265, 340, t, 0.1, 0.5))
    a.append(A.popin('<circle cx="372" cy="246" r="3" fill="#2EA6C8"/>' + label(372, 222, "you", "#2EA6C8"), 372, 240, t, 0.5))
    drop_u = ramp(t, 0.8, 2.6)
    if drop_u > 0:
        a.append(f'<path d="M372 250 L372 {250 + 176*drop_u:.1f}" stroke="#2EA6C8" stroke-width="2.5" stroke-dasharray="3 6"/>')
    a.append(chip(265, 470, "75 cm = 220 × your height", t, 1.0, "#FF8A3A"))
    # right: skyscraper
    if t > 1.8:
        k = A.out_back(ramp(t, 1.8, 2.3))
        bld = V.iso_box(690, 428, 40, 40, 300, "#B9A2FF", "#7A5CF0", "#5236C0") + V.iso_windows(690, 428, 40, 40, 300, random.Random(3), "#FFE27A", "#2A1A6A")
        a.append(f'<g transform="translate(690 428) scale(1 {k:.3f}) translate(-690 -428)">{bld}</g>')
        a.append('<rect x="560" y="428" width="270" height="4" rx="2" fill="#8A7AD8"/>')
        a.append(chip(690, 470, "the same fall for a human: 375 m", t, 2.4, "#FF4F9A"))
    a.append(kinetic("YOUR FALL", 265, 120, t, 0.15, 34) + kinetic("AT HUMAN SIZE", 690, 120, t, 1.9, 34))
    L = [("bg", 1.0, st, True, None), ("act", 1.0, "".join(a), False, None)]
    return dict(layers=L, defs=V.lin("ifg", [(0, "#4A20C0"), (1, "#1E0E6A")]), cam=(0, 0, 1.0), overlay="")


FLOOR = Cam(hz=300, vp=(480, -6000), near=640)


@shot("f_land")
def _(t, D, c):
    """Low on the kitchen floor: you float down into frame, land softly, stand up."""
    cam = FLOOR
    st_far = kitchen_far()
    fl = (f'<path d="M-400 {cam.hz} L1360 {cam.hz} L1360 900 L-400 900 Z" fill="url(#kfloor)"/>' +
          "".join(f'<path d="M{480 + (k*140 - 480)*0.25:.0f} {cam.hz} L{480 + (k*140 - 480)*2.4:.0f} 640" stroke="#5A3AC0" stroke-width="2.5" opacity="0.6"/>' for k in range(-6, 14)) +
          "".join(f'<path d="M-400 {cam.gy(d):.1f} L1360 {cam.gy(d):.1f}" stroke="#5A3AC0" stroke-width="{1 + 3*d:.1f}" opacity="0.5"/>' for d in (0.25, 0.45, 0.65, 0.85)))
    leg = sh(R(180, -600, 90, cam.gy(0.5) + 600, 10), "#E8A06A", "#B86A3A", "#FFD0A0", 2) + contact(225, cam.gy(0.5), 70)
    yy = cam.gy(0.55)
    land = 1.0
    if t < land:
        u = t / land
        y = -120 + (yy + 120) * (1 - (1 - u) ** 1.5)
        act = g(front("fall", "fall", "surprised", 0, False), 480, y, 0.34, 8 * math.sin(t * 5))
    else:
        sq = 1 - 0.14 * math.sin(math.pi * min(1, (t - land) / 0.3))
        arms = "brace" if t < land + 0.8 else "thumbs"
        act = contact(480, yy, 50) + g(front(arms, "stand", "surprised" if t < land + 0.8 else "happy", 0, False), 480, yy, 0.34) if True else ""
        act = contact(480, yy, 50) + f'<g transform="translate(480 {yy:.1f}) scale({0.34/sq**0.5:.4f} {0.34*sq:.4f})">{front(arms, "stand", "surprised" if t < land + 0.8 else "happy")}</g>'
        u = (t - land) / 0.7
        if u < 1:
            for k in range(9):
                an = math.pi * k / 8
                act += f'<circle cx="{480 + math.cos(an)*70*u:.1f}" cy="{yy - math.sin(an)*20*u:.1f}" r="{6*(1-u):.1f}" fill="#C8B8FF" opacity="{0.9*(1-u):.2f}"/>'
    L = [("far", 0.2, st_far, True, 8), ("floor", 0.7, fl + leg, True, None), ("act", 0.8, act, False, None)]
    return dict(layers=L, defs=KDEFS, cam=(0, 0, 1.0 + 0.04 * t), overlay="")


@shot("f_cube")
def _(t, D, c):
    """Square-cube law, done as a clean diagram: a cube splits, surface vs weight counters."""
    st = f'<rect x="-300" y="-300" width="1560" height="1140" fill="url(#cbg2)"/>' + "".join(
        f'<path d="M{k*40} 0 L{k*40 - 300} 540" stroke="#FFFFFF" stroke-width="1" opacity="0.04"/>' for k in range(-10, 34))
    c1 = c[1] if len(c) > 1 else 4.6
    a = []
    s = 150 * (1 - 0.8 * ease(ramp(t, c1 + 0.3, c1 + 2.6)))
    a.append(f'<ellipse cx="250" cy="404" rx="{s*1.1:.1f}" ry="{s*0.28:.1f}" fill="#0A0420" opacity="0.3"/>' + V.iso_box(250, 400, s, s, s, "#9AF0FF", "#2EA6C8", "#1E7A9A"))
    a.append(chip(250, 110, "shrink 500×", t, c1 + 0.1, "#FF4F9A"))
    for i, (name, val, col, frac, t0) in enumerate([("Surface", "÷ 250,000", "#46E0D0", 0.45, 0.6), ("Weight", "÷ 125,000,000", "#FFD23A", 0.92, 1.2)]):
        y = 210 + i * 130
        a.append(kinetic(name, 600, y, t, t0, 30))
        if t > t0:
            bar = R(500, y + 20, 380, 30, 15)
            sk = ease(ramp(t, c1 + 0.8 + i * 1.6, c1 + 3.0 + i * 1.6))
            wd = 380 * (1 - frac * sk)
            a.append(f'<rect x="500" y="{y + 20}" width="380" height="30" rx="15" fill="#2A0E80"/>' + inside(bar, f'<rect x="500" y="{y + 20}" width="{wd:.1f}" height="30" rx="15" fill="{col}"/><rect x="500" y="{y + 20}" width="{wd:.1f}" height="9" fill="#FFFFFF" opacity="0.35"/>'))
            a.append(chip(820, y - 8, val, t, c1 + 1.6 + i * 1.6, "#1A0A4A", col))
    L = [("bg", 1.0, st, True, None), ("act", 1.0, "".join(a), False, None)]
    return dict(layers=L, defs=V.lin("cbg2", [(0, "#4A20C0"), (1, "#22107A")]), cam=(0, 0, 1.0), overlay="")


@shot("f_drift")
def _(t, D, c):
    """Tracking alongside you as you drift down past the table leg, air streaming up."""
    st = kitchen_far()
    scroll = 160 * t
    leg = f'<g transform="translate(0 {-scroll*0.9:.1f})">' + "".join(sh(R(250, -600 + k * 800, 80, 820, 10), "#E8A06A", "#B86A3A", "#FFD0A0", 2) for k in range(3)) + '</g>'
    chair = f'<g transform="translate(0 {-scroll*1.5:.1f})" filter="url(#b8)">' + "".join(sh(R(820, -600 + k * 900, 60, 920, 10), "#FF8AC8", "#C9408A", "#FFC0E0", 2) for k in range(3)) + '</g>'
    rr = random.Random(5)
    streaks = "".join(f'<path d="M{480 + rr.uniform(-90, 90):.1f} {(rr.uniform(0, 600) - t * 420) % 600:.1f} l0 -30" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" opacity="0.45"/>' for _ in range(14))
    you = g(front("fall", "fall", "happy", 0, (t % 2.2) < 0.1), 480, 330 + 6 * math.sin(t * 1.4), 0.36, 14 * math.sin(t * 1.3))
    ov = chip(480, 470, "about 9 km/h: a slow jog", t, 0.8, "#2A1470", size=18)
    L = [("far", 0.15, st, True, 8), ("leg", 1.0, leg, False, None), ("act", 1.0, streaks + you, False, None), ("fg", 1.0, chair, False, None)]
    return dict(layers=L, defs=KDEFS, cam=(0, 0, 1.0), overlay=ov)


@shot("f_antfall")
def _(t, D, c):
    """Eye level in the garden: an ant tumbles off a leaf, lands, and walks away."""
    cam = Cam(hz=320, vp=(480, -30000), near=600)
    st_sky = sky("day", (760, 120))
    st = forest(cam, 41) + ground(cam, "day", seed=9) + blades(cam, 33, 34, 0.02, 0.4, 260, 520, avoid=(260, 760, 0.25))
    lf = leaf(330, 120, 380, 60, 8, ("#46E08A", "#1EA864", "#C2FFD8")) + sh(S("M140 -400 Q170 0 150 140", 16), "#6A4A8A", "#4A2A6A")
    yy = cam.gy(0.55)
    u = t - 0.4
    if u < 0:
        a = g(ant(t, 0.0), 470, 112, 0.7)
    else:
        fall_t = 0.85
        if u < fall_t:
            y = 112 + (yy - 112) * (u / fall_t) ** 2
            a = g(ant(t, 0.3), 470 + 30 * u, y, 0.7, 260 * u)
        else:
            w = u - fall_t
            bounce = -14 * abs(math.sin(min(w, 0.5) / 0.5 * math.pi)) * (1 - min(w, 0.5) / 0.5)
            ax = 495 + 95 * max(0, w - 0.6)
            a = contact(ax, yy, 30) + g(ant(t, 1.0 if w > 0.6 else 0.0), ax, yy + bounce, 0.7)
    L = [("sky", 0.1, st_sky, True, None), ("gnd", 0.6, st, True, None), ("leaf", 0.8, lf, True, None), ("act", 0.8, a, False, None),
         ("fg", 1.3, blades(Cam(hz=320, vp=(480, -30000), near=700), 34, 6, 0.85, 1.0, 140, 240, 1.0, avoid=(250, 710, 0.0)), True, 8)]
    return dict(layers=L, defs=sky_defs("day"), cam=(20 * ease(t / D), 0, 1.0), overlay="")
