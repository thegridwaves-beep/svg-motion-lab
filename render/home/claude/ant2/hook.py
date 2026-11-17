"""16-22 s motion test: the new cold open, animated shot by shot."""
import math, random, sys, json
sys.path.insert(0, "/home/claude/bible"); sys.path.insert(0, "/home/claude/ant")
import vivid as V
V.ANIM = True
from kit import inside, P, S, E, C, R, U, g, text
import assets as A
from assets import blade, drop, ant, spider, raindrop, glow, sparkle, ball, sh, label, GREENS, crumb, YOU, leaf, pebble
import ep1
ep1.MODE = "all"
import rig

W, H = 960, 540
ease = V.ease


def ramp(t, a, b):
    return A.ramp(t, a, b)


def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = max(0.0, min(1.0, x))
    return x ** 3


def cam(body, z, fx, fy, sx=W / 2, sy=H / 2):
    return f'<g transform="translate({sx:.2f} {sy:.2f}) scale({z:.5f}) translate({-fx:.3f} {-fy:.3f})">{body}</g>'


def kinetic(word, x, y, t, t0, size=72, col="#FFFFFF", anchor="middle", out_t=None):
    """Word slides up out of a mask, holds, and slides out upward."""
    if t < t0 or (out_t and t > out_t + 0.35):
        return ""
    u = ease_out((t - t0) / 0.32)
    dy = (1 - u) * size * 1.1
    if out_t and t > out_t:
        dy = -ease_in((t - out_t) / 0.3) * size * 1.1
    w = len(word) * size * 0.62 + 40
    x0 = x - w / 2 if anchor == "middle" else x - 20
    mid = f"km{abs(hash((word, t0))) % 10**8}"
    return (f'<clipPath id="{mid}"><rect x="{x0:.1f}" y="{y - size*1.05:.1f}" width="{w:.1f}" height="{size*1.35:.1f}"/></clipPath>'
            f'<g clip-path="url(#{mid})"><g transform="translate(0 {dy:.2f})">'
            + text(x, y + 3, word, size, "#0A0420", 700, anchor, op=0.35) + text(x, y, word, size, col, 700, anchor) + '</g></g>')


def you_at(arms, legs="stand", expr="neutral", tilt=0, blink=False, k=0.16, x=480, y=432, squash=1.0, rot=0):
    lg = rig.LEGS[legs] if isinstance(legs, str) else legs
    body = rig.person(YOU, arms, lg, expr, tilt, blink)
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k / squash**0.5:.5f} {k * squash:.5f})">{body}</g>'


def blinking(t, period=3.1, ph=0.0):
    return ((t + ph) % period) < 0.12


# ================================================================== S1: shrink dive (human garden -> ant world)
MACRO_DEFS = (V.lin("msky", [(0, "#4A3AE0"), (0.55, "#46A8F0"), (1, "#FFC8D8")]) + V.lin("mlawn", [(0, "#3FD68A"), (1, "#178A60")]))


def macro_world(t):
    rr = random.Random(41)
    o = [f'<rect x="-2000" y="-2000" width="5000" height="2600" fill="url(#msky)"/>']
    o.append(glow(780, 120, 160, "#FFF4D8", 0.6, 30) + ball(780, 120, 44, "#FFF8E0", "#FFE6A8", "#FFFFFF"))
    # far hedge and trees
    for k in range(14):
        x = -200 + k * 100 + rr.uniform(-20, 20)
        o.append(sh(C(x, 380, rr.uniform(60, 90)), "#2EA67A", "#17785A", "#7AE8B8", 2))
    # house corner with a window on the left
    o.append(sh(R(-260, 120, 360, 400, 8), "#FFB3C8", "#E07A9A", "#FFE0EA", 3))
    o.append(sh(R(-10, 200, 70, 90, 6), "#9AE8FF", "#4AA8E0", "#E8FBFF", 1))
    # fence
    for k in range(22):
        x = 120 + k * 44
        o.append(sh(P(f"M{x} 470 L{x} 340 L{x+14} 326 L{x+28} 340 L{x+28} 470 Z"), "#FFF4E8", "#D8C4D8", "#FFFFFF", 0.6))
    o.append(f'<rect x="110" y="380" width="1000" height="10" rx="4" fill="#E8D8E8"/>')
    o.append(f'<rect x="-2000" y="470" width="5000" height="1000" fill="url(#mlawn)"/>')
    # lawn blades at human scale
    for k in range(160):
        x = rr.uniform(-100, 1060); y = rr.uniform(468, 560); h = rr.uniform(10, 26) * (1 + (y - 470) / 60)
        c = rr.choice(GREENS)
        o.append(f'<path d="M{x-2:.1f} {y:.1f} Q{x:.1f} {y-h*0.6:.1f} {x+rr.uniform(-4,4):.1f} {y-h:.1f} Q{x+1:.1f} {y-h*0.5:.1f} {x+2:.1f} {y:.1f} Z" fill="{c[1] if rr.random()<0.5 else c[0]}"/>')
    for (x, y) in [(300, 500), (330, 520), (640, 505), (700, 530), (150, 520)]:
        for a in range(6):
            o.append(f'<ellipse cx="{x + 7*math.cos(a*1.05):.1f}" cy="{y + 7*math.sin(a*1.05):.1f}" rx="5" ry="3" fill="#FFFFFF" transform="rotate({a*60} {x + 7*math.cos(a*1.05):.1f} {y + 7*math.sin(a*1.05):.1f})"/>')
        o.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#FFD23A"/>')
    # micro detail at your feet (only visible as we dive)
    for k in range(40):
        x = 480 + rr.uniform(-14, 14); y = 470 + rr.uniform(-0.5, 2)
        h = rr.uniform(1.5, 4.5)
        o.append(f'<path d="M{x-0.25:.2f} {y:.2f} Q{x:.2f} {y-h*0.6:.2f} {x+rr.uniform(-0.6,0.6):.2f} {y-h:.2f} Q{x+0.1:.2f} {y-h*0.5:.2f} {x+0.25:.2f} {y:.2f} Z" fill="{rr.choice(GREENS)[0]}"/>')
    o.append(g(ant(t, 1.0), 486 - 0.6 * t, 470.3, 0.012, 0, flip=True))
    return "".join(o)


def micro_world(t):
    return ep1.garden_bg(t, ground=432) + ep1.grass_field(random.Random(21), 60, 360, 438, 150, 300, 18, 34, 8, 0.0) + \
        ep1.grass_field(random.Random(22), 640, 960, 438, 150, 320, 18, 34, 8, 0.0) + \
        blade(560, 436, 372, 40, -30, GREENS[0], 6 * math.sin(t * 0.9)) + drop(392, 300, 9, t) + drop(705, 270, 12, t) + \
        g(ant(t, 1.0), 620 - 22 * max(0, t - 2.4), 433, 0.78, 0, flip=True)


def s1(t):
    """0..3.5. Person stays the same size on screen; the world grows around them."""
    t_s0, t_s1 = 1.55, 3.0
    u = ramp(t, t_s0, t_s1)
    # anticipation crouch before shrinking, then a little stretch as you go
    sq = 1.0 - 0.06 * math.sin(math.pi * ramp(t, 1.2, 1.6)) + 0.05 * math.sin(math.pi * u)
    # macro camera: zoom 1 -> 26 into your feet, person on screen 260 tall with feet at y 470
    zm = 26 ** u
    s_human = 1 / zm
    feet_screen = 470 - 60 * u          # feet rise a bit so we see the ground as it opens up
    body = []
    mac = cam(macro_world(t), zm, 480, 470, 480, feet_screen)
    a_mac = 1 - ramp(u, 0.64, 0.78)
    body.append(f'<rect width="{W}" height="{H}" fill="#2A1680"/>')
    if u > 0.55:
        zmi = 0.42 * (zm / 26 ** 0.62) if u < 1 else 0.42 * 26 ** 0.38
        zmi *= 1 + 0.12 * ramp(t, t_s1, 3.5)
        body.append(cam(micro_world(t), zmi * 2.5, 480, 432, 480, feet_screen))
    if a_mac > 0:
        body.append(f'<g opacity="{a_mac:.3f}">{mac}</g>')
    # speed lines while diving
    if 0.05 < u < 0.98:
        rr = random.Random(int(t * 30))
        for k in range(26):
            a = rr.uniform(0, 2 * math.pi)
            r0 = rr.uniform(160, 520)
            body.append(f'<path d="M{480 + math.cos(a)*r0:.1f} {feet_screen - 130 + math.sin(a)*r0:.1f} l{math.cos(a)*60:.1f} {math.sin(a)*60:.1f}" stroke="#FFFFFF" stroke-width="2" opacity="{0.35*math.sin(math.pi*u):.2f}" stroke-linecap="round"/>')
    # you, constant size on screen
    blink = blinking(t, 2.2, 0.4)
    arms = rig.lerp_pose(rig.ARMS["stand"], rig.ARMS["brace"], ramp(t, 1.3, 1.7))
    expr = "neutral" if t < 1.4 else "surprised"
    k = 0.5 * (1 - 0.0 * u)
    body.append(f'<ellipse cx="480" cy="{feet_screen + 2:.1f}" rx="44" ry="7" fill="#140830" opacity="0.35"/>')
    body.append(you_at(arms, "stand", expr, 0, blink, k, 480, feet_screen, sq))
    return "".join(body), MACRO_DEFS + ep1.GARDEN_DEFS


# ================================================================== S2: heartbeat flatline
def s2(t):
    """3.5..6.2"""
    o = [f'<rect width="{W}" height="{H}" fill="#14072E"/>']
    o.append(glow(480, 300, 300, "#5A1A7A", 0.6, 30))
    # faint silhouette of tiny you in the dark
    o.append(f'<g opacity="0.18">{you_at(rig.ARMS["stand"], "stand", "neutral", 0, False, 0.2, 480, 470)}</g>')
    # ECG line drawn progressively
    beats = [0.45, 1.15]
    pts = []
    head_x = 60 + 840 * min(1, t / 2.3)
    xs = [60 + i * 3 for i in range(int((head_x - 60) / 3))]
    for x in xs:
        tt = (x - 60) / 840 * 2.3
        y = 250
        for b in beats:
            d = tt - b
            if -0.05 < d < 0.12:
                y += (-110 * math.exp(-((d - 0.02) / 0.018) ** 2) + 45 * math.exp(-((d - 0.06) / 0.02) ** 2))
        pts.append((x, y))
    if len(pts) > 1:
        d_ = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        flat = t > 1.4
        col = "#FF4F7A" if not flat else "#FF4F7A"
        o.append(f'<path d="{d_}" stroke="{col}" stroke-width="10" fill="none" opacity="0.25" filter="url(#b8)"/>')
        o.append(f'<path d="{d_}" stroke="{col}" stroke-width="3.5" fill="none" stroke-linejoin="round"/>')
        hx, hy = pts[-1]
        o.append(glow(hx, hy, 14, "#FF8AA0", 0.9, 4) + f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="4" fill="#FFFFFF"/>')
    # heart icon pulses on beats then dims
    hb = 1 + 0.18 * max(math.exp(-((t - b) / 0.08) ** 2) for b in beats)
    dim = 1 - 0.75 * ramp(t, 1.4, 2.0)
    heart = P("M0 22 Q-34 0 -24 -16 Q-14 -30 0 -14 Q14 -30 24 -16 Q34 0 0 22 Z")
    o.append(f'<g transform="translate(480 120) scale({1.6*hb:.3f})" opacity="{dim:.2f}">{sh(heart, "#FF4F7A", "#C0204A", "#FFB0C0", 0.7)}</g>')
    o.append(kinetic("ALMOST INSTANTLY", 480, 420, t, 1.15, 64, "#FFFFFF"))
    return "".join(o), ""


# ================================================================== S3: the fall you'd survive
def s3(t):
    """6.2..8.85: step off a leaf edge, drift down, land."""
    o = []
    # parallax layers: camera pans down with you
    pan = 260 * ease(ramp(t, 0.5, 2.0))
    o.append(f'<g transform="translate(0 {-pan*0.25:.1f})">{ep1.garden_bg(t, ground=700, seed=12)}</g>')
    o.append(f'<g transform="translate(0 {-pan*0.6:.1f})" filter="url(#b4)">' + ep1.grass_field(random.Random(3), -100, 1060, 800, 300, 500, 30, 60, 14, t) + '</g>')
    mid = []
    mid.append(leaf(300, 230, 420, 70, 6, ("#46E08A", "#1EA864", "#C2FFD8")))
    mid.append(f'<rect x="-100" y="{560}" width="1160" height="400" fill="#3A1A7A"/>')
    for k in range(18):
        mid.append(pebble(40 + k * 55, 565 + (k % 3) * 8, 14, 8))
    o.append(f'<g transform="translate(0 {-pan:.1f})">{"".join(mid)}</g>')
    # you: walk to the edge, step off, drift with a gentle sway, land
    if t < 0.55:
        x, y, rot, arms, legs = 430 + 60 * ramp(t, 0, 0.55), 236, 0, rig.ARMS["walk"], "walk"
        expr = "neutral"
    elif t < 2.05:
        u = (t - 0.55) / 1.5
        x = 490 + 30 * u + 10 * math.sin(u * 6)
        y = 236 + (560 - 236) * (u ** 1.15) - pan
        rot = 12 * math.sin(u * 5)
        arms, legs, expr = rig.ARMS["fall"], "fall", "surprised"
    else:
        x, y, rot = 520, 560 - pan, 0
        arms = rig.lerp_pose(rig.ARMS["brace"], rig.ARMS["thumbs"], ramp(t, 2.15, 2.5))
        legs, expr = "stand", "happy"
    if t < 0.55:
        y = 236 - pan
    sq = 1 - 0.12 * math.sin(math.pi * min(1, max(0, (t - 2.05) / 0.25)))
    o.append(you_at(arms, legs, expr, 0, blinking(t, 2.6), 0.16, x, y, sq, rot))
    if 2.0 < t < 2.6:
        u = (t - 2.0) / 0.6
        for k in range(7):
            a = math.pi * k / 6
            o.append(f'<circle cx="{x + math.cos(a)*30*u:.1f}" cy="{y - math.sin(a)*10*u:.1f}" r="{4*(1-u):.1f}" fill="#C8B8FF" opacity="{1-u:.2f}"/>')
    # air streaks during the drift
    if 0.6 < t < 2.0:
        rr = random.Random(9)
        for k in range(8):
            yy = (rr.uniform(0, 400) - t * 500) % 400
            o.append(f'<path d="M{x + rr.uniform(-50, 50):.1f} {y - 60 + yy - 200:.1f} l0 -28" stroke="#FFFFFF" stroke-width="2" opacity="0.4" stroke-linecap="round"/>')
    o.append(A.popin(label(x, y - 112, "survivable", "#2EB872", size=18), x, y - 112, t, 1.25))
    o.append(f'<g transform="translate(0 {-pan*1.6:.1f})">{ep1.fg_blades(t, 31, 900, 6)}</g>')
    zf = 1.9
    return cam("".join(o), zf, x, y - 40), ep1.GARDEN_DEFS


# ================================================================== S4: the montage
def s4a(t):
    """spiders: legs sweep in, eyes glint."""
    o = [ep1.garden_bg(t, ground=432, seed=5, warm=0.5)]
    o.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#0A0420" opacity="0.35"/>')
    o.append(f'<ellipse cx="480" cy="434" rx="16" ry="3" fill="#140830" opacity="0.5"/>')
    z = 2.4 + 0.25 * t
    inner = you_at(rig.lerp_pose(rig.ARMS["stand"], rig.ARMS["brace"], ramp(t, 0.2, 0.5)), "stand", "surprised", -4, False, 0.16, 480, 432)
    sx = 760 - 160 * ease_out(ramp(t, 0.0, 0.8))
    inner += g(A.spider(t), sx, 400, 1.3, 0, flip=True)
    o.append(cam(inner, z, 500, 380))
    o.append(kinetic("SPIDERS", 480, 120, t, 0.15, 70))
    return "".join(o), ep1.GARDEN_DEFS


def s4b(t):
    """cold: frost grows over the frame."""
    o = [ep1.garden_bg(t, ground=432, seed=6, warm=0.2)]
    o.append(f'<rect width="{W}" height="{H}" fill="#4A8AE0" opacity="0.3"/>')
    jit = 1.2 * math.sin(t * 50)
    o.append(cam(you_at(rig.ARMS["shiver"], "stand", "sad", 0, False, 0.16, 480 + jit * 0.1, 432), 2.8 + 0.2 * t, 480, 385))
    rr = random.Random(4)
    fr = ease_out(ramp(t, 0.0, 0.8))
    for k in range(70):
        a = rr.uniform(0, 2 * math.pi)
        d = 560 - fr * rr.uniform(120, 330)
        x, y = 480 + math.cos(a) * d * 1.2, 270 + math.sin(a) * d * 0.7
        o.append(sparkle(round(x), round(y), rr.uniform(6, 16) * fr + 1, "#E8F8FF", 0.85))
    o.append(f'<rect width="{W}" height="{H}" fill="none" stroke="#E8F8FF" stroke-width="{120*fr:.1f}" opacity="0.35" filter="url(#b16)"/>')
    o.append(kinetic("COLD", 480, 120, t, 0.1, 70, "#E8F8FF"))
    return "".join(o), ep1.GARDEN_DEFS


def s4c(t):
    """rain: a drop the size of a car falls straight at us."""
    o = [ep1.garden_bg(t, ground=432, seed=7, warm=0.3)]
    o.append(f'<rect width="{W}" height="{H}" fill="#2A3A8A" opacity="0.4"/>')
    o.append(cam(you_at(rig.ARMS["head"], "crouch", "surprised", 0, False, 0.16, 480, 432), 2.4, 480, 380))
    u = ramp(t, 0.0, 0.75)
    r = 20 + 280 * ease_in(u)
    o.append(raindrop(480, -60 + 330 * ease_in(u), r))
    if t > 0.72:
        v = ramp(t, 0.72, 0.95)
        o.append(f'<rect width="{W}" height="{H}" fill="#DFF6FF" opacity="{0.9*(1-abs(2*v-1)):.2f}"/>')
    o.append(kinetic("RAIN", 480, 120, t, 0.05, 70, "#14286A"))
    return "".join(o), ep1.GARDEN_DEFS


def s4d(t):
    """coming for you: everything converges, camera slowly pulls out."""
    o = [ep1.garden_bg(t, ground=432, seed=8, warm=0.25, sun=(820, 60))]
    o.append(f'<rect width="{W}" height="{H}" fill="#1A0A3A" opacity="0.35"/>')
    inner = []
    inner.append(ep1.grass_field(random.Random(23), 40, 380, 438, 150, 300, 18, 34, 9, t))
    inner.append(ep1.grass_field(random.Random(24), 600, 960, 438, 150, 300, 18, 34, 9, t))
    sy = 150 + 120 * ease_out(ramp(t, 0.0, 1.5))
    inner.append(f'<path d="M330 -300 L330 {sy - 20:.1f}" stroke="#E8E0FF" stroke-width="1.2"/>' + g(A.spider(t), 330, sy, 0.55, 90))
    for k in range(3):
        ax = 760 + k * 70 - 50 * t
        inner.append(g(ant(t + k * 0.4, 1.0), ax, 430, 0.5, 0, flip=True))
    inner.append(f'<ellipse cx="480" cy="434" rx="14" ry="3" fill="#140830" opacity="0.5"/>')
    inner.append(you_at(rig.ARMS["brace"], "stand", "surprised", 3 * math.sin(t * 1.3), blinking(t, 1.8), 0.16, 480, 432))
    rr = random.Random(2)
    for k in range(30):
        x = rr.uniform(-100, 1060); y = (rr.uniform(-300, 400) + t * 330) % 700 - 300
        inner.append(raindrop(x, y, rr.uniform(6, 10), 0.7))
    z = 2.6 - 1.2 * ease(ramp(t, 0.0, 2.1))
    o.append(cam("".join(inner), z, 480, 360))
    fr = 0.5 + 0.2 * t
    o.append(f'<rect width="{W}" height="{H}" fill="none" stroke="#DFF4FF" stroke-width="{60*fr:.1f}" opacity="0.18" filter="url(#b16)"/>')
    return "".join(o), ep1.GARDEN_DEFS


# ================================================================== S5: inside your head
def s5(t):
    """14.4..17.6: push into your face; the head turns see-through and the brain glows red."""
    o = [ep1.garden_bg(t, ground=432, seed=9, warm=0.4)]
    o.append(f'<rect width="{W}" height="{H}" fill="#0A0420" opacity="{0.25 + 0.4*ramp(t, 0.8, 1.6):.2f}"/>')
    z = 4.5 + 5.0 * ease(ramp(t, 0.0, 2.6))
    fy = 432 - 0.16 * 444
    you = you_at(rig.ARMS["stand"], "stand", "neutral" if t < 1.0 else "surprised", 0, blinking(t, 2.4, 0.9), 0.16, 480, 432)
    xr = ramp(t, 0.9, 1.6)
    brain = ""
    if xr > 0:
        hx, hy = 480, fy - 2
        rr = random.Random(3)
        lobes = "".join(f'<circle cx="{hx + rr.uniform(-4, 4):.2f}" cy="{hy - 4 + rr.uniform(-2, 1.5):.2f}" r="{rr.uniform(2.2, 3.4):.2f}" fill="#FF7AB0"/>' for _ in range(12))
        pulse = 0.5 + 0.5 * math.sin(t * 7)
        sparks = "".join(f'<circle cx="{hx + rr.uniform(-6, 6):.2f}" cy="{hy - 4 + rr.uniform(-4, 4):.2f}" r="0.5" fill="#FFFFFF" opacity="{(0.5 + 0.5*math.sin(t*9 + k)):.2f}"/>' for k in range(10))
        brain = (glow(hx, hy - 4, 10 + 3 * pulse, "#FF2A5A", 0.8 * xr, 4) + f'<g opacity="{xr:.2f}">{lobes}{sparks}</g>')
    skull = E(480, fy - 3.6, 7.3, 5.3)
    o.append(cam(you + inside(skull, f'<rect x="460" y="{fy - 20:.2f}" width="40" height="40" fill="#2A0A3A" opacity="{0.6*xr:.2f}"/>' + brain), z, 480, fy + 3))
    o.append(f'<rect width="{W}" height="{H}" fill="url(#redvig)" opacity="{ramp(t, 1.2, 2.0):.2f}"/>')
    return "".join(o), ep1.GARDEN_DEFS + '<radialGradient id="redvig" cx="0.5" cy="0.5" r="0.7"><stop offset="0.55" stop-color="#FF2A5A" stop-opacity="0"/><stop offset="1" stop-color="#7A0A2A" stop-opacity="0.6"/></radialGradient>'


# ================================================================== S6: cheat death, start the clock
def s6(t):
    """17.6..22: brighten, the survival clock slams in and starts counting."""
    o = [ep1.garden_bg(t, ground=432, seed=21, warm=1.0)]
    inner = ep1.grass_field(random.Random(21), 60, 360, 438, 150, 300, 18, 34, 8, t) + ep1.grass_field(random.Random(22), 640, 960, 438, 150, 320, 18, 34, 8, t)
    arms = rig.lerp_pose(rig.ARMS["stand"], rig.ARMS["fist"], ramp(t, 0.6, 1.0))
    inner += f'<ellipse cx="480" cy="434" rx="14" ry="3" fill="#140830" opacity="0.5"/>'
    inner += you_at(arms, "stand", "neutral" if t < 0.6 else "happy", -4 * ramp(t, 0.6, 1.0), blinking(t, 2.9, 1.5), 0.16, 480, 432)
    o.append(cam(inner, 2.4 - 0.5 * ease(ramp(t, 0, 4)), 480, 370))
    # clock
    k = A.out_back(ramp(t, 0.2, 0.65)) if t > 0.2 else 0
    if k > 0:
        el = max(0.0, t - 1.6)
        mm, ss, cs = int(el // 60), int(el % 60), int((el * 100) % 100)
        face = (f'<rect x="-170" y="-46" width="340" height="92" rx="24" fill="#140A3A" opacity="0.88"/>'
                f'<rect x="-170" y="-46" width="340" height="92" rx="24" fill="none" stroke="#FF4F9A" stroke-width="3"/>'
                + text(0, 22, f"{mm:02d}:{ss:02d}.{cs:02d}", 58, "#FFFFFF", 700, "middle") +
                f'<circle cx="-140" cy="0" r="7" fill="#FF4F7A" opacity="{0.5 + 0.5*math.sin(t*8):.2f}"/>')
        o.append(f'<g transform="translate(480 110) scale({k:.3f})">{face}</g>')
    o.append(kinetic("How long would you last?", 480, 480, t, 2.2, 40, "#FFFFFF"))
    return "".join(o), ep1.GARDEN_DEFS


SHOTS = [(0.0, 3.5, s1), (3.5, 6.2, s2), (6.2, 8.85, s3), (8.85, 10.2, s4a), (10.2, 11.25, s4b), (11.25, 12.3, s4c),
         (12.3, 14.4, s4d), (14.4, 17.6, s5), (17.6, 22.0, s6)]
TOTAL = 22.0


def frame(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            body, defs = fn(t - t0)
            return V.svg(body, defs)
    return V.svg("", "")
