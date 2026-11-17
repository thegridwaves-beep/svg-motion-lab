"""Short 7: What happens if a screwworm fly lays eggs in you? (~65 s) - the danger, how it escalates, the 3 moves that save you."""
import os
os.environ["SHORT"] = "screwworm"
import anim_core
from sw_props import *
anim_core.ANIM[:] = []
from people3 import ADULTS, adult
SIT = R3.F_SIT

SW_DEFS = lin("hospW", [(0, "#E8F2F8"), (1, "#CFE2EE")])


def SS(layers, cam=(0, 0, 1.0), overlay="", lights=()):
    return SV(layers, cam, SW_DEFS, overlay, lights)


def badge_num(n, u, x=480, y=70):
    if u <= 0:
        return ""
    k = 0.6 + 0.4 * eo(min(1, u * 2))
    return (f'<g transform="translate({x} {y}) scale({k:.3f})" opacity="{clamp(u * 3):.2f}"><circle r="34" fill="{PINK}" stroke="#FFFFFF" stroke-width="5"/>'
            + text(0, 14, str(n), 42, "#FFFFFF", 700, "middle") + '</g>')


def bounce_fly(t, x, y, s, t0, seed=0):
    """A fly that comes in, hits a barrier at t0 and bounces off, comically."""
    u = t - t0
    if u < 0:
        fx, fy = x + 120 * (-u), y - 80 * (-u)
    else:
        fx, fy = x + 140 * u, y - 160 * u + 260 * u * u
    return fly3d(fx, fy, s, -30 + 200 * max(0, u), t, flap=1.0, legs="fly")


# ================================================================== the danger
@shot5(0.0, "w01", "CRANE DOWN from the stars past the treetops to a campsite: the boy asleep in a sleeping bag by a dying fire. A fly zips past the lens.")
def w01(t, D):
    u = eio(ramp(t, 0, D))
    zip_fly = fly3d(lerp(260, 760, ramp(t, 0.3, 1.0)), lerp(80, 260, ramp(t, 0.3, 1.0)), 2.6, -20, t, flap=1.0, legs="fly") if 0.3 < t < 1.05 else ""
    cam = (lerp(0, 0, u), lerp(-420, 140, u), lerp(1.0, 1.35, u), lerp(-6, 0, u))
    return SS([(sky(t, 0.0), 0.35, False), (trees(0.0), 0.7, True), (ground(0.0) + tent(250, 390, 1.0) + campfire(660, 420, t, 1.0, 0.3) + sleeper(t, 480, 470, 0.78), 1.0, False),
               (f'<g filter="url(#b3)">{zip_fly}</g>', 1.6, False)], cam, lights=(L_NIGHT,))


@shot5(Pn(0, 1) - 0.1, "w02", "TRACK along the sleeping bag to his bare ankle poking out; push in to a tiny cut glistening in the firelight.")
def w02(t, D):
    u = eio(ramp(t, 0, D))
    ax, ay = 480 + 190 * 0.78, 470 - 14 * 0.78
    cam = (lerp(-120, ax - CX + 11, u), lerp(60, ay - CY, u), lerp(1.8, 6.5, u), lerp(-4, 4, u))
    return SS([(sky(t, 0.0), 0.35, True), (ground(0.0) + campfire(660, 420, t, 1.0, 0.3) + sleeper(t, 480, 470, 0.78), 1.0, False)], cam, lights=(L_NIGHT,))


@shot5(Ln(1) - 0.1, "w03", "SLAM: macro on the cut; the fly drops from above the lens and lands right beside it. The camera kicks.")
def w03(t, D):
    land = eo(ramp(t, 0.0, 0.5))
    f = fly3d(500, lerp(-150, 270, land), lerp(7.0, 3.2, land), -20, t, flap=1 - 0.9 * land, legs="land" if land > 0.9 else "fly")
    kick = 16 * math.sin(math.pi * clamp((t - 0.5) / 0.25)) * (1 - ramp(t, 0.5, 0.9))
    bg = skin_macro(8) + cut(470, 330, 260, 16, 1.0, 0.0, 1.0, -6) + '<rect x="-600" y="-600" width="2160" height="1800" fill="#1A1440" opacity="0.35"/>' + glow(700, 120, 300, "#FF9A4A", 0.35, 40)
    cam = (0, lerp(20, 40, land) + kick, lerp(1.45, 1.7, eio(ramp(t, 0.5, D))), lerp(-12, 0, eo(ramp(t, 0, 0.7))))
    return SS([(bg, 0.8, True), (f, 1.0, False), (fg_hairs(t, 21, 4, 30), 2.2, False)], cam, lights=(L_NIGHT,))


@shot5(Pn(1, 1) - 0.1, "w04", "3D ORBIT around the fly: metallic blue-green body, three dark stripes, its big orange eyes catch the firelight and glow.")
def w04(t, D):
    u = eio(ramp(t, 0, D))
    f = fly3d(480, 300, 3.6, lerp(-10, -150, u), t, legs="land", glow_eyes=ramp(t, D * 0.4, D))
    bg = f'<g filter="url(#b4)">{skin_macro(8)}</g>' + '<rect x="-600" y="-600" width="2160" height="1800" fill="#1A1440" opacity="0.35"/>' + cut(470, 360, 260, 16, 1.0)
    fl = flare(lerp(560, 400, u), 290, clamp(1 - abs(u - 0.55) * 4), "#FFB070")
    cam = (lerp(-80, 80, u), 20, lerp(1.6, 1.9, u), lerp(-14, 14, u))
    return SS([(bg, 0.45, True), (f + fl, 1.0, False), (fg_hairs(t, 23, 3, 0, 0.8, 8), 2.4, False)], cam, lights=(L_NIGHT,))


@shot5(Pn(1, 2) - 0.1, "w05", "CRASH ZOOM onto its face, head-on; the word SCREWWORM slams onto the screen.")
def w05(t, D):
    u = ei(ramp(t, 0, D * 0.5))
    f = fly3d(480, 300, 3.6, -80, t, legs="land", glow_eyes=0.6)
    bg = f'<g filter="url(#b6)">{skin_macro(8)}</g>' + '<rect x="-600" y="-600" width="2160" height="1800" fill="#1A1440" opacity="0.45"/>'
    cam = (0, -10, lerp(1.6, 2.7, u), 0)
    return SS([(bg, 0.5, True), (f, 1.0, False), ui(streaks(t, CX, CY, 0.8 * (1 - ramp(t, D * 0.5, D))) + tag_big("SCREWWORM", 480, 470, ramp(t, D * 0.35, D * 0.6), 54, "#FF8A3A"))], cam, lights=(L_NIGHT,))


@shot5(Ln(2) - 0.1, "w06", "MACRO TRACK along the edge of the cut as she lays: rows of rice-white eggs pile up like roof shingles; a counter flicks up to ~200.")
def w06(t, D):
    lay = ramp(t, 0.15, D * 0.95)
    eggs = egg_shingles(470, 316, 240, 60, lay, 1.6, seed=4, ang=-6)
    fx = lerp(370, 590, lay)
    f = fly3d(fx, 250, 2.6, -15, t, legs="land")
    n = int(200 * eo(lay))
    cam = (lerp(-90, 110, eio(lay)), 40, 2.0, lerp(4, -4, lay))
    bg = skin_macro(8) + cut(470, 330, 260, 16, 1.0, 0.0, 1.0, -6) + '<rect x="-600" y="-600" width="2160" height="1800" fill="#1A1440" opacity="0.35"/>'
    return SS([(bg, 0.85, True), (eggs + f, 1.0, False), ui(chip(f"~{n} EGGS", 480, 60, ramp(t, 0.3, 0.6), 24, edge="#FF8A3A"))], cam, lights=(L_NIGHT,))


@shot5(Pn(2, 2) - 0.1, "w07", "OVERHEAD PULL-OUT, rotating: the whole cut ringed with white egg clusters while he sleeps on, unaware.")
def w07(t, D):
    u = eio(ramp(t, 0, D))
    bg = skin_macro(8) + cut(470, 300, 260, 16, 1.0, 0.0, 1.0, -6) + egg_shingles(470, 284, 240, 60, 1.0, 1.6, seed=4, ang=-6) + egg_shingles(470, 318, 220, 50, 1.0, 1.6, seed=9, ang=174) + '<rect x="-600" y="-600" width="2160" height="1800" fill="#1A1440" opacity="0.35"/>'
    cam = (0, 0, lerp(2.4, 1.1, u), lerp(-30, 20, u))
    return SS([(bg, 1.0, True)], cam, lights=(L_NIGHT,))


@shot5(Ln(3) - 0.1, "w08", "TIME-LAPSE: wide campsite, the moon sinks and the sun rises in seconds, shadows sweep, the fire dies to smoke. Chip: WITHIN A DAY.")
def w08(t, D):
    day = eio(ramp(t, 0.1, D * 0.9))
    cam = (0, lerp(60, 30, day), 1.3, lerp(-3, 3, day))
    return SS([(sky(t * 4, day), 0.35, False), (trees(day), 0.7, False), (ground(day) + tent(250, 390, 1.0, day) + campfire(660, 420, t, 1.0, day) + sleeper(t, 480, 470, 0.78, L_DAY if day > 0.5 else L_NIGHT), 1.0, False),
               ui(chip("WITHIN A DAY", 480, 60, ramp(t, 0.2, 0.5), 24, edge="#FFD23F"))], cam, lights=(L_NIGHT, L_DAY))


@shot5(Pn(3, 1) - 0.15, "w09", "LOW DOLLY across the cut: the eggs split and dozens of white maggots pour out and swarm into the wound.")
def w09(t, D):
    h = ramp(t, 0.0, D * 0.4); crawl = ramp(t, D * 0.25, D)
    bg = skin_macro(8) + cut(470, 330, 260, 16 + 20 * crawl, 1.0, 0.3 * crawl, 1.0, -6)
    eggs = egg_shingles(470, 316, 240, 60, 1.0, 1.6, hatch=h, seed=4, ang=-6)
    r = random.Random(3); mg = ""
    for k in range(26):
        sx_, sy_ = 360 + r.uniform(0, 220), 300 + r.uniform(-20, 10)
        tx, ty = 420 + r.uniform(0, 100), 330 + r.uniform(-6, 6)
        cu = clamp(crawl * 1.4 - k * 0.02)
        mg += screw_maggot(lerp(sx_, tx, cu), lerp(sy_, ty, cu), 0.32, t + k, 90 + r.uniform(-40, 40), 1.0, 1.0)
    cam = (lerp(-60, 60, eio(ramp(t, 0, D))), 50, 2.3, lerp(-8, 8, ramp(t, 0, D)))
    return SS([(bg, 0.9, True), (eggs + mg, 1.0, False)], cam, lights=(L_DAY,))


@shot5(Pn(3, 2) - 0.1, "w10", "LOW DUTCH: the boy jolts awake, eyes wide, mouth open; red flash on 'Alive'.")
def w10(t, D):
    jolt = eo(ramp(t, 0, 0.3))
    J = R3.FRONT | dict(head=(0, 0, -8), el=(-110, -300), hl=(-140, -380), er=(110, -300), hr=(140, -380),
                        face=fc(open=lerp(0.3, 1.6, jolt), lift=lerp(0.2, 1.2, jolt), knit=0.4, mouth="o", mo=lerp(0.2, 0.8, jolt), look=(0.4, 0.8)))
    b = boy(J, "w10", 480, lerp(700, 640, jolt), 1.0, L_DAY)
    flash = flashw(clamp(1 - abs(t - (Pn(3, 3) - Ln(3) - (Pn(3, 2) - 0.1 - Ln(3)))) / 0.1) * 0.6, "#FF3A3A")
    cam = (0, lerp(0, -30, eio(ramp(t, 0, D))), lerp(1.4, 1.65, eio(ramp(t, 0, D))), -10)
    return SS([(sky(t, 1.0) + trees(1.0) + ground(1.0), 0.6, True), (b, 1.0, False), ui(flash)], cam, lights=(L_DAY,))


@shot5(Ln(4) - 0.1, "w11", "X-RAY DIVE: the camera plunges into the skin cross-section after the maggots as they spiral head-first into the flesh like screws.")
def w11(t, D):
    u = eio(ramp(t, 0, D))
    r = random.Random(5); mg = ""
    for k in range(9):
        x0 = 400 + k * 20 + r.uniform(-8, 8); dd = clamp(u * 1.3 - k * 0.04)
        mg += screw_maggot(x0, SURF + 10 + 150 * dd, 0.55, t * 1.4 + k, 90 + r.uniform(-15, 15), 2.0, 0.6)
    tunnel = "".join(f'<path d="M{400 + k * 20} {SURF} L{400 + k * 20} {SURF + 150 * clamp(u * 1.3 - k * 0.04):.0f}" stroke="#7A2A3A" stroke-width="14" stroke-linecap="round"/>' for k in range(9))
    cam = (lerp(0, 10, u), lerp(-40, 150, u), lerp(1.2, 2.3, u), lerp(10, -10, u))
    return SS([(skin_xsec(t, pocket=0.0, hair=True), 1.0, False), (tunnel + mg, 1.0, False)], cam)


@shot5(Pn(4, 2) - 0.1, "w12", "OVERHEAD TIME-LAPSE, slow spin: the wound widens, the maggots packed inside, wriggling.")
def w12(t, D):
    u = eio(ramp(t, 0, D))
    r = random.Random(7); mg = ""
    for k in range(int(20 + 30 * u)):
        a = r.uniform(0, TAU); rr = r.uniform(0, 1) ** 0.5
        mg += screw_maggot(470 + (100 + 40 * u) * rr * math.cos(a), 330 + (16 + 22 * u) * rr * math.sin(a), 0.3, t + k, math.degrees(a) + 90, 1.0, 1.0)
    bg = skin_macro(8)
    w = cut(470, 330, 260 + 60 * u, 16, 1.0, lerp(0.3, 1.0, u), 1.0, -6)
    cam = (0, 30, lerp(2.0, 2.3, u), lerp(0, 50, u))
    return SS([(bg, 1.0, True), (w + mg, 1.0, False)], cam, lights=(L_DAY,))


@shot5(Pn(4, 3) - 0.1, "w13", "WIDE, CRANE UP and orbit: more flies spiral down out of the sky toward his ankle.")
def w13(t, D):
    u = eio(ramp(t, 0, D))
    fl = ""
    for k in range(10):
        a = t * 3 + k * TAU / 10; rr = 160 * (1 - 0.6 * u) + 20 * (k % 3)
        fl += fly3d(660 + rr * math.cos(a), 300 + 0.4 * rr * math.sin(a) - 200 * (1 - u) * (k % 2), 0.55, math.degrees(a), t, flap=1.0, legs="fly")
    cam = (lerp(160, 140, u), lerp(-40, 80, u), lerp(1.3, 1.9, u), lerp(-10, 10, u))
    return SS([(sky(t, 1.0), 0.35, True), (trees(1.0), 0.7, True), (ground(1.0) + tent(250, 390, 1.0, 1.0) + sleeper(t, 480, 470, 0.78, L_DAY), 1.0, False), (fl, 1.0, False)], cam, lights=(L_DAY,))


@shot5(Ln(5) - 0.1, "w14", "X-RAY HEAD, side view: a glowing red trail creeps from the nose up through the sinuses toward the brain; the camera tracks with it.")
def w14(t, D):
    p = ramp(t, 0.1, D)
    pts = [(712, 330), (660, 318), (620, 298), (598, 262), (580, 230), (540, 200)]
    n = len(pts) - 1; f = min(p * n, n - 1e-6); i = int(f); v = f - i
    hx, hy = lerp(pts[i][0], pts[i + 1][0], v), lerp(pts[i][1], pts[i + 1][1], v)
    cam = (hx - CX, hy - CY, lerp(2.4, 1.8, eio(p)), lerp(-8, 8, p))
    return SS([(xray_head(t, p, hot=0.3 * p), 1.0, False)], cam)


@shot5(Pn(5, 2) - 0.1, "w15", "PUSH IN on the brain as it pulses red; a heartbeat thud and a hard cut to black.")
def w15(t, D):
    pulse = 0.5 + 0.5 * math.sin(t * 9)
    cam = (40, -110, lerp(1.6, 2.6, ei(ramp(t, 0, D))), 0)
    return SS([(xray_head(t, 1.0, hot=0.6 + 0.4 * pulse), 1.0, False), ui(flashw(ramp(t, D - 0.15, D), "#000000"))], cam)


# ================================================================== the three moves
@shot5(Ln(6) - 0.1, "w16", "WHIP out of black into bright daylight: the boy stands at the campsite and points at the camera.")
def w16(t, D):
    J = R3.FRONT | dict(er=(100, -330), hr=(150, -420), face=fc(open=1.1, lift=0.6, mouth="grin", look=(0, 0)))
    b = boy(J, "w16", 480, 470, 0.75, L_DAY)
    wp = 1 - ramp(t, 0, 0.3)
    cam = (lerp(-200, 0, eo(ramp(t, 0, 0.35))), -20, lerp(1.25, 1.4, eio(ramp(t, 0, D))), 0)
    return SS([(sky(t, 1.0) + trees(1.0), 0.6, True), (ground(1.0) + tent(250, 390, 1.0, 1.0), 1.0, True), (b, 1.0, False), ui(hstreaks(wp))], cam, lights=(L_DAY,))


@shot5(Pn(6, 1) - 0.1, "w17", "PUNCH-IN: '3 MOVES' slams onto screen with three icons: a plaster, a net, a doctor's cross.")
def w17(t, D):
    u = ramp(t, 0, 0.3)
    icons = ""
    for k, (sym, col) in enumerate((("+", "#E8C8A0"), ("#", "#8AD0FF"), ("✚", "#FF5A6A"))):
        a = ramp(t, 0.25 + 0.15 * k, 0.45 + 0.15 * k)
        icons += f'<g transform="translate({380 + 100 * k} 330) scale({0.6 + 0.4 * eo(a):.2f})" opacity="{a:.2f}"><circle r="40" fill="{col}" stroke="#FFFFFF" stroke-width="5"/>' + text(0, 16, sym, 44, INK, 700, "middle") + '</g>'
    bg = sky(t, 1.0) + trees(1.0) + ground(1.0)
    cam = (0, 0, 1.3 + 0.2 * math.exp(-t * 5), 0)
    return SS([(f'<g filter="url(#b8)">{bg}</g>', 0.6, True), ui(tag_big("3 MOVES", 480, 220, u, 80, "#FFD23F") + icons)], cam, lights=(L_DAY,))


@shot5(Ln(7) - 0.1, "w18", "MOVE 1, SLOW MOTION: a plaster slaps over the cut; a fly comes in and bounces off it, comically.")
def w18(t, D):
    slap = eo(ramp(t, 0.1, 0.45))
    bg = skin_macro(8) + cut(470, 330, 200, 12, 1.0, 0.0, 1.0, -6)
    pl = (f'<g transform="translate(470 {lerp(120, 330, slap):.0f}) rotate(-6) scale({lerp(1.4, 1.0, slap):.2f})"><rect x="-150" y="-50" width="300" height="100" rx="40" fill="#E8C8A0"/>'
          '<rect x="-60" y="-34" width="120" height="68" rx="10" fill="#F8E8D8"/>' + "".join(f'<circle cx="{-120 + 18 * k}" cy="{-30 + 20 * (k % 3)}" r="2" fill="#C8A880"/>' for k in range(14)) + '</g>')
    f = bounce_fly(t, 470, 300, 1.5, D * 0.55)
    hit = flashw(clamp(1 - abs(t - 0.45) / 0.06) * 0.6)
    cam = (0, 20, 1.6 + 0.25 * math.exp(-max(0, t - 0.45) * 5) * (t > 0.45), 0)
    return SS([(bg, 0.9, True), (pl + f, 1.0, False), ui(badge_num(1, ramp(t, 0, 0.25)) + hit)], cam, lights=(L_DAY,))


@shot5(Pn(7, 1) + 1.3, "w19", "MOVE 2, CRANE DOWN: a mosquito net drops over the sleeping boy; flies slam into the mesh and bounce away.")
def w19(t, D):
    drop = eo(ramp(t, 0.1, 0.7))
    top = lerp(-260, 250, drop)
    o = []
    for k in range(-12, 13):
        x0 = 470 + k * 26
        o.append(f'<path d="M470 {top:.0f} Q{470 + k * 18:.0f} {top + 80:.0f} {x0 + k * 6:.0f} 500" stroke="#FFFFFF" stroke-width="1.4" fill="none" opacity="0.55"/>')
    for j in range(1, 8):
        yy = lerp(top, 500, j / 8); ww = lerp(30, 320, (j / 8) ** 0.7)
        o.append(f'<path d="M{470 - ww:.0f} {yy:.0f} Q470 {yy - 18:.0f} {470 + ww:.0f} {yy:.0f}" stroke="#FFFFFF" stroke-width="1.4" fill="none" opacity="0.5"/>')
    dome = f'<path d="M150 500 Q160 {top + 120:.0f} 470 {top:.0f} Q780 {top + 120:.0f} 790 500 Z" fill="#FFFFFF" opacity="0.14"/>'
    net_ = f'<g opacity="{0.4 + 0.6 * drop:.2f}">{dome}{"".join(o)}</g>' + f'<path d="M470 {top:.0f} L470 -400" stroke="#DDDDDD" stroke-width="2"/>'
    fl = bounce_fly(t, 640, 330, 0.9, D * 0.55) + bounce_fly(t, 320, 340, 0.8, D * 0.75)
    cam = (0, lerp(-100, 40, eio(ramp(t, 0, D * 0.6))), lerp(1.2, 1.5, eio(ramp(t, 0, D))), 0)
    return SS([(sky(t, 0.0) + trees(0.0), 0.5, True), (ground(0.0) + tent(250, 390, 1.0) + campfire(660, 420, t, 1.0, 0.2) + sleeper(t, 480, 470, 0.78), 1.0, False), (net_ + fl, 1.0, False),
               ui(badge_num(2, ramp(t, 0, 0.25)))], cam, lights=(L_NIGHT,))


@shot5(Ln(8) - 0.1, "w20", "MOVE 3, DUTCH CU: his hand comes in with tweezers toward the wound... a doctor's gloved hand slaps it away. 'Don't!'")
def w20(t, D):
    reach = eo(ramp(t, 0, D * 0.45)); slap = eo(ramp(t, D * 0.5, D * 0.62))
    bg = skin_macro(8) + cut(470, 330, 300, 16, 1.0, 0.9, 1.0, -6)
    r = random.Random(7); mg = "".join(screw_maggot(470 + r.uniform(-100, 100), 330 + r.uniform(-18, 18), 0.3, t + k, r.uniform(0, 360), 1.0, 1.0) for k in range(24))
    tw = tweezers(lerp(820, 560, reach) + 200 * slap, lerp(120, 290, reach) - 120 * slap, 1.4, lerp(150, 160, reach) + 40 * slap)
    glove = f'<ellipse cx="{lerp(140, 560, slap):.0f}" cy="{lerp(80, 220, slap):.0f}" rx="90" ry="60" fill="#8AD0E8" opacity="{ramp(t, D * 0.45, D * 0.5):.2f}"/>'
    cam = (0, 30, 1.7 + 0.2 * math.exp(-max(0, t - D * 0.62) * 6) * (t > D * 0.62), -10)
    return SS([(bg, 0.9, True), (mg + tw + glove, 1.0, False), ui(badge_num(3, ramp(t, 0, 0.25)) + tag_big("DON'T!", 480, 200, ramp(t, D * 0.6, D * 0.75), 60, "#FF5A5A"))], cam, lights=(L_DAY,))


@shot5(Pn(8, 2) - 0.1, "w21", "ORBIT in a clinic: a doctor carefully lifts maggots out one by one into a jar of alcohol; the boy watches from the bed, relieved.")
def w21(t, D):
    u = eio(ramp(t, 0, D))
    doc = adult(R3.FRONT | dict(el=(-60, -280), hl=(-10, -300), er=(70, -300), hr=(40, -330), face=fc(open=0.9, mouth="flat", knit=0.3, look=(0.6, 0.7))), ADULTS[3], "w21d", 420, 470, 0.6, L_CLIN)
    J = SIT | dict(face=fc(open=1.0, mouth="smile", lift=0.3, look=(-0.6, 0.2)))
    b = boy(J, "w21b", 590, 300, 0.48, L_CLIN)
    j = jar(330, 410, 1.2, int(4 + 10 * u), t) + tweezers(420 + 0.6 * 40, 470 - 0.6 * 330, 0.6, -30, 0.8)
    cam = (lerp(-60, 60, u), 0, lerp(1.3, 1.5, u), lerp(-6, 6, u))
    return SS([(clinic(t), 0.8, True), (b + doc + j, 1.0, False)], cam, lights=(L_CLIN,))


# ================================================================== the crazy part
@shot5(Ln(9) - 0.1, "w22", "WHIP up into the sky: tracking alongside an old 1960s cargo plane flying over the clouds. Chip: 1960s.")
def w22(t, D):
    wp = 1 - ramp(t, 0, 0.3)
    p = plane(480 + 20 * math.sin(t * 2), 260 + 10 * math.sin(t * 1.4), 1.0, t)
    clouds = "".join(f'<ellipse cx="{(x - t * 260) % 1400 - 200:.0f}" cy="{y}" rx="{w}" ry="{w * 0.3:.0f}" fill="#FFFFFF" opacity="0.85" filter="url(#b8)"/>' for x, y, w in ((100, 420, 220), (600, 460, 300), (1100, 400, 260), (850, 500, 200)))
    cam = (0, 0, 1.3, lerp(-8, 0, eo(ramp(t, 0, 0.5))))
    return SS([(sky(t, 1.0), 0.3, True), (p, 1.0, False), (clouds, 1.5, False), ui(hstreaks(wp) + chip("1960s", 480, 60, ramp(t, 0.2, 0.5), 22, edge="#5AE8FF"))], cam, lights=(L_DAY,))


@shot5(Pn(9, 2) - 0.1, "w23", "The plane's hatch opens and a cloud of flies pours out; the camera dives down with them over farmland. Counter: BILLIONS of sterile flies.")
def w23(t, D):
    u = eio(ramp(t, 0, D))
    r = random.Random(4); fl = ""
    for k in range(70):
        d = (t * 0.9 + r.random()) % 1.0
        fl += f'<circle cx="{560 + r.uniform(-60, 60) + 200 * d * r.uniform(-1, 1):.0f}" cy="{270 + 600 * d:.0f}" r="{1.5 + 2 * d:.1f}" fill="#1A2A2A" opacity="{0.8 * (1 - d * 0.5):.2f}"/>'
    farms = '<rect x="-600" y="300" width="2160" height="1200" fill="#6AA84A"/>' + "".join(f'<rect x="{-600 + k * 160}" y="{700 + (k % 3) * 40}" width="150" height="400" fill="{("#7AB85A", "#C8B86A", "#5A9A4A")[k % 3]}"/>' for k in range(14))
    p = plane(560, 240, 1.0, t, door=1.0)
    cam = (40, lerp(0, 300, u), lerp(1.3, 1.1, u), 0)
    return SS([(sky(t, 1.0), 0.3, True), (farms, 0.8, True), (p + fl, 1.0, False), ui(chip("BILLIONS OF STERILE FLIES", 480, 60, ramp(t, 0.3, 0.6), 20, edge="#5AE8FF"))], cam, lights=(L_DAY,))


@shot5(Ln(10) - 0.1, "w24", "MAP of the Americas, camera sweeping north: a red wave spreads from Panama up through Central America and into Mexico.")
def w24(t, D):
    p = eio(ramp(t, 0, D))
    x0, y0 = AM_P(-80, 9); x1, y1 = AM_P(-100, 24)
    cam = (lerp(x0, x1, p) - CX, lerp(y0, y1, p) - CY, lerp(2.4, 1.8, p), 0)
    return SS([(americas(t, 0.05 + 0.75 * p), 1.0, False)], cam)


@shot5(Pn(10, 1) - 0.1, "w25", "PUSH NORTH to the US: a red pin pulses on the East Coast. Chip: 2025, FIRST US HUMAN CASE.")
def w25(t, D):
    p = eio(ramp(t, 0, D * 0.7))
    x1, y1 = AM_P(-100, 24); x2, y2 = AM_P(-85, 36)
    cam = (lerp(x1, x2, p) - CX, lerp(y1, y2, p) - CY, lerp(1.8, 1.4, p), 0)
    return SS([(americas(t, 0.85, ramp(t, D * 0.4, D * 0.6)), 1.0, False), ui(chip("2025: FIRST US HUMAN CASE", 480, 60, ramp(t, D * 0.4, D * 0.6), 20, edge="#FF5A5A"))], cam)


@shot5(Ln(11) - 0.1, "w26", "Back at the campsite at night: the boy in his sleeping bag looks at the camera and zips it up over his face. A fly lands on the tent. CRANE UP to the stars (loops to the start).")
def w26(t, D):
    z = eo(ramp(t, 0.4, 1.4))
    face = fc(open=1.2, lift=0.6, mouth="flat", look=(0.6, -0.6))
    cam = (lerp(-60, 0, eio(ramp(t, 0, D))), lerp(80, -300, ei(ramp(t, D * 0.55, D))), lerp(1.7, 1.1, ei(ramp(t, D * 0.55, D))), 0)
    f = fly3d(300, lerp(200, 290, eo(ramp(t, 0.8, 1.5))), 0.8, -20, t, flap=1 - ramp(t, 1.4, 1.6), legs="land")
    return SS([(sky(t, 0.0), 0.35, False), (trees(0.0), 0.7, True), (ground(0.0) + tent(250, 390, 1.0) + campfire(660, 420, t, 1.0, 0.3) + sleeper(t, 480, 470, 0.78, face=face, zip_=z) + f, 1.0, False)], cam, lights=(L_NIGHT,))
