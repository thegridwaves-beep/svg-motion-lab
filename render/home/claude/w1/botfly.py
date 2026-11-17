"""Short 1: What happens if a botfly lays eggs in you? 9:16, portrait window x 300..660, y -50..590."""
import os
os.environ.setdefault("SHORT", "botfly")
from wcore import *
import rig3 as R3

SIT = R3.F_SIT
L_ARM = Light("bfArm", amb=(1.0, 0.93, 0.88), sat=1.0, key="#FFD8A0", key_op=0.3, ang=-50, spread=0.8, shade="#3A1A30", shade_op=0.3, rim="#FFE8C8", rim_op=0.4, rim_w=6)
L_JUN = Light("bfJungle", amb=(0.82, 0.96, 0.8), sat=1.0, key="#D8FF9A", key_op=0.35, ang=-70, spread=0.8, shade="#0A2010", shade_op=0.45, rim="#E8FFB0", rim_op=0.5, rim_w=7)


# ================================================================== props
def skin_macro(seed=3, tone=("#F2C2A2", "#E0A486", "#C88A70")):
    """A whole frame of skin seen very close: soft tone, pores, fine hairs, faint creases. Static."""
    r = random.Random(seed)
    o = ['<rect x="-600" y="-600" width="2160" height="1800" fill="url(#skinG)"/>']
    for k in range(9):
        y = -200 + k * 110 + r.uniform(-20, 20)
        o.append(f'<path d="M-600 {y:.0f} Q480 {y + r.uniform(-40, 40):.0f} 1560 {y + r.uniform(-30, 30):.0f}" stroke="{tone[2]}" stroke-width="2" fill="none" opacity="0.25"/>')
    for k in range(260):
        x, y = r.uniform(-300, 1260), r.uniform(-300, 900)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(1.2, 2.6):.1f}" fill="{tone[2]}" opacity="0.5"/>')
    for k in range(70):
        x, y = r.uniform(-300, 1260), r.uniform(-300, 900); a = r.uniform(-0.6, 0.6); L = r.uniform(30, 70)
        o.append(f'<path d="M{x:.0f} {y:.0f} q{L * 0.4 * math.cos(a):.0f} {-L * 0.5:.0f} {L * math.cos(a):.0f} {-L * 0.8 + L * 0.3 * math.sin(a):.0f}" stroke="#6A4A3A" stroke-width="2.2" fill="none" opacity="0.55" stroke-linecap="round"/>')
    return "".join(o)


def bokeh(cols, seed=4, n=26, op=0.35):
    r = random.Random(seed)
    return "".join(f'<circle cx="{r.uniform(-200, 1160):.0f}" cy="{r.uniform(-300, 900):.0f}" r="{r.uniform(30, 110):.0f}" fill="{r.choice(cols)}" opacity="{op * r.uniform(0.4, 1):.2f}" filter="url(#b12)"/>' for _ in range(n))


def egg(x, y, s=1.0, rot=0.0, crack=0.0, t=0.0, warm=0.0):
    """Cream, banana-shaped egg ~22 units long at s=1; crack 0..1 splits the tip and a tiny larva head peeks out."""
    o = [f'<path d="M-11 0 Q-10 -6 0 -6 Q11 -6 12 0 Q11 6 0 6 Q-10 6 -11 0 Z" fill="{mixc("#FFF4DC", "#FFC8A0", warm)}" stroke="#C8A878" stroke-width="1.2"/>',
         '<ellipse cx="-2" cy="-2.6" rx="6" ry="1.6" fill="#FFFFFF" opacity="0.8"/>']
    if crack > 0:
        o.append(f'<path d="M7 -5 L9 -1 L6 1 L9 4" stroke="#8A6A48" stroke-width="1.2" fill="none"/>')
        hx = 12 + 7 * clamp(crack * 1.4 - 0.2)
        o.append(f'<ellipse cx="{hx:.1f}" cy="0" rx="{4 + 2 * crack:.1f}" ry="3.6" fill="#FFF0E0" stroke="#C89A88" stroke-width="1"/><circle cx="{hx + 3:.1f}" cy="-0.5" r="1" fill="#2A1010"/>')
    if warm > 0:
        o.append(f'<ellipse cx="0" cy="0" rx="16" ry="10" fill="#FF7A4A" opacity="{0.25 * warm:.2f}" filter="url(#b4)"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">{"".join(o)}</g>'


def egg_cluster(x, y, s=1.0, n=7, t=0.0, gone=()):
    o = []
    for k in range(n):
        if k in gone:
            continue
        o.append(egg(x - 34 * s + k * 10 * s, y + 6 * s + 3 * s * math.sin(k * 1.7), 0.9 * s, 70 + 8 * math.sin(k), t=t))
    return "".join(o)


def mosq_eggs(x, y, s, t, rot=0.0, flip=False, land=False, flap=1.0, gone=(), seed=2):
    """The mosquito with the botfly's eggs glued under its abdomen."""
    m = mosq(x, y, s, t, rot=rot, flip=flip, land=land, flap=flap, seed=seed)
    sx = -1 if flip else 1
    ex = f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx * s:.4f} {s:.4f})">{egg_cluster(-20, 10, 0.55, 7, t, gone)}</g>'
    return m + ex


def botfly(x, y, s=1.0, t=0.0, rot=0.0, flip=False, flap=1.0):
    """Human botfly, side view facing right, ~120 units long at s=1: hairy grey-yellow head, big brick-red eyes,
    metallic blue abdomen, smoky wings, hairy legs."""
    r = random.Random(7)
    fl = math.sin(t * 34) * flap
    o = []
    for k, (hx, kx, fx) in enumerate(((10, -14, -36), (18, 4, -6), (26, 32, 40))):
        o.append(f'<path d="M{hx} 14 L{kx} 36 L{fx} 58" stroke="#3A2E24" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        o += [f'<path d="M{lerp(kx, fx, j / 4):.1f} {lerp(36, 58, j / 4):.1f} l-5 -4" stroke="#5A4A3A" stroke-width="1.5"/>' for j in range(1, 4)]
    o.append('<path d="M-6 -4 Q-40 -26 -78 -2 Q-84 14 -60 26 Q-30 36 -4 20 Z" fill="#2A4AA8"/>'
             '<path d="M-14 -10 Q-46 -24 -72 -4" stroke="#7AA8FF" stroke-width="5" fill="none" opacity="0.7" stroke-linecap="round"/>'
             '<path d="M-30 -14 L-34 28 M-50 -12 L-54 26" stroke="#1A2A6A" stroke-width="3" opacity="0.6"/>')
    o.append('<ellipse cx="14" cy="2" rx="26" ry="22" fill="#6A6458"/>')
    for k in range(40):
        a = r.uniform(0, TAU); rr = r.uniform(14, 26)
        o.append(f'<path d="M{14 + rr * math.cos(a):.1f} {2 + rr * 0.85 * math.sin(a):.1f} l{5 * math.cos(a):.1f} {5 * math.sin(a):.1f}" stroke="#A89A80" stroke-width="1.4"/>')
    o.append('<circle cx="48" cy="2" r="20" fill="#E8D890"/><ellipse cx="54" cy="-2" rx="15" ry="17" fill="#A82418"/><ellipse cx="58" cy="-8" rx="5" ry="4" fill="#FF8A6A" opacity="0.7"/>'
             '<path d="M62 14 Q70 20 66 26" stroke="#3A2E24" stroke-width="3" fill="none"/>')
    for wk in range(2):
        a = -160 + 30 * fl + 12 * wk
        o.append(f'<g transform="translate(8 -16) rotate({a:.1f})"><path d="M0 0 Q30 -14 70 -4 Q74 4 64 8 Q30 10 0 0 Z" fill="#8A8070" opacity="0.42"/>'
                 '<path d="M2 0 L66 0 M10 -2 L50 -8" stroke="#5A5040" stroke-width="1" opacity="0.6"/></g>')
    sx = -s if flip else s
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx:.4f} {s:.4f})">{"".join(o)}</g>'


def grub(x, y, s=1.0, t=0.0, rot=0.0, wig=1.0, head_up=False):
    """Botfly larva: a cream, bottle-shaped maggot with rings of dark spines, ~80 units long at s=1.
    Head (thin end) at +x; the breathing end (fat, with two spiracle slits) at -x."""
    o = []
    segs = 9
    for k in range(segs, -1, -1):
        u = k / segs
        w = 10 + 18 * math.sin(math.pi * (0.25 + 0.75 * (1 - u))) if u > 0.15 else 10
        px = -40 + 82 * u; py = 5 * wig * math.sin(t * 7 - k * 0.9)
        o.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{8 + 2 * (1 - u):.1f}" ry="{w:.1f}" fill="{mixc("#FFF2E0", "#F2D2B8", u):s}" stroke="#D8B498" stroke-width="1.2"/>')
        if 1 <= k <= 7:
            o += [f'<path d="M{px - 2 + j * 0.0:.1f} {py - w + 4 + j * (2 * w - 8) / 5:.1f} l-4 -1" stroke="#3A2010" stroke-width="1.8" stroke-linecap="round"/>' for j in range(6)]
    hy = 5 * wig * math.sin(t * 7)
    o.append(f'<circle cx="44" cy="{hy:.1f}" r="6" fill="#F2D2B8"/><path d="M47 {hy - 4:.1f} q8 -2 9 4 M47 {hy + 4:.1f} q8 2 9 -4" stroke="#1A0808" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
    o.append('<ellipse cx="-47" cy="1" rx="4" ry="8" fill="#8A5A3A"/><path d="M-47 -5 L-47 7" stroke="#3A1A10" stroke-width="2"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">{"".join(o)}</g>'


SURF = 170      # skin surface height in the cross-section shots


def skin_xsec(t, hole_x=480, pocket=1.0, bacon_on=0.0, glow_=0.6, hair=True):
    """Cross-section of the arm: air above, epidermis, dermis with blood vessels, fat. A pocket under the hole."""
    o = ['<rect x="-600" y="-600" width="2160" height="1800" fill="#3A2A5A"/>', glow(480, SURF - 160, 420, "#FFD8A0", 0.45, 40),
         f'<path d="M-600 {SURF} Q480 {SURF - 14} 1560 {SURF} L1560 1200 L-600 1200 Z" fill="#F2C2A2"/>',
         f'<path d="M-600 {SURF + 34} Q480 {SURF + 22} 1560 {SURF + 34} L1560 1200 L-600 1200 Z" fill="url(#dermis)"/>',
         f'<path d="M-600 {SURF + 330} Q480 {SURF + 310} 1560 {SURF + 330} L1560 1200 L-600 1200 Z" fill="#F4D890"/>']
    r = random.Random(5)
    for k in range(30):
        cx, cy = r.uniform(-300, 1260), r.uniform(SURF + 345, SURF + 600)
        o.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r.uniform(18, 34):.0f}" fill="#FFE8A8" stroke="#E8C870" stroke-width="2"/>')
    for k in range(3):
        y0 = SURF + 120 + k * 70
        o.append(f'<path d="M-600 {y0} Q{200 + 120 * k} {y0 + 40} 1560 {y0 - 20}" stroke="#B8202E" stroke-width="{10 - 2 * k}" fill="none" opacity="0.8"/>')
        for j in range(8):
            x = ((j * 170 + t * (40 + 15 * k)) % 1500) - 300
            o.append(f'<ellipse cx="{x:.0f}" cy="{y0 + 40 * math.sin((x + 600) / 2160 * math.pi) * 0.5:.0f}" rx="6" ry="3.5" fill="#FF6A6A"/>')
    if hair:
        for x in (300, 380, 590, 660, 760):
            o.append(f'<path d="M{x} {SURF + 120} L{x + 6} {SURF} Q{x + 20} {SURF - 60} {x + 44} {SURF - 110}" stroke="#4A3022" stroke-width="5" fill="none"/>'
                     f'<ellipse cx="{x}" cy="{SURF + 126}" rx="10" ry="14" fill="#C8806A"/>')
    if pocket > 0:
        pw, ph = 70 * pocket, 110 * pocket
        o.append(f'<path d="M{hole_x - 5} {SURF - 2} L{hole_x - 9} {SURF + 30} Q{hole_x - pw} {SURF + 40} {hole_x - pw} {SURF + 40 + ph / 2} Q{hole_x - pw} {SURF + 40 + ph} {hole_x} {SURF + 40 + ph} '
                 f'Q{hole_x + pw} {SURF + 40 + ph} {hole_x + pw} {SURF + 40 + ph / 2} Q{hole_x + pw} {SURF + 40} {hole_x + 9} {SURF + 30} L{hole_x + 5} {SURF - 2} Z" fill="#7A2A3A" stroke="#C85A6A" stroke-width="3"/>'
                 + f'<ellipse cx="{hole_x}" cy="{SURF + 40 + ph / 2}" rx="{pw * 0.8:.0f}" ry="{ph * 0.45:.0f}" fill="url(#pocketG)" opacity="{0.35 * glow_:.2f}"/>')
    if bacon_on > 0:
        o.append(f'<g opacity="{clamp(bacon_on * 3):.2f}">{bacon(hole_x, SURF - 16, 1.4, 0, 0.0, flat=True)}</g>')
    return "".join(o)


def bacon(x, y, s=1.0, rot=0.0, wave=0.0, flat=False):
    """A strip of streaky bacon ~240 x 46 units at s=1, wavy unless flat."""
    w = 0 if flat else 1
    top = " ".join(f"{-120 + k * 24},{-20 + w * 9 * math.sin(k * 1.3 + wave):.1f}" for k in range(11))
    bot = " ".join(f"{120 - k * 24},{24 + w * 9 * math.sin((10 - k) * 1.3 + wave):.1f}" for k in range(11))
    o = [f'<polygon points="{top} {bot}" fill="url(#bacon)" stroke="#6A1A10" stroke-width="2"/>']
    for k, (yy, c) in enumerate(((-8, "#FFE8D8"), (10, "#FFDCC8"))):
        pts = " ".join(f"{-114 + j * 24},{yy + w * 9 * math.sin(j * 1.3 + wave) + 2 * math.sin(j * 3.1 + k):.1f}" for j in range(10))
        o.append(f'<polyline points="{pts}" stroke="{c}" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.92"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">{"".join(o)}</g>'


def arm_close(x, y, s=1.0, ang=0.0, bump=0.0, t=0.0, wig=0.0, hole=0.0):
    """His forearm, big, skin-textured, with an optional red bump that wriggles."""
    a = forearm(x, y, s, ang)
    if bump <= 0:
        return a
    bx, by = x + 150 * s, y - 10 * s
    w = 1 + 0.08 * wig * math.sin(t * 9); sh = 4 * wig * math.sin(t * 7) * s
    b = (f'<g transform="translate({bx + sh:.1f} {by:.1f}) rotate({ang:.1f}) scale({s * w:.3f} {s / w:.3f})">'
         f'<ellipse cx="0" cy="0" rx="{26 * bump:.1f}" ry="{18 * bump:.1f}" fill="#E8907A" opacity="0.85"/><ellipse cx="-4" cy="-4" rx="{14 * bump:.1f}" ry="{9 * bump:.1f}" fill="#F4B09A"/>'
         + (f'<circle cx="0" cy="0" r="{2.5 * hole:.1f}" fill="#3A1014"/>' if hole > 0 else "") + '</g>')
    return a + b


def jungle(t, seed=6):
    r = random.Random(seed)
    o = ['<rect x="-600" y="-600" width="2160" height="1800" fill="url(#jungle)"/>', glow(560, 40, 380, "#E8FF9A", 0.35, 40)]
    for k in range(18):
        x = r.uniform(-200, 1160); y = r.uniform(-100, 700); s_ = r.uniform(0.8, 2.2)
        o.append(f'<g transform="translate({x:.0f} {y:.0f}) rotate({r.uniform(-50, 50):.0f}) scale({s_:.2f})" opacity="{r.uniform(0.3, 0.7):.2f}"><path d="M0 0 Q60 -40 140 0 Q60 40 0 0 Z" fill="{r.choice(("#2E7A3A", "#1E5A2A", "#4A9A3A"))}"/><path d="M0 0 L140 0" stroke="#0E3A1A" stroke-width="2"/></g>')
    return "".join(o)


def you_sit(J, uid, x, y, s, Lt):
    J = dict(J); J["face"] = blink(J["face"], 0.0)
    return boy(J, uid, x, y, s, Lt)


# ================================================================== shots
@shot5(0.0, "b01", "ECU, travelling: a mosquito swoops in over the hairs of his forearm and touches down right in front of the lens; the camera tracks it in and pushes to a macro.")
def b01(t, D):
    u = eio(ramp(t, 0, D * 0.75))
    mx, my = lerp(360, 470, u), lerp(170, 300, u) - 30 * math.sin(math.pi * u)
    land = u > 0.95
    m = mosq_eggs(mx, my, lerp(2.0, 2.4, u), t, rot=lerp(-20, 8, u), land=land, flap=1 - 0.8 * u, seed=2)
    sh = f'<ellipse cx="{mx + 10:.0f}" cy="{330 + 20 * u:.0f}" rx="{40 + 20 * u:.0f}" ry="8" fill="#5A2A1A" opacity="{0.25 * u:.2f}" filter="url(#b4)"/>'
    cam = (lerp(-90, 0, u), lerp(-80, 30, u), lerp(1.25, 1.6, eio(ramp(t, 0, D))))
    return SV([(skin_macro(), 0.85, True), (sh + m, 1.0, False), (bokeh(("#FFE8C8", "#FFC8A0"), 2, 10, 0.25), 1.5, True)], cam, lights=(L_ARM,))


@shot5(Ln(1) - 0.1, "b02", "ORBIT around the landed mosquito at macro scale: as the camera swings round, a row of glistening cream eggs glued under its belly catches the light.")
def b02(t, D):
    u = eio(ramp(t, 0, D))
    flip = u > 0.5
    k = abs(u - 0.5) * 2
    sx = lerp(0.25, 1.0, k)
    m = mosq_eggs(0, 0, 3.0, t, rot=6, land=True, flap=0.0, seed=2)
    m = f'<g transform="translate(470 300) scale({(-1 if flip else 1) * sx:.3f} 1) translate(-470 -300)">{mosq_eggs(470, 300, 3.0, t, rot=6, land=True, flap=0.0, seed=2)}</g>'
    gl = glow(450, 340, 60, "#FFF4DC", 0.6 * clamp(1 - abs(u - 0.75) * 4), 10)
    bg = skin_macro(5)
    cam = (lerp(-90, 90, u), 50, lerp(1.7, 2.0, u), lerp(-7, 7, u))
    return SV([(bg, 0.6, True), (m + gl, 1.0, False), (bokeh(("#FFFFFF", "#FFD8B0"), 9, 8, 0.2), 1.6, True)], cam, lights=(L_ARM,))


@shot5(Ln(2) - 0.1, "b03", "WHIP into a flashback, deep jungle: a fat blue botfly snatches the mosquito out of the air, clamps it with its legs and presses its eggs onto the belly. Small 'EARLIER' chip.")
def b03(t, D):
    u = eo(ramp(t, 0.15, D * 0.45)); press = eo(ramp(t, D * 0.45, D * 0.8))
    bx, by = lerp(720, 440, u), lerp(80, 230, u)
    f = botfly(bx, by, 1.5, t, rot=lerp(-20, 4, u))
    mx, my = lerp(420, bx + 6, u), lerp(380, by + 92, u)
    m = mosq_eggs(mx, my, 1.6, t, rot=lerp(-10, 0, u), flap=1.0, gone=tuple(range(7)) if press < 0.3 else tuple(range(int(7 * (1 - press)))), seed=4)
    sm = smear(whip(t, 0.0, 0.3), "#E8FFC8")
    cam = (lerp(40, 0, u), lerp(-20, 30, u), lerp(1.35, 1.6, ramp(t, 0, D)))
    tint = f'<rect x="-600" y="-600" width="2160" height="1800" fill="#E8D890" opacity="0.08"/>'
    return SV([(jungle(t), 0.5, True), (m + f, 1.0, False), (tint, 1.0, True), ui(sm + chip("EARLIER", 480, 40, ramp(t, 0.1, 0.4), 18, edge="#C8FF7A"))], cam, lights=(L_JUN,))


@shot5(Ln(3) - 0.1, "b04", "TRACK down the mosquito's leg to the skin: one egg slips off, lands on his arm, glows warm from his body heat and cracks; a tiny larva head pokes out.")
def b04(t, D):
    drop = eo(ramp(t, 0.1, 0.7)); crack = ramp(t, D * 0.55, D * 0.9); warm = ramp(t, 0.6, D * 0.6)
    m = mosq_eggs(470, 180, 3.0, t, rot=6, land=True, flap=0.0, gone=(3,), seed=2)
    ex, ey = lerp(460, 500, drop), lerp(222, 400, drop)
    e = egg(ex, ey, 2.2, lerp(70, 95, drop), crack, t, warm)
    heat = "".join(f'<path d="M{470 + 20 * k} {420} q8 -20 0 -40 q-8 -20 0 -40" stroke="#FF9A6A" stroke-width="3" fill="none" opacity="{0.35 * warm * (0.5 + 0.5 * math.sin(t * 6 + k)):.2f}"/>' for k in range(3))
    cam = (0, lerp(-80, 120, eio(ramp(t, 0, D * 0.7))), lerp(1.9, 2.6, eio(ramp(t, 0.4, D))))
    return SV([(skin_macro(5), 0.8, True), (m + heat + e, 1.0, False)], cam, lights=(L_ARM,))


@shot5(Pn(3, 1) - 0.05, "b05", "X-RAY CRANE DIVE: the skin goes see-through and the camera plunges below the surface after the maggot as it burrows head-first through the layers.")
def b05(t, D):
    u = eio(ramp(t, 0, D))
    dig = ramp(t, 0.1, D * 0.85)
    g = grub(480, SURF + 10 + 150 * dig, lerp(0.5, 0.9, dig), t, rot=90, wig=1.0)
    trail = f'<path d="M480 {SURF} L480 {SURF + 150 * dig:.0f}" stroke="#7A2A3A" stroke-width="{18 * lerp(0.5, 0.9, dig):.0f}" stroke-linecap="round"/>'
    cam = (0, lerp(-60, 170, u), lerp(1.1, 1.9, u))
    return SV([(skin_xsec(t, pocket=0.0, hair=True), 1.0, False), (trail + g, 1.0, False)], cam)


@shot5(Ln(4) - 0.1, "b06", "CU inside its pocket under the skin, slow push: the maggot curls in its cave, spines ringing its body, its tail end pressed to a little hole in the surface. Bubbles of air go in and out.")
def b06(t, D):
    u = eio(ramp(t, 0, D))
    g = grub(480, SURF + 92, 1.15, t, rot=90, wig=0.6)
    bub = "".join(f'<circle cx="{480 + 4 * math.sin(t * 5 + k):.1f}" cy="{SURF + 30 - ((t * 60 + k * 22) % 60):.1f}" r="{3 + k % 3}" fill="#E8FAFF" opacity="0.7"/>' for k in range(4))
    lbl = label("breathing hole", 540, SURF - 46, 18, "#FFFFFF", u=ramp(t, 0.6, 1.0)) + leader(520, SURF - 38, 486, SURF - 4, ramp(t, 0.6, 1.0))
    cam = (0, 80, lerp(1.45, 1.7, u), lerp(-3, 3, u))
    return SV([(skin_xsec(t, pocket=1.0, hair=False), 1.0, False), (g + bub, 1.0, False), (lbl, 1.0, False)], cam)


@shot5(Pn(4, 1) - 0.1, "b07", "MED, living room, slow push-in: weeks later, the boy on the couch scrolling his phone. He scratches his forearm, stops, lifts it: a red bump. He stares at it.")
def b07(t, D):
    u = eio(ramp(t, 0, D)); look = eo(ramp(t, D * 0.35, D * 0.6))
    J = SIT | dict(el=(-84, -284), hl=(lerp(-20, -10, look), lerp(-230, -300, look)), er=(84, -290), hr=(lerp(30, 0, look), lerp(-240, -320, look)),
                   head=(0, 10 * look, 0), face=fc(open=lerp(0.95, 1.3, look), lift=lerp(0.1, 0.7, look), knit=0.2 * look, mouth="flat", look=(lerp(0.0, -0.2, look), lerp(0.2, 1.0, look))))
    body = boy(J, "b7", 450, 498, 0.62, LI)
    ax, ay = 450 + 0.62 * lerp(-20, -10, look), 498 + 0.62 * lerp(-230, -300, look)
    bump = f'<circle cx="{ax + 8:.1f}" cy="{ay + 14:.1f}" r="5" fill="#E86A5A"/>' + glow(ax + 8, ay + 14, 16, "#FF5A4A", 0.6 * look, 4)
    ring = f'<circle cx="{ax + 8:.1f}" cy="{ay + 14:.1f}" r="{lerp(40, 18, look):.1f}" fill="none" stroke="#FFD23F" stroke-width="3" opacity="{look * (1 - ramp(t, D * 0.85, D)):.2f}"/>'
    ph = '<rect x="430" y="330" width="34" height="56" rx="6" fill="#1A1A24"/><rect x="433" y="334" width="28" height="48" rx="4" fill="#5AE8FF" opacity="0.8"/>' if look < 0.3 else ""
    cam = (lerp(-10, -30, u), lerp(20, 30, u), lerp(1.25, 1.75, u))
    return SV([(living_room(t, 0.1), 0.85, True), (body + ph + bump + ring, 1.0, False)], cam, lights=(LI,))


@shot5(Ln(5) - 0.1, "b08", "ECU, the bump fills the frame: it bulges and twitches. Something is moving in there. Tiny dark breathing hole in the middle.")
def b08(t, D):
    arm = arm_close(170, 290, 2.2, -4, bump=1.0, t=t, wig=1.6, hole=1.0)
    cam = (-10, 0, lerp(1.5, 1.9, eio(ramp(t, 0, D))), lerp(-4, 3, ramp(t, 0, D)))
    return SV([('<rect x="-600" y="-600" width="2160" height="1800" fill="url(#lroomW)"/>', 0.7, True), (arm, 1.0, False)], cam, lights=(LI,))


@shot5(Pn(5, 0) + 0.75, "b08b", "LOW CU on his face, the camera tilting up: his eyes go wide, mouth drops open. Dutch angle.")
def b08b(t, D):
    J = R3.FRONT | dict(head=(0, 0, -5), face=fc(open=1.55, lift=1.2, knit=0.4, mouth="o", mo=0.7, look=(0.2, 0.9)))
    face = boy(J, "b8b", 480, 640, 1.0, LI)
    cam = (0, lerp(-10, -50, eio(ramp(t, 0, D))), 1.55, -8)
    return SV([('<rect x="-600" y="-600" width="2160" height="1800" fill="url(#lroomW)"/>' + glow(480, 120, 200, "#FFE8C8", 0.4, 30), 0.7, True), (face, 1.0, False)], cam, lights=(LI,))


@shot5(Ln(6) - 0.1, "b09", "WIDE kitchen: he marches in, grabs a strip of raw bacon and slaps it onto his arm, deadpan, holding eye contact with the camera.")
def b09(t, D):
    slap = eo(ramp(t, D * 0.55, D * 0.68))
    J = R3.FRONT | dict(el=(-90, -280), hl=(-40, -250), er=(90, -300), hr=(lerp(120, -30, slap), lerp(-380, -255, slap)),
                        face=fc(open=0.75, lift=0.1, mouth="flat", look=(0, 0)))
    body = boy(J, "b9", 470, 470, 0.66, LI)
    bx, by = 470 + 0.66 * lerp(130, -40, slap), 470 + 0.66 * lerp(-395, -258, slap)
    b = bacon(bx, by, 0.32, lerp(-40, 0, slap), t * 2)
    sp = "".join(f'<path d="M{bx + 28 * math.cos(a):.0f} {by + 28 * math.sin(a):.0f} l{12 * math.cos(a):.0f} {12 * math.sin(a):.0f}" stroke="#FFFFFF" stroke-width="3" opacity="{clamp(1 - abs(t - D * 0.68) * 5):.2f}"/>' for a in [k * TAU / 8 for k in range(8)])
    cam = cam_keys(t, [(0, (0, -10, 1.05)), (D * 0.5, (0, 0, 1.15)), (D, (0, -40, 1.45))])
    return SV([(kitchen(t), 0.85, True), (body + b + sp, 1.0, False)], cam, lights=(LI,))


@shot5(Ln(8) - 0.1, "b10", "X-RAY under the bacon: no air comes through the hole. The maggot squirms, then inches up and out of its pocket, into the bacon.")
def b10(t, D):
    up = eo(ramp(t, D * 0.3, D))
    g = grub(480, lerp(SURF + 92, SURF + 30, up), 1.15, t, rot=90, wig=1.2)
    gone = '<rect x="-600" y="-600" width="2160" height="1800" fill="#000" opacity="0"/>'
    cam = (0, lerp(60, 20, up), lerp(1.7, 1.6, up))
    return SV([(skin_xsec(t, pocket=1.0, bacon_on=1.0, hair=False), 1.0, False), (g + gone, 1.0, False),
               (bacon(480, SURF - 16, 1.4, 0, 0, flat=True).replace('<g transform', '<g opacity="0.55" transform'), 1.0, False)], cam)


@shot5(Pn(8, 1) - 0.05, "b11", "ECU: he peels the bacon back, the maggot is stuck in it, wriggling. In the soft background his face: disgust, then relief.")
def b11(t, D):
    peel = eo(ramp(t, 0.1, D * 0.6))
    arm = arm_close(300, 430, 1.4, -6, bump=lerp(1.0, 0.5, peel), t=t, wig=0.0, hole=1.0)
    bb = bacon(500, lerp(380, 250, peel), 0.75, lerp(0, -18, peel), t)
    gb = grub(500, lerp(380, 250, peel) + 18, 0.38, t, rot=100, wig=1.0)
    J = R3.FRONT | dict(face=fc(open=lerp(0.6, 1.0, peel), lift=0.4, knit=lerp(0.8, 0.0, ramp(t, D * 0.7, D)), mouth="grit" if t < D * 0.7 else "smile"))
    face = f'<g filter="url(#b6)" opacity="0.85">{boy(J, "b11", 560, 520, 0.9, LI)}</g>'
    cam = (0, -10, 1.6)
    return SV([('<rect x="-600" y="-600" width="2160" height="1800" fill="url(#lroomW)"/>', 0.6, True), (face, 0.8, False), (arm + bb + gb, 1.0, False)], cam, lights=(LI,))


@shot5(Ln(9) - 0.1, "b12", "OVERHEAD, rotating: the boy flopped back on the couch, arms out, relieved... a mosquito drifts down onto his OTHER arm. The camera spirals down onto it (loops into b01).")
def b12(t, D):
    u = eio(ramp(t, 0, D))
    floor_ = '<rect x="-600" y="-600" width="2160" height="1800" fill="#B07A5A"/>' + "".join(f'<path d="M-600 {y} L1560 {y}" stroke="#9A6A4A" stroke-width="3" opacity="0.5"/>' for y in range(-600, 1200, 60))
    rug = '<ellipse cx="480" cy="300" rx="360" ry="290" fill="#C85A6A" opacity="0.75"/>'
    seat = ('<rect x="250" y="40" width="460" height="470" rx="46" fill="#2E4690"/><rect x="250" y="40" width="70" height="470" rx="34" fill="#3A56A8"/>'
            '<rect x="640" y="40" width="70" height="470" rx="34" fill="#3A56A8"/><rect x="330" y="60" width="300" height="430" rx="30" fill="#5A7AD8"/>'
            '<path d="M330 275 L630 275" stroke="#3A56A8" stroke-width="5"/><ellipse cx="480" cy="110" rx="90" ry="40" fill="#FFE0A0"/>')
    J = R3.FRONT | dict(el=(-120, -250), hl=(-170, -190), er=(120, -250), hr=(170, -190), kl=(-50, -120), fl=(-60, 0), kr=(50, -120), fr=(60, 0),
                        face=fc(open=0.15, mouth="smile", lift=0.2, look=(0.0, 0.0)))
    body = boy(J, "b12", 480, 470, 0.6, LI)
    mx, my = lerp(660, 585, u), lerp(60, 352, u)
    m = mosq_eggs(mx, my, lerp(0.8, 1.25, u), t, rot=lerp(30, 10, u), flap=1.0 - 0.7 * ramp(t, D * 0.8, D), seed=6)
    sh = f'<ellipse cx="{mx:.0f}" cy="{my + 40 * (1 - u) + 20:.0f}" rx="{14 + 10 * u:.0f}" ry="5" fill="#000" opacity="{0.2 * u:.2f}" filter="url(#b3)"/>'
    cam = (lerp(0, 100, u), lerp(-10, 80, u), lerp(1.0, 2.4, u), lerp(0, 35, u))
    return SV([(floor_ + rug + seat, 1.0, True), (body, 1.0, False), (sh + m, 1.0, False)], cam, lights=(LI,))
