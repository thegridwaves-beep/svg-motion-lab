"""Second 10 (superpower), minute 1 (cold), minute 5 (thirst)."""
import math, random, sys
sys.path.insert(0, "/home/claude/ant"); sys.path.insert(0, "/home/claude/ant2")
from engine import shot, W, H
import vivid as V
from kit import inside, P, S, E, C, R, U, g, text
import assets as A
from assets import drop, ant, glow, ball, sh, GREENS, pebble, sparkle, raindrop, crumb, spider, leaf, label, sugar, shrew
from kit2 import *
import kit2, rig
from shots_a import eo, ei, kitchen_far, KDEFS

ease = V.ease
ramp = A.ramp
GAR = Cam(hz=330, vp=(480, -40000), near=600)
LOW = Cam(hz=450, vp=(480, -1700), near=650)


def garden_layers(cam, mood, seed, sun=(720, 140), avoid=(300, 680, 0.25), dense=34):
    return [("sky", 0.1, sky(mood, sun), True, None),
            ("forest", 0.25, forest(cam, seed + 1), True, None),
            ("gnd", 0.6, ground(cam, mood, seed=seed) + blades(cam, seed + 2, dense, 0.02, 0.45, 260, 520, avoid=avoid), True, None)]


def fg(cam, seed, n=5):
    return ("fg", 1.4, blades(Cam(cam.hz, cam.vp, cam.near + 120), seed, max(2, n - 2), 0.85, 1.0, 150, 230, 1.0, avoid=(180, 780, 0.0), tuft_n=2), True, 8)


def breath(x, y, t, every=1.1):
    o = ""
    for k in range(3):
        u = ((t + k * every / 3) % every) / every
        o += f'<circle cx="{x + 10 + u*26:.1f}" cy="{y - u*14:.1f}" r="{3 + u*8:.1f}" fill="#FFFFFF" opacity="{0.55*(1-u):.2f}" filter="url(#b2)"/>'
    return o


# ================================================================ SECOND 10: superpower
@shot("s_crumb")
def _(t, D, c):
    cam = GAR
    L = garden_layers(cam, "day", 50)
    yy = cam.gy(0.55)
    cr = crumb(600, yy - 46, 56, 7)
    x = 380 + 140 * ramp(t, 0.2, 2.0)
    arms = "walk" if t < 2.0 else rig.lerp_pose(rig.ARMS["stand"], rig.ARMS["brace"], ramp(t, 2.0, 2.4))
    act = contact(600, yy, 70) + cr + contact(x, yy, 24) + g(front(arms, "walk" if t < 2.0 else "stand", "neutral" if t < 2.4 else "think", 0, (t % 2.5) < 0.1), x, yy, 0.17)
    L.append(("act", 0.75, act, False, None))
    L.append(fg(cam, 51))
    c1 = c[1] if len(c) > 1 else 1.8
    ov = (chip(330, 112, "muscle strength ÷ 250,000", t, c1 + 0.6, "#46E0D0", "#0A0420") +
          chip(680, 112, "body weight ÷ 125,000,000", t, c1 + 2.0, "#FFD23A", "#0A0420"))
    return dict(layers=L, defs=sky_defs("day"), cam=(20 * ease(t / D), 0, 1.0 + 0.05 * ease(t / D)), overlay=ov)


@shot("s_lift")
def _(t, D, c):
    """Low angle hero shot against the sun."""
    cam = LOW
    L = [("sky", 0.1, sky("gold", (500, 130)), True, None), ("forest", 0.25, forest(cam, 61), True, 2),
         ("gnd", 0.6, ground(cam, "gold", seed=60) + blades(cam, 62, 26, 0.03, 0.5, 300, 700, avoid=(330, 640, 0.2)), True, None)]
    yy = cam.gy(0.55)
    k = 0.4
    lift = ease(ramp(t, 0.6, 1.8))
    arms = rig.lerp_pose(rig.ARMS["brace"], rig.ARMS["cheer"], lift)
    sq = 1 - 0.08 * math.sin(math.pi * ramp(t, 0.5, 1.0))
    hand_y = yy - k * (214 + (470 - 214) * lift)
    cr = crumb(480, hand_y - 60 * (0.3 + 0.7 * lift), 95, 7)
    act = contact(480, yy, 70) + f'<g transform="translate(480 {yy:.1f}) scale({k/sq**0.5:.4f} {k*sq:.4f})">{front(arms, "stand", "angry" if t < 1.6 else "happy", 0, False)}</g>' + cr
    L.append(("act", 0.85, act, False, None))
    L.append(("fg", 1.4, pblade(cam, -30, 640, 1200, 130, GREENS[3], 0.1) + pblade(cam, 1000, 650, 1200, 140, GREENS[0], -0.08), True, 8))
    ov = chip(480, 490, "10× your own weight", t, 2.6, "#FF4F9A", size=20)
    return dict(layers=L, defs=sky_defs("gold"), cam=(0, -10 * ease(t / D), 1.0 + 0.06 * ease(t / D)), overlay=ov)


@shot("s_hero")
def _(t, D, c):
    """Over the shoulder of a watching ant: you show off with the crumb overhead."""
    cam = GAR
    L = garden_layers(cam, "gold", 70, sun=(760, 160))
    yy = cam.gy(0.5)
    bob = 6 * math.sin(t * 3)
    act = contact(560, yy, 24) + g(front("cheer", "stand", "laugh", 4 * math.sin(t * 3), False), 560, yy, 0.17) + crumb(560, yy - 0.17 * 470 - 28 + bob * 0.3, 34, 7)
    L.append(("act", 0.75, act, False, None))
    ant_fg = g(ant(t, 0.0, antenna=-4 + 6 * math.sin(t * 2)), 210, 590, 3.0)
    L.append(("ant", 1.3, ant_fg, False, 4))
    ov = kinetic("being tiny is amazing", 520, 470, t, 2.4, 34, "#FFFFFF", out_t=None)
    return dict(layers=L, defs=sky_defs("gold"), cam=(-20 * ease(t / D), 0, 1.0 + 0.05 * ease(t / D)), overlay=ov)


# ================================================================ MINUTE 1: the cold
@shot("c_shiver")
def _(t, D, c):
    """Close-up: you start shivering; the light cools."""
    cool = ramp(t, 0.0, 1.6)
    bg = sky("cold", (760, 300), False)
    jit = 2.2 * math.sin(t * 50) * cool
    face = g(face_close("sad" if t > 0.5 else "neutral", 0, False), 480 + jit, 300, 3.6)
    body = g(front("shiver", "stand", "sad", 0, False), 480 + jit, 300 + 3.6 * 444, 3.6)
    act = body + breath(520, 330, t, 1.0)
    grade = f'<rect width="{W}" height="{H}" fill="#6A9AE8" opacity="{0.25*cool:.2f}"/>'
    L = [("bg", 0.2, bg + f'<g filter="url(#b16)">{blades(GAR, 80, 30, 0.0, 0.5, 260, 520)}</g>', True, None), ("act", 1.0, act, False, None), ("grade", 1.0, grade, False, None)]
    return dict(layers=L, defs=sky_defs("cold"), cam=(0, 0, 1.0 + 0.04 * t), overlay="")


def heat_particles(t, cx, cy, rate, cold=0.0, n=60, seed=3, spread=1.0):
    rr = random.Random(seed)
    o = []
    for k in range(int(n * rate)):
        a = rr.uniform(0, 2 * math.pi)
        u = ((t * rate * 0.5 + rr.random()) % 1.0)
        d = 40 + u * 220 * spread
        x, y = cx + math.cos(a) * d * 0.6, cy + math.sin(a) * d - u * 30
        col = "#FFB060" if cold < 0.5 else "#9AD8FF"
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4*(1-u)+1:.2f}" fill="{col}" opacity="{0.8*(1-u):.2f}"/>')
    return "".join(o)


@shot("c_heat")
def _(t, D, c):
    """Thermal view: your body glows; heat streams off your skin."""
    bg = f'<rect x="-300" y="-300" width="1560" height="1140" fill="url(#therm)"/>'
    pulse = 0.5 + 0.5 * math.sin(t * 2.6)
    body = front("stand", "stand", "neutral", 0, (t % 2.8) < 0.1)
    sil = (f'<g transform="translate(480 500) scale(0.82)"><g opacity="0.25">{body}</g></g>'
           + glow(480, 300, 150, "#FF6A2A", 0.5, 30) + glow(480, 300, 70 + 8 * pulse, "#FFD27A", 0.8, 16))
    parts = heat_particles(t, 480, 290, 1.0 + 0.6 * ramp(t, 3.0, 5.0))
    L = [("bg", 1.0, bg, True, None), ("act", 1.0, sil + parts, False, None)]
    ov = chip(480, 70, "37 °C inside", t, 1.6, "#FF8A3A", size=22) + kinetic("heat leaks out through your skin", 480, 490, t, 3.6, 30)
    return dict(layers=L, defs='<radialGradient id="therm" cx="0.5" cy="0.55" r="0.8"><stop offset="0" stop-color="#5A1A7A"/><stop offset="1" stop-color="#120630"/></radialGradient>',
                cam=(0, 0, 1.0 + 0.03 * t), overlay=ov, clock=True)


@shot("c_skin")
def _(t, D, c):
    """One big block loses heat slowly. Chop it into tiny blocks and the arrows multiply."""
    bg = f'<rect x="-300" y="-300" width="1560" height="1140" fill="url(#cbg3)"/>'
    a = []
    big = V.iso_box(270, 380, 120, 120, 120, "#FFB38A", "#FF7A4A", "#D8501E")
    a.append(A.popin(big, 270, 320, t, 0.1))
    for k, (dx, dy) in enumerate([(-110, -60), (110, -60), (0, -170), (-70, 30), (70, 30)]):
        u = ((t * 0.8 + k * 0.2) % 1)
        a.append(f'<path d="M{270 + dx*0.6:.1f} {320 + dy*0.6:.1f} l{dx*0.25*u:.1f} {dy*0.25*u:.1f}" stroke="#FFD27A" stroke-width="4" stroke-linecap="round" opacity="{1-u:.2f}"/>')
    split = ramp(t, 1.2, 2.2)
    if split > 0:
        for i in range(4):
            for j in range(4):
                x, y = 600 + i * 70 + j * 0 - 35 * j * 0.0, 300 + j * 60 + (i % 2) * 6
                a.append(A.popin(V.iso_box(x, y, 26, 26, 26, "#FFB38A", "#FF7A4A", "#D8501E"), x, y - 13, t, 1.2 + (i + j) * 0.06))
                for k, (dx, dy) in enumerate([(-30, -20), (30, -20), (0, -46)]):
                    u = ((t * 1.4 + k * 0.33 + i * 0.1 + j * 0.17) % 1)
                    if t > 1.6:
                        a.append(f'<path d="M{x + dx*0.4:.1f} {y - 13 + dy*0.4:.1f} l{dx*0.5*u:.1f} {dy*0.5*u:.1f}" stroke="#9AD8FF" stroke-width="3" stroke-linecap="round" opacity="{1-u:.2f}"/>')
    L = [("bg", 1.0, bg, True, None), ("act", 1.0, "".join(a), False, None)]
    ov = chip(270, 470, "you, human sized", t, 0.4, "#FF8A3A") + chip(710, 500, "you, ant sized: 500× more skin per bit", t, 2.2, "#2EA6C8")
    return dict(layers=L, defs=V.lin("cbg3", [(0, "#3A1AA8"), (1, "#14084A")]), cam=(0, 0, 1.0), overlay=ov)


STAGE = Cam(hz=300, vp=(480, -9000), near=620)


def stage_floor(mood="day"):
    cam = STAGE
    return (f'<rect x="-300" y="-300" width="1560" height="1140" fill="url(#stg2)"/>' +
            "".join(f'<circle cx="{(k*173) % 960}" cy="{(k*97) % 300}" r="{40 + (k*31) % 60}" fill="#FFFFFF" opacity="0.04"/>' for k in range(14)) +
            f'<path d="M-300 {cam.hz} L1260 {cam.hz} L1260 900 L-300 900 Z" fill="#2A1478"/>' +
            "".join(f'<path d="M{480 + (k*120 - 480)*0.3:.0f} {cam.hz} L{480 + (k*120 - 480)*2.2:.0f} 640" stroke="#4A2AA8" stroke-width="2" opacity="0.7"/>' for k in range(-6, 14)))


STG_DEFS = V.lin("stg2", [(0, "#5A24C8"), (1, "#2A1080")])


def scale_device(x, y, val, t, t0):
    plat = sh(P(f"M{x-170} {y} L{x+170} {y} L{x+190} {y+30} L{x-190} {y+30} Z"), "#E8ECFF", "#A8B0E0", "#FFFFFF", 1.4)
    base = sh(R(x - 120, y + 30, 240, 70, 14), "#9AA8D8", "#6A78B0", "#DDE4FF", 1.2)
    disp = R(x - 60, y + 46, 120, 40, 8)
    shown = val if t > t0 else "0.00 g"
    return plat + base + disp("#0E1A3A") + text(x, y + 75, shown, 24, "#46E0D0", 700, "middle")


@shot("c_shrew")
def _(t, D, c):
    st = stage_floor()
    sniff = 3 * math.sin(t * 14) * (1 if (t % 1.6) < 0.8 else 0)
    act = scale_device(380, 380, "2.0 g", t, 1.2) + g(shrew(t), 380 + sniff * 0.3, 380, 1.3)
    act += chip(380, 230, "Etruscan shrew", t, 0.3, "#FF8A3A", size=20)
    L = [("bg", 1.0, st, True, None), ("act", 1.0, act, False, None)]
    return dict(layers=L, defs=STG_DEFS, cam=(0, 0, 1.0 + 0.04 * t), overlay=kinetic("smallest warm blooded animal", 560, 130, t, 1.6, 34))


@shot("c_shrew2")
def _(t, D, c):
    st = stage_floor()
    eat = ramp(t, 0.3, 3.8)
    rr = random.Random(4)
    pile = ""
    for k in range(int(40 * eat)):
        x, y = 640 + rr.uniform(-80, 80), 400 - rr.uniform(0, 60) * (k / 40)
        pile += ball(x, y, rr.uniform(11, 16), rr.choice(["#FFB03A", "#FF8A3A", "#FFD27A"]), "#C0601E")
    chew = 2 * math.sin(t * 20)
    act = g(shrew(t), 330, 400 + chew * 0.2, 1.15) + pile
    day = (f'<g transform="translate(800 120)"><circle r="44" fill="#140A3A" opacity="0.85"/>'
           f'<path d="M0 0 L{38*math.sin(eat*6.283):.1f} {-38*math.cos(eat*6.283):.1f}" stroke="#FFD23A" stroke-width="5" stroke-linecap="round"/>'
           f'<circle r="44" fill="none" stroke="#FFD23A" stroke-width="3"/></g>')
    L = [("bg", 1.0, st, True, None), ("act", 1.0, act + day, False, None)]
    ov = chip(640, 300, "2× its weight", t, 1.6, "#FFD23A", "#2A1470", 18) + chip(800, 190, "every day", t, 0.6, "#FF4F9A")
    return dict(layers=L, defs=STG_DEFS, cam=(0, 0, 1.0), overlay=ov)


@shot("c_sugar")
def _(t, D, c):
    """Overhead on the table: you lying next to a grain of sugar the same size."""
    wood = f'<rect x="-300" y="-300" width="1560" height="1140" fill="url(#ktop)"/>' + "".join(
        f'<path d="M-300 {-200 + k*48} Q480 {-190 + k*48 + (8 if k % 2 else -6)} 1260 {-200 + k*48}" stroke="#B8703E" stroke-width="3" fill="none" opacity="0.45"/>' for k in range(20))
    cube = (sh(R(560, 200, 130, 130, 16), "#FFFFFF", "#E0DCF4", "#FFFFFF", 2) +
            inside(R(560, 200, 130, 130, 16), '<path d="M560 200 L690 200 L640 250 L560 250 Z" fill="#FFFFFF"/><rect x="600" y="240" width="60" height="50" rx="6" fill="#F0ECFF"/>') +
            f'<rect x="560" y="200" width="130" height="130" rx="16" fill="#120830" opacity="0.15" transform="translate(10 12)" filter="url(#b8)"/>')
    you_top = f'<ellipse cx="380" cy="280" rx="80" ry="64" fill="#120830" opacity="0.25" filter="url(#b8)"/>' + g(top(0.4, 0.0), 370, 262, 1.25, -12)
    act = cube + you_top
    L = [("bg", 1.0, wood, True, None), ("act", 1.0, act, False, None)]
    ov = chip(380, 430, "you: 0.5 mg", t, 0.6, "#2EA6C8", size=20) + chip(625, 430, "a grain of sugar", t, 1.3, "#FFFFFF", "#2A1470", 18)
    ov += kinetic("thousands of times lighter than the shrew", 480, 500, t, 2.9, 28)
    return dict(layers=L, defs=KDEFS, cam=(0, 0, 1.06 - 0.06 * ease(t / D)), overlay=ov)


@shot("c_freeze")
def _(t, D, c):
    cam = GAR
    L = garden_layers(cam, "cold", 90, sun=(780, 260 + 25 * t))
    yy = cam.gy(0.55)
    fr = ramp(t, 0.5, 5.5)
    jit = 1.2 * fr * math.sin(t * 48)
    act = (heat_particles(t, 480, yy - 50, 0.6, 1.0, n=40, spread=0.4) + contact(480, yy, 24) +
           g(front("shiver", "stand", "sad", 0, (t % 2.2) < 0.1), 480 + jit, yy, 0.17) + breath(486, yy - 76, t, 1.2))
    L.append(("act", 0.75, act, False, None))
    L.append(fg(cam, 91))
    rr = random.Random(9)
    frost = "".join(sparkle(round(x), round(y), rr.uniform(4, 10) * fr + 0.5, "#E8F8FF", 0.75) for x, y in
                    [((rr.choice([rr.uniform(0, 110), rr.uniform(850, 960)])), rr.uniform(0, 540)) for _ in range(70)])
    ov = (f'<rect width="{W}" height="{H}" fill="#5A8AE0" opacity="{0.22*fr:.2f}"/>' + f'<g filter="url(#b2)">{frost}</g>' +
          f'<rect width="{W}" height="{H}" fill="none" stroke="#DFF4FF" stroke-width="{90*fr:.1f}" opacity="0.22" filter="url(#b16)"/>')
    return dict(layers=L, defs=sky_defs("cold"), cam=(0, 130, 2.0 + 0.2 * ease(t / D)), overlay=ov)


# ================================================================ MINUTE 5: thirst
@shot("d_find")
def _(t, D, c):
    """Tracking shot: walking through the grass, layers sliding past at different speeds."""
    cam = GAR
    L = [("sky", 0.0, sky("day", (720, 140)), True, None), ("forest", 0.15, forest(cam, 101), True, None),
         ("gnd", 0.5, ground(cam, "day", seed=100, x0=-900, x1=1900) + blades(cam, 102, 60, 0.05, 0.45, 260, 520, avoid=(380, 580, 0.35), umin=-2.2, umax=2.2), True, None)]
    yy = cam.gy(0.78)
    sw = math.sin(t * 7)
    act = contact(480, yy, 48) + g(front("walk", "walk" if sw > 0 else "stand", "neutral", 0, (t % 2.4) < 0.1), 480, yy - 4 * abs(sw), 0.38, flip=sw < 0)
    L.append(("act", 0.0, act, False, None))
    L.append(("fg", 1.6, blades(Cam(cam.hz, cam.vp, cam.near + 120), 103, 10, 0.85, 1.0, 150, 260, 1.0, avoid=(330, 630, 0.0), umin=-2.4, umax=2.4), True, 8))
    return dict(layers=L, defs=sky_defs("day"), cam=(-120 * t, 0, 1.0), overlay="")


def leaf_floor(top=420):
    surf = P(f"M-400 {top + 40} Q480 {top - 20} 1360 {top + 40} L1360 900 L-400 900 Z")
    return (sh(surf, "#46E08A", "#1EA864", "#C2FFD8", 4) +
            inside(surf, "".join(f'<path d="M{-200 + k*170} 900 Q{-100 + k*170} {top + 60} {40 + k*170} {top - 10}" stroke="#2EB872" stroke-width="5" fill="none" opacity="0.5"/>' for k in range(10)) +
                   f'<path d="M-400 {top + 60} Q480 {top} 1360 {top + 60}" stroke="#2AA060" stroke-width="10" fill="none" opacity="0.6"/>'))


@shot("d_drop")
def _(t, D, c):
    """Over your shoulder: the dewdrop glitters ahead on a leaf."""
    cam = GAR
    L = [("sky", 0.1, sky("dawn", (760, 160)), True, None), ("forest", 0.25, forest(cam, 111), True, 2), ("leaf", 0.6, leaf_floor(420), True, None)]
    dx, dr = 600, 70
    tw = 0.5 + 0.5 * math.sin(t * 5)
    d = drop(dx, 420 - dr + 6, dr, t, 0.006) + sparkle(dx - 26, 420 - dr - 30, 10 + 6 * tw, "#FFFFFF", 0.9) + sparkle(dx + 30, 420 - dr + 20, 5 + 3 * tw, "#FFFFFF", 0.7)
    L.append(("drop", 0.7, d, False, None))
    L.append(("you", 1.2, g(back("stand", "stand", 0), 250, 700, 0.62), False, 2))
    return dict(layers=L, defs=sky_defs("dawn"), cam=(25 * ease(t / D), 0, 1.0 + 0.05 * ease(t / D)), overlay="")


@shot("d_stop")
def _(t, D, c):
    """Extreme close-up: your hand stops a finger's width from the water."""
    bg = sky("dawn", (700, 200), False) + f'<g filter="url(#b16)">{leaf_floor(470)}</g>'
    reach = ease(ramp(t, 0.0, 0.5))
    hx = 230 + 140 * reach
    sk = A.YOU.skin
    hand = (sh(S(f"M-120 460 Q{hx - 160:.1f} 380 {hx - 50:.1f} 330", 80), *A.YOU.top, 2) +
            sh(E(hx - 52, 330, 20, 44), A.YOU.top[1], A.YOU.top[1], A.YOU.top[2], 0.8) +
            sh(P(f"M{hx - 40:.1f} 300 Q{hx - 10:.1f} 280 {hx + 30:.1f} 296 Q{hx + 46:.1f} 320 {hx + 30:.1f} 352 Q{hx - 10:.1f} 372 {hx - 40:.1f} 356 Z"), *sk, 1.2) +
            sh(S(f"M{hx + 20:.1f} 302 Q{hx + 60:.1f} 292 {hx + 92:.1f} 296", 24), *sk, 0.6) +
            sh(S(f"M{hx - 20:.1f} 300 Q{hx:.1f} 284 {hx + 18:.1f} 286", 18), *sk, 0.5) +
            f'<ellipse cx="{hx + 94:.1f}" cy="296" rx="7" ry="6" fill="#FFE2D0" opacity="0.7"/>')
    d = drop(720, 300, 210, t, 0.01)
    L = [("bg", 0.3, bg, True, None), ("drop", 1.0, d, False, None), ("hand", 1.0, hand, False, None)]
    return dict(layers=L, defs=sky_defs("dawn"), cam=(0, 0, 1.0 + 0.06 * t), overlay="", )


@shot("d_tension")
def _(t, D, c):
    """Cross-section of a drop: molecules hold hands at the surface and pull inward."""
    bg = f'<rect x="-300" y="-300" width="1560" height="1140" fill="url(#cbg3)"/>'
    cx, cy, r = 400, 280, 190
    a = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#3AA8E0" opacity="0.25"/>']
    rr = random.Random(2)
    pts = []
    for k in range(70):
        ang, rad = rr.uniform(0, 6.283), r * math.sqrt(rr.random()) * 0.88
        pts.append((cx + math.cos(ang) * rad + 3 * math.sin(t * 3 + k), cy + math.sin(ang) * rad + 3 * math.cos(t * 2.6 + k)))
    for x, y in pts:
        a.append(ball(x, y, 9, "#9AE8FF", "#3A8CC8", "#EFFFFF"))
    ring = []
    for k in range(28):
        ang = 6.283 * k / 28
        ring.append((cx + math.cos(ang) * r * 0.97, cy + math.sin(ang) * r * 0.97))
    link = ramp(t, 1.0, 2.0)
    for i in range(28):
        (x1, y1), (x2, y2) = ring[i], ring[(i + 1) % 28]
        a.append(f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="#FFFFFF" stroke-width="3" opacity="{0.8*link:.2f}"/>')
    for x, y in ring:
        a.append(ball(x, y, 10, "#BFF4FF", "#4AA8E0", "#FFFFFF"))
    pull = ramp(t, 2.0, 3.0)
    if pull > 0:
        for x, y in ring[::3]:
            dx, dy = cx - x, cy - y
            a.append(f'<path d="M{x:.1f} {y:.1f} l{dx*0.18*pull:.1f} {dy*0.18*pull:.1f}" stroke="#FF4F9A" stroke-width="4" stroke-linecap="round"/>')
    c1 = c[1] if len(c) > 1 else 4.2
    if t > c1:
        k = A.out_back(ramp(t, c1, c1 + 0.5))
        y0 = 400
        cmp = (f'<g transform="translate(760 {y0}) scale({k:.3f})">' + g(front("stand", "stand", "surprised"), -50, 0, 0.3) +
               f'<path d="M30 -150 L30 -20" stroke="#FF4F9A" stroke-width="10" stroke-linecap="round"/><path d="M14 -40 L30 -16 L46 -40" stroke="#FF4F9A" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>')
        a.append(cmp)
    L = [("bg", 1.0, bg, True, None), ("act", 1.0, "".join(a), False, None)]
    ov = chip(400, 60, "surface tension", t, 0.8, "#2EA6C8", size=20) + chip(760, 470, "≈ 100× your weight", t, (c[1] if len(c) > 1 else 4.2) + 0.7, "#FF4F9A", size=20)
    return dict(layers=L, defs=V.lin("cbg3", [(0, "#3A1AA8"), (1, "#14084A")]), cam=(0, 0, 1.0), overlay=ov)


@shot("d_touch")
def _(t, D, c):
    """Side on, close: the water grabs your hand and creeps up your arm."""
    cam = GAR
    L = [("sky", 0.1, sky("dawn", (760, 160)), True, None), ("forest", 0.25, forest(cam, 121), True, 2), ("leaf", 0.6, leaf_floor(420), True, None)]
    top_ = 420
    dx, dr = 590, 46
    dcy = top_ - dr + 6
    yx = 520
    touch = ease(ramp(t, 0.3, 2.4))
    wob = 0.02 + 0.03 * touch
    act = drop(dx, dcy, dr, t, wob) + contact(yx, top_ - 2, 14) + g(front("point", "stand", "surprised" if touch > 0.2 else "neutral", -6 * touch, False), yx - 3 * math.sin(t * 9) * touch, top_ - 2, 0.15)
    if touch > 0:
        pts = [(dx - dr + 8, dcy - 8), (yx + 28, top_ - 64), (yx + 9, top_ - 54), (yx + 4, top_ - 30)]
        segs = touch * 3
        path = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
        for i in range(3):
            if segs <= 0:
                break
            f_ = min(1, segs)
            (xa, ya), (xb, yb) = pts[i], pts[i + 1]
            path += f" L{xa + (xb - xa)*f_:.1f} {ya + (yb - ya)*f_:.1f}"
            segs -= 1
        act += f'<g opacity="0.82">{sh(S(path, 10), "#8EE6FF", "#3AA8E0", "#E8FDFF", 0.3)}</g>'
    L.append(("act", 0.7, act, False, None))
    return dict(layers=L, defs=sky_defs("dawn"), cam=(-10, 70, 2.2 + 0.25 * ease(t / D)), overlay="")


@shot("d_wax")
def _(t, D, c):
    """Insect armor beads water away. Then you, in your soaked sweater."""
    cut = 3.3
    if t < cut:
        bg = f'<rect x="-300" y="-300" width="1560" height="1140" fill="url(#cbg3)"/>'
        legs = P("M120 330 Q480 290 840 330 L840 362 Q480 322 120 362 Z")
        a = [sh(legs, "#5A2846", "#341430", "#FF8AA0", 2)]
        for k in range(26):
            a.append(f'<path d="M{140 + k*27} {326 - 3*math.sin(k)} l-6 -14" stroke="#341430" stroke-width="3" stroke-linecap="round"/>')
        for k, (x, r) in enumerate([(230, 26), (390, 36), (560, 30), (720, 22)]):
            roll = 18 * t if k == 3 else 0
            a.append(drop(x + roll, 312 - r + 2 * math.sin(t * 3 + k), r, t))
        L = [("bg", 1.0, bg, True, None), ("act", 1.0, "".join(a), False, None)]
        ov = chip(480, 120, "waxy, water repelling armor", t, 0.4, "#2EA6C8", size=22)
        return dict(layers=L, defs=V.lin("cbg3", [(0, "#3A1AA8"), (1, "#14084A")]), cam=(0, 0, 1.0 + 0.03 * t), overlay=ov)
    u = t - cut
    cam = GAR
    L = garden_layers(cam, "dawn", 130, sun=(760, 160))
    yy = cam.gy(0.55)
    wet = front("brace", "stand", "sad", 0, False)
    drips = "".join(f'<circle cx="{-40 + k*16}" cy="{-300 + ((u*120 + k*37) % 160):.1f}" r="5" fill="#9AE8FF" opacity="0.85"/>' for k in range(6))
    act = contact(480, yy, 24) + g(wet + f'<g opacity="0.6">{drips}</g>', 480, yy, 0.22)
    L.append(("act", 0.75, act, False, None))
    ov = kinetic("you have a sweater", 480, 120, u, 0.1, 40)
    return dict(layers=L, defs=sky_defs("dawn"), cam=(0, 110, 2.2 + 0.1 * u), overlay=ov)
