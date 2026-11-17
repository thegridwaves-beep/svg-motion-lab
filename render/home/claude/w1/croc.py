"""Short 3/7: What to do if a crocodile grabs you (~64 s). The ambush, the death roll, the move that saves you."""
import os
os.environ["SHORT"] = "croc"
import anim_core
from croc_props import *
anim_core.ANIM[:] = []

B = {}
for i, ph in PH.items():
    for k, q in enumerate(ph):
        B[(i, k)] = q["t"]
TEND = round(TEND, 3)
CR_DEFS = lin("stageG", [(0, "#2A1E4A"), (1, "#120C24")]) + CROC_DEFS
WY = WATER_Y


def SS(layers, cam=(0, 0, 1.0), overlay="", lights=(L_RIVER,)):
    return SV(layers, cam, CR_DEFS, overlay, lights)


def badge(txt, u, col=PINK, y=78):
    if u <= 0:
        return ""
    k = 0.6 + 0.4 * eo(min(1, u * 2))
    fs = min(40, 520 / max(1, len(txt))); w = len(txt) * fs * 0.62 + 50
    return (f'<g transform="translate(480 {y}) scale({k:.3f})" opacity="{clamp(u * 3):.2f}"><rect x="{-w / 2}" y="-34" width="{w}" height="68" rx="34" fill="{col}" stroke="#FFFFFF" stroke-width="5"/>'
            + text(0, fs * 0.36, txt, fs, "#FFFFFF", 700, "middle") + '</g>')


def red_x(x, y, u, s=1.0):
    if u <= 0:
        return ""
    k = s * (0.5 + 0.5 * eo(min(1, u * 2)))
    return (f'<g transform="translate({x} {y}) scale({k:.3f})" opacity="{clamp(u * 3):.2f}">'
            f'<path d="M-70 -70 L70 70 M70 -70 L-70 70" stroke="{INK}" stroke-width="44" stroke-linecap="round"/>'
            '<path d="M-70 -70 L70 70 M70 -70 L-70 70" stroke="#FF3A4A" stroke-width="28" stroke-linecap="round"/></g>')


def check(x, y, u, s=1.0):
    if u <= 0:
        return ""
    k = s * (0.5 + 0.5 * eo(min(1, u * 2)))
    return (f'<g transform="translate({x} {y}) scale({k:.3f})" opacity="{clamp(u * 3):.2f}"><path d="M-60 0 L-15 45 L70 -50" stroke="{INK}" stroke-width="44" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            '<path d="M-60 0 L-15 45 L70 -50" stroke="#4AE07A" stroke-width="28" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>')


def vign(op, col="#000000"):
    return f'<rect x="200" y="-150" width="560" height="840" fill="none" stroke="{col}" stroke-width="220" opacity="{op:.2f}" filter="url(#b40)"/>'


def kick(t, t0, amp=14, dur=0.25):
    return amp * math.sin(math.pi * clamp((t - t0) / dur)) * (1 - clamp((t - t0) / dur)) if t > t0 else 0.0


def river(t, x1=520):
    return [(river_back(), 0.3, True), (water_back(), 1.0, True), (bank(x1), 1.0, True)]


def stage(t):
    return '<rect x="-600" y="-600" width="2160" height="1800" fill="url(#stageG)"/>' + glow(480, 360, 300, "#3AC8A0", 0.3, 40) + '<ellipse cx="480" cy="430" rx="420" ry="40" fill="#000000" opacity="0.3"/>'


def croc_on_arm(t, hx, hy, s=1.1, yaw=180, open_=0.14, tug=0.0, roll=0.0, blink=0.0, pitch=18):
    """Croc (facing left) lunging up out of the water, its jaw tip clamped on the boy's hand at (hx, hy)."""
    return croc3d(0, 0, s, yaw, t, open_=open_, roll=roll, sway=0.6, blink=blink, pitch=pitch, anchor=(hx + 30 * tug, hy))


BOYX, BOYY, BS = 470, 418, 0.5          # boy standing at the waterline on the bank slope


def held_hand(J, x=BOYX, y=BOYY, s=BS):
    hx, hy = J["h2"]; px, py = J["hip"]; a = math.radians(J["lean"])
    rx, ry = hx * math.cos(a) - (hy + 200) * math.sin(a), hx * math.sin(a) + (hy + 200) * math.cos(a)
    return x + (px + rx) * s, y + (py + ry - 200) * s


# ================================================================== the ambush
@shot5(0.0, "c01", "DRONE SWOOP down a jungle river to the boy kneeling at the water's edge, dipping a bottle in. A dark shape glides under the surface toward him.")
def c01(t, D):
    u = eio(ramp(t, 0, D))
    J = crouch_J(1.0)
    me = boy(J, "c01", 455, 418, 0.42, L_RIVER, side=True)
    hx, hy = 455 + 150 * 0.42 + 10, 418 - 150 * 0.42 + 40
    rip = "".join(f'<ellipse cx="{hx:.0f}" cy="{WY + 2}" rx="{10 + 30 * ((t * 0.8 + k / 3) % 1):.0f}" ry="{3 + 8 * ((t * 0.8 + k / 3) % 1):.0f}" fill="none" stroke="#E8FFF8" stroke-width="2" opacity="{0.8 * (1 - (t * 0.8 + k / 3) % 1):.2f}"/>' for k in range(3))
    shape = f'<g opacity="0.5" filter="url(#b4)">{croc3d(lerp(1000, 760, u), 480, 0.9, 180, t, sil="#0A2424", sway=0.8)}</g>'
    cam = (lerp(60, 30, u), lerp(-200, 70, u), lerp(1.0, 1.45, u), lerp(-10, 0, u))
    return SS(river(t, 470) + [(shape, 1.0, False), (water_front(t, WY, 0.3) + rip, 1.0, False), (me + bottle(hx, hy, 0.4, 100), 1.0, False)], cam)

@shot5(B[(0, 1)] - 0.1, "c02", "WATER LEVEL, SLOW-MO: the surface erupts and the croc launches out jaws wide; the boy jerks back, bottle flying.")
def c02(t, D):
    u = ramp(t, 0.15, 1.2)
    rise = eo(u)
    cr = croc3d(lerp(700, 640, rise), lerp(560, 470, rise), 1.1, 185, t, open_=clamp(rise * 1.4), sway=1.0, pitch=28 * rise)
    jerk = eo(ramp(t, 0.35, 0.8))
    J = crouch_J(1.0 - jerk, fc(open=1.5, lift=1.2, mouth="gasp", look=(1, 0))) | dict(lean=lerp(18, -14, jerk), hip=(-10, lerp(70, 30, jerk)))
    me = boy(J, "c02", 455 - 20 * jerk, 418, 0.42, L_RIVER, side=True)
    bt = bottle(lerp(530, 580, jerk), lerp(400, 250, jerk) + 300 * max(0, jerk - 0.6) ** 2, 0.4, 100 + 400 * jerk)
    zu = ei(ramp(t, 1.2, D))
    cam = (lerp(40, 60, zu), lerp(60, 50, zu), lerp(1.2, 1.6, zu), lerp(-6, 0, zu))
    return SS(river(t, 470) + [(me + bt, 1.0, False), (cr, 1.0, False), (water_front(t, WY + 15, 0.55) + splash(620, WY + 15, u, 1.2), 1.0, False),
                               ui(streaks(t, CX, CY, 0.6 * zu))], cam)

@shot5(B[(1, 0)] - 0.1, "c03", "IMPACT FRAME: the jaws slam shut on his forearm. White flash, freeze, the teeth in close-up.")
def c03(t, D):
    J = arm_pulled_J(0.2)
    me = boy(J, "c03", BOYX, BOYY, BS, L_RIVER, side=True)
    hx, hy = held_hand(J)
    clamp_ = eo(ramp(t, 0, 0.18))
    cr = croc_on_arm(t, hx, hy, 1.1, 180, lerp(0.8, 0.1, clamp_))
    hit = clamp(1 - abs(t - 0.25) / 0.1)
    cam = (hx - CX + 30, hy - CY + 30 + kick(t, 0.25, 14), lerp(2.4, 2.1, ramp(t, 0, D)), lerp(8, 0, ramp(t, 0, 0.5)))
    return SS(river(t, 470) + [(me, 1.0, False), (cr, 1.0, False), (water_front(t, WY, 0.55), 1.0, False), ui(flashw(hit) + vign(0.35))], cam)


@shot5(B[(1, 1)] - 0.1, "c04", "SIDE TRACK: the croc yanks backward; his shoes skid through the mud toward the water while he leans back with everything.")
def c04(t, D):
    pull = ramp(t, 0, D)
    drag = 40 * ei(pull)
    J = arm_pulled_J(0.8)
    bx = BOYX - 40 + drag
    me = boy(J, "c04", bx, BOYY - 10, BS, L_RIVER, side=True)
    hx, hy = held_hand(J, bx, BOYY - 10)
    jerk = 6 * math.sin(t * 14)
    cr = croc_on_arm(t, hx + jerk, hy, 1.1, 180, 0.1, tug=0.3)
    mud = "".join(f'<ellipse cx="{bx - 20 - 30 * k:.0f}" cy="{BOYY - 8 + 2 * k}" rx="{18 - 3 * k}" ry="5" fill="#5A4024" opacity="0.6"/>' for k in range(5))
    cam = (hx - CX + 10, 10, 1.15, -4 + jerk * 0.3)
    return SS(river(t, 470) + [(mud + me, 1.0, False), (cr, 1.0, False), (water_front(t, WY, 0.55), 1.0, False)], cam)


@shot5(B[(2, 0)] - 0.1, "c05", "3D ORBIT around the croc's head clamped on, the camera circling past the teeth. Chip: STRONGEST BITE EVER MEASURED.")
def c05(t, D):
    u = eio(ramp(t, 0, D))
    cr = croc3d(630, 390, 1.5, lerp(-150, -210, u), t, open_=0.12, sway=0.4)
    arm = f'<path d="M{lerp(160, 300, u):.0f} 300 L{lerp(560, 640, u):.0f} 320" stroke="#2EA0B0" stroke-width="40" stroke-linecap="round" opacity="0.0"/>'
    cam = (lerp(-20, 20, u), 60, lerp(1.5, 1.7, u), lerp(-8, 8, u))
    return SS([(river_back(), 0.3, True), (water_back(), 1.0, True), (cr + arm, 1.0, False), (water_front(t, 380, 0.45), 1.0, False)], cam,
              overlay=kmh_chip(480, 90, "STRONGEST", "BITE EVER MEASURED", ramp(t, 0.6, 0.9), edge="#FFB040"))


@shot5(B[(2, 1)] - 0.1, "c06", "SLOW-MO DEMO: a thick branch between the jaws; they slam shut and it snaps clean in two.")
def c06(t, D):
    sn = ramp(t, 0.35, 0.5)
    op = lerp(0.2, 0.9, eo(ramp(t, 0, 0.35))) if t < 0.35 else 0.9 * (1 - ei(sn))
    cr = croc3d(330, 400, 1.6, 0, t, open_=op, sway=0.3)
    jx, jy = 330 + 118 * 1.6, 400 - 26 * 1.6
    if t < 0.5:
        log = f'<circle cx="{jx:.0f}" cy="{jy:.0f}" r="22" fill="#8A6040" stroke="#5A3A22" stroke-width="5"/><circle cx="{jx:.0f}" cy="{jy:.0f}" r="12" fill="none" stroke="#C8A070" stroke-width="3"/>'
    else:
        f = ramp(t, 0.5, 1.4)
        log = "".join(f'<g transform="translate({jx + d * 120 * f:.0f} {jy - 160 * f + 260 * f * f:.0f}) rotate({d * 300 * f:.0f})"><path d="M0 -22 A22 22 0 0 {1 if d > 0 else 0} 0 22 Z" fill="#8A6040" stroke="#5A3A22" stroke-width="5"/></g>' for d in (-1, 1))
        log += "".join(f'<rect x="{jx + 70 * math.cos(k) * f:.0f}" y="{jy + 70 * math.sin(k * 1.7) * f - 30 * f:.0f}" width="9" height="5" fill="#C8A070" opacity="{1 - f:.2f}"/>' for k in range(12))
    cam = (jx - CX - 20, jy - CY + 30 + kick(t, 0.5, 14), lerp(1.7, 1.85, ramp(t, 0, D)), 0)
    return SS([(river_back(), 0.3, True), (water_back(), 1.0, True), (cr + log, 1.0, False), (water_front(t, WY + 15, 0.5), 1.0, False)], cam,
              overlay=impact_star(480, 270, clamp((t - 0.5) / 0.3), 0.5) if t > 0.5 else "")

@shot5(B[(2, 2)] - 0.1, "c07", "DOLLY IN: he hauls back with both hands, nothing moves. Red X.")
def c07(t, D):
    J = arm_pulled_J(1.0) | dict(e1=(80, -290), h1=(150, -225))
    me = boy(J, "c07", BOYX, BOYY, BS, L_RIVER, side=True)
    hx, hy = held_hand(J)
    cr = croc_on_arm(t, hx + 3 * math.sin(t * 20), hy, 1.1, 180, 0.1)
    cam = (hx - CX - 20, 0, lerp(1.2, 1.4, eio(ramp(t, 0, D))), 0)
    return SS(river(t, 470) + [(me, 1.0, False), (cr, 1.0, False), (water_front(t, WY, 0.55), 1.0, False), ui(red_x(480, 250, ramp(t, 0.6, 0.85), 1.2))], cam)


# ================================================================== the death roll
@shot5(B[(3, 0)] - 0.1, "c08", "WATER LEVEL: the croc twists its whole body over, the camera rolling with it; white water churns. DEATH ROLL.")
def c08(t, D):
    u = ramp(t, 0, D)
    roll = 360 * ei(u) * 1.2
    cr = croc3d(500, 470, 1.0, 175, t, open_=0.12, roll=roll, sway=1.0)
    churn = "".join(f'<ellipse cx="{380 + 30 * k + 10 * math.sin(t * 9 + k):.0f}" cy="{WY + 30 + 6 * math.sin(t * 7 + k * 2):.0f}" rx="{26 + 8 * (k % 3)}" ry="10" fill="#E8FFFA" opacity="0.7"/>' for k in range(9))
    cam = (0, 170, 1.7, lerp(0, 40, ei(u)))
    return SS([(river_back(), 0.3, True), (water_back(), 1.0, True), (cr, 1.0, False), (water_front(t, WY + 20, 0.55) + churn, 1.0, False)], cam,
              overlay=tag_big("DEATH ROLL", 480, 90, ramp(t, 0.2, 0.5), 52, "#FF4A4A"))


@shot5(B[(3, 1)] - 0.1, "c09", "UNDERWATER CORKSCREW: below the surface the croc spins over and over, bubbles spiralling, dragging downward.")
def c09(t, D):
    u = ramp(t, 0, D)
    roll = 360 * 2.2 * u
    cr = croc3d(480, lerp(260, 380, eio(u)), 0.75, 170, t, open_=0.0, roll=roll, sway=1.0)
    cam = (0, 40, lerp(1.2, 1.4, u), -120 * u)
    return SS([(underwater_bg(t), 0.4, False), (cr, 1.0, False), (bubbles2(t, 480, 520, 24, 6, 160, 240), 1.2, False)], cam, lights=(L_UNDER,))

@shot5(B[(4, 0)] - 0.1, "c10", "SMASH: the boy flops flat on the mud, eyes shut, playing dead; a giant red X slams over him. DON'T PLAY DEAD.")
def c10(t, D):
    J = dict(R3.SIDE) | dict(face=fc(open=0.0, mouth="smile", mo=0.0), e2=(20, -260), h2=(40, -200), e1=(10, -260), h1=(30, -200))
    me = f'<g transform="translate(590 394) rotate(-90)">' + boy(J, "c10", 0, 0, 0.42, L_RIVER, side=True) + '</g>'
    cam = (0, 70, 1.3, kick(t, 0.1, 6))
    return SS(river(t, 600) + [(me, 1.0, False), ui(red_x(480, 250, ramp(t, 0.05, 0.3), 1.2))], cam,
              overlay=tag_big("DON'T PLAY DEAD", 480, 90, ramp(t, 0.1, 0.4), 36, "#FF4A4A"))

@shot5(B[(4, 1)] - 0.1, "c11", "CALLBACK: a flash of yesterday's forest, the grizzly; a green tick: that's where playing dead works.")
def c11(t, D):
    g_ = bear3d(480, 420, 0.75, -30, t, "grizzly")
    from bear_props import forest_back, pine_row, trail_side
    cam = (0, 0, lerp(1.45, 1.55, ramp(t, 0, D)), 0)
    return SS([(forest_back(t), 0.3, True), (pine_row(380, 21, "#1E4A36", 14, 220, 340), 0.65, True), (trail_side(420), 1.0, True), (g_, 1.0, False),
               ui(check(560, 160, ramp(t, 0.15, 0.4), 0.8))], cam, overlay=badge("GRIZZLY ONLY", ramp(t, 0.1, 0.35), "#C8742A"))


@shot5(B[(4, 2)] - 0.1, "c12", "WHIP back to the river: the boy's eyes snap open, his free fist clenches. FIGHT.")
def c12(t, D):
    J = arm_pulled_J(0.6, fc(open=1.2, knit=1.2, lift=-0.3, mouth="grit", look=(1, 0))) | dict(e1=(-30, -300), h1=(-60, -360))
    me = boy(J, "c12", BOYX, BOYY, BS, L_RIVER, side=True)
    hx, hy = held_hand(J)
    cr = croc_on_arm(t, hx, hy, 1.1, 180, 0.1)
    wp = 1 - ramp(t, 0, 0.25)
    cam = (lerp(-200, hx - CX - 30, eo(ramp(t, 0, 0.3))), -10, lerp(1.4, 1.55, ramp(t, 0, D)), -6)
    return SS(river(t, 470) + [(me, 1.0, False), (cr, 1.0, False), (water_front(t, WY, 0.55), 1.0, False), ui(hstreaks(wp))], cam,
              overlay=tag_big("FIGHT", 480, 90, ramp(t, 0.85, 1.1), 84, "#FFE45A"))


@shot5(B[(5, 0)] - 0.1, "c13", "CRASH ZOOM onto the croc's raised eye; a yellow target ring locks on.")
def c13(t, D):
    u = ei(ramp(t, 0, 0.6))
    cr = croc3d(420, 400, 2.2, -150, t, open_=0.1, sway=0.2)
    ex, ey = 420 + (79 * math.cos(math.radians(-150)) - 11 * math.sin(math.radians(-150))) * 2.2, 400 - 42 * 2.2
    ring = f'<circle cx="{ex:.0f}" cy="{ey:.0f}" r="{lerp(90, 34, eo(ramp(t, 0.4, 0.8))):.0f}" fill="none" stroke="#FFE45A" stroke-width="6" opacity="{ramp(t, 0.4, 0.6):.2f}"/>'
    cam = (ex - CX, ey - CY + 20, lerp(1.4, 3.2, u), 0)
    return SS([(f'<g filter="url(#b8)">{river_back()}{water_back(330)}</g>', 0.4, True), (cr + ring, 1.0, False), (water_front(t, 420, 0.45), 1.0, False)], cam,
              overlay=tag_big("THE EYES", 480, 90, ramp(t, 0.4, 0.7), 70, "#FFE45A"))


@shot5(B[(5, 1)] - 0.1, "c14", "CLOSE: the boy's fist drives in from the side straight at the eye; impact; the eye squeezes shut.")
def c14(t, D):
    jab = clamp(1 - abs(t - 0.35) / 0.3)
    cr = croc3d(420, 400, 2.2, -150, t, open_=0.0, sway=0.2, blink=1.0 if t > 0.38 else 0.0)
    ex, ey = 420 + (82 * math.cos(math.radians(-150)) - 12 * math.sin(math.radians(-150))) * 2.2, 400 - 46 * 2.2
    fist = hand_grip(lerp(ex + 230, ex + 30, jab), lerp(ey + 120, ey + 10, jab), 1.2)
    cam = (ex - CX + 40, ey - CY + 40 + kick(t, 0.35, 12), 2.0, 0)
    return SS([(f'<g filter="url(#b8)">{river_back()}{water_back(330)}</g>', 0.4, True), (cr, 1.0, False), (water_front(t, 420, 0.45), 1.0, False), (fist, 1.0, False),
               ui(impact_star(480, 250, clamp((t - 0.35) / 0.3), 0.6) if t > 0.35 else "")], cam)

@shot5(B[(5, 2)] - 0.1, "c15", "IMPACT FRAMES: punch, then the water bottle cracks across the eye; the croc flinches every hit.")
def c15(t, D):
    hits = [0.35, 1.2, 2.1]
    sw = max(clamp(1 - abs(t - h) / 0.22) for h in hits)
    J = arm_pulled_J(0.5, fc(open=1.2, knit=1.2, mouth="grit", look=(1, 0))) | dict(e1=(lerp(-20, 90, sw), lerp(-360, -310, sw)), h1=(lerp(-40, 230, sw), lerp(-420, -280, sw)), lean=lerp(-14, 4, sw))
    me = boy(J, "c15", BOYX, BOYY, BS, L_RIVER, side=True)
    hx, hy = held_hand(J)
    fl = max(clamp(1 - abs(t - h - 0.12) / 0.3) for h in hits)
    cr = croc_on_arm(t, hx + 8 * fl, hy, 1.1, 180, 0.1 + 0.1 * fl, blink=fl)
    bx, by = held_hand(J | dict(h2=J["h1"]))
    bt = bottle(bx, by, 0.35, lerp(-60, 90, sw)) if t > 1.0 else ""
    ex, ey = hx + 70 * 1.1 * 0.85, hy - 55
    stars = "".join(impact_star(ex, ey, clamp((t - h) / 0.3), 0.4) for h in hits if t > h)
    cam = (hx - CX + 60 + kick(t, 0.35, 8) + kick(t, 1.2, 8) + kick(t, 2.1, 8), 10, 1.45, -4)
    return SS(river(t, 470) + [(me, 1.0, False), (cr, 1.0, False), (water_front(t, WY, 0.55), 1.0, False), (me[:0] + bt + stars, 1.0, False)], cam)


# ================================================================== the throat flap
@shot5(B[(6, 0)] - 0.1, "c16", "SIDE CLOSE-UP: his forearm is jammed deep between the jaws; the camera pushes in along it toward the back of the mouth.")
def c16(t, D):
    u = eio(ramp(t, 0, D))
    cr = croc3d(560, 400, 1.6, 180, t, open_=0.3, sway=0.2)
    hx, hy = 560 - 75 * 1.6, 400 - 26 * 1.6
    arm = f'<path d="M150 {hy + 40:.0f} L{hx + 6:.0f} {hy + 4:.0f}" stroke="#36A8B8" stroke-width="20" stroke-linecap="round"/>' + hand_grip(hx + 4, hy + 4, 0.5)
    gl = glow(hx - 10, hy, 70, "#FFE45A", 0.55 * ramp(t, 1.0, 1.8), 10)
    cam = (lerp(-60, hx - CX, u), lerp(80, hy - CY + 30, u), lerp(1.3, 2.4, ei(u)), 0)
    return SS(river(t, 300) + [(cr, 1.0, False), (arm + gl, 1.0, False), (water_front(t, WY, 0.45), 1.0, False)], cam)

@shot5(B[(6, 1)] - 0.1, "c17", "INSIDE THE MOUTH: looking down the throat past the teeth; a fleshy flap sits sealed over the opening and lights up gold.")
def c17(t, D):
    u = eio(ramp(t, 0, D))
    m = mouth_inside(480, 280, lerp(0.9, 1.15, u), 0.0, ramp(t, 0.9, 1.5), 0.0, t)
    cam = (0, 0, 1.0, lerp(-4, 4, u))
    return SS([('<rect x="-600" y="-600" width="2160" height="1800" fill="#3A0A14"/>', 0.4, True), (m, 1.0, False)], cam, lights=(),
              overlay=tag_big("THE THROAT FLAP", 480, 90, ramp(t, 1.0, 1.3), 36, "#FFE45A"))


@shot5(B[(6, 2)] - 0.1, "c18", "UNDERWATER CUTAWAY: the croc opens its jaws below the surface; water fills the mouth but stops dead at the sealed flap.")
def c18(t, D):
    u = eio(ramp(t, 0, D))
    cr = croc3d(480, 360, 1.3, 180, t, open_=eo(ramp(t, 0.2, 1.0)), sway=0.4)
    stop = f'<path d="M{480 - 70 * 1.3:.0f} {320} l0 50" stroke="#FFE45A" stroke-width="10" stroke-linecap="round" opacity="{ramp(t, 1.0, 1.4):.2f}"/>'
    arrows = "".join(f'<path d="M{300 + 40 * k} {330 + 10 * (k % 2)} l50 0 m-14 -12 l14 12 l-14 12" stroke="#9AF0F4" stroke-width="6" fill="none" opacity="{ramp(t, 0.8, 1.2) * (1 - ramp(t, 2.6, D)):.2f}"/>' for k in range(3))
    cam = (lerp(-60, -100, u), -20, lerp(1.6, 1.9, u), 0)
    return SS([(underwater_bg(t), 0.4, True), (cr + stop + arrows, 1.0, False), (bubbles2(t, 400, 520, 10, 9), 1.2, False)], cam, lights=(L_UNDER,),
              overlay=badge("WATER STOPS HERE", ramp(t, 1.2, 1.5), "#2A6A8A", 90))


@shot5(B[(7, 0)] - 0.1, "c19", "INSIDE THE MOUTH: a hand reaches in and shoves the flap down hard.")
def c19(t, D):
    push = eo(ramp(t, 0.4, 1.1))
    m = mouth_inside(480, 280, 1.15, push, 1.0 - 0.6 * push, 0.0, t)
    hand = hand_grip(lerp(620, 500, ramp(t, 0, 0.5)), lerp(480, 250 + 40 * push, ramp(t, 0, 0.5)), 1.4)
    cam = (0, 0, 1.05, 0)
    return SS([('<rect x="-600" y="-600" width="2160" height="1800" fill="#3A0A14"/>', 0.4, True), (m + hand, 1.0, False)], cam, lights=(), overlay=tag_big("PUSH IT", 480, 90, ramp(t, 0.5, 0.8), 70, "#FFE45A"))


@shot5(B[(7, 1)] - 0.1, "c20", "INSIDE: with the flap pushed down, water floods into the open throat.")
def c20(t, D):
    m = mouth_inside(480, 280, 1.15, 1.0, 0.0, eo(ramp(t, 0, 0.8)), t)
    return SS([('<rect x="-600" y="-600" width="2160" height="1800" fill="#3A0A14"/>', 0.4, True), (m, 1.0, False)], (0, 0, 1.05, 0), lights=())


@shot5(B[(7, 1)] + 1.2, "c20b", "CUT to the river: the jaws spring open, the boy rips his arm free and scrambles up the bank. IT LETS GO.")
def c20b(t, D):
    u = ramp(t, 0, D)
    J = run_J((t * 1.6) % 1, lean=12, panic=0.5, face=fc(open=1.3, lift=0.8, mouth="gasp", look=(1, 0)))
    bx = lerp(440, 360, eo(u))
    me = boy(J, "c20b", bx, 400, 0.45, L_RIVER, side=True, flip=True)
    cr = croc3d(lerp(640, 720, eo(u)), 470, 1.0, 180, t, open_=lerp(0.9, 0.3, u), sway=0.8, pitch=25 * (1 - u))
    cam = (0, 40, 1.15, 0)
    return SS(river(t, 470) + [(me, 1.0, False), (cr, 1.0, False), (water_front(t, WY, 0.5) + splash(600, WY, clamp(u * 2), 0.6), 1.0, False)], cam,
              overlay=kmh_chip(480, 90, "IT LETS GO", "OFTEN", ramp(t, 0.2, 0.5), edge="#5AE08A"))

@shot5(B[(8, 0)] - 0.1, "c21", "TURNTABLE: the croc revolves on a dark stage, jaws gaping. THE TWIST.")
def c21(t, D):
    cr = croc3d(480, 340, 1.0, 150 + 60 * t, t, open_=0.6)
    return SS([(stage(t), 0.4, True), (cr, 1.0, False)], (0, 40, 1.05, 0), lights=(), overlay=tag_big("THE TWIST", 480, 90, ramp(t, 0.05, 0.3), 62, "#FFE45A"))


@shot5(B[(8, 1)] - 0.1, "c22", "SLOW-MO CLOSE-UP: the jaws slam shut, huge red arrows pressing down. CLOSING: MASSIVE.")
def c22(t, D):
    op = 1 - ei(ramp(t, 0.3, 0.6))
    cr = croc3d(420, 360, 1.5, 0, t, open_=op)
    ar = "".join(f'<path d="M{560 + 50 * k} {150 - 30 * op} l0 60 m-18 -22 l18 22 l18 -22" stroke="#FF4A4A" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' for k in range(3))
    cam = (110, 0, 1.6, 0) if True else None
    return SS([(stage(t), 0.4, True), (cr + ar, 1.0, False)], (110, 20 + kick(t, 0.6, 10), 1.6, 0), lights=(), overlay=badge("CLOSING: MASSIVE", ramp(t, 0.6, 0.9), "#C83A4A", 90))


@shot5(B[(8, 2)] - 0.1, "c23", "SAME ANGLE: the jaws strain to open, barely creaking apart; a tiny wobbly blue arrow. OPENING: WEAK.")
def c23(t, D):
    op = 0.12 * abs(math.sin(t * 3)) * ramp(t, 0.2, 0.6)
    cr = croc3d(420, 360, 1.5, 0, t, open_=op)
    ar = f'<path d="M640 {200 - 6 * math.sin(t * 9):.0f} l0 -22 m-8 10 l8 -10 l8 10" stroke="#5AC8FF" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    return SS([(stage(t), 0.4, True), (cr + ar, 1.0, False)], (110, 20, 1.6, 0), lights=(), overlay=badge("OPENING: WEAK", ramp(t, 0.4, 0.7), "#2A6A9A", 90))


@shot5(B[(8, 3)] - 0.1, "c24", "PULL OUT: a small croc, about as long as the boy's leg, sits on the mud beside him.")
def c24(t, D):
    u = eio(ramp(t, 0, D))
    cr = croc3d(530, 420, 0.45, 180, t, small=True, sway=0.5)
    J = dict(R3.SIDE) | dict(face=fc(open=1.1, look=(1, 0.4)))
    me = boy(J, "c24", 400, 420, 0.42, L_RIVER, side=True)
    cam = (0, 60, lerp(1.45, 1.3, u), 0)
    return SS(river(t, 900) + [(me + cr, 1.0, False)], cam, overlay=badge("SMALL CROC", ramp(t, 0.2, 0.5), "#3A6A3A"))

@shot5(B[(8, 4)] - 0.1, "c25", "CLOSE: two hands clamp around the small croc's snout; it twists and strains but the jaws stay shut.")
def c25(t, D):
    u = eio(ramp(t, 0, D))
    wig = 5 * math.sin(t * 7)
    cr = croc3d(560, 420, 0.95, 180 + wig, t, small=True, sway=1.0, open_=0.0)
    sx, sy = 560 - 120 * 0.95, 420 - 26 * 0.95
    hands = hand_grip(sx - 18, sy, 0.6) + hand_grip(sx + 22, sy + 2, 0.6)
    strain = "".join(f'<path d="M{sx + 10 * k:.0f} {sy - 30 - 6 * abs(math.sin(t * 9 + k)):.0f} l0 -10" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity="0.7"/>' for k in (-1, 0, 1))
    cam = (sx - CX + 60 + wig, sy - CY + 20, lerp(1.5, 1.7, u), wig * 0.3)
    return SS(river(t, 1100) + [(cr + hands + strain, 1.0, False)], cam, overlay=tag_big("HELD SHUT", 480, 90, ramp(t, 0.6, 0.9), 64, "#FFE45A"))

@shot5(B[(9, 0)] - 0.1, "c26", "WHIP PAN to the riverbank, wide and calm; light glinting off the water.")
def c26(t, D):
    wp = 1 - ramp(t, 0, 0.3)
    J = walk_J((t * 0.9) % 1, face=fc(open=1.0, look=(1, 0)))
    me = boy(J, "c26", 380 + 40 * t, 400, 0.4, L_RIVER, side=True)
    cam = (lerp(-260, 0, eo(ramp(t, 0, 0.3))), 30, 1.15, 0)
    return SS(river(t, 520) + [(me, 1.0, False), (water_front(t, WY, 0.25), 1.0, False), ui(hstreaks(wp))], cam)


@shot5(B[(9, 1)] - 0.1, "c27", "OVERHEAD: the boy takes three big steps back from the water; a red DANGER strip glows along the edge.")
def c27(t, D):
    u = ramp(t, 0, D)
    step = eo(clamp(u * 1.4))
    bx, by = lerp(470, 300, step), 300
    sw = 6 * math.sin(t * 9) * (1 - step)
    me = (f'<g transform="translate({bx:.0f} {by}) rotate({90 + sw:.1f}) scale(1.7)"><ellipse cx="0" cy="0" rx="40" ry="20" fill="#2EA0B0"/><ellipse cx="-38" cy="0" rx="10" ry="12" fill="#2EA0B0"/><ellipse cx="38" cy="0" rx="10" ry="12" fill="#2EA0B0"/>'
          '<circle cx="0" cy="0" r="22" fill="#3A2A3A"/><path d="M-14 -12 Q0 -26 14 -12" stroke="#4A3646" stroke-width="6" fill="none"/></g>')
    strip = f'<path d="M520 -800 Q480 300 560 1400" stroke="#FF3A4A" stroke-width="110" fill="none" opacity="{0.35 * ramp(t, 0.3, 0.8):.2f}"/>'
    prints = "".join(f'<ellipse cx="{lerp(470, 320, k / 3):.0f}" cy="{300 + (14 if k % 2 else -14)}" rx="12" ry="7" fill="#5A4024" opacity="{0.6 * ramp(t, 0.3 * k, 0.3 * k + 0.2):.2f}"/>' for k in range(4))
    cam = (-60, 0, lerp(1.1, 1.25, u), lerp(-6, 6, u))
    return SS([(topdown_river(t), 1.0, True), (strip + prints + me, 1.0, False)], cam, overlay=badge("DANGER ZONE", ramp(t, 0.5, 0.8), "#C83A4A", 90))

@shot5(B[(9, 2)] - 0.1, "c28", "WATER LEVEL: two eyes surface right at the edge... the croc lunges and snaps on empty air. He's out of reach.")
def c28(t, D):
    lg = eo(ramp(t, 0.9, 1.4))
    cr = croc3d(lerp(700, 640, lg), lerp(490, 470, lg), 1.2, 180, t, pitch=30 * lg, open_=clamp(lg * 2) * (1 - ramp(t, 1.4, 1.6)), sway=0.8)
    J = dict(R3.SIDE) | dict(face=fc(open=1.3, lift=0.8, mouth="o", look=(1, 0)))
    me = boy(J, "c28", 400, 390, 0.42, L_RIVER, side=True)
    cam = (10, 60, 1.1, 0)
    return SS(river(t, 470) + [(me, 1.0, False), (cr, 1.0, False), (water_front(t, WY, 0.6) + splash(560, WY, clamp((t - 0.9) * 1.5) if t > 0.9 else 0, 0.6), 1.0, False)], cam)


@shot5(B[(10, 0)] - 0.1, "c29", "SPLIT CHOICE: a huge croc eye on top, the glowing throat flap below, a white slash between them.")
def c29(t, D):
    top = croc3d(560, 330, 2.8, -150, t, open_=0.0, sway=0.2, eye_glow=ramp(t, 0.5, 1.0))
    m = mouth_inside(480, 470, 0.5, 0.0, ramp(t, 1.5, 2.0), 0.0, t)
    clip = '<clipPath id="c29top"><rect x="200" y="-200" width="560" height="470"/></clipPath>'
    sl = '<path d="M200 300 L760 240" stroke="#FFFFFF" stroke-width="10"/>'
    return SS([(stage(t), 0.4, True), (clip + f'<g clip-path="url(#c29top)">{top}</g>' + m + sl, 1.0, False)], (0, 40, 1.0, 0), lights=(),
              overlay=tag_big("EYES?", 480, 40, ramp(t, 0.6, 0.9), 54, "#FFE45A") + tag_big("THROAT FLAP?", 480, 470, ramp(t, 1.5, 1.8), 44, "#FFE45A"))

@shot5(B[(10, 2)] - 0.1, "c30", "BACK TO THE START: the boy kneels at the river's edge again... two eyes rise behind the bottle. Loops.")
def c30(t, D):
    u = eio(ramp(t, 0, D))
    J = crouch_J(0.7)
    me = boy(J, "c30", 420, 390, 0.42, L_RIVER, side=True)
    hand = (420 + 150 * 0.42, 390 - 150 * 0.42)
    cr = croc3d(680, 480 - 10 * u, 1.0, 180, t, sway=0.3, eye_glow=u)
    cam = (40, 50, lerp(1.4, 1.6, u), 0)
    return SS(river(t) + [(cr, 1.0, False), (water_front(t, WY, 0.6), 1.0, False), (me + bottle(hand[0], hand[1] + 30, 0.4, 70), 1.0, False)], cam,
              overlay=tag_big("WHICH ONE?", 480, 90, ramp(t, 0.2, 0.5), 60, "#FFE45A"))
