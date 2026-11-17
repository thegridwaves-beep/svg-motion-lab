"""Minute 15 (rain), minute 20 (no one hears), minute 25 (locals), the truth, the ending."""
import math, random, sys
sys.path.insert(0, "/home/claude/ant"); sys.path.insert(0, "/home/claude/ant2")
from engine import shot, W, H
import vivid as V
from kit import inside, P, S, E, C, R, U, g, text
import assets as A
from assets import drop, ant, glow, ball, sh, GREENS, pebble, sparkle, raindrop, crumb, spider, leaf, label, mosquito, neuron, bird_shadow, splash
from kit2 import *
import kit2, rig
from shots_a import eo, ei
from shots_b import GAR, LOW, garden_layers, fg, leaf_floor, stage_floor, STG_DEFS
import ep1

ease = V.ease
ramp = A.ramp
DIAG = V.lin("dg", [(0, "#3A1AA8"), (1, "#14084A")])
DIAG_BG = f'<rect x="-300" y="-300" width="1560" height="1140" fill="url(#dg)"/>' + "".join(
    f'<circle cx="{(k*173) % 960}" cy="{(k*97) % 540}" r="{40 + (k*31) % 60}" fill="#FFFFFF" opacity="0.035"/>' for k in range(14))


def rainfield(t, n=50, seed=12, y0=-300, y1=470, rmin=8, rmax=15, avoid=None, spd=(330, 420)):
    rr = random.Random(seed)
    o = []
    for k in range(n):
        x = rr.uniform(-100, 1060)
        sp = rr.uniform(*spd)
        ph = rr.uniform(0, 3)
        period = (y1 - y0) / sp
        u = ((t + ph) % period) / period
        y = y0 + u * (y1 - y0)
        r = rr.uniform(rmin, rmax)
        if avoid and abs(x - avoid) < 30:
            continue
        o.append(raindrop(x, y, r, 0.9))
        if u < 0.12 and t > period * 0.5:
            o.append(splash(x, y1, r * 1.6, u / 0.12))
    return "".join(o)


# ================================================================ MINUTE 15: rain
@shot("r_dark")
def _(t, D, c):
    cam = GAR
    L = garden_layers(cam, "gold", 140, sun=(760, 160))
    dk = ease(ramp(t, 0.0, 1.6))
    clouds = "".join(f'<ellipse cx="{x + 40*t:.1f}" cy="{-140 + 160*dk + dy:.1f}" rx="{rx}" ry="{rx*0.45:.0f}" fill="#1A1440"/>' for x, dy, rx in
                     [(100, 0, 260), (400, -30, 300), (700, 10, 280), (980, -20, 240), (250, 60, 200), (820, 70, 220)])
    yy = cam.gy(0.55)
    act = contact(480, yy, 24) + g(front("stand", "stand", "surprised" if t > 0.6 else "neutral", -8 * ramp(t, 0.5, 1.0), False), 480, yy, 0.17)
    L.append(("act", 0.75, act, False, None))
    L.append(("clouds", 0.3, f'<g filter="url(#b16)" opacity="{0.9*dk:.2f}">{clouds}</g>', False, None))
    L.append(fg(cam, 141))
    ov = f'<rect width="{W}" height="{H}" fill="#14123A" opacity="{0.45*dk:.2f}"/>'
    return dict(layers=L, defs=sky_defs("gold"), cam=(0, 60, 1.6 - 0.2 * ease(t / D)), overlay=ov)


@shot("r_drop")
def _(t, D, c):
    """Side by side: you and a single raindrop, with its weight and speed."""
    cam = GAR
    L = garden_layers(cam, "storm", 150, sun=None)
    yy = cam.gy(0.6)
    fall = (t * 0.9) % 1.0
    act = contact(400, yy, 26) + g(front("brace", "stand", "surprised", 0, (t % 2.4) < 0.1), 400, yy, 0.2)
    dy = yy - 80
    act += "".join(f'<circle cx="{580 + 6*math.sin(k*1.7):.1f}" cy="{dy - 70 - k*26 - ((t*90) % 26):.1f}" r="{5 - k*0.8:.1f}" fill="#BFF0FF" opacity="{0.55 - k*0.1:.2f}"/>' for k in range(5)) + raindrop(580, dy, 46)
    L.append(("act", 0.75, act, False, None))
    ov = chip(580, 150, "up to 100× your weight", t, 0.6, "#2EA6C8", size=20) + chip(580, 200, "falling at 30 km/h", t, 2.4, "#FF4F9A", size=20)
    return dict(layers=L, defs=sky_defs("storm"), cam=(30, 60, 1.8), overlay=ov + f'<rect width="{W}" height="{H}" fill="#14123A" opacity="0.25"/>')


@shot("r_truck")
def _(t, D, c):
    """Low angle in the downpour: drops slam into the ground all around you."""
    cam = LOW
    L = [("sky", 0.1, sky("storm", None), True, None), ("forest", 0.25, forest(cam, 161), True, 2),
         ("gnd", 0.6, ground(cam, "storm", seed=160) + blades(cam, 162, 24, 0.03, 0.5, 300, 700, avoid=(330, 640, 0.2)), True, None)]
    yy = cam.gy(0.55)
    act = contact(480, yy, 60) + g(front("head", "crouch", "surprised", 0, False), 480, yy, 0.4)
    act += rainfield(t, 70, 13, -400, yy + 20, 10, 22, avoid=480, spd=(500, 650))
    L.append(("act", 0.85, act, False, None))
    L.append(("fg", 1.4, rainfield(t + 0.3, 8, 14, -500, 700, 30, 50), False, 4))
    return dict(layers=L, defs=sky_defs("storm"), cam=(0, 0, 1.0 + 0.06 * t), overlay=f'<rect width="{W}" height="{H}" fill="#14123A" opacity="0.2"/>')


@shot("r_mosq")
def _(t, D, c):
    """Tracking down with a falling drop: a mosquito rides it, then slips off and flies away."""
    st = sky("storm", None)
    scroll = 380 * t
    bladesv = f'<g filter="url(#b16)" opacity="0.8">{blades(GAR, 180, 30, 0.0, 0.5, 260, 520)}</g>'
    d = raindrop(480, 270, 60)
    off = ramp(t, 2.6, 3.2)
    mx = 470 + 220 * ease(ramp(t, 2.8, 4.4)) + 8 * math.sin(t * 12) * off
    my = 200 - 120 * ease(ramp(t, 2.8, 4.4)) + 30 * off
    act = d + g(mosquito(t), mx, my, 2.0, -20 * off)
    streaks = "".join(raindrop(rx, (ry - t*700) % 700 - 80, rr_, 0.7) for rx, ry, rr_ in
                      [(150, 0, 14), (300, 200, 10), (640, 100, 12), (820, 400, 16), (380, 500, 9), (720, 300, 11)])
    L = [("sky", 0.0, st, True, None), ("bl", 0.3, bladesv, True, None), ("rain", 0.6, f'<g filter="url(#b4)">{streaks}</g>', False, None), ("act", 1.0, act, False, None)]
    ov = chip(480, 470, "too light to be hurt", t, 1.2, "#2EA6C8", size=18)
    return dict(layers=L, defs=sky_defs("storm"), cam=(0, 0, 1.0), overlay=ov)


HIGH2 = Cam(hz=40, vp=(480, 2600), near=600)


@shot("r_puddle")
def _(t, D, c):
    """High angle: a puddle spreads at your feet, ripples everywhere."""
    cam = HIGH2
    st = f'<rect x="-300" y="-300" width="1560" height="1140" fill="url(#soil_storm)"/>' + ground(cam, "storm", seed=170, n=150) + blades(cam, 171, 30, 0.0, 1.0, 120, 260, 1.0, avoid=(300, 700, 0.3))
    pud = E(520, 330, 300, 120)
    rip = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{((t*0.9 + k/3) % 1)*80:.1f}" ry="{((t*0.9 + k/3) % 1)*30:.1f}" fill="none" stroke="#DFF4FF" stroke-width="2" opacity="{1 - ((t*0.9 + k/3) % 1):.2f}"/>'
                  for (x, y) in [(420, 300), (600, 360), (520, 280), (680, 320)] for k in range(3))
    puddle = sh(pud, "#4A6AC8", "#2A3A90", "#9AC0FF", 3) + inside(pud, rip)
    yy = 430
    step = ease(ramp(t, 0.8, 1.6))
    act = contact(330 - 30 * step, yy, 24) + g(front("brace", "stand", "surprised", 0, False), 330 - 30 * step, yy, 0.24)
    L = [("bg", 1.0, st, True, None), ("pud", 1.0, puddle, False, None), ("act", 1.0, act, False, None),
         ("rain", 1.1, rainfield(t, 30, 15, -300, 600, 7, 12), False, None)]
    return dict(layers=L, defs=sky_defs("storm"), cam=(0, 0, 1.12 - 0.08 * ease(t / D)), overlay=f'<rect width="{W}" height="{H}" fill="#14123A" opacity="0.2"/>')


# ================================================================ MINUTE 20: no one can hear you
def rings(cx, cy, t, n=5, spd=0.9, rmax=260, col="#FFFFFF"):
    o = ""
    for k in range(n):
        u = ((t * spd + k / n) % 1)
        r = 20 + u * rmax
        o += f'<path d="M{cx + r*0.3:.1f} {cy - r*0.8:.1f} A{r:.1f} {r:.1f} 0 0 1 {cx + r*0.3:.1f} {cy + r*0.8:.1f}" stroke="{col}" stroke-width="4" fill="none" stroke-linecap="round" opacity="{0.8*(1-u):.2f}"/>'
    return o


@shot("v_scream")
def _(t, D, c):
    bg = sky("storm", None) + f'<g filter="url(#b16)">{blades(GAR, 180, 30, 0.0, 0.5, 260, 520)}</g>'
    act = g(front("cheer", "stand", "surprised", -4, False), 430, 300 + 3.2 * 444, 3.2) + rings(560, 330, t, 6, 1.1, 380)
    drips = "".join(f'<circle cx="{300 + k*60}" cy="{(k*70 + t*200) % 540:.1f}" r="5" fill="#BFF0FF" opacity="0.7"/>' for k in range(8))
    L = [("bg", 0.3, bg, True, None), ("act", 1.0, act + drips, False, None)]
    return dict(layers=L, defs=sky_defs("storm"), cam=(0, 0, 1.0 + 0.05 * t), overlay=f'<rect width="{W}" height="{H}" fill="#14123A" opacity="0.15"/>')


@shot("v_ultra")
def _(t, D, c):
    a = []
    x0, x1 = 120, 840
    lg = lambda hz: x0 + (x1 - x0) * (math.log10(hz) - 1) / (math.log10(200000) - 1)
    a.append(A.popin(f'<rect x="{x0}" y="260" width="{x1 - x0}" height="20" rx="10" fill="#2A1478"/>', 480, 270, t, 0.1))
    hb = ease(ramp(t, 0.4, 1.4))
    a.append(f'<rect x="{lg(20):.1f}" y="260" width="{(lg(20000) - lg(20))*hb:.1f}" height="20" rx="10" fill="#46E0D0"/>')
    a.append(kinetic("what humans can hear", (lg(20) + lg(20000)) / 2, 230, t, 1.0, 26, "#46E0D0"))
    for hz, s_ in [(20, "20 Hz"), (1000, "1 kHz"), (20000, "20 kHz"), (100000, "100 kHz")]:
        a.append(A.popin(text(lg(hz), 320, s_, 18, "#C8B8FF", 600, "middle", "Inter") + f'<rect x="{lg(hz)-1:.1f}" y="284" width="2" height="12" fill="#C8B8FF"/>', lg(hz), 310, t, 0.5))
    # your normal voice, then sliding up and out of range
    move = ease(ramp(t, 2.6, 5.0))
    vx = lg(150) + (lg(60000) - lg(150)) * move
    a.append(A.popin(f'<circle cx="{vx:.1f}" cy="270" r="18" fill="#FF4F9A"/><circle cx="{vx:.1f}" cy="270" r="30" fill="#FF4F9A" opacity="0.25"/>', vx, 270, t, 1.8))
    a.append(A.popin(label(vx, 190 if move < 0.5 else 360, "your voice" if move < 0.3 else "your voice, 500× higher", "#FF4F9A", size=18), vx, 190, t, 2.0))
    if move > 0.7:
        a.append(A.popin(f'<path d="M{lg(20000) + 10:.1f} 240 L{lg(20000) + 10:.1f} 300" stroke="#FFD23A" stroke-width="3" stroke-dasharray="5 5"/>', lg(20000), 270, t, 4.6))
    L = [("bg", 1.0, DIAG_BG, True, None), ("act", 1.0, "".join(a), False, None)]
    return dict(layers=L, defs=DIAG, cam=(0, 0, 1.0), overlay="")


@shot("v_ultra2")
def _(t, D, c):
    """Low angle: a giant shoe lifts and walks away; you scream at it, unheard."""
    cam = LOW
    L = [("sky", 0.1, sky("storm", None), True, None), ("forest", 0.25, forest(cam, 191), True, 2),
         ("gnd", 0.6, ground(cam, "storm", seed=190) + blades(cam, 192, 18, 0.03, 0.5, 300, 700, avoid=(250, 900, 0.15)), True, None)]
    yy = cam.gy(0.55)
    lift = ease(ramp(t, 0.3, 1.6))
    shoe = P("M540 560 Q500 470 610 440 L770 405 Q830 330 930 300 L1300 270 L1320 560 Z")
    s_ = sh(shoe, "#F4F0FF", "#B9B0DA", "#FFFFFF", 4) + inside(shoe, '<rect x="480" y="515" width="900" height="50" fill="#FF4F9A"/><rect x="480" y="500" width="900" height="16" fill="#FFFFFF"/>'
        '<path d="M560 470 Q700 440 800 470 L780 500 Q680 480 570 500 Z" fill="#DCD4F4"/>' + "".join(f'<ellipse cx="{860 + k*44}" cy="{352 - k*6}" rx="14" ry="6" fill="#5A4A9A"/>' for k in range(5)))
    s_ = f'<g transform="translate({120*lift:.1f} {-420*lift:.1f}) rotate({-12*lift:.1f} 800 560)">{s_}</g>'
    act = contact(380, yy, 50) + g(front("cheer", "stand", "surprised", 0, False), 380, yy, 0.38) + rings(420, yy - 150, t, 5, 1.2, 200)
    L.append(("act", 0.85, act, False, None))
    L.append(("shoe", 1.0, s_, False, None))
    ov = kinetic("ULTRASOUND", 480, 110, t, 0.1, 64)
    return dict(layers=L, defs=sky_defs("storm"), cam=(0, 0, 1.0 + 0.04 * t), overlay=ov)


@shot("v_blur")
def _(t, D, c):
    """Your point of view: the giant is a blur."""
    bl = 30 if t > 0.6 else 16
    face = (f'<rect x="-300" y="-300" width="1560" height="1140" fill="#7A6AA8"/><circle cx="480" cy="250" r="260" fill="#E8B08A"/><circle cx="390" cy="210" r="34" fill="#2A1A3A"/><circle cx="570" cy="210" r="34" fill="#2A1A3A"/>'
            f'<path d="M340 40 Q480 -60 640 40 L660 110 Q480 30 320 110 Z" fill="#3A2A5A"/><ellipse cx="480" cy="360" rx="80" ry="22" fill="#C8605A"/><rect x="280" y="470" width="400" height="220" rx="90" fill="#FF6F61"/>')
    L = [("face", 1.0, f'<g filter="url(#b{bl})">{face}</g>', False, None)]
    ov = f'<rect width="{W}" height="{H}" fill="url(#eyevig)"/>'
    return dict(layers=L, defs='<radialGradient id="eyevig" cx="0.5" cy="0.5" r="0.62"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#0A0420" stop-opacity="0.85"/></radialGradient>',
                cam=(0, 0, 1.0 + 0.05 * t), overlay=ov)


@shot("v_pupil")
def _(t, D, c):
    a = []
    hair = R(120, 200, 720, 70, 35)
    a.append(A.popin(sh(hair, "#7A4A2A", "#4A2A1A", "#C8885A", 1.2) + inside(hair, "".join(f'<rect x="{120 + k*36}" y="200" width="3" height="70" fill="#5A3A20" opacity="0.4" transform="rotate(20 {120 + k*36} 235)"/>' for k in range(22))), 480, 235, t, 0.2))
    a.append(chip(480, 160, "a human hair: 70 µm", t, 0.6, "#C8885A", "#2A1470", 18))
    if t > 1.6:
        a.append(glow(480, 235, 10, "#FFFFFF", 0.9, 2) + A.popin('<circle cx="480" cy="235" r="5" fill="#FFFFFF"/>', 480, 235, t, 1.6))
        a.append(chip(480, 320, "your pupil: 8 µm", t, 2.0, "#FFFFFF", "#2A1470", 18))
    if t > 3.6:
        u = ease(ramp(t, 3.6, 4.6))
        for k in range(7):
            yk = 380 + k * 14
            a.append(f'<path d="M140 {yk} L{140 + 300*u:.1f} {yk}" stroke="#FFE27A" stroke-width="3" opacity="0.8"/>')
            a.append(f'<path d="M440 440 L{440 + 380*u:.1f} {440 + (k - 3) * 40 * u:.1f}" stroke="#FFE27A" stroke-width="3" opacity="{0.6*u:.2f}"/>')
        a.append(f'<rect x="436" y="420" width="8" height="40" rx="4" fill="#FFFFFF"/>')
        a.append(chip(700, 510, "light spreads out instead of focusing", t, 4.4, "#FF4F9A", size=16))
    L = [("bg", 1.0, DIAG_BG, True, None), ("act", 1.0, "".join(a), False, None)]
    return dict(layers=L, defs=DIAG, cam=(0, 0, 1.0), overlay="")


# ================================================================ MINUTE 25: the locals
@shot("l_notice")
def _(t, D, c):
    bg = sky("gold", None) + f'<g filter="url(#b16)">{blades(GAR, 200, 30, 0.0, 0.5, 260, 520)}</g>'
    widen = t > 0.7
    act = g(front("brace", "stand", "surprised" if widen else "neutral", 0, False), 480, 300 + 3.0 * 444, 3.0)
    sx = -700 + 2200 * ease(ramp(t, 0.5, 1.8))
    shade = f'<ellipse cx="{sx:.1f}" cy="270" rx="520" ry="420" fill="#0A0420" opacity="0.55" filter="url(#b30)"/>'
    L = [("bg", 0.3, bg, True, None), ("act", 1.0, act, False, None), ("shade", 1.0, shade, False, None)]
    return dict(layers=L, defs=sky_defs("gold"), cam=(0, 0, 1.0 + 0.08 * ease(t / D)), overlay="")


@shot("l_spider")
def _(t, D, c):
    cam = LOW
    L = [("sky", 0.1, sky("gold", (700, 120)), True, None), ("forest", 0.25, forest(cam, 211), True, 2),
         ("gnd", 0.6, ground(cam, "gold", seed=210) + blades(cam, 212, 20, 0.03, 0.5, 300, 700, avoid=(250, 750, 0.2)), True, None)]
    yy = cam.gy(0.6)
    sy = -200 + 480 * eo(ramp(t, 0.0, 1.2)) + 6 * math.sin(t * 3)
    act = contact(380, yy, 44) + g(front("brace", "stand", "surprised", 0, False), 380, yy, 0.36)
    act += f'<path d="M620 -400 L620 {sy - 60:.1f}" stroke="#E8E0FF" stroke-width="2"/>' + g(spider(t), 620, sy, 2.4, 0)
    L.append(("act", 0.85, act, False, None))
    return dict(layers=L, defs=sky_defs("gold"), cam=(0, 0, 1.0 + 0.08 * t), overlay=kinetic("lunch", 760, 470, t, 0.6, 44))


@shot("l_bird")
def _(t, D, c):
    cam = HIGH2
    st = f'<rect x="-300" y="-300" width="1560" height="1140" fill="url(#soil_gold)"/>' + ground(cam, "gold", seed=220, n=150) + blades(cam, 221, 30, 0.0, 1.0, 120, 260, 1.0, avoid=(330, 630, 0.35))
    yy = cam.gy(0.6)
    act = contact(480, yy, 26) + g(front("head", "crouch", "surprised", 0, False), 480, yy, 0.22)
    bx = -500 + 1900 * ease(ramp(t, 0.0, 1.7))
    sh_ = g(bird_shadow(0.45), bx, 300, 4.2, 10)
    L = [("bg", 1.0, st, True, None), ("act", 1.0, act, False, None), ("shadow", 1.0, f'<g filter="url(#b8)">{sh_}</g>', False, None)]
    return dict(layers=L, defs=sky_defs("gold"), cam=(0, 0, 1.1), overlay=kinetic("snack", 480, 110, t, 0.5, 44))


@shot("l_ants")
def _(t, D, c):
    """A column of ants marching out of the distance toward you."""
    cam = Cam(hz=300, vp=(480, -30000), near=600)
    L = [("sky", 0.1, sky("gold", (760, 150)), True, None), ("forest", 0.25, forest(cam, 231), True, None),
         ("gnd", 0.6, ground(cam, "gold", seed=230) + blades(cam, 232, 30, 0.02, 0.45, 260, 520, avoid=(420, 900, 0.1)), True, None)]
    ants = []
    for k in range(7):
        d = 0.05 + ((k * 0.105 + t * 0.045) % 0.73)
        x = cam.gx(0.32 - 0.2 * d, d)
        y = cam.gy(d)
        sc = cam.scale(d) * 0.5
        ants.append((d, contact(x, y, 40 * sc) + g(ant(t + k * 0.37, 1.0), x, y, sc, 0, flip=True)))
    ants.sort()
    yy = cam.gy(0.62)
    you = (0.62, contact(290, yy, 26) + g(front("brace", "stand", "surprised", 0, (t % 2) < 0.1), 290, yy, 0.22, 0, flip=True))
    items = sorted(ants + [you])
    L.append(("act", 0.75, "".join(s for _, s in items), False, None))
    L.append(fg(cam, 233))
    ov = kinetic("they never come alone", 480, 110, t, 1.8, 38)
    return dict(layers=L, defs=sky_defs("gold"), cam=(20, 40, 1.3), overlay=ov)


# ================================================================ THE TRUTH
def big_clock(val, x=480, y=230, s=1.0, frozen=False):
    col = "#8A8AB0" if frozen else "#FF4F9A"
    return (f'<g transform="translate({x} {y}) scale({s:.3f})"><rect x="-220" y="-64" width="440" height="128" rx="32" fill="#140A3A" opacity="0.9"/>'
            f'<rect x="-220" y="-64" width="440" height="128" rx="32" fill="none" stroke="{col}" stroke-width="4"/>' + text(0, 28, val, 80, "#FFFFFF", 700, "middle") + '</g>')


@shot("t_stop")
def _(t, D, c):
    bg = DIAG_BG
    a = [big_clock("00:25:41", 480, 220, 1.0, frozen=t > 0.3)]
    icons = [(260, 410, "cold", 1.3), (480, 420, "water", 2.0), (700, 410, "bite", 2.7)]
    for x, y, kind, t0 in icons:
        if kind == "cold":
            ic = ball(x, y, 40, "#9AE8FF", "#3A8CC8", "#EFFFFF") + "".join(f'<path d="M{x} {y} L{x + 26*math.cos(an):.1f} {y + 26*math.sin(an):.1f}" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>' for an in [k * math.pi / 3 for k in range(6)])
        elif kind == "water":
            ic = raindrop(x, y + 16, 26)
        else:
            ic = g(spider(t), x, y, 0.6)
        a.append(A.popin(ic, x, y, t, t0))
        a.append(A.popin(text(x, y + 80, "?", 40, "#FFD23A", 700, "middle"), x, y + 66, t, t0 + 0.2))
    L = [("bg", 1.0, bg, True, None), ("act", 1.0, "".join(a), False, None)]
    return dict(layers=L, defs=DIAG, cam=(0, 0, 1.0 + 0.03 * t), overlay="", clock=False)


@shot("t_none")
def _(t, D, c):
    u = ease(ramp(t, 0.6, 2.4))
    secs = int((25 * 60 + 41) * (1 - u))
    val = f"00:{secs // 60:02d}:{secs % 60:02d}"
    a = [big_clock(val, 480, 240, 1.0 + 0.1 * math.sin(t * 9) * (0 < u < 1))]
    fade = 1 - ramp(t, 0.0, 0.5)
    for x, y in [(260, 410), (480, 420), (700, 410)]:
        a.append(f'<g opacity="{fade:.2f}"><circle cx="{x}" cy="{y}" r="40" fill="#FFFFFF" opacity="0.15"/></g>')
    a.append(kinetic("we cheated", 480, 430, t, 1.0, 44, "#FFD23A"))
    L = [("bg", 1.0, DIAG_BG, True, None), ("act", 1.0, "".join(a), False, None)]
    return dict(layers=L, defs=DIAG, cam=(0, 0, 1.0), overlay="", clock=False)


def silhouette(kind, x, y, s):
    if kind == "mouse":
        return g('<ellipse cx="0" cy="-20" rx="40" ry="22" fill="#FFFFFF"/><circle cx="34" cy="-30" r="14" fill="#FFFFFF"/><circle cx="28" cy="-46" r="8" fill="#FFFFFF"/><path d="M-38 -16 Q-70 -10 -80 10" stroke="#FFFFFF" stroke-width="4" fill="none"/>', x, y, s)
    if kind == "human":
        return g('<circle cx="0" cy="-150" r="22" fill="#FFFFFF"/><rect x="-26" y="-124" width="52" height="80" rx="20" fill="#FFFFFF"/><rect x="-22" y="-50" width="18" height="50" rx="8" fill="#FFFFFF"/><rect x="4" y="-50" width="18" height="50" rx="8" fill="#FFFFFF"/>', x, y, s)
    return g('<path d="M-150 -40 Q-90 -100 20 -90 Q110 -84 140 -40 Q150 -10 110 0 Q20 10 -90 -10 Q-120 -14 -140 -26 Z" fill="#FFFFFF"/>'
             '<path d="M-140 -30 L-190 -70 Q-180 -40 -200 -10 Z" fill="#FFFFFF"/><path d="M10 -6 Q30 20 0 34 Q-6 14 -10 -8 Z" fill="#FFFFFF"/>', x, y, s)


def cell_disc(cx, cy, r=58, n=25):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#1A0A5A" stroke="#FFFFFF" stroke-width="3"/>' +
            inside(C(cx, cy, r - 2), "".join(f'<circle cx="{cx - 60 + (k % 5)*30 + (15 if (k//5) % 2 else 0)}" cy="{cy - 60 + (k//5)*30}" r="13" fill="#FF7AC8" opacity="0.85"/><circle cx="{cx - 60 + (k % 5)*30 + (15 if (k//5) % 2 else 0)}" cy="{cy - 60 + (k//5)*30}" r="4.5" fill="#8A2A8A"/>' for k in range(n))))


@shot("t_cells")
def _(t, D, c):
    c1 = c[1] if len(c) > 1 else 6.3
    a = []
    out = ramp(t, c1 - 0.4, c1)
    for i, (kind, x, s_) in enumerate([("mouse", 190, 1.3), ("human", 480, 1.0), ("whale", 770, 0.9)]):
        a.append(f'<g opacity="{1 - out:.2f}">' + A.popin(f'<g opacity="0.85">{silhouette(kind, x, 260, s_)}</g>', x, 220, t, 0.4 + i * 0.7) +
                 A.popin(cell_disc(x, 380), x, 380, t, 2.4 + i * 0.4) + '</g>')
    if out < 1:
        a.append(f'<g opacity="{1 - out:.2f}">' + chip(480, 480, "same size cells", t, 4.4, "#FF4F9A") + '</g>')
    if t > c1:
        k = A.out_back(ramp(t, c1, c1 + 0.5))
        a.append(f'<g transform="translate(480 300) scale({k:.3f})">' + g(front("stand", "stand", "neutral"), 0, 120, 0.35) +
                 f'<circle cx="160" cy="0" r="70" fill="#1A0A5A" stroke="#FFFFFF" stroke-width="3"/>' +
                 "".join(f'<circle cx="{140 + (k2 % 2)*40}" cy="{-20 + (k2 // 2)*40}" r="16" fill="#FF7AC8"/>' for k2 in range(2)) + '</g>')
        a.append(chip(480, 470, "far fewer of them", t, c1 + 0.6, "#2EA6C8"))
    L = [("bg", 1.0, DIAG_BG, True, None), ("act", 1.0, "".join(a), False, None)]
    return dict(layers=L, defs=DIAG, cam=(0, 0, 1.0), overlay="", clock=False)


@shot("t_brain")
def _(t, D, c):
    rr = random.Random(7)
    thin = ease(ramp(t, 3.4, 5.4))
    a = [f'<ellipse cx="480" cy="290" rx="320" ry="210" fill="#2A1478" opacity="0.6"/>']
    for k in range(80):
        x, y = 480 + rr.uniform(-290, 290), 290 + rr.uniform(-180, 180)
        if ((x - 480) / 310) ** 2 + ((y - 290) / 200) ** 2 > 1:
            continue
        keep = k % 11 == 0
        op = (1.0 if keep else 1 - thin) * min(1, max(0, (t - 0.2 - k * 0.01) / 0.3))
        if op > 0.02:
            a.append(f'<g opacity="{op:.2f}">{neuron(x, y, 9, k)}</g>')
    a.append(f'<g opacity="{1 - thin:.2f}">' + label(480, 56, "86,000,000,000 neurons", "#FF7AC8", "#14084A", 20) + '</g>')
    a.append(f'<g opacity="{thin:.2f}">' + label(480, 56, "fewer than 1,000", "#FFD23A", "#14084A", 20) + '</g>')
    L = [("bg", 1.0, DIAG_BG, True, None), ("act", 1.0, "".join(a), False, None)]
    return dict(layers=L, defs=DIAG, cam=(0, 0, 1.0), overlay="", clock=False)


@shot("t_antbrain")
def _(t, D, c):
    a = [g(ant(t, 0.0), 470, 420, 3.6)]
    pulse = 0.5 + 0.5 * math.sin(t * 5)
    a.append(glow(470 + 38 * 3.6, 420 - 37 * 3.6, 30 + 8 * pulse, "#FF7AC8", 0.85, 8))
    for k in range(14):
        an = k * 0.45 + t
        a.append(f'<circle cx="{470 + 38*3.6 + 18*math.cos(an):.1f}" cy="{420 - 37*3.6 + 14*math.sin(an*1.3):.1f}" r="2" fill="#FFFFFF" opacity="0.8"/>')
    a.append(chip(480, 90, "an ant: about 250,000 neurons", t, 0.3, "#FF7AC8", "#14084A", 20))
    L = [("bg", 1.0, DIAG_BG, True, None), ("act", 1.0, "".join(a), False, None)]
    return dict(layers=L, defs=DIAG, cam=(0, 0, 1.0 + 0.04 * t), overlay="", clock=False)


@shot("t_vanish")
def _(t, D, c):
    cam = GAR
    L = garden_layers(cam, "dawn", 240, sun=(760, 160))
    yy = cam.gy(0.55)
    dis = ease(ramp(t, 3.4, 6.8))
    a = [f'<g opacity="{1 - dis:.2f}">' + contact(480, yy, 24) + g(front("stand", "stand", "neutral", 0, (t % 2.6) < 0.1), 480, yy, 0.17) + '</g>']
    if dis > 0:
        rr = random.Random(2)
        for k in range(120):
            x0, y0 = 480 + rr.uniform(-14, 14), yy - rr.uniform(0, 88)
            u = max(0.0, min(1.0, dis * 1.4 - rr.uniform(0, 0.4)))
            x, y = x0 + rr.uniform(-60, 60) * u, y0 - 90 * u
            a.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.8*(1-u)+0.3:.2f}" fill="{rr.choice(["#2EA6C8", "#C98B62", "#FFFFFF", "#3A2A6E"])}" opacity="{(1-u)*min(1, dis*4):.2f}"/>')
    L.append(("act", 0.75, "".join(a), False, None))
    L.append(fg(cam, 241))
    ov = f'<rect width="{W}" height="{H}" fill="#0A0420" opacity="{0.4 + 0.15*dis:.2f}"/>'
    return dict(layers=L, defs=sky_defs("dawn"), cam=(0, 60, 2.0 + 0.3 * ease(t / D)), overlay=ov, clock=False)


# ================================================================ ENDING
@shot("e_nature")
def _(t, D, c):
    cam = Cam(hz=300, vp=(480, -30000), near=600)
    L = [("sky", 0.1, sky("gold", (640, 200)), True, None), ("forest", 0.25, forest(cam, 251), True, None),
         ("gnd", 0.6, ground(cam, "gold", seed=250) + blades(cam, 252, 40, 0.02, 0.5, 260, 520, avoid=(300, 760, 0.3)), True, None)]
    ants = []
    for k in range(7):
        d = (0.1 + k * 0.12 + t * 0.03) % 0.95
        x = cam.gx(-0.3 + 0.6 * (k % 2), d) + 40 * math.sin(k)
        ants.append((d, contact(x, cam.gy(d), 40 * cam.scale(d) * 0.7) + g(ant(t + k * 0.3, 1.0), x, cam.gy(d), cam.scale(d) * 0.7, 0, flip=k % 2 == 0)))
    ants.sort()
    L.append(("act", 0.75, "".join(s for _, s in ants), False, None))
    L.append(fg(cam, 253))
    return dict(layers=L, defs=sky_defs("gold"), cam=(0, -20 + 30 * ease(t / D), 1.0 + 0.08 * ease(t / D)), overlay="", clock=False)


@shot("e_anatomy")
def _(t, D, c):
    a = []
    K_ = 4.2
    ax, ay = 470, 420
    a.append(f'<ellipse cx="{ax}" cy="{ay + 6}" rx="300" ry="26" fill="#0A0420" opacity="0.35"/>' + g(ant(t, 0.0), ax, ay, K_))
    pts = [("armor, not skin", (-40, -44), (180, 120), 0.2, "#FF8A3A"), ("tubes, not lungs", (8, -30), (470, 480), 1.9, "#2EA6C8"),
           ("thousands of tiny eyes", (42, -40), (790, 130), 4.0, "#46E0D0"), ("a densely packed brain", (34, -32), (800, 290), 6.2, "#FF4F9A")]
    for i, (s_, (px, py), (lx, ly), t0, col) in enumerate(pts):
        if t < t0:
            continue
        X, Y = ax + px * K_, ay + py * K_
        f = ramp(t, t0, t0 + 0.5)
        if i == 1:
            a.append(f'<g opacity="{f:.2f}"><path d="M{ax - 120} {ay - 120} Q{ax} {ay - 150} {ax + 110} {ay - 120}" stroke="#9AF0FF" stroke-width="3" fill="none" stroke-dasharray="6 6"/></g>')
        if i == 2:
            a.append(f'<g opacity="{f:.2f}">' + "".join(f'<circle cx="{X - 10 + (k % 4)*6 + (3 if (k//4) % 2 else 0):.1f}" cy="{Y - 8 + (k//4)*5:.1f}" r="2.2" fill="#9AF0FF"/>' for k in range(16)) + '</g>')
        if i == 3:
            a.append(f'<g opacity="{f:.2f}">' + glow(X, Y, 26, "#FF7AC8", 0.9, 8) + '</g>')
        a.append(f'<g opacity="{f:.2f}"><path d="M{X:.1f} {Y:.1f} L{lx} {ly}" stroke="#FFFFFF" stroke-width="1.6" opacity="0.8"/><circle cx="{X:.1f}" cy="{Y:.1f}" r="4" fill="#FFFFFF"/></g>')
        a.append(chip(lx, ly, s_, t, t0 + 0.1, col, size=18))
    L = [("bg", 1.0, DIAG_BG, True, None), ("act", 1.0, "".join(a), False, None)]
    return dict(layers=L, defs=DIAG, cam=(0, 0, 1.06 - 0.06 * ease(t / D)), overlay="", clock=False)


@shot("e_end")
def _(t, D, c):
    cam = GAR
    L = garden_layers(cam, "gold", 260, sun=(640, 250))
    yy = cam.gy(0.55)
    act = contact(450, yy, 24) + g(back("stand", "stand", 0), 450, yy, 0.17) + contact(530, yy, 36) + g(ant(t, 0.0), 530, yy, 0.62, 0)
    L.append(("act", 0.75, act, False, None))
    L.append(fg(cam, 261))
    return dict(layers=L, defs=sky_defs("gold"), cam=(10, 70, 1.6 + 0.4 * ease(t / D)), overlay="", clock=False)


@shot("e_become")
def _(t, D, c):
    cam = GAR
    L = garden_layers(cam, "gold", 260, sun=(640, 250))
    yy = cam.gy(0.55)
    m = ease(ramp(t, 0.4, 1.6))
    act = (f'<g opacity="{1 - m:.2f}">' + contact(480, yy, 24) + g(front("stand", "stand", "happy"), 480, yy, 0.17) + '</g>' +
           f'<g opacity="{m:.2f}">' + contact(480, yy, 36) + g(ant(t, 0.0), 480, yy, 0.62) + '</g>')
    if 0.3 < t < 1.8:
        rr = random.Random(5)
        for k in range(40):
            u = ramp(t, 0.3, 1.8)
            a = rr.uniform(0, 6.28)
            act += f'<circle cx="{480 + math.cos(a)*40*u:.1f}" cy="{yy - 40 + math.sin(a)*40*u:.1f}" r="1.6" fill="#FFF2D8" opacity="{1-u:.2f}"/>'
    L.append(("act", 0.75, act, False, None))
    L.append(fg(cam, 261))
    endc = ease(ramp(t, 2.4, 3.2))
    ov = ""
    if endc > 0:
        ov = (f'<rect width="{W}" height="{H}" fill="#14084A" opacity="{0.7*endc:.2f}"/>' +
              f'<g opacity="{endc:.2f}">' + text(480, 270, "Sandbox", 72, "#FFFFFF", 700, "middle") + text(480, 312, "big questions, small worlds", 20, "#C8B8FF", 600, "middle", "Inter") + '</g>')
    return dict(layers=L, defs=sky_defs("gold"), cam=(0, 70, 2.0 - 0.3 * ease(t / D)), overlay=ov, clock=False)
