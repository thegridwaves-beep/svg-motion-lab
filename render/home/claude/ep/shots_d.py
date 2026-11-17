"""Coverage pass: replaces the repetitive front-facing shots with side tracking, POV, top-down,
over-the-shoulder, predator POV and silhouette shots. Imported last, so these definitions win."""
import math, random, sys
sys.path.insert(0, "/home/claude/ant"); sys.path.insert(0, "/home/claude/ant2")
from engine import shot, W, H
import vivid as V
from kit import inside, P, S, E, C, R, U, g, text
import assets as A
from assets import drop, ant, glow, sh, GREENS, sparkle, raindrop, crumb, spider, label, bird_shadow
from kit2 import *
from kit3 import side, pov_arm, silhouette, SIL_DEFS, topdown, top_contact, dof
import kit3
from shots_a import eo, ei, kitchen_far, KDEFS
from shots_b import GAR, LOW, leaf_floor, breath, heat_particles

ease = V.ease
ramp = A.ramp
SIDE = Cam(hz=360, vp=(480, -40000), near=560)
TILE = 1560


def tiled(fn, ks):
    return "".join(f'<g transform="translate({k * TILE} 0)">{fn(k)}</g>' for k in ks)


def side_layers(mood, seed, ks=(-1, 0, 1), sun=(720, 150), dense=30, cam=SIDE, avoid=None):
    gnd = tiled(lambda k: ground(cam, mood, seed=seed + k, n=120) + blades(cam, seed + 10 + k, dense, 0.02, 0.42, 260, 520,
                                                                         avoid=avoid if k == 0 else None), ks)
    fr = tiled(lambda k: forest(cam, seed + 20 + k), ks)
    return [("sky", 0.04, sky(mood, sun), True, None), ("forest", 0.22, fr, True, 2), ("gnd", 0.55, gnd, True, None)]


def side_fg(seed, ks=(-1, 0, 1), n=4, cam=SIDE):
    c2 = Cam(cam.hz, cam.vp, cam.near + 140)
    return ("fg", 1.6, tiled(lambda k: blades(c2, seed + k, max(2, n - 2), 0.9, 1.0, 150, 240, 1.1, avoid=(200, 760, 0.0), tuft_n=2), ks), True, 8)


def yy_side(d=0.62, cam=SIDE):
    return cam.gy(d)


# ================================================================ 00:00:01
@shot("f_land")
def _(t, D, c):
    """Straight down at the kitchen floor: you fall away from the lens, land, and get up."""
    tiles = []
    for i in range(-3, 10):
        for j in range(-3, 7):
            col = "#5A3AB8" if (i + j) % 2 else "#6444C4"
            tiles.append(f'<rect x="{i*150 + 4}" y="{j*150 + 4}" width="142" height="142" rx="14" fill="{col}"/>')
    floor = f'<rect x="-400" y="-400" width="1800" height="1400" fill="#2A1870"/>' + "".join(tiles)
    floor += f'<rect x="-400" y="-400" width="1800" height="1400" fill="url(#fl_light)"/>'
    leg = top_contact(170, 80, 120, 0.5) + f'<rect x="60" y="-40" width="210" height="210" rx="26" fill="#B86A3A"/>' + \
        inside(R(60, -40, 210, 210, 26), '<rect x="60" y="-40" width="210" height="210" fill="#E8A06A"/><circle cx="110" cy="10" r="160" fill="#FFD0A0" opacity="0.35" filter="url(#b30)"/>')
    rr = random.Random(4)
    crumbs = "".join(top_contact(x, y, 10, 0.4) + crumb(x, y, rr.uniform(10, 18), k) for k, (x, y) in enumerate([(720, 120), (790, 160), (300, 420), (860, 430)]))
    land = 1.0
    u = min(1.0, t / land)
    s_ = 2.6 - 2.0 * (1 - (1 - u) ** 2.2)
    cx, cy = 520 - 40 * (1 - u), 300 + 30 * (1 - u)
    a = []
    sh_r = 70 + 220 * (1 - u)
    a.append(f'<ellipse cx="{cx + 14:.1f}" cy="{cy + 20:.1f}" rx="{sh_r:.1f}" ry="{sh_r*0.8:.1f}" fill="#120626" opacity="{0.15 + 0.35*u:.2f}" filter="url(#b16)"/>')
    if t > land:
        v = (t - land) / 0.8
        if v < 1:
            for k in range(14):
                an = TAU_ * k / 14
                a.append(f'<circle cx="{cx + math.cos(an)*(60 + 110*v):.1f}" cy="{cy + math.sin(an)*(50 + 90*v):.1f}" r="{9*(1-v):.1f}" fill="#C8B8FF" opacity="{0.8*(1-v):.2f}" filter="url(#b2)"/>')
        sq = 1 - 0.12 * math.sin(math.pi * min(1, (t - land) / 0.35))
        arms = 0.9 - 0.7 * ramp(t, land + 0.6, land + 1.4)
        body = g(top(arms, 0.0), cx, cy, s_ * sq)
    else:
        body = g(top(0.9 + 0.1 * math.sin(t * 6), 0.0), cx, cy, s_, 10 * math.sin(t * 3))
    blur = max(0.0, (s_ - 0.9) * 6)
    a.append(f'<g filter="url(#b{8 if blur > 6 else (4 if blur > 2 else 2)})">{body}</g>' if blur > 0.8 else body)
    L = [("floor", 1.0, floor + leg + crumbs, True, None), ("act", 1.0, "".join(a), False, None)]
    defs = KDEFS + '<radialGradient id="fl_light" cx="0.3" cy="0.2" r="0.9"><stop offset="0" stop-color="#FFE2B0" stop-opacity="0.4"/><stop offset="1" stop-color="#FFE2B0" stop-opacity="0"/></radialGradient>'
    return dict(layers=L, defs=defs, cam=(0, 0, 1.0 + 0.03 * t), overlay="")


TAU_ = 2 * math.pi


@shot("f_drift")
def _(t, D, c):
    """Side on, tracking down with you as you float past the table leg."""
    st = kitchen_far()
    scroll = 170 * t
    leg = f'<g transform="translate(0 {-scroll:.1f})">' + "".join(sh(R(640, -600 + k * 800, 110, 820, 10), "#E8A06A", "#B86A3A", "#FFD0A0", 2) for k in range(3)) + '</g>'
    rr = random.Random(5)
    motes = "".join(f'<circle cx="{rr.uniform(0, 960):.1f}" cy="{(rr.uniform(0, 640) - t * 260) % 640 - 50:.1f}" r="{rr.uniform(2, 5):.1f}" fill="#FFF2D8" opacity="{rr.uniform(0.25, 0.6):.2f}" filter="url(#b2)"/>' for _ in range(26))
    you = g(side("float", 0, "happy", (t % 2.2) < 0.1, lean=-8 + 6 * math.sin(t * 1.3)), 380, 400 + 8 * math.sin(t * 1.4), 0.5)
    chair = f'<g transform="translate(0 {-scroll*1.6:.1f})">' + "".join(sh(R(-40, -600 + k * 900, 90, 920, 10), "#FF8AC8", "#C9408A", "#FFC0E0", 2) for k in range(3)) + '</g>'
    ov = chip(480, 490, "about 9 km/h: a slow jog", t, 0.8, "#2A1470", size=18)
    L = [("far", 0.15, st, True, 8), ("leg", 1.0, leg, False, None), ("act", 1.0, motes + you, False, None), ("fg", 1.0, f'<g filter="url(#b8)">{chair}</g>', False, None)]
    return dict(layers=L, defs=KDEFS, cam=(0, 0, 1.0), overlay=ov)


# ================================================================ 00:00:10
@shot("s_crumb")
def _(t, D, c):
    """Side tracking: you walk up to a crumb and put your shoulder into it."""
    L = side_layers("day", 300, ks=(-1, 0, 1))
    yy = yy_side()
    c1 = c[1] if len(c) > 1 else 1.8
    stop = 2.2
    x = 200 + 300 * min(1.0, t / stop) if t < stop else 500
    nudge = 18 * ease(ramp(t, 3.2, 4.6))
    cx = 640 + nudge
    cr = contact(cx, yy, 90) + crumb(cx, yy - 70, 82, 7)
    if t < stop:
        you = side("walk", t * 1.3, "neutral", (t % 2.5) < 0.1)
    else:
        you = side("push", 0, "strain" if t > 3.0 else "neutral", False)
    act = cr + contact(x + nudge * (t > stop), yy, 34) + g(you, x + nudge * (t > stop), yy, 0.42)
    L.append(("act", 1.0, act, False, None))
    L.append(side_fg(301))
    ov = (chip(330, 112, "muscle strength ÷ 250,000", t, c1 + 0.6, "#46E0D0", "#0A0420") +
          chip(680, 112, "body weight ÷ 125,000,000", t, c1 + 2.0, "#FFD23A", "#0A0420"))
    camx = 60 * ease(min(1, t / stop)) - 60
    return dict(layers=L, defs=sky_defs("day"), cam=(camx, 40, 1.15), overlay=ov, pad=(420, 160))


@shot("s_lift")
def _(t, D, c):
    """Low angle, silhouetted against a huge sun: the lift."""
    cam = LOW
    L = [("sky", 0.1, sky("gold", (480, 250)) + glow(480, 250, 220, "#FFF2C8", 0.7, 30), True, None), ("forest", 0.25, forest(cam, 61), True, 2),
         ("gnd", 0.6, ground(cam, "gold", seed=60) + blades(cam, 62, 26, 0.03, 0.5, 300, 700, avoid=(300, 660, 0.15)), True, None)]
    yy = cam.gy(0.55)
    k = 0.42
    lift = ease(ramp(t, 0.6, 1.8))
    arms = rig_lerp("brace", "cheer", lift)
    sq = 1 - 0.08 * math.sin(math.pi * ramp(t, 0.5, 1.0))
    hand_y = yy - k * (214 + (470 - 214) * lift)
    cr = crumb(480, hand_y - 60 * (0.3 + 0.7 * lift), 95, 7)
    body = f'<g transform="translate(480 {yy:.1f}) scale({k/sq**0.5:.4f} {k*sq:.4f})">{front(arms, "stand", "angry")}</g>' + cr
    act = contact(480, yy, 70) + silhouette(body)
    L.append(("act", 0.85, act, False, None))
    L.append(("fg", 1.4, pblade(cam, -30, 640, 1200, 130, GREENS[3], 0.1) + pblade(cam, 1000, 650, 1200, 140, GREENS[0], -0.08), True, 8))
    ov = chip(480, 500, "10× your own weight", t, 2.6, "#FF4F9A", size=20)
    return dict(layers=L, defs=sky_defs("gold") + SIL_DEFS, cam=(0, -10 * ease(t / D), 1.0 + 0.06 * ease(t / D)), overlay=ov)


def rig_lerp(a, b, u):
    import rig
    return rig.lerp_pose(rig.ARMS[a], rig.ARMS[b], u)


# ================================================================ 00:01:00
@shot("c_freeze")
def _(t, D, c):
    """Side on, close: hunched and shivering, breath fogging, frost crawling in. Camera eases back."""
    L = side_layers("cold", 330, ks=(0,), sun=(820, 300 + 20 * t))
    yy = yy_side()
    fr = ramp(t, 0.4, 5.6)
    jit = 1.6 * fr * math.sin(t * 46)
    you = g(side("shiver", 0, "sad" if t < 3 else "sleepy" if (t % 1.4) < 0.25 else "sad", False), 470 + jit, yy, 0.46)
    act = contact(470, yy, 40) + heat_particles(t, 470, yy - 120, 0.6, 1.0, n=30, spread=0.5) + you + breath(470 + 0.46 * 66, yy - 0.46 * 440, t, 1.3)
    rr = random.Random(9)
    frost_g = "".join(sparkle(round(x), round(yy + rr.uniform(-4, 30)), rr.uniform(3, 8) * fr + 0.5, "#E8F8FF", 0.8)
                      for x in [rr.choice([rr.uniform(-100, 300), rr.uniform(640, 1060)]) for _ in range(40)])
    L.append(("act", 1.0, act + f'<g filter="url(#b2)">{frost_g}</g>', False, None))
    L.append(side_fg(331, ks=(0,)))
    ov = (f'<rect width="{W}" height="{H}" fill="#5A8AE0" opacity="{0.22*fr:.2f}"/>' +
          f'<rect width="{W}" height="{H}" fill="none" stroke="#DFF4FF" stroke-width="{100*fr:.1f}" opacity="0.25" filter="url(#b16)"/>')
    z = 2.1 - 0.7 * ease(t / D)
    return dict(layers=L, defs=sky_defs("cold"), cam=(-10, 40 - 30 * ease(t / D), z), overlay=ov)


# ================================================================ 00:05:00
@shot("d_find")
def _(t, D, c):
    """Side tracking walk through the grass; foreground blades sweep past."""
    v = 150
    L = side_layers("day", 340, ks=(-1, 0, 1, 2), sun=(760, 140))
    yy = yy_side()
    x = 380 + v * t
    act = contact(x, yy, 30) + g(side("walk", t * 1.25, "neutral", (t % 2.4) < 0.1), x, yy, 0.4)
    L.append(("act", 1.0, act, False, None))
    L.append(side_fg(341, ks=(0, 1, 2), n=5))
    return dict(layers=L, defs=sky_defs("day"), cam=(v * t - 100, 30, 1.12), overlay="", pad=(900, 160))


@shot("d_stop")
def _(t, D, c):
    """Your eyes: both hands out, the right one freezes a finger's width from the water."""
    bg = sky("dawn", (700, 200), False) + f'<g filter="url(#b16)">{leaf_floor(470)}</g>'
    d = drop(800, 250, 230, t, 0.01) + sparkle(720, 120, 14, "#FFFFFF", 0.9)
    reach = eo(ramp(t, 0.0, 0.45))
    rec = 0.0 if t < 0.5 else 14 * math.sin(math.pi * ramp(t, 0.5, 0.8))
    right = pov_arm(400 + 60 * reach - rec, 440 - 60 * reach + rec * 0.5, 38, True, 0.9)
    left = pov_arm(150 + 30 * reach, 520 - 20 * reach, 18, False, 0.5)
    L = [("bg", 0.3, bg, True, None), ("drop", 1.0, d, False, None), ("hands", 1.0, left + right, False, None)]
    return dict(layers=L, defs=sky_defs("dawn"), cam=(0, 0, 1.0 + 0.05 * t), overlay=kinetic("DON'T", 300, 110, t, 0.35, 56, "#FFD23A"))


@shot("d_touch")
def _(t, D, c):
    """Your eyes: fingertips touch, the water grabs the hand and crawls down the sleeve."""
    bg = sky("dawn", (700, 200), False) + f'<g filter="url(#b16)">{leaf_floor(470)}</g>'
    wob = 0.012 + 0.03 * ramp(t, 0.4, 1.4)
    d = drop(690, 240, 260, t, wob)
    touch = ease(ramp(t, 0.5, 3.8))
    pull = 10 * math.sin(t * 9) * ramp(t, 1.2, 1.8)
    ang = 42
    wx, wy = 470 + pull, 330 + pull * 0.4
    arm = pov_arm(wx, wy, ang, True, 0.6)
    a = math.radians(ang)
    ux, uy = math.sin(a), -math.cos(a)
    tip = (wx + ux * 150, wy + uy * 150)
    end = (wx - ux * (60 + 380 * touch), wy - uy * (60 + 380 * touch))
    water = ""
    if t > 0.5:
        film = S(f"M {tip[0]:.1f} {tip[1]:.1f} L {end[0]:.1f} {end[1]:.1f}", 150)
        water = (f'<g opacity="0.55">{sh(film, "#8EE6FF", "#3AA8E0", "#E8FDFF", 3)}</g>' +
                 f'<path d="M {tip[0] - 40:.1f} {tip[1] + 20:.1f} L {end[0] - 40:.1f} {end[1] + 20:.1f}" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round" opacity="0.45" filter="url(#b2)"/>')
    left = pov_arm(170 - pull * 0.5, 540, -12 - 8 * ramp(t, 1.0, 1.6), False, 0.9)
    L = [("bg", 0.3, bg, True, None), ("drop", 1.0, d, False, None), ("hands", 1.0, arm + water + left, False, None)]
    return dict(layers=L, defs=sky_defs("dawn"), cam=(0, 0, 1.04 + 0.05 * ease(t / D)), overlay="")


# ================================================================ 00:15:00
@shot("r_dark")
def _(t, D, c):
    """Low, over your shoulder: you look up as clouds swallow the sun."""
    cam = LOW
    dk = ease(ramp(t, 0.2, 1.8))
    sunp = (640, 140)
    L = [("sky", 0.1, sky("gold", sunp), True, None), ("forest", 0.25, forest(cam, 351), True, 2),
         ("gnd", 0.6, ground(cam, "gold", seed=350) + blades(cam, 352, 22, 0.03, 0.5, 300, 700, avoid=(-200, 420, 0.1)), True, None)]
    clouds = "".join(f'<ellipse cx="{x - 260 * dk + 300:.1f}" cy="{y:.1f}" rx="{rx}" ry="{rx*0.5:.0f}" fill="#1E1646"/>' for x, y, rx in
                     [(520, 60, 260), (760, 120, 300), (980, 40, 260), (640, 200, 200), (880, 220, 230), (1200, 120, 280)])
    L.append(("clouds", 0.15, f'<g filter="url(#b16)" opacity="{0.25 + 0.7*dk:.2f}">{clouds}</g>', False, None))
    you = g(back("stand", "stand", -6 * dk), 250, 720, 0.85)
    L.append(("you", 1.15, you, False, None))
    ov = f'<rect width="{W}" height="{H}" fill="#14123A" opacity="{0.5*dk:.2f}"/>'
    return dict(layers=L, defs=sky_defs("gold"), cam=(0, 0, 1.0 + 0.05 * ease(t / D)), overlay=ov)


@shot("r_drop")
def _(t, D, c):
    """Side on, slow motion: a single raindrop, bigger than you, coming down beside you."""
    L = side_layers("storm", 360, ks=(0,), sun=None, avoid=(520, 780, 0.0))
    yy = yy_side()
    u = t / D
    dy = -160 + (yy - 150 + 160) * u
    trail = "".join(f'<circle cx="{640 + 4*math.sin(k):.1f}" cy="{dy - 150 - k*30:.1f}" r="{7 - k:.1f}" fill="#BFF0FF" opacity="{0.5 - k*0.08:.2f}" filter="url(#b2)"/>' for k in range(6))
    act = contact(330, yy, 34) + g(side("brace", 0, "surprised", (t % 2.4) < 0.1, lean=-10), 330, yy, 0.42) + trail + raindrop(640, dy, 120)
    gl = f'<ellipse cx="640" cy="{yy:.1f}" rx="{70 + 60*u:.1f}" ry="{12 + 8*u:.1f}" fill="#120830" opacity="{0.15 + 0.3*u:.2f}" filter="url(#b8)"/>'
    L.append(("act", 1.0, gl + act, False, None))
    L.append(side_fg(361, ks=(0,)))
    ov = chip(470, 112, "up to 100× your weight", t, 0.6, "#2EA6C8", size=20) + chip(470, 160, "falling at 30 km/h", t, 2.4, "#FF4F9A", size=20)
    return dict(layers=L, defs=sky_defs("storm"), cam=(0, 30, 1.12), overlay=ov + f'<rect width="{W}" height="{H}" fill="#14123A" opacity="0.22"/>')


def impact(x, y, t, t0, big=1.0):
    o = ""
    if t0 - 0.45 < t < t0:
        u = (t - (t0 - 0.45)) / 0.45
        r = (190 * (1 - u) + 34) * big
        bl = 30 if u < 0.4 else (16 if u < 0.75 else 4)
        o += f'<g filter="url(#b{bl})" opacity="{0.3 + 0.6*u:.2f}"><circle cx="{x - 60*(1-u):.1f}" cy="{y - 60*(1-u):.1f}" r="{r:.1f}" fill="#8ED8FF"/><circle cx="{x - 60*(1-u) - r*0.3:.1f}" cy="{y - 60*(1-u) - r*0.3:.1f}" r="{r*0.3:.1f}" fill="#FFFFFF" opacity="0.6"/></g>'
        o += f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{40*big*u:.1f}" ry="{34*big*u:.1f}" fill="#0A0620" opacity="{0.35*u:.2f}" filter="url(#b8)"/>'
    elif t >= t0:
        v = min(1.0, (t - t0) / 0.9)
        o += f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{60*big:.1f}" ry="{52*big:.1f}" fill="#1E2A6A" opacity="0.55" filter="url(#b4)"/>'
        if v < 1:
            o += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{(40 + 150*v)*big:.1f}" fill="none" stroke="#BFEFFF" stroke-width="{10*(1-v)*big + 1:.1f}" opacity="{0.8*(1-v):.2f}" filter="url(#b2)"/>'
            for k in range(12):
                an = TAU_ * k / 12 + x
                rr_ = (50 + 170 * v) * big
                o += f'<circle cx="{x + math.cos(an)*rr_:.1f}" cy="{y + math.sin(an)*rr_:.1f}" r="{(9*(1-v) + 1)*big:.1f}" fill="#DFF8FF" opacity="{0.85*(1-v):.2f}"/>'
    return o


@shot("r_truck")
def _(t, D, c):
    """Straight down from above: drops slam in around you, faster and faster."""
    st = topdown(370, "storm", n_bl=26, avoid=(480, 290, 160))
    rr = random.Random(3)
    times = [0.35, 1.05, 1.6, 2.0, 2.3, 2.55, 2.75, 2.92, 3.05, 3.18, 3.3, 3.4, 3.5, 3.6, 3.68, 3.76, 3.84, 3.92, 4.0, 4.1]
    pts = [(300, 220, 1.2), (700, 360, 1.3), (380, 430, 1.0), (640, 140, 1.1)] + [(rr.uniform(40, 920), rr.uniform(40, 500), rr.uniform(0.6, 1.1)) for _ in range(16)]
    hits = "".join(impact(x, y, t, t0, b) for (x, y, b), t0 in zip(pts, times))
    flinch = sum(math.exp(-((t - t0) / 0.12) ** 2) for t0 in times[:4])
    you = top_contact(480, 290, 40) + g(top(0.1, 0.55 + 0.3 * min(1, flinch)), 480 + 3 * math.sin(t * 30) * min(1, flinch), 290, 0.62)
    L = [("bg", 1.0, st, True, None), ("act", 1.0, you + hits, False, None)]
    return dict(layers=L, defs=sky_defs("storm"), cam=(0, 0, 1.0 + 0.08 * ease(t / D), 4 * ease(t / D)),
                overlay=f'<rect width="{W}" height="{H}" fill="#14123A" opacity="0.2"/>')


@shot("r_puddle")
def _(t, D, c):
    """Side tracking: you sprint, and a spreading puddle rolls in behind you."""
    v = 210
    L = side_layers("storm", 380, ks=(-1, 0, 1), sun=None)
    yy = yy_side()
    x = 420 + v * t
    wave_x = 120 + (v + 70) * t
    wx = wave_x
    crest = yy - 110 - 8 * math.sin(t * 7)
    wave = P(f"M -900 {yy + 40:.1f} L -900 {yy - 60:.1f} Q {wx - 300:.1f} {yy - 70:.1f} {wx - 110:.1f} {crest + 10:.1f} Q {wx - 30:.1f} {crest - 14:.1f} {wx + 30:.1f} {crest + 20:.1f} "
             f"Q {wx + 50:.1f} {crest + 46:.1f} {wx + 20:.1f} {crest + 50:.1f} Q {wx + 60:.1f} {yy - 20:.1f} {wx + 40:.1f} {yy + 40:.1f} Z")
    inner = (f'<rect x="-900" y="{yy - 200:.1f}" width="{wx + 1100:.1f}" height="300" fill="url(#wavg)"/>' +
             "".join(f'<ellipse cx="{wx - 120 - k*140 + 30*math.sin(t*3 + k):.1f}" cy="{yy - 40 + 10*math.sin(k*2.1):.1f}" rx="60" ry="10" fill="#FFFFFF" opacity="0.18"/>' for k in range(8)) +
             f'<path d="M {wx - 260:.1f} {yy - 66:.1f} Q {wx - 100:.1f} {crest + 4:.1f} {wx + 20:.1f} {crest + 18:.1f}" stroke="#FFFFFF" stroke-width="12" fill="none" stroke-linecap="round" opacity="0.6" filter="url(#b4)"/>')
    wv = f'<g opacity="0.88">{wave("#4A7AE0")}{inside(wave, inner)}</g>' + "".join(
        f'<circle cx="{wx + 20 + 34*math.sin(t*6 + k):.1f}" cy="{crest + 10 - ((t*2.4 + k*0.17) % 1)*70:.1f}" r="{7 - k*0.6:.1f}" fill="#E8F8FF" opacity="{0.8 - 0.07*k:.2f}"/>' for k in range(9))
    act = contact(x, yy, 30) + g(side("run", t * 2.1, "scared", False), x, yy, 0.4) + wv
    rain = "".join(raindrop(rx, (ry + t * 520) % 700 - 120, 8, 0.75) for rx, ry in [(x - 300 + k * 97, k * 61) for k in range(12)])
    L.append(("act", 1.0, f'<g filter="url(#b2)">{rain}</g>' + act, False, None))
    L.append(side_fg(381, ks=(0, 1)))
    return dict(layers=L, defs=sky_defs("storm") + '<linearGradient id="wavg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AD8FF"/><stop offset="0.5" stop-color="#3A6AD0"/><stop offset="1" stop-color="#1E2E8A"/></linearGradient>', cam=(v * t - 40, 30, 1.15), overlay=f'<rect width="{W}" height="{H}" fill="#14123A" opacity="0.18"/>', pad=(1000, 160))


# ================================================================ 00:20:00
@shot("v_ultra2")
def _(t, D, c):
    """Your eyes, flat on your back: the sole of a giant shoe lifts away overhead. You scream; nothing."""
    bg = sky("storm", None) + f'<g filter="url(#b16)">{blades(Cam(hz=700, vp=(480, -900), near=800), 391, 30, 0.2, 1.0, 300, 600)}</g>'
    lift = ramp(t, 0.15, 2.1) ** 1.7
    upper = P("M 30 60 Q 0 -10 90 -40 Q 230 -70 360 -120 Q 460 -240 610 -260 L 860 -268 Q 985 -258 992 -120 L 1000 60 Z")
    sole = P("M 0 70 Q 0 160 70 170 L 930 170 Q 1010 168 1006 90 L 1004 50 L 8 50 Z")
    laces = "".join(f'<ellipse cx="{390 + i*58}" cy="{-130 - i*30}" rx="34" ry="12" fill="#5A4A9A" transform="rotate(-28 {390 + i*58} {-130 - i*30})"/>' for i in range(5))
    shoe_svg = (sh(upper, "#F6F2FF", "#B9B0DA", "#FFFFFF", 6) + inside(upper, laces + '<path d="M 30 60 Q 20 -20 140 -40 L 160 60 Z" fill="#E4DEF8"/><rect x="760" y="-280" width="240" height="360" rx="60" fill="#FF6FB5" opacity="0.85"/>') +
                sh(sole, "#FF4F9A", "#B82E72", "#FFC0E0", 5) + inside(sole, '<rect x="0" y="50" width="1010" height="34" fill="#FFFFFF" opacity="0.85"/>' +
                "".join(f'<rect x="{40 + i*64}" y="140" width="40" height="40" rx="12" fill="#B82E72" opacity="0.6"/>' for i in range(15))))
    shoe = f'<g transform="translate({470 + 260*lift:.1f} {190 - 250*lift:.1f}) scale({0.62 - 0.22*lift:.3f}) rotate({8 - 16*lift:.1f}) translate(-500 -40)">{shoe_svg}</g>'
    rings = ""
    for k in range(4):
        u = ((t * 1.3 + k / 4) % 1)
        rings += f'<ellipse cx="480" cy="560" rx="{80 + 420*u:.1f}" ry="{50 + 300*u:.1f}" fill="none" stroke="#FFFFFF" stroke-width="5" opacity="{0.55*(1-u):.2f}" filter="url(#b2)"/>'
    wave = 12 * math.sin(t * 14)
    hands = pov_arm(250 + wave, 470, -20 + wave * 0.5, False, 1.0) + pov_arm(710 - wave, 470, 20 - wave * 0.5, True, 1.0)
    L = [("bg", 0.3, bg, True, None), ("shoe", 1.0, f'<g filter="url(#b{2 if lift < 0.5 else 4})">{shoe}</g>', False, None), ("hands", 1.0, rings + hands, False, None)]
    return dict(layers=L, defs=sky_defs("storm"), cam=(0, 0, 1.0), overlay=kinetic("ULTRASOUND", 480, 470, t, 0.2, 60))


# ================================================================ 00:25:00
@shot("l_notice")
def _(t, D, c):
    """Over your shoulder: a vast shadow slides across the ground toward you."""
    L = side_layers("gold", 400, ks=(0,), sun=(760, 140))
    yy = yy_side(0.5)
    sx = 1400 - 1700 * ease(ramp(t, 0.1, 1.9))
    shade = f'<ellipse cx="{sx:.1f}" cy="{yy + 30:.1f}" rx="520" ry="160" fill="#0A0420" opacity="0.55" filter="url(#b30)"/>'
    L.append(("shade", 0.8, shade, False, None))
    flinch = ramp(t, 0.9, 1.3)
    L.append(("you", 1.2, g(back("brace" if flinch > 0.5 else "stand", "stand", 8 * flinch), 300, 700 + 10 * flinch, 0.8), False, None))
    dim = f'<rect width="{W}" height="{H}" fill="#0A0420" opacity="{0.3 * ramp(t, 0.6, 1.6):.2f}"/>'
    return dict(layers=L, defs=sky_defs("gold"), cam=(0, 20, 1.05 + 0.06 * ease(t / D)), overlay=dim)


@shot("l_spider")
def _(t, D, c):
    """Through the spider's eyes: four lenses, one small running snack."""
    cam = GAR
    scene_bg = (sky("gold", (700, 140), False) + forest(cam, 411, 30) + ground(cam, "gold", seed=410, n=50) + blades(cam, 412, 14, 0.02, 0.45, 260, 520, avoid=(250, 750, 0.3)))
    yy = cam.gy(0.6)
    x = 600 - 160 * t
    you = contact(x, yy, 26) + g(side("run", t * 2.2, "scared", False), x, yy, 0.22, 0, flip=True)
    eyes = [(330, 270, 230), (650, 270, 230), (150, 120, 90), (830, 120, 90)]
    feather = '<radialGradient id="lensm"><stop offset="0.86" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>'

    def lenses(mid, content_fn):
        mk = "".join(f'<circle cx="{ex}" cy="{ey}" r="{er}" fill="url(#lensm)"/>' for ex, ey, er in eyes)
        views = "".join(f'<g transform="translate({ex} {ey}) scale({1.25 if er > 100 else 0.7}) translate({-480} {-yy + 40})">{content_fn()}</g>' for ex, ey, er in eyes)
        return (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-300" y="-300" width="1560" height="1140"><rect x="-300" y="-300" width="1560" height="1140" fill="#000"/>{mk}</mask>'
                f'<g mask="url(#{mid})">{views}</g>')
    bg = f'<rect x="-300" y="-300" width="1560" height="1140" fill="#0A0418"/>' + lenses("spm1", lambda: scene_bg)
    fgv = lenses("spm2", lambda: f'<g transform="translate({480 - x:.1f} 0)">{you}</g>') + "".join(f'<circle cx="{ex}" cy="{ey}" r="{er}" fill="url(#lensv)"/>' for ex, ey, er in eyes)
    defs = sky_defs("gold") + feather + '<radialGradient id="lensv" cx="0.4" cy="0.35" r="0.65"><stop offset="0.6" stop-color="#3A0A30" stop-opacity="0"/><stop offset="1" stop-color="#3A0A30" stop-opacity="0.75"/></radialGradient>'
    L = [("eyes", 1.0, bg, True, None), ("you", 1.0, fgv, False, None)]
    return dict(layers=L, defs=defs, cam=(0, 0, 1.0 + 0.05 * t, -4), overlay=kinetic("lunch", 480, 500, t, 0.5, 48, "#FF4F9A"))


@shot("l_bird")
def _(t, D, c):
    """Straight down, very high: the bird's shadow sweeps over a tiny you."""
    st = topdown(420, "gold", n_peb=140, n_bl=40, k=(1.15, 1.3), avoid=(480, 280, 60))
    yy = 280
    you = top_contact(480, yy, 24) + g(top(0.0, 0.7 * ramp(t, 0.4, 0.8)), 480, yy, 0.34)
    bx = -600 + 2000 * ease(ramp(t, 0.0, 1.6))
    shd = f'<g filter="url(#b16)">{g(bird_shadow(0.55), bx, 260 + 0.12 * (bx - 480), 5.5, 12)}</g>'
    L = [("bg", 1.0, st, True, None), ("act", 1.0, you + shd, False, None)]
    return dict(layers=L, defs=sky_defs("gold"), cam=(0, 0, 0.92 + 0.12 * ease(t / D)), overlay=kinetic("snack", 480, 110, t, 0.5, 44))


@shot("l_ants")
def _(t, D, c):
    """Side on at ground level: a column of ants marches in from the right; you back away."""
    L = side_layers("gold", 430, ks=(0,), sun=(760, 140))
    yy = yy_side()
    ants = ""
    for k in range(6):
        x = 1040 + k * 200 - 150 * t
        ants += contact(x, yy, 70) + g(ant(t + k * 0.37, 1.0), x, yy, 1.5, 0, flip=True)
    back_x = 340 - 100 * ease(ramp(t, 0.6, 3.8))
    you = contact(back_x, yy, 30) + g(side("walk", -t * 0.9 if 0.6 < t < 3.8 else 0, "scared", False, lean=-6), back_x, yy, 0.4)
    L.append(("act", 1.0, you + ants, False, None))
    L.append(side_fg(431, ks=(0,)))
    ov = kinetic("they never come alone", 480, 110, t, 1.8, 38)
    return dict(layers=L, defs=sky_defs("gold"), cam=(0, 30, 1.1 + 0.05 * ease(t / D)), overlay=ov)


# ================================================================ THE TRUTH
@shot("t_vanish")
def _(t, D, c):
    """Profile silhouette against the dawn, coming apart into light."""
    L = side_layers("dawn", 440, ks=(0,), sun=(480, 330), avoid=(330, 640, 0.0))
    L[0] = ("sky", 0.04, sky("dawn", (480, 330)) + glow(480, 330, 200, "#FFE6C8", 0.75, 30), True, None)
    yy = yy_side()
    dis = ease(ramp(t, 3.2, 6.8))
    body = g(side("stand", 0, "neutral", (t % 2.6) < 0.1), 480, yy, 0.5)
    a = [contact(480, yy, 40, 0.45 * (1 - dis)), f'<g opacity="{1 - dis:.2f}">{silhouette(body)}</g>']
    if dis > 0:
        rr = random.Random(2)
        for k in range(160):
            x0, y0 = 480 + rr.uniform(-24, 30), yy - rr.uniform(0, 230)
            u = max(0.0, min(1.0, dis * 1.5 - rr.uniform(0, 0.5)))
            x, y = x0 + rr.uniform(-40, 140) * u, y0 - 160 * u
            a.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{2.6*(1-u) + 0.4:.2f}" fill="{rr.choice(["#FFE6C8", "#FFC79A", "#FFFFFF", "#FF9AC0"])}" opacity="{(1-u)*min(1, dis*4):.2f}"/>')
    L.append(("act", 1.0, "".join(a), False, None))
    L.append(side_fg(441, ks=(0,)))
    return dict(layers=L, defs=sky_defs("dawn") + SIL_DEFS, cam=(0, 10, 1.25 + 0.15 * ease(t / D)), overlay="", clock=False)
