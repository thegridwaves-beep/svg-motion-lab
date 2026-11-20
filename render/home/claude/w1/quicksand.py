"""Short 4/7: What to do if you sink in quicksand (~56 s). The trap, the wrong moves, the float, the move that saves you."""
import os
os.environ["SHORT"] = "quicksand"
import anim_core
from qs_props import *
anim_core.ANIM[:] = []

B = {}
for i, ph in PH.items():
    for k, q in enumerate(ph):
        B[(i, k)] = q["t"]
TEND = round(TEND, 3)
G, BX, BS = 400, 480, 0.5          # ground line where he stands, his x, his scale
WAIST = 196 * BS                   # how far he sinks when floating waist deep


def SS(layers, cam=(0, 0, 1.0), overlay="", lights=(L_BEACH,)):
    return SV(layers, cam, QS_DEFS, overlay, lights)


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


def badge(txt, u, col=PINK, y=78, x=480):
    """Pill label in overlay space. Sized for the portrait squeeze (overlay x0.375)."""
    if u <= 0:
        return ""
    k = 0.6 + 0.4 * eo(min(1, u * 2))
    fs = min(74, 860 / max(1, len(txt))); w = len(txt) * fs * 0.62 + 70; h = fs * 1.6
    return (f'<g transform="translate({x} {y}) scale({k:.3f})" opacity="{clamp(u * 3):.2f}"><rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="{h / 2}" fill="{col}" stroke="#FFFFFF" stroke-width="7"/>'
            + text(0, fs * 0.36, txt, fs, "#FFFFFF", 700, "middle") + '</g>')


def eqs(x, y, u, w=60):
    """Equals sign drawn as two bars (world space)."""
    if u <= 0:
        return ""
    k = eo(min(1, u * 2))
    return "".join(f'<rect x="{x - w / 2 * k:.1f}" y="{y + dy - 8:.1f}" width="{w * k:.1f}" height="16" rx="8" fill="#FFFFFF" stroke="{INK}" stroke-width="5"/>' for dy in (-16, 16))


def legs_through(J, uid, x, y, s, x0, x1, G, depth, op=0.92):
    """Redraw the boy clipped to the cut-away box so his buried legs show through the sand section."""
    cid = f"lt_{uid}"
    return (f'<clipPath id="{cid}"><rect x="{x0}" y="{G}" width="{x1 - x0}" height="{depth}"/></clipPath>'
            f'<g clip-path="url(#{cid})" opacity="{op}">{kid(J, uid + "L", x, y, s)}</g>')


def kick(t, t0, amp=14, dur=0.25):
    return amp * math.sin(math.pi * clamp((t - t0) / dur)) * (1 - clamp((t - t0) / dur)) if t > t0 else 0.0


def back(t, dusk=0.0, pool=None):
    return [(beach_sky(dusk) + headland(), 0.3, True), (sea(t) + SAND + (quick_pool(*pool) if pool else ""), 1.0, False)]


def shadow(x, y, w):
    return f'<ellipse cx="{x:.1f}" cy="{y + 2:.1f}" rx="{w:.1f}" ry="{w * 0.16:.1f}" fill="#3A2A1A" opacity="0.25"/>'


# ------------------------------------------------------------------ poses (boy faces right, feet at y=0 local)
def stuck_J(t, churn=1.0, face=None):
    w = math.sin(t * 7) * churn
    J = dict(R3.SIDE)
    J.update(lean=6 * w, hip=(4 * w, 0), e1=(-60, -300 + 10 * w), h1=(-100 + 14 * w, -350 - 20 * w), e2=(60, -305 - 10 * w), h2=(110 - 10 * w, -335 + 18 * w),
             k1=(26 + 10 * w, -110), k2=(6 - 10 * w, -112),
             face=face or fc(open=1.5, lift=1.2, knit=0.8, mouth="gasp", look=(0.3, 1.0)))
    return J


def pull_J(u, face=None):
    """Bent over, both hands clamped round his own thigh, hauling up (u = effort 0..1)."""
    J = dict(R3.SIDE)
    J.update(lean=lerp(10, 26, u), hip=(0, lerp(0, -14, u)), e1=(-6, -262), h1=(34, -196 - 14 * u), e2=(20, -266), h2=(52, -192 - 14 * u),
             k1=(36, -112 - 20 * u), f1=(4, -8 * u), k2=(10, -108), f2=(10, 0),
             face=face or fc(open=1.0, knit=1.4, mouth="grit", look=(0.6, 0.8)))
    return J


def reach_J(u, face=None):
    """Both arms stretched forward to the helpers (he faces them)."""
    J = dict(R3.SIDE)
    J.update(lean=lerp(4, 18, u), e1=(70, -322), h1=(150, -318), e2=(76, -326), h2=(158, -322),
             k1=(16, -110), k2=(16, -110), face=face or fc(open=1.3, knit=1.2, lift=1.0, mouth="grit", look=(1, 0)))
    return J


def calm_J(t, face=None, wig=0.0):
    b = math.sin(t * 2.2)
    J = dict(R3.SIDE)
    J.update(lean=-2, e1=(-60, -270), h1=(-100, -232 + 4 * b), e2=(64, -272), h2=(104, -236 - 4 * b),
             k1=(16 + 22 * math.cos(t * 4) * wig, -110 + 10 * math.sin(t * 4) * wig), f1=(-10 + 30 * math.cos(t * 4) * wig, 14 * math.sin(t * 4) * wig),
             k2=(16 + 22 * math.cos(t * 4 + 2) * wig, -110 + 10 * math.sin(t * 4 + 2) * wig), f2=(10 + 30 * math.cos(t * 4 + 2) * wig, 14 * math.sin(t * 4 + 2) * wig),
             face=face or fc(open=0.8, mouth="flat", look=(1, 0.2)))
    return J


def float_J(u, t=0.0, face=None):
    """Arms spreading wide like a starfish, legs drifting up in front (rotate the whole body to lie back)."""
    J = dict(R3.SIDE)
    J.update(lean=0, e1=(lerp(-60, -110, u), lerp(-270, -330, u)), h1=(lerp(-100, -180, u), lerp(-232, -360, u)),
             e2=(lerp(64, 110, u), lerp(-272, -330, u)), h2=(lerp(104, 180, u), lerp(-236, -360, u)),
             k1=(lerp(16, 60, u), lerp(-110, -100, u)), f1=(lerp(-10, 80, u), lerp(0, -20, u)), k2=(lerp(16, 50, u), lerp(-110, -104, u)), f2=(lerp(10, 70, u), lerp(0, -16, u)),
             face=face or fc(open=0.9, mouth="flat", look=(0.6, -0.4)))
    return J


def kid(J, uid, x, y, s=BS, flip=False, rot=0.0, Lt=L_BEACH):
    """The boy, optionally rotated about his hip (to lie back)."""
    body = boy(J, uid, x, y, s, Lt, side=True, flip=flip)
    if rot:
        px, py = x, y - 200 * s
        body = f'<g transform="rotate({rot:.2f} {px:.1f} {py:.1f})">{body}</g>'
    return body


# ================================================================== the trap
@shot5(0.0, "q01", "WIDE, LOW TIDE: glistening flats to the horizon, the boy strolls along in the morning sun. A darker glossy patch ahead.")
def q01(t, D):
    u = eio(ramp(t, 0, D))
    x = lerp(380, 470, ramp(t, 0, D))
    J = walk_J((t * 0.9) % 1, face=fc(open=1.0, mouth="smile", look=(1, 0)))
    me = shadow(x, G, 40) + kid(J, "q01", x, G)
    cam = (lerp(-10, 20, u), lerp(60, 70, u), lerp(1.2, 1.4, u), 0)
    return SS(back(t, pool=(BX + 30, G + 6, 0.8)) + [(me, 1.0, False)], cam)


@shot5(B[(0, 1)] - 0.1, "q02", "LOW CLOSE AT SAND LEVEL: his shoe lands on the glossy patch, the sand quivers and swallows it to the shin; the second foot goes in too.")
def q02(t, D):
    sink = 52 * eo(ramp(t, 0.15, D))
    wob = 3 * math.sin(t * 30) * (1 - ramp(t, 0.2, 0.8))
    J = stuck_J(t, 0.3 * ramp(t, 0.6, D), fc(open=1.2, lift=1.0, mouth="o", look=(0.4, 1.0))) | dict(lean=8)
    me = kid(J, "q02", BX, G + sink)
    front = sand_front("q02", G, BX, BS, sink, t, churn=0.6)
    cam = (BX - CX + 10, G - CY - 30 + wob, lerp(2.7, 2.4, ramp(t, 0, D)), 0)
    return SS(back(t, pool=(BX, G + 6, 1.0)) + [(me, 1.0, False), (front, 1.0, False)], cam)


@shot5(B[(1, 0)] - 0.15, "q03", "MEDIUM: knee deep, he twists and flails, every jerk pulls him lower. QUICKSAND.")
def q03(t, D):
    sink = lerp(52, 82, eio(ramp(t, 0, D)))
    J = stuck_J(t, 1.0)
    me = kid(J, "q03", BX, G + sink)
    front = sand_front("q03", G, BX, BS, sink, t, churn=1.0)
    cam = (BX - CX, G - CY - 70, lerp(1.25, 1.4, eio(ramp(t, 0, D))), 2 * math.sin(t * 2))
    return SS(back(t, pool=(BX, G + 6, 1.0)) + [(me, 1.0, False), (front, 1.0, False)], cam,
              overlay=badge("QUICKSAND", ramp(t, 0.1, 0.4), "#C8803A", 90) + tag_big("IT WON'T LET GO", 480, 210, ramp(t, B[(1, 1)] - B[(1, 0)], B[(1, 1)] - B[(1, 0)] + 0.3), 84, "#FFE45A"))


# ================================================================== the wrong moves
@shot5(B[(2, 0)] - 0.15, "q04", "CLOSE, SLIGHT HIGH ANGLE: he grabs his own thigh with both hands and heaves; the sand doesn't budge.")
def q04(t, D):
    eff = 0.5 + 0.5 * math.sin(t * 5.5)
    J = pull_J(eff)
    sink = 82 + 4 * eff
    me = kid(J, "q04", BX, G + sink)
    front = sand_front("q04", G, BX, BS, sink, t, churn=0.5)
    strain = "".join(f'<path d="M{BX + 24 + 10 * k} {G - 50 - 12 * k} l8 -10" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity="{0.8 * eff:.2f}"/>' for k in range(3))
    cam = (BX - CX + 10, G - CY - 40, lerp(1.6, 1.75, ramp(t, 0, D)), -3)
    return SS(back(t, pool=(BX, G + 6, 1.0)) + [(me, 1.0, False), (front + strain, 1.0, False)], cam)


@shot5(B[(2, 1)] - 0.12, "q05", "Freeze on the heave, a big red X slams over it: DON'T.")
def q05(t, D):
    J = pull_J(1.0)
    me = kid(J, "q05", BX, G + 86)
    front = sand_front("q05", G, BX, BS, 86, 0.5, churn=0.0)
    cam = (BX - CX + 10, G - CY - 40 + kick(t, 0.1, 10), 1.75, -3)
    return SS(back(0.5, pool=(BX, G + 6, 1.0)) + [(me, 1.0, False), (front + red_x(BX + 10, G - 60, ramp(t, 0.05, 0.3), 0.55), 1.0, False)], cam,
              overlay=tag_big("DON'T", 480, 120, ramp(t, 0.05, 0.3), 130, "#FF5A5A"))


@shot5(B[(2, 2)] - 0.15, "q06", "CUT-AWAY: his buried leg with an arrow pulling up... equals a car being hoisted off the ground. Same force.")
def q06(t, D):
    u = ramp(t, 0, D)
    sink, x = 82, 400
    J = pull_J(0.6, fc(open=1.0, knit=1.4, mouth="grit", look=(0.6, 0.8)))
    me = kid(J, "q06", x, G + sink)
    front = sand_front("q06", G, x, BS, sink, t, churn=0.2, pool=False)
    cut = sand_cut(x - 50, x + 50, G, 90, t) + legs_through(J, "q06", x, G + sink, BS, x - 50, x + 50, G, 90)
    up = arrow_up(x + 52, G - 10, 120, 40, "#FFE45A", ramp(t, 0.4, 0.9))
    lift = eo(ramp(t, 1.4, 2.4))
    cx, cy = 588, G + 20 - 70 * lift
    chain = (f'<path d="M{cx} -300 L{cx} {cy - 92:.0f}" stroke="#4A4A5A" stroke-width="5"/>'
             f'<path d="M{cx - 44} {cy - 64:.0f} L{cx} {cy - 92:.0f} L{cx + 44} {cy - 64:.0f}" stroke="#4A4A5A" stroke-width="4" fill="none"/>')
    carg = shadow(cx, G + 20, 70 * (1 - 0.4 * lift)) + chain + car(cx, cy, 0.46) + arrow_up(cx, cy - 104, 70, 34, "#FFE45A", ramp(t, 1.6, 2.1))
    cam = (494 - CX, G - CY - 70, 1.0, 0)
    return SS(back(t) + [(me, 1.0, False), (front + cut, 1.0, False), (up + carg + eqs(500, G - 60, ramp(t, 1.0, 1.3)), 1.0, False)], cam,
              overlay=badge("ONE FOOT = A CAR", ramp(t, 1.8, 2.2), "#E8504A", 90))


@shot5(B[(3, 0)] - 0.15, "q07", "He faces left: a friend's arms reach in and grab his wrists and haul; his body stretches, a red strain flares at the shoulders. Red X.")
def q07(t, D):
    pull = 0.5 + 0.5 * math.sin(t * 4.0) * ramp(t, 0.4, 1.0)
    J = reach_J(pull)
    x = 520
    me = kid(J, "q07", x, G + 82, flip=True)
    front = sand_front("q07", G, x, BS, 82, t, churn=0.3)
    a = math.radians(J["lean"])
    hx = x - (J["h1"][0] * math.cos(a) - (J["h1"][1] + 200) * math.sin(a)) * BS
    hy = G + 82 + (J["h1"][0] * math.sin(a) + (J["h1"][1] + 200) * math.cos(a) - 200) * BS
    arms = friend_arms(hx, hy, 1.0, pull, t)
    hurt = clamp((t - (B[(3, 1)] - B[(3, 0)])) / 0.6)
    flare = glow(x - 20, G + 82 - 330 * BS, 36, "#FF3A4A", 0.6 * hurt * (0.6 + 0.4 * pull), 8) if hurt > 0 else ""
    cam = (x - CX - 60, G - CY - 60, 1.25, 0)
    return SS(back(t, pool=(x, G + 6, 1.0)) + [(me + flare, 1.0, False), (front, 1.0, False), (arms, 1.0, False)], cam,
              overlay=tag_big("NO PULLING", 480, 120, ramp(t, 0.1, 0.4), 110, "#FF5A5A") + tag_big("IT CAN HURT YOU", 480, 230, ramp(t, B[(3, 2)] - B[(3, 0)], B[(3, 2)] - B[(3, 0)] + 0.3), 80, "#FFFFFF"))


# ================================================================== the twist
@shot5(B[(4, 0)] - 0.15, "q08", "OLD MOVIE FRAME: a man sinks out of sight in sepia quicksand, one hand left, bubbles. A red MYTH stamp slams down.")
def q08(t, D):
    u = ramp(t, 0, D)
    cx, cy, w, h = 480, 210, 280, 210
    sy = cy + 30                                            # sand line inside the frame
    hs = lerp(-70, 70, eio(ramp(t, 0.0, 1.5)))
    hand = (f'<g transform="translate({cx} {sy + hs:.0f})"><rect x="-13" y="-20" width="26" height="90" rx="10" fill="#6A4428"/>'
            '<path d="M-14 -20 Q-24 -40 -16 -58 M-6 -24 L-6 -72 M4 -24 L6 -76 M14 -22 L20 -66" stroke="#6A4428" stroke-width="11" stroke-linecap="round" fill="none"/>'
            '<rect x="-20" y="30" width="40" height="40" rx="8" fill="#5A4A3A"/></g>')
    inner = (f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" fill="url(#qsFilm)"/>' + hand
             + f'<path d="M{cx - w / 2} {sy} Q{cx} {sy - 6} {cx + w / 2} {sy} L{cx + w / 2} {cy + h / 2} L{cx - w / 2} {cy + h / 2} Z" fill="#6A4A2A"/>'
             + f'<ellipse cx="{cx}" cy="{sy + 2}" rx="40" ry="6" fill="#4A3220"/>'
             + "".join(f'<circle cx="{cx + 16 * math.sin(k * 2 + t * 3):.0f}" cy="{sy - 4 - ((t * 40 + 14 * k) % 34):.0f}" r="{3 + k % 3}" fill="none" stroke="#F0DCB8" stroke-width="2" opacity="{ramp(t, 1.0, 1.3):.2f}"/>' for k in range(4)))
    fr = film_frame(cx, cy, w, h, inner, t)
    return SS([(f'<rect x="-800" y="-800" width="2560" height="2000" fill="url(#stageQ)"/>', 0.3, True), (fr + stamp(cx, cy + 20, "MYTH", ramp(t, 1.0, 1.25), size=56), 1.0, False)],
              (0, -50, lerp(1.15, 1.22, u), 0), lights=(), overlay=badge("IN THE MOVIES", ramp(t, 0.05, 0.35), "#5A4AB0", 90))


@shot5(B[(4, 1)] - 0.15, "q09", "CUT-AWAY SIDE VIEW: the boy settles, floating waist deep. Grains and water packed below him. 2x DENSER than you.")
def q09(t, D):
    u = ramp(t, 0, D)
    sink = lerp(112, WAIST, eo(ramp(t, 0.2, 2.2))) + 3 * math.sin(t * 2)
    J = calm_J(t, fc(open=1.2, lift=1.0, mouth="o", look=(0.4, 0.8)))
    me = kid(J, "q09", BX, G + sink)
    front = sand_front("q09", G, BX, BS, sink, t, churn=0.1, pool=False)
    cut = sand_cut(BX - 70, BX + 70, G, 140, t) + legs_through(J, "q09", BX, G + sink, BS, BX - 70, BX + 70, G, 140)
    bar = ""
    k1 = ramp(t, B[(4, 1)] - B[(4, 1)] + 0.4, 1.2)
    if k1 > 0:
        for j, (lab, h, col) in enumerate((("YOU", 60, "#2EA6C8"), ("SAND", 120, "#C8A06A"))):
            bx = 585 + 62 * j; hh = h * eo(k1)
            bar += (f'<rect x="{bx - 18}" y="{G + 110 - hh:.0f}" width="36" height="{hh:.0f}" rx="6" fill="{col}" stroke="{INK}" stroke-width="4"/>'
                    + text(bx, G + 138, lab, 22, "#FFFFFF", 700, "middle").replace("<text ", f'<text stroke="{INK}" stroke-width="5" paint-order="stroke" '))
    float_tag = tag_big("YOU FLOAT", 480, 230, ramp(t, B[(4, 2)] - B[(4, 1)], B[(4, 2)] - B[(4, 1)] + 0.3), 110, "#FFE45A")
    waist = (f'<path d="M{BX - 110} {G:.0f} L{BX + 110} {G:.0f}" stroke="#FFE45A" stroke-width="5" stroke-dasharray="12 8" opacity="{ramp(t, B[(4, 3)] - B[(4, 1)], B[(4, 3)] - B[(4, 1)] + 0.3):.2f}"/>')
    cam = (lerp(40, 50, u), G - CY - 20, lerp(1.0, 1.08, u), 0)
    return SS(back(t) + [(me, 1.0, False), (front + cut + waist, 1.0, False), (bar, 1.0, False)], cam,
              overlay=badge("SAND: 2x DENSER", ramp(t, 0.5, 0.9), "#C8803A", 90) + float_tag)


@shot5(B[(5, 0)] - 0.15, "q10", "MEDIUM: waist deep, he stops panicking and breathes out. Relief... then he turns to look out to sea.")
def q10(t, D):
    turn = ramp(t, 1.4, 2.2)
    J = calm_J(t, fc(open=lerp(0.7, 1.4, turn), mouth="smile" if turn < 0.5 else "o", look=(1, lerp(0.3, -0.3, turn))))
    me = kid(J, "q10", BX, G + WAIST)
    front = sand_front("q10", G, BX, BS, WAIST, t, churn=0.0)
    cam = (BX - CX + 10, G - CY - 80, lerp(1.6, 1.8, eio(ramp(t, 0, D))), 0)
    return SS(back(t, pool=(BX, G + 6, 1.0)) + [(me, 1.0, False), (front, 1.0, False)], cam)


@shot5(B[(5, 1)] - 0.2, "q11", "WIDE TIME-LAPSE, LIGHT TURNING GOLD: the sea slides in across the flats toward the tiny boy stuck in the sand.")
def q11(t, D):
    u = ramp(t, 0, D)
    dusk = 0.6 * u
    edge = lerp(HZ + 70, G - 10, eio(u))
    me = kid(calm_J(t, fc(open=1.5, lift=1.3, mouth="gasp", look=(1, -0.2))), "q11", BX, G + WAIST)
    front = sand_front("q11", G, BX, BS, WAIST, t, churn=0.0)
    water = tide_sheet(t * 3, edge, 0.85)
    cam = (BX - CX + 20, G - CY - 60, lerp(0.85, 0.95, u), 0)
    return SS([(beach_sky(dusk) + headland(), 0.3, False), (sea(t) + SAND + quick_pool(BX, G + 6, 1.0) + water, 1.0, False), (me, 1.0, False), (front, 1.0, False)], cam, lights=(L_DUSK,),
              overlay=tag_big("THE TIDE", 480, 130, ramp(t, B[(5, 2)] - B[(5, 1)] + 0.1, B[(5, 2)] - B[(5, 1)] + 0.4), 130, "#FF5A5A"))


# ================================================================== the move
@shot5(B[(6, 0)] - 0.15, "q12", "CLOSE ON HIS FACE: eyes close, a slow breath out. THE MOVE.")
def q12(t, D):
    J = calm_J(t, fc(open=0.1 if t < 0.5 else 0.8, mouth="flat", look=(1, 0)))
    me = kid(J, "q12", BX, G + WAIST)
    front = sand_front("q12", G, BX, BS, WAIST, t, churn=0.0)
    cam = (BX - CX + 10, G + WAIST - 380 * BS - CY + 20, 2.4, 0)
    return SS(back(t, pool=(BX, G + 6, 1.0)) + [(me, 1.0, False), (front, 1.0, False)], cam,
              overlay=badge("THE MOVE", ramp(t, 0.05, 0.3), "#3AB07A", 90))


@shot5(B[(6, 1)] - 0.1, "q13", "CUT-AWAY UNDER THE SAND: his legs trace slow small circles; blue water trickles down the gaps and the grains loosen around them.")
def q13(t, D):
    u = ramp(t, 0, D)
    J = calm_J(t, fc(open=0.8, mouth="flat", look=(0.6, 0.6)), wig=1.0)
    me = kid(J, "q13", BX, G + WAIST)
    front = sand_front("q13", G, BX, BS, WAIST, t, churn=0.15, pool=False)
    seep = ramp(t, B[(6, 3)] - B[(6, 1)], B[(6, 3)] - B[(6, 1)] + 1.0)
    cut = sand_cut(BX - 80, BX + 90, G, 150, t, seep=seep, loose=seep) + legs_through(J, "q13", BX, G + WAIST, BS, BX - 80, BX + 90, G, 150)
    circ = "".join(f'<ellipse cx="{BX + dx}" cy="{G + WAIST - 14}" rx="20" ry="8" fill="none" stroke="#FFE45A" stroke-width="3" stroke-dasharray="6 5" opacity="{ramp(t, 0.6, 1.0):.2f}" transform="rotate({t * 120:.0f} {BX + dx} {G + WAIST - 14})"/>' for dx in (-6, 8))
    drips = "".join(f'<path d="M{BX + dx} {G + 6 + ((t * 50 + 30 * k) % 110):.0f} q-6 10 0 16" stroke="#3AB4E8" stroke-width="4" fill="none" stroke-linecap="round" opacity="{seep * 0.9:.2f}"/>' for k, dx in enumerate((-40, -20, 24, 46, 62)))
    cam = (BX - CX + 10, G + 40 - CY, lerp(1.7, 1.9, u), 0)
    return SS(back(t) + [(me, 1.0, False), (front + cut + circ + drips, 1.0, False)], cam,
              overlay=tag_big("WIGGLE SLOWLY", 480, 120, ramp(t, 0.1, 0.4), 100, "#FFE45A") + badge("WATER LOOSENS IT", ramp(t, B[(6, 3)] - B[(6, 1)], B[(6, 3)] - B[(6, 1)] + 0.3), "#2E8AC8", 230))


@shot5(B[(7, 0)] - 0.15, "q14", "SIDE: he lies back, arms spread wide like a starfish; his legs ease up toward the surface as he floats flat.")
def q14(t, D):
    lean = eio(ramp(t, 0, B[(7, 1)] - B[(7, 0)] + 0.3))
    spread = eio(ramp(t, B[(7, 1)] - B[(7, 0)], B[(7, 1)] - B[(7, 0)] + 0.6))
    rise = eio(ramp(t, B[(7, 2)] - B[(7, 0)], D))
    J = float_J(spread, t, fc(open=0.9, mouth="flat", look=(0.4, -0.6)))
    sink = WAIST + 6 - 8 * rise
    me = kid(J, "q14", BX, G + sink, rot=lerp(0, -68, lean) - 10 * rise)
    front = sand_front("q14", G, BX, BS, sink, t, churn=0.05)
    cam = (BX - CX - 20, G - CY - 40, lerp(1.35, 1.25, ramp(t, 0, D)), 0)
    return SS(back(t, pool=(BX, G + 6, 1.0)) + [(me, 1.0, False), (front, 1.0, False)], cam,
              overlay=tag_big("LEAN BACK", 480, 120, ramp(t, 0.05, 0.35), 110, "#FFE45A") + tag_big("ARMS OUT", 480, 230, ramp(t, B[(7, 1)] - B[(7, 0)], B[(7, 1)] - B[(7, 0)] + 0.3), 90, "#FFFFFF"))


@shot5(B[(7, 3)] - 0.15, "q15", "TRACKING SIDE: floating flat, half in the sand, he scoots left a little at a time toward the dry grassy bank, and finally grabs it.")
def q15(t, D):
    step = t * 1.4; inch = (math.floor(step) + eio(step % 1)) * 20
    x = BX - inch
    FX = BX - 150                                           # foot of the firm bank
    grab = eio(ramp(t, D - 1.1, D - 0.5))
    J = float_J(1.0, t, fc(open=0.9 + 0.4 * grab, mouth="smile" if grab > 0.5 else "flat", look=(0.4, -0.6)))
    if grab > 0:
        J = J | dict(e1=(lerp(-110, -40, grab), lerp(-330, -380, grab)), h1=(lerp(-180, -40, grab), lerp(-360, -470, grab)))
    me = kid(J, "q15", x, G + WAIST + 2, rot=-72 + 3 * math.sin(step * TAU))
    bank = (f'<path d="M-900 {G - 26} L{FX - 40} {G - 26} Q{FX} {G - 24} {FX + 30} {G + 2} L{FX + 30} {G + 30} L-900 {G + 30} Z" fill="#E8D6AA"/>'
            f'<path d="M-900 {G - 26} L{FX - 40} {G - 26} Q{FX} {G - 24} {FX + 30} {G + 2}" stroke="#F6EACC" stroke-width="5" fill="none"/>'
            + "".join(f'<path d="M{FX - 30 - 34 * k} {G - 26} q-4 -18 -9 -26 M{FX - 30 - 34 * k} {G - 26} q2 -20 7 -30 M{FX - 30 - 34 * k} {G - 26} q6 -14 14 -18" stroke="#6E9A50" stroke-width="3.5" fill="none" stroke-linecap="round"/>' for k in range(12)))
    front = sand_front("q15", G, x, BS, WAIST, t, churn=0.1)
    cam = (x - CX - 40, G - CY - 50, 1.35, 0)
    return SS(back(t, pool=(BX - 60, G + 6, 1.4)) + [(bank, 1.0, False), (me, 1.0, False), (front, 1.0, False)], cam,
              overlay=tag_big("INCH BY INCH", 480, 120, ramp(t, 0.05, 0.35), 100, "#FFE45A") + tag_big("FIRM GROUND", 480, 230, ramp(t, D - 1.0, D - 0.7), 90, "#4AE07A"))


# ================================================================== the question
@shot5(B[(8, 0)] - 0.15, "q16", "SPLIT SCREEN: left, the boy heaving at his leg (red); right, the boy floating back calmly (green). Which one?")
def q16(t, D):
    s2 = 0.42
    Lb = kid(pull_J(0.5 + 0.5 * math.sin(t * 5)), "q16a", 392, G + 70, s2) + sand_front("q16a", G, 392, s2, 70, t, churn=0.5, pool=False)
    Rb = kid(float_J(1.0, t), "q16b", 590, G + 92, s2, flip=True, rot=76) + sand_front("q16b", G, 590, s2, 92, t, churn=0.0, pool=False)
    div = '<rect x="476" y="-300" width="8" height="1000" fill="#FFFFFF"/>'
    tint = (f'<rect x="200" y="-300" width="276" height="1000" fill="#FF3A4A" opacity="{0.2 * ramp(t, 0.2, 0.6):.2f}"/>'
            f'<rect x="484" y="-300" width="300" height="1000" fill="#3AE07A" opacity="{0.2 * ramp(t, B[(8, 2)] - B[(8, 0)], B[(8, 2)] - B[(8, 0)] + 0.4):.2f}"/>')
    cam = (0, G - CY - 70, 1.0, 0)
    return SS(back(t) + [(Lb, 1.0, False), (Rb, 1.0, False), (tint + div, 1.0, False)], cam,
              overlay=tag_big("PULL?", 250, 140, ramp(t, 0.3, 0.6), 110, "#FF5A5A") + tag_big("LEAN BACK?", 712, 140, ramp(t, B[(8, 2)] - B[(8, 0)], B[(8, 2)] - B[(8, 0)] + 0.3), 62, "#4AE07A"))
