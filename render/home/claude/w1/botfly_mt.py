"""Botfly motion test: the first 13 s (lines 0-3) re-cut with aggressive camera language:
crash zoom, slam landing, 180 orbit with rack focus, whip pan, jungle chase with impact frame, falling-egg dive,
and a dive straight through the skin into the x-ray."""
import os
os.environ.setdefault("SHORT", "botfly")
import anim_core
from botfly import *          # props (skin, eggs, mosquito with eggs, botfly, grub, cross-section)
anim_core.ANIM[:] = []        # this module defines its own shots

TEND_MT = round(Ln(4) - 0.35, 3)


def fg_hairs(t, seed=11, n=7, speed=0.0, op=0.9, blur=6):
    """Out-of-focus hairs right in front of the lens (put on a deep layer, depth ~2.2): sells depth when the camera moves."""
    r = random.Random(seed); o = []
    for k in range(n):
        x = r.uniform(150, 810) + speed * t; y = r.uniform(380, 720); L = r.uniform(260, 460); a = r.uniform(-0.5, 0.5)
        o.append(f'<path d="M{x:.0f} {y:.0f} q{L * 0.3 * math.sin(a):.0f} {-L * 0.5:.0f} {L * math.sin(a + 0.4):.0f} {-L:.0f}" stroke="#4A2E22" stroke-width="{r.uniform(10, 18):.0f}" fill="none" stroke-linecap="round" opacity="{op:.2f}"/>')
    return f'<g filter="url(#b{blur})">{"".join(o)}</g>'


def dust(t, seed=3, n=40, drift=(12, -8), col="#FFF4DC", op=0.55):
    r = random.Random(seed); o = []
    for k in range(n):
        x = (r.uniform(-200, 1160) + drift[0] * t) % 1360 - 200; y = (r.uniform(-300, 900) + drift[1] * t) % 1200 - 300
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(1.5, 4):.1f}" fill="{col}" opacity="{op * r.uniform(0.3, 1):.2f}"/>')
    return "".join(o)


def flare(x, y, u, col="#FFF4DC"):
    if u <= 0:
        return ""
    return (glow(x, y, 120 * u, col, 0.7 * u, 18) + f'<path d="M{x - 220 * u:.0f} {y} L{x + 220 * u:.0f} {y}" stroke="{col}" stroke-width="3" opacity="{0.8 * u:.2f}"/>'
            + f'<path d="M{x} {y - 90 * u:.0f} L{x} {y + 90 * u:.0f}" stroke="{col}" stroke-width="2" opacity="{0.6 * u:.2f}"/>'
            + f'<circle cx="{x + 140 * u:.0f}" cy="{y + 60 * u:.0f}" r="{14 * u:.0f}" fill="{col}" opacity="{0.25 * u:.2f}"/>')


def streaks(t, cx, cy, u, col="#FFFFFF", n=34, seed=4):
    """Radial speed streaks for crash zooms (u = strength)."""
    if u <= 0:
        return ""
    return air_like(t, cx, cy, u, col, n, seed)


def air_like(t, cx, cy, u, col, n, seed):
    r = random.Random(seed); o = []
    for i in range(n):
        a = r.uniform(0, TAU); z = (r.random() + t * 3.0) % 1.0
        d = 60 + 420 * z ** 1.4; ln = 30 + 200 * z ** 2
        o.append(f'<path d="M{cx + d * math.cos(a):.1f} {cy + d * math.sin(a):.1f} L{cx + (d + ln) * math.cos(a):.1f} {cy + (d + ln) * math.sin(a):.1f}" stroke="{col}" stroke-width="{2 + 6 * z:.1f}" stroke-linecap="round" opacity="{u * 0.6 * min(1, z * 3):.2f}"/>')
    return "".join(o)


def hstreaks(u, col="#FFFFFF", y0=-60, y1=600, n=26, seed=6):
    """Horizontal smear for whip pans."""
    if u <= 0:
        return ""
    r = random.Random(seed)
    return "".join(f'<rect x="200" y="{r.uniform(y0, y1):.0f}" width="560" height="{r.uniform(6, 30):.0f}" fill="{col}" opacity="{0.25 * u * r.uniform(0.4, 1):.2f}" filter="url(#b10)"/>' for _ in range(n))


def flashw(u, col="#FFFFFF"):
    return f'<rect x="200" y="-200" width="560" height="900" fill="{col}" opacity="{clamp(u):.2f}"/>' if u > 0 else ""


def leaves_fg(t, speed, seed=9, n=7):
    r = random.Random(seed); o = []
    for k in range(n):
        x = (r.uniform(0, 1400) - speed * t) % 1600 - 300; y = r.uniform(-100, 650); s_ = r.uniform(1.6, 3.2)
        o.append(f'<g transform="translate({x:.0f} {y:.0f}) rotate({r.uniform(-40, 40):.0f}) scale({s_:.2f})"><path d="M0 0 Q60 -40 140 0 Q60 40 0 0 Z" fill="{r.choice(("#1E5A2A", "#2E7A3A", "#14401E"))}"/><path d="M0 0 L140 0" stroke="#0A2A12" stroke-width="2"/></g>')
    return f'<g filter="url(#b8)">{"".join(o)}</g>'


# ================================================================== shots
@shot5(0.0, "mt1", "CRASH ZOOM: wide on the boy on the couch at dusk; the camera rockets at his forearm, streaks flying past.")
def mt1(t, D):
    u = ei(ramp(t, 0, D))
    J = SIT | dict(el=(-84, -284), hl=(-20, -236), er=(84, -290), hr=(30, -240), face=fc(open=0.9, mouth="smile", look=(0.3, 0.4)))
    body = boy(J, "mt1", 450, 498, 0.62, LI)
    ph = '<rect x="430" y="330" width="34" height="56" rx="6" fill="#1A1A24"/><rect x="433" y="334" width="28" height="48" rx="4" fill="#5AE8FF" opacity="0.8"/>'
    ax, ay = 450 - 0.62 * 20, 498 - 0.62 * 236
    cam = (lerp(-30, ax - CX, u), lerp(20, ay - CY, u), lerp(1.2, 7.0, u), lerp(0, -18, u))
    return SV([(living_room(t, 0.1), 0.9, True), (body + ph, 1.0, False), ui(streaks(t, CX, CY, u) + flashw(ramp(t, D - 0.08, D), "#FFE8D0"))], cam, lights=(LI,))


@shot5(0.85, "mt2", "SLAM: macro on the skin, a mosquito drops from above the lens and slams down; the camera kicks and rolls with the landing. Hairs blur past in front.")
def mt2(t, D):
    land = eo(ramp(t, 0.0, 0.45)); settle = ramp(t, 0.45, 0.8)
    s = lerp(5.5, 2.4, land)
    mx, my = 470, lerp(-60, 300, land)
    m = mosq_eggs(mx, my, s, t, rot=lerp(-30, 8, land), land=land > 0.9, flap=1 - 0.9 * land, seed=2)
    kick = 18 * math.sin(math.pi * clamp((t - 0.45) / 0.25)) * (1 - settle)
    sh = f'<ellipse cx="{mx + 10:.0f}" cy="350" rx="{lerp(140, 70, land):.0f}" ry="12" fill="#5A2A1A" opacity="{0.3 * land:.2f}" filter="url(#b6)"/>'
    cam = (lerp(-20, 0, eio(ramp(t, 0, D))), lerp(10, 30, land) + kick, lerp(1.35, 1.75, eio(ramp(t, 0.4, D))), lerp(-14, 0, eio(ramp(t, 0, 0.7))) + 0.15 * kick)
    return SV([(skin_macro(), 0.8, True), (sh + m, 1.0, False), (dust(t, 3, 30), 1.4, False), (fg_hairs(t, 11, 5, 40), 2.2, False)], cam, lights=(L_ARM,))


@shot5(Ln(1) - 0.15, "mt3", "180 ORBIT with RACK FOCUS: the camera swings around the mosquito (a true 3D turn: side, head-on with the needle pointing at us, then the other side); a glint flares off the eggs, then a CRASH ZOOM onto them.")
def mt3(t, D):
    from mosq3d import mosq3d
    u = eio(ramp(t, 0, D * 0.72)); cz = ei(ramp(t, D * 0.72, D))
    yaw = lerp(-10, -170, u)
    m = mosq3d(470, 300, 3.0, yaw, t, eggs=True)
    fl = flare(lerp(450, 500, u), 336, clamp(1 - abs(u - 0.8) * 5))
    bg = f'<g filter="url(#b{4 if u < 0.5 else 2})">{skin_macro(5)}</g>'
    cam = (lerp(-90, 90, u), lerp(40, 60, u), lerp(1.7, 2.0, u) + 2.2 * cz, lerp(-12, 12, u))
    return SV([(bg, 0.45, True), (m + fl, 1.0, False), (fg_hairs(t, 13, 4, 0, 0.8, 8), 2.4, False), ui(streaks(t, CX, CY, cz, "#FFF4DC"))], cam, lights=(L_ARM,))


@shot5(Ln(2) - 0.1, "mt4", "WHIP PAN into the jungle flashback: the camera races sideways alongside a mosquito in flight, leaves ripping past in the foreground.")
def mt4(t, D):
    u = eio(ramp(t, 0, D))
    wp = 1 - ramp(t, 0, 0.3)
    m = mosq_eggs(480 + 30 * math.sin(t * 3), 300 + 20 * math.sin(t * 2.3), 1.9, t, rot=-6, flap=1.0, gone=tuple(range(7)), seed=4)
    cam = (lerp(-60, 0, u), 0, 1.45, lerp(10, 0, u))
    tint = '<rect x="-600" y="-600" width="2160" height="1800" fill="#E8D890" opacity="0.08"/>'
    return SV([(jungle(t), 0.35, True), (m, 1.0, False), (leaves_fg(t, 900), 2.0, False), (tint, 1.0, True),
               ui(hstreaks(wp, "#E8FFC8") + chip("EARLIER", 480, 40, ramp(t, 0.15, 0.4), 18, edge="#C8FF7A"))], cam, lights=(L_JUN,))


@shot5(Pn(2, 0) + 1.15, "mt5", "IMPACT: the botfly dives in from above and grabs the mosquito; a white impact frame, a punch-in, then slow motion as it presses its eggs onto the mosquito's belly.")
def mt5(t, D):
    hit_t = 0.35
    dive = eo(ramp(t, 0, hit_t)); slow = ramp(t, hit_t, D)
    press = eo(ramp(t, hit_t + 0.2, D * 0.9))
    bx, by = lerp(560, 452, dive), lerp(-160, 226, dive)
    m = mosq_eggs(462, 318, 1.9, t * (0.3 if t > hit_t else 1), rot=-4, flap=0.4 if t > hit_t else 1.0, gone=tuple(range(int(7 * (1 - press)))), seed=4)
    f = botfly(bx, by, 1.7, t * (0.25 if t > hit_t else 1), rot=lerp(40, 4, dive), flap=1.0)
    punch = 0.35 * math.exp(-max(0, t - hit_t) * 6) if t > hit_t else 0
    cam = (lerp(0, -10, slow), lerp(-40, 20, dive), 1.5 + punch + 0.25 * slow, lerp(6, -6, slow))
    return SV([(jungle(t * 0.3), 0.35, True), (m + f, 1.0, False), (leaves_fg(t * (0.2 if t > hit_t else 1), 900, 12, 4), 2.0, False),
               ui(flashw(clamp(1 - abs(t - hit_t) / 0.06)) + chip("EARLIER", 480, 40, 1.0, 18, edge="#C8FF7A"))], cam, lights=(L_JUN,))


@shot5(Ln(3) - 0.15, "mt6", "VERTICAL DIVE: the camera falls with one egg from the mosquito's belly down to his skin, which rushes up to meet us; it lands, bounces, glows warm and cracks.")
def mt6(t, D):
    fall = ei(ramp(t, 0, D * 0.45)); land_ = ramp(t, D * 0.45, D * 0.55)
    bounce = 12 * math.sin(math.pi * clamp((t - D * 0.45) / 0.18)) * (1 - ramp(t, D * 0.45, D * 0.65))
    crack = ramp(t, D * 0.72, D); warm = ramp(t, D * 0.5, D * 0.75)
    skin = f'<g transform="translate(480 330) scale({lerp(0.25, 1.0, fall):.3f}) translate(-480 -330)">{skin_macro(5)}</g>'
    m = mosq_eggs(470, lerp(260, -420, fall), 3.0, t, rot=6, land=True, flap=0.0, gone=(3,), seed=2)
    e = egg(480, 330 - bounce, 3.0, 80 + 60 * (1 - fall), crack, t, warm)
    heat = "".join(f'<path d="M{450 + 30 * k} 300 q12 -30 0 -60 q-12 -30 0 -60" stroke="#FF9A6A" stroke-width="4" fill="none" opacity="{0.4 * warm * (0.5 + 0.5 * math.sin(t * 6 + k)):.2f}"/>' for k in range(3))
    sz = 1.9 + 1.1 * eo(ramp(t, D * 0.7, D * 0.8))
    cam = (0, 30, sz, lerp(-40, 0, fall))
    return SV([(skin, 1.0, False), (m + heat + e, 1.0, False), (dust(t, 8, 26, (0, -90)), 1.6, False), ui(streaks(t, CX, CY, 0.7 * (1 - fall) * ramp(t, 0, 0.1)))], cam, lights=(L_ARM,))


@shot5(Pn(3, 1) - 0.05, "mt7", "DIVE THROUGH THE SKIN: the camera plunges into the surface; skin, then pink dermis, then fat rush past the lens in layers, and we land in the x-ray cross-section as the maggot burrows down past camera.")
def mt7(t, D):
    th = 0.9
    if t < th:
        u = ei(t / th); o = []
        cols = ["#F2C2A2", "#F0A08E", "#C86A62", "#B8202E", "#F4D890"]
        for k, c in enumerate(cols):
            z = 0.3 + k * 0.5 - 2.6 * u
            if z <= 0.02:
                continue
            R = 160 / z
            o.append(f'<circle cx="480" cy="270" r="{R:.0f}" fill="{c}" opacity="{clamp(1.4 - z * 0.4):.2f}"/>')
        o.reverse()
        bg = '<rect x="-600" y="-600" width="2160" height="1800" fill="#3A1A2A"/>' + "".join(o)
        return SV([(bg, 1.0, False), ui(streaks(t, CX, CY, 0.9, "#FFE8D8"))], (0, 0, 1.0, 40 * u))
    v = (t - th) / max(1e-6, D - th)
    dig = eo(v)
    g = grub(480, SURF + 10 + 170 * dig, lerp(0.6, 0.95, dig), t, rot=90, wig=1.0)
    trail = f'<path d="M480 {SURF} L480 {SURF + 170 * dig:.0f}" stroke="#7A2A3A" stroke-width="{18 * lerp(0.6, 0.95, dig):.0f}" stroke-linecap="round"/>'
    cam = (lerp(30, 0, v), lerp(40, 190, eio(v)), lerp(2.2, 1.7, eio(v)), lerp(20, 0, eo(v)))
    return SV([(skin_xsec(t, pocket=0.0, hair=True), 1.0, False), (trail + g, 1.0, False), ui(flashw(1 - ramp(t, th, th + 0.12), "#FFE8D8"))], cam)


# ================================================================== part 2 (lines 4-9)
TEND_FULL = 30.099


def bubbles(t, x, y0, y1, n=6, speed=90, op=0.75, seed=2):
    r = random.Random(seed); o = []
    for k in range(n):
        yy = y0 - ((t * speed + k * (y0 - y1) / n) % max(1, (y0 - y1)))
        o.append(f'<circle cx="{x + 5 * math.sin(t * 5 + k):.1f}" cy="{yy:.1f}" r="{r.uniform(2.5, 6):.1f}" fill="#E8FAFF" opacity="{op:.2f}" stroke="#FFFFFF" stroke-width="1"/>')
    return "".join(o)


@shot5(Ln(4) - 0.35, "mt8", "TIME-LAPSE ORBIT inside the pocket: the camera circles the maggot as it fattens up; a counter spins WEEK 1 to WEEK 6; blood cells stream past behind.")
def mt8(t, D):
    u = eio(ramp(t, 0, D))
    wk = 1 + int(5 * ramp(t, 0.2, D * 0.9))
    g = grub(480, SURF + 92, lerp(0.85, 1.25, u), t, rot=90, wig=0.7)
    b = bubbles(t, 480, SURF + 30, SURF - 40, 4, 50)
    cam = (lerp(-50, 50, u), 90, lerp(1.5, 1.85, u), lerp(-22, 22, u))
    return SV([(skin_xsec(t * 2.5, pocket=lerp(0.85, 1.15, u), hair=False), 1.0, False), (g + b, 1.0, False),
               ui(chip(f"WEEK {wk}", 480, 60, ramp(t, 0.1, 0.4), 24, edge="#FF8A6A"))], cam)


@shot5(Pn(4, 1) - 0.1, "mt9", "CRANE UP THE BREATHING TUBE: the camera rides the air bubbles up from the maggot's tail, through the little hole, and bursts out onto the skin surface.")
def mt9(t, D):
    u = eio(ramp(t, 0, D * 0.8))
    g = grub(480, SURF + 92, 1.25, t, rot=90, wig=0.5)
    b = bubbles(t, 480, SURF + 40, SURF - 120, 7, 130, 0.9, 5)
    burst = ramp(t, D * 0.72, D * 0.85)
    cam = (0, lerp(90, -60, u), lerp(1.9, 3.2, eio(ramp(t, D * 0.55, D))), lerp(10, -10, u))
    return SV([(skin_xsec(t, pocket=1.15, hair=True), 1.0, False), (g + b, 1.0, False), ui(flashw(clamp(1 - abs(t - D * 0.85) / 0.08) * 0.85, "#FFE8D8"))], cam)


@shot5(Ln(5) - 0.05, "mt10", "REVERSE CRASH ZOOM: from the macro hole the camera rockets back out to reveal the boy on the couch staring at his arm in horror.")
def mt10(t, D):
    u = eo(ramp(t, 0, D * 0.8))
    J = SIT | dict(el=(-84, -284), hl=(-10, -300), er=(84, -290), hr=(0, -320), head=(0, 12, 0),
                   face=fc(open=1.45, lift=1.1, knit=0.4, mouth="o", mo=0.5, look=(-0.2, 1.0)))
    body = boy(J, "mt10", 450, 498, 0.62, LI)
    ax, ay = 450 - 0.62 * 10, 498 - 0.62 * 300
    bump = f'<circle cx="{ax + 8:.1f}" cy="{ay + 14:.1f}" r="5" fill="#E86A5A"/>' + glow(ax + 8, ay + 14, 16, "#FF5A4A", 0.7, 4)
    cam = (lerp(ax + 8 - CX, -20, u), lerp(ay + 14 - CY, 20, u), lerp(9.0, 1.45, u), lerp(25, 0, u))
    return SV([(living_room(t, 0.1), 0.9, True), (body + bump, 1.0, False), ui(streaks(t, CX, CY, (1 - u) * 0.9))], cam, lights=(LI,))


@shot5(Pn(5, 0) + 0.75, "mt11", "ECU on the bump: it bulges and twitches under the skin; the camera kicks with every wriggle.")
def mt11(t, D):
    kick = 6 * math.sin(t * 22) * (0.5 + 0.5 * math.sin(t * 4))
    arm = arm_close(170, 290, 2.2, -4, bump=1.0, t=t, wig=1.8, hole=1.0)
    cam = (-10 + kick * 0.4, kick * 0.3, lerp(1.6, 2.2, eio(ramp(t, 0, D))), lerp(-8, 6, ramp(t, 0, D)))
    return SV([('<rect x="-600" y="-600" width="2160" height="1800" fill="url(#lroomW)"/>', 0.7, True), (arm, 1.0, False)], cam, lights=(LI,))


@shot5(Ln(6) - 0.15, "mt12", "LOW DUTCH on his face: horror... then his eyes narrow, an idea. WHIP to the right.")
def mt12(t, D):
    idea = ramp(t, D * 0.45, D * 0.65)
    J = R3.FRONT | dict(head=(0, 0, lerp(-6, 4, idea)), face=fc(open=lerp(1.5, 0.8, idea), lift=lerp(1.1, 0.3, idea), knit=lerp(0.4, 0.7, idea),
                                                            mouth="o" if idea < 0.5 else "smirk", mo=lerp(0.6, 0.0, idea), look=(lerp(0.2, 0.8, idea), lerp(0.9, -0.2, idea))))
    face = boy(J, "mt12", 480, 640, 1.0, LI)
    wp = ramp(t, D - 0.25, D)
    cam = (lerp(0, 160, ei(wp)), lerp(-20, -50, eio(ramp(t, 0, D))), 1.55, lerp(-10, -3, idea))
    return SV([('<rect x="-600" y="-600" width="2160" height="1800" fill="url(#lroomW)"/>' + glow(480, 120, 200, "#FFE8C8", 0.4, 30), 0.7, True), (face, 1.0, False), ui(hstreaks(wp))], cam, lights=(LI,))


@shot5(Ln(7) - 0.1, "mt13", "TRACKING into the kitchen: he grabs a strip of bacon mid-stride; SLOW MOTION slap onto his arm with an impact flash and a punch-in. Deadpan stare into the lens.")
def mt13(t, D):
    walk = eio(ramp(t, 0, D * 0.4)); slap_t = D * 0.62
    slap = eo(ramp(t, D * 0.45, slap_t))
    J = R3.FRONT | dict(el=(-90, -280), hl=(-40, -250), er=(90, -300), hr=(lerp(120, -30, slap), lerp(-380, -255, slap)),
                        face=fc(open=0.75, lift=0.1, mouth="flat", look=(0, 0)))
    bxp = lerp(300, 470, walk)
    body = boy(J, "mt13", bxp, 470, 0.66, LI)
    bx, by = bxp + 0.66 * lerp(130, -40, slap), 470 + 0.66 * lerp(-395, -258, slap)
    b = bacon(bx, by, 0.32, lerp(-40, 0, slap), t * 2)
    hit = clamp(1 - abs(t - slap_t) / 0.07)
    sp = "".join(f'<path d="M{bx + 30 * math.cos(a):.0f} {by + 30 * math.sin(a):.0f} l{18 * math.cos(a):.0f} {18 * math.sin(a):.0f}" stroke="#FFFFFF" stroke-width="4" opacity="{clamp(1 - abs(t - slap_t) * 4):.2f}"/>' for a in [k * TAU / 10 for k in range(10)])
    punch = 0.3 * math.exp(-max(0, t - slap_t) * 5) if t > slap_t else 0
    cam = (lerp(-170, 0, walk), lerp(-10, -40, ramp(t, slap_t, D)), lerp(1.2, 1.45, ramp(t, slap_t, D)) + punch, lerp(6, 0, walk))
    return SV([(kitchen(t), 0.75, True), (body + b + sp, 1.0, False), ui(flashw(hit * 0.8))], cam, lights=(LI,))


@shot5(Ln(8) - 0.1, "mt14", "X-RAY under the bacon: the bubbles stop. The maggot thrashes; the camera spins slowly around it.")
def mt14(t, D):
    g = grub(480, SURF + 92, 1.25, t * 1.8, rot=90, wig=1.8)
    cam = (0, 60, lerp(1.6, 1.9, eio(ramp(t, 0, D))), lerp(-15, 15, eio(ramp(t, 0, D))))
    return SV([(skin_xsec(t, pocket=1.15, bacon_on=1.0, hair=False), 1.0, False), (g, 1.0, False),
               (bacon(480, SURF - 16, 1.4, 0, 0, flat=True).replace('<g transform', '<g opacity="0.55" transform'), 1.0, False)], cam)


@shot5(Pn(8, 1) - 0.05, "mt15", "The maggot squirms up and out into the bacon (camera rises with it); HARD CUT to the ECU peel: the maggot hangs in the bacon. Rack focus to his face: disgust, then relief.")
def mt15(t, D):
    cut = D * 0.45
    if t < cut:
        up = eo(ramp(t, 0, cut))
        g = grub(480, lerp(SURF + 92, SURF + 10, up), 1.25, t * 1.5, rot=90, wig=1.4)
        cam = (0, lerp(60, 0, up), 1.8, lerp(10, -5, up))
        return SV([(skin_xsec(t, pocket=1.15, bacon_on=1.0, hair=False), 1.0, False), (g, 1.0, False),
                   (bacon(480, SURF - 16, 1.4, 0, 0, flat=True).replace('<g transform', '<g opacity="0.55" transform'), 1.0, False)], cam)
    v = (t - cut) / max(1e-6, D - cut)
    peel = eo(ramp(v, 0, 0.6))
    arm = arm_close(300, 430, 1.4, -6, bump=lerp(1.0, 0.5, peel), t=t, wig=0.0, hole=1.0)
    bb = bacon(500, lerp(380, 250, peel), 0.75, lerp(0, -18, peel), t)
    gb = grub(500, lerp(380, 250, peel) + 18, 0.38, t, rot=100, wig=1.0)
    rf = ramp(v, 0.55, 0.85)
    J = R3.FRONT | dict(face=fc(open=lerp(0.6, 1.0, rf), lift=0.4, knit=lerp(0.8, 0.0, rf), mouth="grit" if rf < 0.5 else "smile"))
    face = f'<g filter="url(#b{6 if rf < 0.5 else 1})" opacity="0.9">{boy(J, "mt15", 560, 520, 0.9, LI)}</g>'
    fg = f'<g filter="url(#b{1 if rf < 0.5 else 4})">{arm + bb + gb}</g>'
    cam = (lerp(0, 40, rf), -10, lerp(1.7, 1.55, v))
    return SV([('<rect x="-600" y="-600" width="2160" height="1800" fill="url(#lroomW)"/>', 0.6, True), (face, 0.8, False), (fg, 1.0, False)], cam, lights=(LI,))


@shot5(Ln(9) - 0.1, "mt16", "OVERHEAD SPIRAL: the boy flopped back on the couch, relieved... a mosquito drifts down onto his OTHER arm; the camera spirals down onto it (loops to the start).")
def mt16(t, D):
    from mosq3d import mosq3d
    u = eio(ramp(t, 0, D))
    floor_ = '<rect x="-600" y="-600" width="2160" height="1800" fill="#B07A5A"/>' + "".join(f'<path d="M-600 {y} L1560 {y}" stroke="#9A6A4A" stroke-width="3" opacity="0.5"/>' for y in range(-600, 1200, 60))
    rug = '<ellipse cx="480" cy="300" rx="360" ry="290" fill="#C85A6A" opacity="0.75"/>'
    seat = ('<rect x="250" y="40" width="460" height="470" rx="46" fill="#2E4690"/><rect x="250" y="40" width="70" height="470" rx="34" fill="#3A56A8"/>'
            '<rect x="640" y="40" width="70" height="470" rx="34" fill="#3A56A8"/><rect x="330" y="60" width="300" height="430" rx="30" fill="#5A7AD8"/>'
            '<path d="M330 275 L630 275" stroke="#3A56A8" stroke-width="5"/><ellipse cx="480" cy="110" rx="90" ry="40" fill="#FFE0A0"/>')
    J = R3.FRONT | dict(el=(-120, -250), hl=(-170, -190), er=(120, -250), hr=(170, -190), kl=(-50, -120), fl=(-60, 0), kr=(50, -120), fr=(60, 0),
                        face=fc(open=0.15, mouth="smile", lift=0.2, look=(0.0, 0.0)))
    body = boy(J, "mt16", 480, 470, 0.6, LI)
    mx, my = lerp(660, 585, u), lerp(60, 352, u)
    m = mosq3d(mx, my, lerp(0.8, 1.3, u), lerp(-60, -10, u), t, eggs=True, flap=1.0 - ramp(t, D * 0.8, D), legs="fly" if u < 0.9 else "land")
    sh = f'<ellipse cx="{mx:.0f}" cy="{my + 40 * (1 - u) + 30:.0f}" rx="{14 + 10 * u:.0f}" ry="5" fill="#000" opacity="{0.2 * u:.2f}" filter="url(#b3)"/>'
    cam = (lerp(0, 105, u), lerp(-10, 85, u), lerp(1.0, 2.6, u), lerp(0, 50, u))
    return SV([(floor_ + rug + seat, 1.0, True), (body, 1.0, False), (sh + m, 1.0, False)], cam, lights=(LI,))
