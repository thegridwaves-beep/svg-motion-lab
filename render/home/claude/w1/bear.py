"""Short 2/7: What to do if a bear charges you (~62 s). The danger, the escalation, the move that saves you
(and why it depends on which bear it is)."""
import os
os.environ["SHORT"] = "bear"
import anim_core
from bear_props import *
anim_core.ANIM[:] = []

# beat times from the real voice (phrases.json mis-splits lines 6 and 8, so those come from the waveform gaps)
B = dict(steps=Pn(0, 1), sees=Ln(1), charges=Pn(1, 1), run=Ln(2), dont=Pn(2, 1), kmh=Pn(2, 2), human=Pn(2, 3),
         bluff=Ln(3), ground=Pn(3, 1), calm=Pn(3, 2), spray_out=Pn(3, 3), nostop=Ln(4), cloud=Pn(4, 1), enough=Pn(4, 2),
         contact=Ln(5), which=Pn(5, 1), wrong=Pn(5, 2), griz=Ln(6), stomach=35.39, neck=36.44, legs=37.58,
         black=Ln(7), fight=Pn(7, 1), hit=Pn(7, 2), twist=Ln(8), cant=46.73, brown=48.93, gblack=50.36,
         hump=Ln(9), hump2=Pn(9, 1), nohump=Pn(9, 2), q=Ln(10))
for k in B:
    B[k] = round(B[k], 3)

BR_DEFS = lin("stageG", [(0, "#2A1E4A"), (1, "#120C24")]) + lin("topG", [(0, "#7AAA52"), (1, "#5E8E42")])


def SS(layers, cam=(0, 0, 1.0), overlay="", lights=(L_FOREST,)):
    return SV(layers, cam, BR_DEFS, overlay, lights)


def badge(txt, u, col=PINK, y=78):
    if u <= 0:
        return ""
    k = 0.6 + 0.4 * eo(min(1, u * 2))
    fs = min(40, 520 / max(1, len(txt)))
    w = len(txt) * fs * 0.62 + 50
    return (f'<g transform="translate(480 {y}) scale({k:.3f})" opacity="{clamp(u * 3):.2f}"><rect x="{-w / 2}" y="-34" width="{w}" height="68" rx="34" fill="{col}" stroke="#FFFFFF" stroke-width="5"/>'
            + text(0, fs * 0.36, txt, fs, "#FFFFFF", 700, "middle") + '</g>')


def red_x(x, y, u, s=1.0):
    if u <= 0:
        return ""
    k = s * (0.5 + 0.5 * eo(min(1, u * 2)))
    return (f'<g transform="translate({x} {y}) scale({k:.3f})" opacity="{clamp(u * 3):.2f}">'
            f'<path d="M-70 -70 L70 70 M70 -70 L-70 70" stroke="{INK}" stroke-width="44" stroke-linecap="round"/>'
            '<path d="M-70 -70 L70 70 M70 -70 L-70 70" stroke="#FF3A4A" stroke-width="28" stroke-linecap="round"/></g>')


def vign(op, col="#000000"):
    return f'<rect x="200" y="-150" width="560" height="840" fill="none" stroke="{col}" stroke-width="220" opacity="{op:.2f}" filter="url(#b40)"/>'


def kick(t, t0, amp=14, dur=0.25):
    return amp * math.sin(math.pi * clamp((t - t0) / dur)) * (1 - clamp((t - t0) / dur)) if t > t0 else 0.0


def forest_layers(t, ground_y=400, fg=True, warm=0.0):
    L = [(forest_back(t, warm), 0.3, True), (pine_row(ground_y - 40, 21, "#1E4A36", 14, 220, 340), 0.65, True), (trail_side(ground_y), 1.0, True)]
    return L


def paw(x, y, s=1.0, ang=0.0, col="#6A4426"):
    claws = "".join(f'<path d="M{-30 + 20 * k} -46 Q{-34 + 20 * k} -86 {-26 + 20 * k} -104" stroke="#EDE2C8" stroke-width="9" fill="none" stroke-linecap="round"/>' for k in range(4))
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})">{claws}<ellipse cx="0" cy="0" rx="70" ry="56" fill="{col}"/>'
            f'<ellipse cx="0" cy="10" rx="34" ry="24" fill="#3A2416"/>' + "".join(f'<ellipse cx="{-30 + 20 * k}" cy="-36" rx="10" ry="12" fill="#3A2416"/>' for k in range(4)) + '</g>')


# ================================================================== the danger
@shot5(0.0, "b01", "AERIAL DIVE: from high above the pine forest the camera plunges down and swings in beside the boy hiking the trail.")
def b01(t, D):
    u = eio(ramp(t, 0, D))
    bx = 420 + 70 * t
    h = hiker(t, bx, 420, 0.42, L_FOREST, "b01")
    cam = (lerp(-60, bx - CX + 20, u), lerp(-520, 40, u), lerp(0.85, 1.55, u), lerp(-14, 0, u))
    return SS(forest_layers(t, 420) + [(h, 1.0, False), (fg_pines(t, (120, 900), 760, 900), 1.7, True)], cam)


@shot5(B["steps"] - 0.1, "b02", "OVER THE SHOULDER: down the trail ahead, a grizzly lumbers out of the trees onto the path and stops. Crash zoom.")
def b02(t, D):
    w = ramp(t, 0, D * 0.75)
    bear = bear3d(lerp(640, 500, w), 330, 0.42, lerp(-170, -110, eio(w)), t, gait=(t * 0.9) % 1 if w < 1 else 0.0)
    J = R3.FRONT | dict(face=fc(open=1.0))
    me = boy(J, "b02", 360, 760, 0.95, L_FOREST, backv=True)
    zu = ei(ramp(t, D * 0.72, D))
    cam = (lerp(0, 500 - CX + 10, zu), lerp(20, 300 - 90 * 0.42 - CY, zu), lerp(1.0, 2.4, zu), lerp(3, 0, zu))
    return SS([(forest_back(t), 0.3, True), (pine_row(300, 21, "#1E4A36", 14, 160, 260), 0.6, True), (trail_persp(300), 1.0, True), (bear, 1.0, False),
               (me, 1.4, False), ui(streaks(t, CX, CY, 0.7 * zu))], cam)


@shot5(B["sees"] - 0.1, "b03", "ECU head-on on the bear's face: its eyes snap onto the lens, the nose twitches. Slow push in.")
def b03(t, D):
    u = eio(ramp(t, 0, D))
    bl = 1.0 if 0.35 < t < 0.47 else 0.0
    bear = bear3d(480, 520, 2.6, -90 + 8 * math.sin(t * 1.2) * (1 - u), t, blink=bl, head_dy=4 * math.sin(t * 9) * ramp(t, 0.6, 0.9))
    bg = f'<g filter="url(#b12)">{forest_back(t)}{pine_row(300, 21, "#1E4A36", 14, 220, 340)}{trail_persp(300)}</g>'
    cam = (0, lerp(-10, -40, u), lerp(1.55, 1.95, u), 0)
    return SS([(bg, 0.4, True), (bear, 1.0, False), ui(vign(0.35))], cam)


@shot5(B["charges"] - 0.1, "b04", "THE CHARGE: head-on, low to the ground, the grizzly gallops straight at the lens, roaring, dust exploding behind it until it fills the frame.")
def b04(t, D):
    u = ramp(t, 0, D)
    s_ = 0.35 * (1 + 7 * ei(u) ** 1.6)
    bear = bear3d(480 + 10 * math.sin(t * 9), lerp(300, 520, ei(u)), s_, -90, t, gait=(t * 2.4) % 1, run=1.0, roar=clamp(u * 2), persp=0.0016)
    dst = "".join(f'<circle cx="{480 + (k - 6) * 40 * s_ + 10 * math.sin(k * 3):.1f}" cy="{lerp(300, 520, ei(u)) + 10:.1f}" r="{(20 + 8 * (k % 3)) * s_:.1f}" fill="#C8A87A" opacity="0.45" filter="url(#b8)"/>' for k in range(13))
    bump = kick(t, 0.05, 10, 0.2) + 6 * math.sin(t * 15) * u
    cam = (0, 60 + bump, lerp(1.25, 1.45, u), lerp(-4, 5, u))
    fl = flashw(ramp(t, D - 0.12, D))
    return SS([(forest_back(t), 0.3, True), (pine_row(300, 21, "#1E4A36", 14, 160, 260), 0.6, True), (trail_persp(300), 1.0, True), (dst + bear, 1.0, False),
               ui(streaks(t, CX, 250, 0.6 * u) + fl)], cam)


@shot5(B["run"] - 0.1, "b05", "DOLLY ZOOM on the boy's terrified face: the forest stretches behind him; RUN! pulses inside his head.")
def b05(t, D):
    u = eio(ramp(t, 0, D))
    J = R3.FRONT | dict(shr=0.7, el=(-92, -300), hl=(-70, -360), er=(92, -300), hr=(70, -360),
                        face=fc(open=1.5, lift=1.2, knit=0.8, mouth="o", mo=0.6, look=(0.2 * math.sin(t * 7), 0)))
    me = boy(J, "b05", 480, 690, 1.05, L_FOREST)
    bg = f'<g transform="translate(480 300) scale({lerp(1.0, 1.9, u):.3f}) translate(-480 -300)">{forest_back(t)}{pine_row(360, 21, "#1E4A36", 14, 220, 340)}</g>'
    pulse = abs(math.sin(t * 9))
    tag = tag_big("RUN!", 480 + 4 * math.sin(t * 40), 70, ramp(t, 0.15, 0.45), 70, "#FF4A4A")
    return SS([(bg, 0.0, False), (me, 1.0, False), ui(tag + vign(0.25 + 0.25 * pulse, "#5A0000"))], (0, 0, 1.0, 0))


@shot5(B["dont"] - 0.1, "b06", "SNAP: he twists to run, a giant red X slams over him and DON'T stamps on screen. He freezes mid-step.")
def b06(t, D):
    u = eo(ramp(t, 0, 0.25))
    J = run_J(0.15, lean=lerp(0, 22, u), face=fc(open=1.4, lift=1.1, mouth="gasp"))
    me = boy(J, "b06", 480, 470, 0.62, L_FOREST, side=True, flip=True)
    cam = (0, -40 + kick(t, 0.12, 12, 0.2), lerp(1.2, 1.45, eo(ramp(t, 0, 0.3))), 0)
    return SS(forest_layers(t, 470) + [(pack_side(480, 470, 0.62, True) + me, 1.0, False)],
              cam, overlay=red_x(480, 230, ramp(t, 0.1, 0.35), 1.5) + tag_big("DON'T", 480, 420, ramp(t, 0.12, 0.4), 84, "#FF4A4A"))


@shot5(B["kmh"] - 0.1, "b07", "SIDE TRACKING at full speed: the grizzly gallops across the frame, the camera whips along beside it; a speed chip clocks ~55 km/h.")
def b07(t, D):
    bx = 300 + 260 * t
    bear = bear3d(bx, 410, 0.62, 0, t, gait=(t * 2.4) % 1, run=1.0, roar=0.3)
    dst = "".join(f'<circle cx="{bx - 120 - 50 * k - 30 * ((t * 3 + k) % 1):.1f}" cy="{400 - 10 * k:.1f}" r="{14 + 6 * k}" fill="#D8B888" opacity="{0.35 - 0.05 * k:.2f}" filter="url(#b6)"/>' for k in range(5))
    cam = (bx - CX + 20, 110, lerp(1.45, 1.3, ramp(t, 0, D)), -3)
    return SS([(forest_back(t), 0.25, True), (pine_row(370, 21, "#1E4A36", 18, 220, 340), 0.6, True), (trail_side(410), 1.0, True), (dst + bear, 1.0, False)],
              cam, overlay=hstreaks(0.5) + kmh_chip(480, 110, "~55 km/h", "GRIZZLY TOP SPEED", ramp(t, 0.15, 0.45)))


@shot5(B["human"] - 0.1, "b08", "THE RACE: the boy sprints flat out with the world's fastest human pace (~44 km/h) and the bear still blows past him.")
def b08(t, D):
    u = ramp(t, 0, D)
    hx = 420 + 200 * t; bxx = 160 + 330 * t
    me = boy(run_J((t * 2.2) % 1), "b08", hx, 430, 0.42, L_FOREST, side=True)
    bear = bear3d(bxx, 440, 0.52, 0, t, gait=(t * 2.6) % 1, run=1.0)
    cam = ((hx + bxx) / 2 - CX + 40, 110, 1.15, 0)
    chips = kmh_chip(480, 70, "~44 km/h", "FASTEST HUMAN EVER", ramp(t, 0.1, 0.4)) + kmh_chip(480, 200, "~55 km/h", "BEAR", ramp(t, 1.0, 1.3), edge="#FFB040")
    return SS([(forest_back(t), 0.25, True), (pine_row(390, 21, "#1E4A36", 18, 220, 340), 0.6, True), (trail_side(430), 1.0, True),
               (pack_side(hx, 430, 0.42) + me, 1.0, False), (bear, 1.0, False)], cam, overlay=hstreaks(0.35) + chips)


# ================================================================== the moves
@shot5(B["bluff"] - 0.1, "b09", "GROUND LEVEL: the bear thunders at the boy and skids to a dead stop metres away in a spray of dirt. BLUFF.")
def b09(t, D):
    sk = eo(ramp(t, 0.55, 1.05))
    bxx = lerp(900, 600, ramp(t, 0, 0.55)) - 70 * sk
    bear = bear3d(bxx, 430, 0.55, 180, t, gait=(t * 2.4) % 1 if sk < 0.05 else 0.0, run=1.0 - sk, skid=sk if sk < 0.99 else 0.0, roar=0.6 * (1 - sk), head_dy=8 * sk)
    J = R3.SIDE | dict(face=fc(open=1.3, lift=0.9, mouth="gasp", look=(1, 0)))
    me = pack_side(380, 430, 0.42) + boy(J, "b09", 380, 430, 0.42, L_FOREST, side=True)
    dirt = "".join(f'<circle cx="{bxx - 70 + 26 * k:.1f}" cy="{430 - 30 * sk * (k % 3):.1f}" r="{(10 + 6 * k) * sk:.1f}" fill="#C8A070" opacity="{0.5 * (1 - ramp(t, 1.1, D)):.2f}" filter="url(#b4)"/>' for k in range(6))
    cam = (lerp(110, 10, eio(ramp(t, 0, 1.0))), 110 + kick(t, 0.95, 10), lerp(1.1, 1.3, ramp(t, 0, D)), lerp(-6, 0, ramp(t, 0, 1)))
    return SS(forest_layers(t, 430) + [(me + bear + dirt, 1.0, False)], cam, overlay=tag_big("BLUFF", 480, 90, ramp(t, 1.0, 1.3), 76, "#FFE45A"))


@shot5(B["ground"] - 0.1, "b10", "LOW-ANGLE HERO ORBIT around the boy: he plants his feet, stands tall and spreads his arms to look bigger.")
def b10(t, D):
    u = eio(ramp(t, 0, D))
    up = eo(ramp(t, 0, 0.5))
    J = R3.FRONT | dict(el=(-150, -330 - 40 * up), hl=(-210, -380 - 60 * up), er=(150, -330 - 40 * up), hr=(210, -380 - 60 * up),
                        kl=(-40, -100), fl=(-56, 0), kr=(40, -100), fr=(56, 0), face=fc(open=1.0, lift=0.2, knit=0.6, mouth="grit", look=(0, 0)))
    me = boy(J, "b10", 480 + lerp(-30, 30, u), 520, 0.75, L_FOREST)
    bear = f'<g filter="url(#b6)">{bear3d(lerp(620, 340, u), 300, 0.32, lerp(-120, -60, u), t)}</g>'
    cam = (lerp(-30, 30, u), 30, lerp(1.25, 1.4, u), lerp(-9, 9, u))
    return SS([(forest_back(t), 0.2, True), (pine_row(300, 21, "#1E4A36", 14, 160, 260), 0.45, True), (trail_persp(300), 0.7, True), (bear, 0.7, False), (me, 1.0, False)], cam)


@shot5(B["calm"] - 0.1, "b11", "CLOSE-UP: palms out, he talks low and steady; soft calm rings ripple from his voice.")
def b11(t, D):
    talk = abs(math.sin(t * 11))
    J = R3.FRONT | dict(el=(-100, -300), hl=(-90, -380), er=(100, -300), hr=(90, -380),
                        face=fc(open=0.9, lift=0.3, mouth="o" if talk > 0.5 else "smile", mo=0.3 * talk, look=(0.3, 0)))
    me = boy(J, "b11", 480, 700, 1.1, L_FOREST)
    rings = "".join(f'<circle cx="480" cy="230" r="{60 + 120 * ((t * 0.9 + k / 3) % 1):.1f}" fill="none" stroke="#9AE8FF" stroke-width="5" opacity="{0.5 * (1 - (t * 0.9 + k / 3) % 1):.2f}"/>' for k in range(3))
    bg = f'<g filter="url(#b10)">{forest_back(t)}{pine_row(360, 21, "#1E4A36", 14, 220, 340)}</g>'
    cam = (lerp(10, -10, ramp(t, 0, D)), 0, lerp(1.0, 1.08, ramp(t, 0, D)), 0)
    return SS([(bg, 0.3, True), (rings, 0.9, False), (me, 1.0, False)], cam, overlay=tag_big("TALK CALMLY", 480, 470, ramp(t, 0.1, 0.4), 50))


@shot5(B["spray_out"] - 0.1, "b12", "MACRO: a hand rips the bear spray off the belt, the camera tilts up with it and the yellow safety clip flicks off.")
def b12(t, D):
    u = eio(ramp(t, 0, 0.9))
    cy_ = lerp(560, 330, u)
    can = spray_can(480, cy_, 1.6, lerp(-10, 0, u), safety=1 - eo(ramp(t, 1.1, 1.4)))
    hand = hand_grip(480, cy_ - 30, 1.5)
    belt = f'<rect x="-600" y="{lerp(500, 760, u):.0f}" width="2160" height="60" fill="#3A2A22"/><rect x="-600" y="{lerp(440, 700, u):.0f}" width="2160" height="400" fill="#3A4E7A" opacity="0.0"/>'
    bg = f'<g filter="url(#b12)">{forest_back(t)}{pine_row(360, 21, "#1E4A36", 14, 220, 340)}</g>'
    cam = (0, lerp(60, 0, u), lerp(1.2, 1.35, ramp(t, 0, D)), lerp(8, -4, u))
    return SS([(bg, 0.3, True), (belt, 1.0, False), (can + hand, 1.0, False)], cam)


@shot5(B["nostop"] - 0.1, "b13", "OVER THE SHOULDER: can raised at arm's length, the bear comes again, growing in the frame. Push in.")
def b13(t, D):
    u = ramp(t, 0, D)
    bear = bear3d(480, lerp(320, 360, u), lerp(0.4, 0.75, ei(u)), -90, t, gait=(t * 2.2) % 1, run=1.0, roar=0.5, persp=0.001)
    J = R3.FRONT | dict(er=(70, -380), hr=(40, -470), face=fc(open=1.0))
    me = boy(J, "b13", 380, 780, 0.95, L_FOREST, backv=True)
    can = spray_can(420, 300, 0.7, 20, safety=0)
    cam = (lerp(0, 20, u), 0, lerp(1.1, 1.3, eio(u)), 2)
    return SS([(forest_back(t), 0.3, True), (pine_row(300, 21, "#1E4A36", 14, 160, 260), 0.6, True), (trail_persp(300), 1.0, True), (bear, 1.0, False),
               (me + can, 1.4, False)], cam)


@shot5(B["cloud"] - 0.1, "b14", "SLOW-MO SIDE ORBIT: the boy fires; a huge orange cloud blooms right into the bear's face as it runs into it.")
def b14(t, D):
    u = ramp(t, 0, D)
    spr = eo(ramp(t, 0.15, 1.5))
    J = R3.SIDE | dict(e2=(60, -330), h2=(150, -340), e1=(50, -320), h1=(140, -330), lean=-4, face=fc(open=0.8, knit=0.9, mouth="grit", look=(1, 0)))
    me = pack_side(370, 430, 0.42) + boy(J, "b14", 370, 430, 0.42, L_FOREST, side=True)
    can = spray_can(370 + 150 * 0.42, 430 - 340 * 0.42, 0.32, 90, safety=0)
    bxx = lerp(720, 640, eo(u))
    bear = bear3d(bxx, 440, 0.5, 180 - 20 * spr, t * 0.4, gait=(t * 0.9) % 1, run=1 - spr, roar=0.7, blink=1.0 if spr > 0.5 else 0.0, head_dy=-6 * spr)
    cloud = spray_cloud(370 + 170 * 0.42, 430 - 340 * 0.42, spr, t, 1, 0.75)
    cam = (lerp(20, 40, eio(u)), 100, lerp(1.1, 1.18, eio(u)), lerp(-6, 6, eio(u)))
    return SS(forest_layers(t, 440) + [(me + can, 1.0, False), (bear, 1.0, False), (cloud, 1.05, False)], cam)


@shot5(B["enough"] - 0.1, "b15", "The bear wheels round and bolts into the trees, coughing; the camera rises over the boy. ~9 IN 10 stopped.")
def b15(t, D):
    u = ramp(t, 0, D)
    turn = eio(ramp(t, 0, 0.6))
    run_ = ramp(t, 0.4, D)
    bear = bear3d(lerp(620, 1000, ei(run_)), lerp(440, 380, run_), lerp(0.5, 0.42, run_), lerp(180, 20, turn), t, gait=(t * 2.2) % 1, run=run_)
    J = R3.SIDE | dict(e2=(40, -300), h2=(100, -260), face=fc(open=1.0, lift=0.3, mouth="smile", look=(1, 0)))
    me = pack_side(380, 440, 0.42) + boy(J, "b15", 380, 440, 0.42, L_FOREST, side=True)
    haze = f'<rect x="-600" y="-600" width="2160" height="1800" fill="#FFA060" opacity="{0.25 * (1 - u):.2f}" filter="url(#b20)"/>'
    cam = (lerp(30, 110, u), lerp(110, 60, eio(u)), lerp(1.2, 1.0, eio(u)), lerp(4, -4, u))
    return SS(forest_layers(t, 440) + [(me + bear + haze, 1.0, False)], cam,
              overlay=kmh_chip(480, 90, "~9 in 10", "CHARGES STOPPED BY SPRAY", ramp(t, 0.5, 0.8), edge="#5AE08A"))


# ================================================================== it depends on the bear
@shot5(B["contact"] - 0.1, "b16", "IMPACT FRAME: the bear lunges paw-first through the haze at the lens; white flash, the frame freezes red.")
def b16(t, D):
    u = ramp(t, 0, 0.7)
    bear = bear3d(480, lerp(420, 620, ei(u)), lerp(0.7, 2.6, ei(u)), -90, t, gait=0.6, run=1.0, roar=1.0, persp=0.0016)
    hit = clamp(1 - abs(t - 0.75) / 0.1)
    freeze = ramp(t, 0.85, 1.0)
    bg = f'<g filter="url(#b8)">{forest_back(t)}{pine_row(300, 21, "#1E4A36", 14, 160, 260)}{trail_persp(300)}</g>'
    cam = (0, 40 + kick(t, 0.7, 18, 0.2), 1.3, lerp(0, -6, u))
    return SS([(bg, 0.4, True), (bear, 1.0, False), (paw(lerp(520, 600, ei(u)), lerp(560, 330, ei(u)), lerp(0.4, 1.3, ei(u)), 15), 1.3, False)], cam,
              overlay=flashw(hit) + f'<rect x="200" y="-150" width="560" height="840" fill="#FF2A3A" opacity="{0.35 * freeze:.2f}" style="mix-blend-mode:multiply"/>')


def stage(t):
    return '<rect x="-600" y="-600" width="2160" height="1800" fill="url(#stageG)"/>' + glow(480, 360, 300, "#6A4AE0", 0.35, 40) + '<ellipse cx="480" cy="470" rx="420" ry="40" fill="#000000" opacity="0.3"/>'


@shot5(B["which"] - 0.1, "b17", "TURNTABLE: a grizzly and a black bear revolve side by side on a dark stage, a big ? between them.")
def b17(t, D):
    u = ramp(t, 0, D)
    y1 = 190 + 50 * t
    g_ = bear3d(480, 270, 0.72, y1, t, "grizzly")
    b_ = bear3d(480, 510, 0.72, y1 + 180, t, "black")
    cam = (0, 100, lerp(1.08, 1.14, u), 0)
    return SS([(stage(t), 0.4, True), (g_ + b_, 1.0, False)], cam,
              overlay=tag_big("GRIZZLY?", 480, 40, ramp(t, 0.2, 0.5), 42) + tag_big("BLACK BEAR?", 480, 270, ramp(t, 0.5, 0.8), 42) + tag_big("?", 610, 200, ramp(t, 1.0, 1.3), 110, "#FFE45A"),
              lights=())


@shot5(B["wrong"] - 0.1, "b18", "WHIP PANS between the two bears, the light goes blood red: DEADLY.")
def b18(t, D):
    side_ = 0 if t < 0.55 else (1 if t < 1.1 else 0)
    g_ = bear3d(330, 390, 0.62, -40, t, "grizzly", roar=0.8)
    b_ = bear3d(1130, 390, 0.62, -140, t, "black", roar=0.8)
    pos = [0, 1, 0, 1][min(3, int(t / 0.55))]
    x = 330 if pos == 0 else 1130
    wp = max(whip(t, 0.55, 0.12), whip(t, 1.1, 0.12), whip(t, 1.65, 0.12))
    cam = (x - CX + 30, 40, 1.45, 0)
    red = f'<rect x="-600" y="-600" width="2560" height="1800" fill="#FF1A2A" opacity="{0.3 * ramp(t, 0.6, 1.6):.2f}" style="mix-blend-mode:multiply"/>'
    return SS([(stage(t), 0.4, True), (g_ + b_ + red, 1.0, False)], cam,
              overlay=hstreaks(wp) + tag_big("DEADLY", 480, 470, ramp(t, 0.9, 1.2), 84, "#FF4A4A") + vign(0.35 * ramp(t, 0.5, 1.5), "#3A0000"), lights=())


@shot5(B["griz"] - 0.1, "b19", "ORBIT around a roaring grizzly, the camera swinging under its chin. Badge: GRIZZLY.")
def b19(t, D):
    u = eio(ramp(t, 0, D))
    g_ = bear3d(480, 420, 0.75, lerp(-20, -60, u), t, "grizzly", roar=0.6 + 0.4 * math.sin(t * 6))
    cam = (lerp(-40, 30, u), 0, lerp(1.4, 1.6, u), lerp(-8, 8, u))
    return SS(forest_layers(t, 420) + [(g_, 1.0, False)], cam, overlay=badge("GRIZZLY", ramp(t, 0.05, 0.3), "#C8742A"))


def topdown(t):
    r = random.Random(4)
    o = ['<rect x="-800" y="-800" width="2560" height="2200" fill="url(#topG)"/>',
         '<path d="M-800 180 Q480 120 1760 200 L1760 360 Q480 300 -800 340 Z" fill="#C8A070"/>']
    o.append(grass_tufts(-600, 1400, 12, 160, "#4E7E36"))
    o.append(rocks(200, 320, 13, 10))
    for _ in range(18):
        x, y = r.uniform(-500, 1500), r.uniform(-600, 1300)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(8, 18):.0f}" fill="#8AB85A" opacity="0.5"/>')
    return "".join(o)


@shot5(B["stomach"] - 0.25, "b20", "OVERHEAD, ROTATING: the boy drops flat on his stomach and laces his hands behind his neck; the camera corkscrews down.")
def b20(t, D):
    u = eio(ramp(t, 0, D))
    hands = eo(ramp(t, B["neck"] - (B["stomach"] - 0.25), B["neck"] - (B["stomach"] - 0.25) + 0.6))
    J_el = (lerp(-110, -96, hands), lerp(-280, -420, hands))
    me = prone("b20", 612, 300, 0.5, L_FOREST, -90, 0.2)
    if hands < 1:
        J = R3.FRONT | dict(el=J_el, hl=(lerp(-120, -26, hands), lerp(-200, -470, hands)), er=(-J_el[0], J_el[1]), hr=(lerp(120, 26, hands), lerp(-200, -470, hands)),
                            kl=(-46, -100), fl=(-56, 0), kr=(46, -100), fr=(56, 0), face=fc(open=0.2))
        me = f'<g transform="translate(612 300) rotate(-90)">' + lit(back_pose(J), "b20", 0, 0, 0.5, L_FOREST) + '</g>'
    cam = (0, 0, lerp(1.1, 1.65, u), lerp(-40, 10, u))
    return SS([(topdown(t), 1.0, True), (me, 1.0, False)], cam, overlay=tag_big("ON YOUR STOMACH", 480, 470, ramp(t, 0.25, 0.55), 36) if t < 1.1 else tag_big("HANDS ON NECK", 480, 470, ramp(t, 1.1, 1.4), 40))


@shot5(B["legs"] - 0.1, "b21", "OVERHEAD: his legs swing wide; a huge clawed paw shoves at his side and can't roll him over.")
def b21(t, D):
    sp = eo(ramp(t, 0, 0.5))
    shove = math.sin(math.pi * clamp((t - 0.7) / 0.9))
    me = prone("b21", 612, 300 - 6 * shove, 0.5, L_FOREST, -90 + 3 * shove, 0.2 + 0.8 * sp)
    pw = paw(480 + 20 * shove, lerp(-60, 120, clamp((t - 0.6) / 0.4)) + 20 * shove, 0.9, 180)
    arrows = "".join(f'<path d="M{640:.0f} {300 + 60 * k * sp:.0f} l30 {30 * k}" stroke="#FFE45A" stroke-width="10" stroke-linecap="round" opacity="{sp:.2f}"/>' for k in (-1, 1))
    cam = (0, 0, lerp(1.25, 1.4, ramp(t, 0, D)), 0)
    return SS([(topdown(t), 1.0, True), (me + arrows, 1.0, False), (pw, 1.1, False)], cam, overlay=tag_big("LEGS WIDE", 480, 470, ramp(t, 0.15, 0.45), 52))


@shot5(B["black"] - 0.1, "b22", "WHIP PAN: a black bear swings round to face us. Badge: BLACK BEAR.")
def b22(t, D):
    u = eio(ramp(t, 0, D))
    b_ = bear3d(480, 420, 0.75, lerp(-160, -50, eo(ramp(t, 0, 0.5))), t, "black")
    cam = (lerp(-260, 0, eo(ramp(t, 0, 0.3))), 0, lerp(1.5, 1.6, u), 0)
    return SS(forest_layers(t, 420) + [(b_, 1.0, False)], cam, overlay=hstreaks(1 - ramp(t, 0, 0.3)) + badge("BLACK BEAR", ramp(t, 0.1, 0.35), "#3A3448"))


@shot5(B["fight"] - 0.1, "b23", "LOW ANGLE: the boy snatches a thick branch off the ground and raises it overhead, jaw set.")
def b23(t, D):
    up = eo(ramp(t, 0.1, 0.7))
    J = R3.FRONT | dict(er=(110, lerp(-260, -380, up)), hr=(lerp(120, 60, up), lerp(-160, -500, up)), el=(-90, -300), hl=(-60, -340),
                        kl=(-40, -100), fl=(-60, 0), kr=(40, -100), fr=(60, 0), face=fc(open=1.0, knit=1.0, lift=-0.2, mouth="grit", look=(0, 0)))
    hx, hy = 480 + lerp(120, 60, up) * 0.75, 560 + lerp(-160, -500, up) * 0.75
    ang = lerp(20, -60, up)
    st = stick(hx - 40 * math.cos(math.radians(ang)), hy - 40 * math.sin(math.radians(ang)), 0.9, ang)
    me = boy(J, "b23", 480, 560, 0.75, L_FOREST)
    cam = (0, 40, lerp(1.2, 1.35, ramp(t, 0, D)), lerp(6, -3, up))
    return SS([(forest_back(t), 0.2, True), (pine_row(300, 21, "#1E4A36", 14, 160, 260), 0.45, True), (trail_persp(300), 0.8, True), (me + st, 1.0, False)], cam,
              overlay=tag_big("FIGHT BACK", 480, 470, ramp(t, 0.15, 0.45), 60, "#FFE45A"))


@shot5(B["hit"] - 0.1, "b24", "IMPACT FRAMES: whack, whack, the branch cracks across the black bear's nose; it flinches and backs off.")
def b24(t, D):
    hits = [0.55, 1.45, 2.3]
    sw = 0.0
    for h in hits:
        sw = max(sw, clamp(1 - abs(t - h) / 0.25))
    J = R3.SIDE | dict(e2=(50, -340), h2=(lerp(-20, 120, sw), lerp(-480, -300, sw)), e1=(30, -330), h1=(lerp(-30, 100, sw), lerp(-470, -300, sw)),
                       lean=lerp(-6, 10, sw), face=fc(open=1.0, knit=1.0, mouth="grit", look=(1, 0)))
    me = pack_side(400, 440, 0.45) + boy(J, "b24", 400, 440, 0.45, L_FOREST, side=True)
    sx, sy = 400 + lerp(-20, 120, sw) * 0.45, 440 + lerp(-480, -300, sw) * 0.45
    st = stick(sx, sy, 0.6, lerp(-80, 40, sw))
    rec = max(clamp(1 - abs(t - h - 0.15) / 0.3) for h in hits)
    back_off = ramp(t, 2.4, D)
    bear = bear3d(lerp(650, 760, back_off) + 20 * rec, 450, 0.55, 180 + 15 * back_off, t, "black", head_dx=-12 * rec, head_dy=-6 * rec, blink=rec, roar=0.4 * rec,
                  gait=(t * 1.2) % 1 if back_off > 0 else 0.0)
    stars = "".join(impact_star(568, 400, clamp((t - h) / 0.3), 0.5) for h in hits if t > h)
    cam = (40 + kick(t, 0.55, 8) + kick(t, 1.45, 8) + kick(t, 2.3, 8), 100, lerp(0.95, 1.02, ramp(t, 0, D)), -4)
    return SS(forest_layers(t, 440) + [(bear, 1.0, False), (me + st, 1.0, False), (stars, 1.0, False)], cam,
              overlay=tag_big("FACE + NOSE", 480, 90, ramp(t, 0.3, 0.6), 52))


# ================================================================== the twist
CYC = [GRIZ, BLACK_BROWN, GRIZ_DARK, BLACK]


def fur_mix(a, b, u):
    return tuple(mixc(x, y, u) for x, y in zip(a, b))


@shot5(B["twist"] - 0.1, "b25", "THE TWIST: the two bears stand on the stage while their fur colours flicker and swap like a glitch.")
def b25(t, D):
    k = int(t * 5) % 4
    fa = CYC[k]; fb = CYC[(k + 2) % 4]
    g_ = bear3d(480, 280, 0.72, -20, t, "grizzly", fur=fa)
    b_ = bear3d(480, 510, 0.72, -160, t, "black", fur=fb)
    gl = f'<rect x="200" y="{(t * 900) % 700 - 60:.0f}" width="560" height="16" fill="#FFFFFF" opacity="0.15"/>'
    cam = (0, 80, lerp(1.0, 1.06, ramp(t, 0, D)), 0)
    return SS([(stage(t), 0.4, True), (g_ + b_, 1.0, False)], cam, overlay=gl + tag_big("THE TWIST", 480, 40, ramp(t, 0.05, 0.3), 54, "#FFE45A"), lights=())


@shot5(B["cant"] - 0.1, "b26", "PUSH IN: COLOUR LIES stamps over a paint-swatch strip; brown, black, cinnamon, blond all point to both bears.")
def b26(t, D):
    u = eio(ramp(t, 0, D))
    sw = "".join(f'<rect x="{325 + 80 * k}" y="400" width="66" height="66" rx="12" fill="{c}" stroke="#FFFFFF" stroke-width="4" opacity="{clamp((t - 0.15 * k) * 4):.2f}"/>' for k, c in enumerate(["#1E1A22", "#5A381E", "#A86A3A", "#D8B07A"]))
    g_ = bear3d(480, 210, 0.55, -30 + 30 * u, t, "grizzly", fur=GRIZ_DARK)
    b_ = bear3d(480, 350, 0.55, -150 - 30 * u, t, "black", fur=BLACK_BROWN)
    cam = (0, 0, lerp(1.0, 1.08, u), lerp(-3, 3, u))
    return SS([(stage(t), 0.4, True), (g_ + b_, 1.0, False), (sw, 1.0, False)], cam, overlay=tag_big("COLOUR LIES", 480, 60, ramp(t, 0.2, 0.5), 50, "#FF4A6A"), lights=())


@shot5(B["brown"] - 0.1, "b27", "SPOTLIGHT ORBIT: a cinnamon-brown bear walks across the trail... label: BLACK BEAR.")
def b27(t, D):
    u = eio(ramp(t, 0, D))
    b_ = bear3d(lerp(420, 540, u), 430, 0.68, lerp(-10, -40, u), t, "black", fur=BLACK_BROWN, gait=(t * 0.8) % 1)
    cam = (lerp(-40, 60, u), 100, lerp(1.25, 1.4, u), lerp(-6, 6, u))
    return SS(forest_layers(t, 430) + [(b_, 1.0, False)], cam, overlay=badge("BLACK BEAR", ramp(t, 0.15, 0.4), "#3A3448") + tag_big("(it's brown!)", 480, 150, ramp(t, 0.5, 0.8), 46, "#E8A060"))


@shot5(B["gblack"] - 0.1, "b28", "SMASH CUT: a near-black bear looms out of deep shade... label: GRIZZLY.")
def b28(t, D):
    u = eio(ramp(t, 0, D))
    g_ = bear3d(480, 440, lerp(0.6, 0.72, u), lerp(-60, -25, u), t, "grizzly", fur=GRIZ_DARK)
    shade = '<rect x="-600" y="-600" width="2160" height="1800" fill="#0A1420" opacity="0.45"/>'
    cam = (lerp(30, -20, u), 100, lerp(1.25, 1.4, u), lerp(4, -4, u))
    return SS(forest_layers(t, 440) + [(shade, 1.0, True), (g_, 1.0, False)], cam, lights=(L_SHADE,),
              overlay=badge("GRIZZLY", ramp(t, 0.15, 0.4), "#C8742A") + tag_big("(it's black!)", 480, 150, ramp(t, 0.5, 0.8), 46, "#B8B0C8"))


@shot5(B["hump"] - 0.1, "b29", "ORBIT up to the shoulders of the dark grizzly: the big muscle hump lights up in gold.")
def b29(t, D):
    u = eio(ramp(t, 0, D))
    g_ = bear3d(480, 470, 0.95, lerp(-30, 10, u), t, "grizzly", fur=GRIZ_DARK, glow_hump=ramp(t, 0.3, 0.7))
    cam = (lerp(0, 32, u), lerp(110, 60, u), lerp(1.3, 1.75, u), lerp(-8, 4, u))
    return SS(forest_layers(t, 470) + [(g_, 1.0, False)], cam, overlay=tag_big("THE HUMP", 480, 470, ramp(t, 0.3, 0.6), 66, "#FFE45A"))


@shot5(B["hump2"] - 0.1, "b30", "SILHOUETTE CHART: the grizzly outline in profile; its shoulder hump lights up gold with an arrow.")
def b30(t, D):
    u = ramp(t, 0, D)
    g_ = bear3d(480, 360, 0.95, 0, t, "grizzly", sil="#2A1E3A", glow_hump=ramp(t, 0.3, 0.7))
    ax, ay = 480 + 34 * 0.95, 360 - 200 * 0.95
    arrow = f'<path d="M{ax:.0f} {ay - 50 - 8 * math.sin(t * 8):.0f} l0 44 m-18 -20 l18 20 l18 -20" stroke="#E8A020" stroke-width="10" fill="none" stroke-linecap="round" opacity="{ramp(t, 0.6, 0.9):.2f}"/>'
    bg = '<rect x="-600" y="-600" width="2160" height="1800" fill="#F4ECDC"/>'
    cam = (0, 50, lerp(1.1, 1.2, u), 0)
    return SS([(bg, 0.4, True), (g_ + arrow, 1.0, False)], cam, overlay=badge("GRIZZLY = HUMP", ramp(t, 0.1, 0.4), "#C8742A", 60), lights=())


@shot5(B["nohump"] - 0.1, "b31", "The black bear outline slides in under it: a flat line runs across its shoulders, the rump is highest. Red X on the hump spot.")
def b31(t, D):
    u = ramp(t, 0, D)
    g_ = bear3d(480, 230, 0.62, 0, t, "grizzly", sil="#2A1E3A", glow_hump=1.0)
    sl = eo(ramp(t, 0, 0.4))
    b_ = bear3d(lerp(900, 480, sl), 460, 0.62, 0, t, "black", sil="#2A1E3A")
    tr = eio(ramp(t, 0.4, 1.0))
    y_ = 460 - 152 * 0.62
    line_ = f'<path d="M{480 - 100 * 0.62:.0f} {y_:.0f} L{480 + lerp(-100, 110, tr) * 0.62:.0f} {y_:.0f}" stroke="#2AA8E0" stroke-width="8" stroke-dasharray="14 10" stroke-linecap="round" opacity="{sl:.2f}"/>'
    bg = '<rect x="-600" y="-600" width="2160" height="1800" fill="#F4ECDC"/>'
    cam = (0, 60, lerp(1.0, 1.06, u), 0)
    return SS([(bg, 0.4, True), (g_ + b_, 1.0, False), (line_ + red_x(480 + 36 * 0.62, y_ - 30, ramp(t, 1.0, 1.25), 0.4), 1.0, False)], cam,
              overlay=badge("BLACK BEAR: NO HUMP", ramp(t, 0.3, 0.6), "#3A3448", 480), lights=())


@shot5(B["q"] - 0.1, "b32", "BACK ON THE TRAIL: over the boy's shoulder a bear steps out and stares; FLASH, it's the other kind. WHICH ONE? Loops to the start.")
def b32(t, D):
    u = eio(ramp(t, 0, D))
    k = 0 if t < 1.6 else 1
    fur = GRIZ_DARK if k == 0 else BLACK_BROWN
    kind = "grizzly" if k == 0 else "black"
    bear = bear3d(500, 330, 0.42, lerp(-130, -100, u), t, kind, fur=fur)
    J = R3.FRONT | dict(face=fc(open=1.0))
    me = boy(J, "b32", lerp(330, 380, u), 760, 0.95, L_FOREST, backv=True)
    cam = (lerp(-10, 20, u), lerp(0, 20, u), lerp(1.3, 1.5, u), lerp(-4, 2, u))
    fl = flashw(clamp(1 - abs(t - 1.6) / 0.08) * 0.7)
    return SS([(forest_back(t), 0.3, True), (pine_row(300, 21, "#1E4A36", 14, 160, 260), 0.6, True), (trail_persp(300), 1.0, True), (bear, 1.0, False), (me, 1.4, False)],
              cam, overlay=fl + tag_big("WHICH ONE?", 480, 90, ramp(t, 0.4, 0.7), 60, "#FFE45A"))


TEND = round(TEND, 3)
