"""Short: How to Survive If the Sun Vanished, Part 1 (~37 s). The 8-minute delay, the black sky, Earth flung loose, the freeze."""
import os, random
os.environ["SHORT"] = "sun1"
import anim_core
from wcore import *
anim_core.ANIM[:] = []

B = {}
for i, ph in PH.items():
    for k, q in enumerate(ph):
        B[(i, k)] = q["t"]
TEND = round(TEND, 3)
G, BX, BS = 420, 480, 0.5

L_DAY = Light("snDay", amb=(1.0, 0.98, 0.94), sat=1.0, key="#FFF0C8", key_op=0.35, ang=-60, spread=0.8, shade="#2A2A4A", shade_op=0.3, rim="#FFFFFF", rim_op=0.45, rim_w=7)
L_NIGHT = Light("snNight", amb=(0.52, 0.58, 0.82), sat=0.75, key="#9AB8FF", key_op=0.3, ang=-30, spread=0.8, shade="#0A1030", shade_op=0.5, rim="#B8D0FF", rim_op=0.55, rim_w=6)
L_TORCH = Light("snTorch", amb=(0.7, 0.72, 0.9), sat=0.85, key="#FFF2C0", key_op=0.45, ang=-10, spread=0.9, shade="#0A1030", shade_op=0.45, rim="#FFE8A8", rim_op=0.6, rim_w=7)
DEFS = (lin("snDaySky", [(0, "#4AA8F0"), (0.7, "#A8DCFA"), (1, "#E8F6FA")]) + lin("snNightSky", [(0, "#03040C"), (0.7, "#0A1028"), (1, "#141C38")])
        + lin("snGrass", [(0, "#7CC860"), (1, "#4E9A3E")]) + lin("snGrassN", [(0, "#1E3A30"), (1, "#0E2018")])
        + rad("snSun", [(0, "#FFFFF0", 1), (0.35, "#FFE66A", 1), (0.7, "#FFA43A", 0.9), (1, "#FF7A2A", 0)])
        + rad("snEarth", [(0, "#6AC8FF", 1), (1, "#1E5AB0", 1)]) + lin("snFrost", [(0, "#E8F6FF"), (1, "#B8D8F0")])
        + lin("stageS", [(0, "#04050E"), (1, "#0A0C1E")]))


def SS(layers, cam=(0, 0, 1.0), overlay="", lights=(L_DAY,)):
    return SV(layers, cam, DEFS, overlay, lights)


def kick(t, t0, amp=14, dur=0.25):
    return amp * math.sin(math.pi * clamp((t - t0) / dur)) * (1 - clamp((t - t0) / dur)) if t > t0 else 0.0


def badge(txt, u, col=PINK, y=90, x=480):
    if u <= 0:
        return ""
    k = 0.6 + 0.4 * eo(min(1, u * 2))
    fs = min(74, 860 / max(1, len(txt))); w = len(txt) * fs * 0.62 + 70; h = fs * 1.6
    return (f'<g transform="translate({x} {y}) scale({k:.3f})" opacity="{clamp(u * 3):.2f}"><rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="{h / 2}" fill="{col}" stroke="#FFFFFF" stroke-width="7"/>'
            + text(0, fs * 0.36, txt, fs, "#FFFFFF", 700, "middle") + '</g>')


def wtext(x, y, s, size, col="#FFFFFF", u=1.0):
    """World-space bold label with a dark outline."""
    if u <= 0:
        return ""
    return f'<g opacity="{clamp(u * 3):.2f}">' + text(x, y, s, size, col, 700, "middle").replace("<text ", f'<text stroke="{INK}" stroke-width="{size * 0.16:.1f}" paint-order="stroke" ') + '</g>'


# ------------------------------------------------------------------ space
def stars(seed=4, n=160, x0=-300, x1=1260, y0=-400, y1=900, tw=0.0, op=1.0):
    r = random.Random(seed); o = []
    for k in range(n):
        x, y, rr = r.uniform(x0, x1), r.uniform(y0, y1), r.choice([0.8, 1.1, 1.4, 2.0])
        a = (0.5 + 0.5 * math.sin(tw * 3 + k)) * 0.6 + 0.4
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr}" fill="#FFFFFF" opacity="{a * op:.2f}"/>')
    return "".join(o)


STARS = stars()


def sun(x, y, r, op=1.0):
    if op <= 0 or r <= 0:
        return ""
    return (f'<g opacity="{op:.2f}"><circle cx="{x}" cy="{y}" r="{r * 2.2:.1f}" fill="url(#snSun)" opacity="0.55"/>'
            f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="#FFE070"/><circle cx="{x}" cy="{y}" r="{r * 0.8:.1f}" fill="#FFF2A8"/></g>')


def earth(x, y, r, lit=1.0, ang=-30):
    """Earth with continents; lit<1 darkens it (night side spreads over the whole globe)."""
    cid = f"ec{int(x)}_{int(y)}"
    land = "".join(f'<ellipse cx="{x + dx * r:.1f}" cy="{y + dy * r:.1f}" rx="{a * r:.1f}" ry="{b * r:.1f}" fill="#5AB04A" transform="rotate({rt} {x + dx * r:.1f} {y + dy * r:.1f})"/>'
                   for dx, dy, a, b, rt in ((-0.3, -0.2, 0.35, 0.22, 20), (0.25, 0.1, 0.3, 0.4, -10), (-0.1, 0.45, 0.25, 0.12, 0), (0.4, -0.45, 0.2, 0.1, 30)))
    sh = 0.35 + 0.65 * (1 - lit)
    return (f'<clipPath id="{cid}"><circle cx="{x}" cy="{y}" r="{r}"/></clipPath>'
            f'<circle cx="{x}" cy="{y}" r="{r * 1.08:.1f}" fill="#6AB8FF" opacity="{0.25 * lit:.2f}"/>'
            f'<g clip-path="url(#{cid})"><circle cx="{x}" cy="{y}" r="{r}" fill="url(#snEarth)"/>{land}'
            f'<circle cx="{x + r * 0.55 * math.cos(math.radians(ang)):.1f}" cy="{y + r * 0.55 * math.sin(math.radians(ang)):.1f}" r="{r * 1.3:.1f}" fill="#000814" opacity="{sh:.2f}" transform="translate({r * 0.9 * math.cos(math.radians(ang)):.1f} {r * 0.9 * math.sin(math.radians(ang)):.1f})"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#000814" opacity="{0.75 * (1 - lit):.2f}"/></g>')


def moon(x, y, r, lit=1.0):
    return (f'<circle cx="{x}" cy="{y}" r="{r * 1.6:.1f}" fill="#F4F0DC" opacity="{0.18 * lit:.2f}"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#{"%02X%02X%02X" % tuple(int(lerp(a, b, lit)) for a, b in ((26, 236), (30, 232), (44, 214)))}"/>'
            + "".join(f'<circle cx="{x + dx * r:.1f}" cy="{y + dy * r:.1f}" r="{rr * r:.1f}" fill="#000000" opacity="{0.12 * lit + 0.05:.2f}"/>' for dx, dy, rr in ((-0.3, -0.2, 0.18), (0.25, 0.25, 0.22), (0.1, -0.45, 0.1), (-0.2, 0.4, 0.12)))
            + f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#8A96B8" stroke-width="2" opacity="{0.6 * (1 - lit):.2f}"/>')


# ------------------------------------------------------------------ the park
def sky(night=0.0, sunpos=None):
    o = '<rect x="-800" y="-1200" width="2560" height="2000" fill="url(#snDaySky)"/>'
    if sunpos:
        o += sun(*sunpos)
    if night > 0:
        o += f'<rect x="-800" y="-1200" width="2560" height="2000" fill="url(#snNightSky)" opacity="{night:.2f}"/>' + f'<g opacity="{clamp((night - 0.5) * 2):.2f}">{STARS}</g>'
    return o


def skyline(night=0.0, y=G - 40):
    r = random.Random(9); o = []; x = -500
    col = "#8AA6C8" if night < 0.5 else "#0C1226"
    while x < 1500:
        w, h = r.uniform(40, 90), r.uniform(60, 220)
        o.append(f'<rect x="{x:.0f}" y="{y - h:.0f}" width="{w:.0f}" height="{h + 60:.0f}" fill="{col}"/>')
        if night > 0.5:
            for k in range(int(h / 26)):
                if r.random() < 0.35:
                    o.append(f'<rect x="{x + r.uniform(6, w - 14):.0f}" y="{y - h + 12 + 26 * k:.0f}" width="7" height="9" fill="#FFD98A" opacity="0.8"/>')
        x += w + r.uniform(4, 18)
    return "".join(o)


def tree(x, y, s=1.0, night=0.0, frost=0.0):
    leaf = mixc(mixc("#4EA84A", "#16302A", night), "#DDEEFA", frost * 0.8); dark = mixc(mixc("#3A8A3A", "#0C201C", night), "#B0CCE4", frost * 0.8)
    trunk = mixc("#7A5234", "#1A140E", night)
    return (f'<rect x="{x - 9 * s:.1f}" y="{y - 120 * s:.1f}" width="{18 * s:.1f}" height="{120 * s:.1f}" rx="{6 * s:.1f}" fill="{trunk}"/>'
            f'<circle cx="{x:.1f}" cy="{y - 160 * s:.1f}" r="{62 * s:.1f}" fill="{dark}"/><circle cx="{x - 40 * s:.1f}" cy="{y - 130 * s:.1f}" r="{44 * s:.1f}" fill="{dark}"/>'
            f'<circle cx="{x + 42 * s:.1f}" cy="{y - 134 * s:.1f}" r="{46 * s:.1f}" fill="{leaf}"/><circle cx="{x - 8 * s:.1f}" cy="{y - 176 * s:.1f}" r="{48 * s:.1f}" fill="{leaf}"/>')


def lamp(x, y, s=1.0, on=0.0):
    o = (f'<rect x="{x - 4 * s:.1f}" y="{y - 190 * s:.1f}" width="{8 * s:.1f}" height="{190 * s:.1f}" fill="#2A2E3A"/>'
         f'<path d="M{x - 18 * s:.1f} {y - 190 * s:.1f} L{x + 18 * s:.1f} {y - 190 * s:.1f} L{x + 10 * s:.1f} {y - 214 * s:.1f} L{x - 10 * s:.1f} {y - 214 * s:.1f} Z" fill="#2A2E3A"/>'
         f'<rect x="{x - 12 * s:.1f}" y="{y - 190 * s:.1f}" width="{24 * s:.1f}" height="{10 * s:.1f}" fill="{mixc("#C8CCD8", "#FFE8A0", on)}"/>')
    if on > 0:
        o += glow(x, y - 186 * s, 70 * s, "#FFD98A", 0.55 * on, 10) + f'<path d="M{x - 12 * s:.1f} {y - 182 * s:.1f} L{x - 70 * s:.1f} {y:.1f} L{x + 70 * s:.1f} {y:.1f} L{x + 12 * s:.1f} {y - 182 * s:.1f} Z" fill="#FFE8A0" opacity="{0.12 * on:.2f}"/>'
    return o


def park(t, night=0.0, frost=0.0, lamps=0.0, sunpos=None):
    back = sky(night, sunpos) + skyline(night)
    gr = (f'<rect x="-800" y="{G - 40}" width="2560" height="1200" fill="url(#snGrass)"/>'
          f'<rect x="-800" y="{G - 40}" width="2560" height="1200" fill="url(#snGrassN)" opacity="{night * 0.92:.2f}"/>'
          f'<path d="M-800 {G + 30} Q480 {G - 6} 1760 {G + 30} L1760 {G + 60} Q480 {G + 22} -800 {G + 60} Z" fill="{mixc("#E8D8B0", "#2A2E38", night)}"/>')
    if frost > 0:
        r = random.Random(2)
        gr += f'<rect x="-800" y="{G - 40}" width="2560" height="1200" fill="url(#snFrost)" opacity="{0.75 * frost:.2f}"/>'
        gr += "".join(f'<path d="M{x:.0f} {y:.0f} l6 -6 m-6 0 l6 6 m-3 -8 l0 10" stroke="#FFFFFF" stroke-width="1.5" opacity="{frost * 0.8:.2f}"/>'
                      for x, y in ((r.uniform(-300, 1260), r.uniform(G - 30, G + 300)) for _ in range(int(90 * frost))))
    props = tree(250, G - 30, 1.0, night, frost) + tree(720, G - 36, 1.1, night, frost) + lamp(380, G - 20, 1.0, lamps) + lamp(610, G - 20, 1.0, lamps)
    props += (f'<rect x="530" y="{G - 52}" width="90" height="10" rx="3" fill="{mixc("#B07A4A", "#20160E", night)}"/><rect x="530" y="{G - 74}" width="90" height="8" rx="3" fill="{mixc("#B07A4A", "#20160E", night)}"/>'
              f'<rect x="536" y="{G - 52}" width="6" height="26" fill="#2A2E3A"/><rect x="608" y="{G - 52}" width="6" height="26" fill="#2A2E3A"/>')
    return [(back, 0.3, False), (gr + props, 1.0, False)]


def cone(x, y, s=1.0, ang=0.0, melt=0.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})"><path d="M-14 -6 L14 -6 L0 34 Z" fill="#E0A85A" stroke="#B07A34" stroke-width="2"/>'
            '<path d="M-10 0 L8 14 M-4 -4 L10 6 M10 0 L-6 16" stroke="#B07A34" stroke-width="1.5"/>'
            '<circle cx="0" cy="-16" r="16" fill="#FFB8D0"/><circle cx="-6" cy="-21" r="5" fill="#FFFFFF" opacity="0.6"/></g>')


def thermo(x, y, level, s=1.0):
    """Big thermometer; level 0..1 of the tube filled red."""
    h = 230 * s
    return (f'<rect x="{x - 18 * s:.1f}" y="{y - h:.1f}" width="{36 * s:.1f}" height="{h:.1f}" rx="{18 * s:.1f}" fill="#FFFFFF" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="{x - 9 * s:.1f}" y="{y - 10 * s - (h - 30 * s) * level:.1f}" width="{18 * s:.1f}" height="{(h - 30 * s) * level + 10 * s:.1f}" rx="{9 * s:.1f}" fill="#E83A3A"/>'
            f'<circle cx="{x:.1f}" cy="{y + 12 * s:.1f}" r="{30 * s:.1f}" fill="#E83A3A" stroke="{INK}" stroke-width="5"/>'
            + "".join(f'<path d="M{x + 18 * s:.1f} {y - 30 * s - k * 36 * s:.1f} l{10 * s:.1f} 0" stroke="{INK}" stroke-width="3"/>' for k in range(6)))


def breath(x, y, t, op=1.0):
    u = (t * 0.9) % 1
    return f'<ellipse cx="{x + 30 * u:.1f}" cy="{y - 20 * u:.1f}" rx="{8 + 20 * u:.1f}" ry="{5 + 12 * u:.1f}" fill="#E8F4FF" opacity="{op * 0.7 * (1 - u):.2f}"/>'


def torch_beam(x, y, ang, L=360, op=0.5):
    a = math.radians(ang); w = math.radians(13)
    p1 = (x + L * math.cos(a - w), y + L * math.sin(a - w)); p2 = (x + L * math.cos(a + w), y + L * math.sin(a + w))
    return (f'<path d="M{x:.1f} {y:.1f} L{p1[0]:.1f} {p1[1]:.1f} L{p2[0]:.1f} {p2[1]:.1f} Z" fill="#FFF2C0" opacity="{op * 0.35:.2f}"/>'
            f'<path d="M{x:.1f} {y:.1f} L{x + L * 0.6 * math.cos(a - w * 0.5):.1f} {y + L * 0.6 * math.sin(a - w * 0.5):.1f} L{x + L * 0.6 * math.cos(a + w * 0.5):.1f} {y + L * 0.6 * math.sin(a + w * 0.5):.1f} Z" fill="#FFF8DC" opacity="{op * 0.35:.2f}"/>')


def torch(x, y, ang):
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f})"><rect x="-26" y="-7" width="30" height="14" rx="4" fill="#3A3E4A"/><rect x="2" y="-9" width="10" height="18" rx="3" fill="#5A5E6A"/><rect x="11" y="-7" width="3" height="14" fill="#FFF2C0"/></g>'


def front_hand(J, x, y, s, side="r"):
    return x + J["h" + side][0] * s, y + J["h" + side][1] * s


EAT = F_STAND | dict(er=(66, -330), hr=(22, -392), face=fc(open=1.0, mouth="smile", look=(0.4, 0)))
LOOKUP = F_STAND | dict(er=(80, -300), hr=(110, -330), face=fc(open=1.3, lift=1.0, mouth="o", look=(0.2, -1.0)))


# ================================================================== shots
@shot5(0.0, "s01", "SPACE: the Sun blazing; at 0.35 s it collapses to nothing in a flash. Only an empty black spot and a fading ring are left.")
def s01(t, D):
    gone = ramp(t, 0.35, 0.6)
    r = 110 * (1 - eio(gone))
    fl = clamp(1 - abs(t - 0.6) / 0.25)
    ring = f'<circle cx="480" cy="200" r="{110 + 300 * ramp(t, 0.6, D):.0f}" fill="none" stroke="#FFE8A0" stroke-width="5" opacity="{0.6 * (1 - ramp(t, 0.6, D)):.2f}"/>' if t > 0.6 else ""
    o = sun(480, 200, r) + ring + glow(480, 200, 160, "#FFFFFF", 0.9 * fl, 20) + earth(590, 500, 36, 1.0, 160)
    cam = (kick(t, 0.6, 10), 40, lerp(1.0, 1.12, ramp(t, 0, D)), 0)
    return SS([(f'<rect x="-800" y="-800" width="2560" height="2000" fill="url(#stageS)"/>{STARS}', 0.3, True), (o, 1.0, False)], cam, lights=(),
              overlay=tag_big("THE SUN", 480, 95, ramp(t, 0.55, 0.85), 120, "#FFE070") + tag_big("JUST VANISHED", 480, 190, ramp(t, 0.7, 1.0), 100, "#FF6A4A"))


@shot5(B[(0, 1)] - 0.1, "s02", "PARK AT NOON: the boy licks an ice cream under a bright sun, happy. He has no idea.")
def s02(t, D):
    J = EAT | dict(hr=(22, -392 + 10 * math.sin(t * 5)))
    me = boy(J, "s02", BX, G, BS, L_DAY)
    hx, hy = front_hand(J, BX, G, BS)
    cam = (0, -30, lerp(1.25, 1.35, ramp(t, 0, D)), 0)
    return SS(park(t, sunpos=(340, 60, 34)) + [(me + cone(hx, hy - 8, 0.9, 10), 1.0, False)], cam,
              overlay=tag_big("YOU HAVE NO IDEA", 480, 110, ramp(t, 0.1, 0.4), 100, "#FFFFFF"))


@shot5(B[(1, 0)] - 0.1, "s03", "SPACE DIAGRAM: the empty spot where the Sun was, a shell of its last light racing down toward Earth; a clock counts 8:20 to 0. Then cyan gravity ripples ride along with it.")
def s03(t, D):
    u = ramp(t, 0, D)
    sx, sy, ex, ey = 480, 20, 480, 470
    R = lerp(40, ey - sy - 26, u)
    shell = (f'<circle cx="{sx}" cy="{sy}" r="{R:.1f}" fill="none" stroke="#FFE070" stroke-width="10" opacity="0.9"/>'
             f'<circle cx="{sx}" cy="{sy}" r="{R - 14:.1f}" fill="none" stroke="#FFF2B0" stroke-width="4" opacity="0.5"/>')
    gv = ramp(t, B[(1, 2)] - B[(1, 0)], B[(1, 2)] - B[(1, 0)] + 0.4)
    grav = "".join(f'<circle cx="{sx}" cy="{sy}" r="{R - 30 - 26 * k:.1f}" fill="none" stroke="#6AE8F4" stroke-width="4" stroke-dasharray="14 10" opacity="{gv * (0.8 - 0.2 * k):.2f}"/>' for k in range(3)) if gv > 0 else ""
    secs = int(500 * (1 - u)); clock = f"{secs // 60}:{secs % 60:02d}"
    spot = f'<circle cx="{sx}" cy="{sy}" r="14" fill="none" stroke="#8A8AA8" stroke-width="3" stroke-dasharray="5 5"/>'
    o = spot + shell + grav + earth(ex, ey, 40, 1.0, -90) + wtext(ex, ey + 74, "EARTH", 24, "#FFFFFF")
    o += wtext(sx + 110, 140, clock, 52, "#FFE070") + wtext(sx + 110, 170, "MIN LEFT", 18, "#FFFFFF")
    cam = (0, 240 - CY, 1.0, 0)
    return SS([(f'<rect x="-800" y="-800" width="2560" height="2000" fill="url(#stageS)"/>{STARS}', 0.3, True), (o, 1.0, False)], cam, lights=(),
              overlay=tag_big("LIGHT: STILL COMING", 480, 110, ramp(t, 0.1, 0.4), 84, "#FFE070") + tag_big("GRAVITY TOO", 480, 210, gv, 90, "#6AE8F4"))


@shot5(B[(2, 0)] - 0.1, "s04", "PARK: still bright, he finishes his ice cream. 0:03... 0:02... 0:01. At 'black' the sky snaps to night, stars, lamps flick on, he freezes, ice cream drops.")
def s04(t, D):
    tb = B[(2, 2)] - B[(2, 0)] + 0.05
    n = 1.0 if t > tb else 0.0
    lamps = clamp((t - tb - 0.35) / 0.1) * (0.6 + 0.4 * (math.sin(t * 40) > -0.3 if t < tb + 0.9 else 1))
    J = (EAT if t < tb else F_ALARM | dict(face=fc(open=1.6, lift=1.3, mouth="gasp", look=(0, -0.6))))
    me = boy(J, "s04", BX, G, BS, L_DAY if t < tb else L_NIGHT)
    if t < tb:
        hx, hy = front_hand(J, BX, G, BS); ic = cone(hx, hy - 8, 0.9, 10)
    else:
        f = ramp(t, tb, tb + 0.5); ic = cone(BX + 30, lerp(G - 200, G + 6, f * f), 0.9, 10 + 160 * f)
    secs = max(0, 3 - int(t / (tb / 3))) if t < tb else 0
    cam = (kick(t, tb, 12), -30, lerp(1.35, 1.5, ramp(t, 0, D)), 0)
    return SS(park(t, night=n, lamps=lamps, sunpos=None if n else (340, 60, 34)) + [(me + ic, 1.0, False)], cam, lights=(L_DAY if t < tb else L_NIGHT,),
              overlay=(tag_big(f"0:0{secs}", 480, 110, 1.0, 120, "#FFE070") if t < tb else badge("MINUTE 8", ramp(t, tb, tb + 0.2), "#3A3A6A", 90)))


@shot5(B[(3, 0)] - 0.1, "s05", "SPACE TOP VIEW: Earth's dotted orbit around the empty spot; Earth curves along it for a beat, then shoots off straight along the tangent into the dark, a dashed trail behind.")
def s05(t, D):
    cx, cy, R = 480, 230, 150
    a0 = math.radians(90)
    tr = 0.5
    if t < tr:
        a = a0 - 0.9 * t; ex, ey = cx + R * math.cos(a), cy + R * math.sin(a)
    else:
        a = a0 - 0.9 * tr; px, py = cx + R * math.cos(a), cy + R * math.sin(a)
        tx, ty = math.sin(a), -math.cos(a)                   # tangent of the clockwise path
        d = 120 * (t - tr)
        ex, ey = px + tx * d, py + ty * d
    orbit = f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#5A6A9A" stroke-width="3" stroke-dasharray="8 9"/>'
    trail = f'<path d="M{cx + R * math.cos(a0 - 0.9 * tr):.1f} {cy + R * math.sin(a0 - 0.9 * tr):.1f} L{ex:.1f} {ey:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="10 8" opacity="0.7"/>' if t > tr else ""
    spot = f'<circle cx="{cx}" cy="{cy}" r="14" fill="none" stroke="#8A8AA8" stroke-width="3" stroke-dasharray="5 5"/>'
    o = orbit + spot + trail + earth(ex, ey, 30, 0.7, 0)
    cam = (lerp(0, (ex - cx) * 0.8, ramp(t, tr, D)), 230 - CY + lerp(0, (ey - cy) * 0.8, ramp(t, tr, D)), 1.05, 0)
    return SS([(f'<rect x="-800" y="-800" width="2560" height="2000" fill="url(#stageS)"/>{STARS}', 0.3, True), (o, 1.0, False)], cam, lights=(),
              overlay=tag_big("NO SUN = NO ORBIT", 480, 110, ramp(t, 0.6, 0.9), 96, "#FFFFFF"))


@shot5(B[(3, 2)] - 0.1, "s06", "NIGHT PARK: the boy looks up with a flashlight; the full Moon above fades to a dead grey disc.")
def s06(t, D):
    lit = 1 - eio(ramp(t, 0.4, 2.2))
    J = LOOKUP
    me = boy(J, "s06", BX, G, BS, L_TORCH)
    hx, hy = front_hand(J, BX, G, BS)
    o = me + torch(hx, hy, -60) + torch_beam(hx + 6, hy - 10, -60, 420, 0.8)
    cam = (0, -120, lerp(1.0, 1.08, ramp(t, 0, D)), 0)
    return SS(park(t, night=1.0, lamps=1.0) + [(moon(540, 40, 58, lit), 0.6, False), (o, 1.0, False)], cam, lights=(L_TORCH,),
              overlay=tag_big("THE MOON GOES DARK", 480, 110, ramp(t, 0.1, 0.4), 90, "#FFFFFF"))


@shot5(B[(4, 0)] - 0.1, "s07", "FREEZE: frost creeps over the night park, trees whiten, he hugs himself shivering, breath clouds. A giant thermometer plunges: 1 WEEK below 0°F, 1 YEAR -100°F.")
def s07(t, D):
    fr = eio(ramp(t, 0, D * 0.8))
    lvl = lerp(0.62, 0.3, eio(ramp(t, 0.2, 2.0)))
    yr = B[(4, 2)] - B[(4, 0)]
    if t > yr:
        lvl = lerp(0.3, 0.05, eio(ramp(t, yr, yr + 1.4)))
    sh = 3 * math.sin(t * 40)
    J = F_SHIVER
    me = boy(J, "s07", BX - 50 + sh * 0.5, G, BS, L_NIGHT) + breath(BX - 50 + 10, G - 400 * BS, t)
    th = thermo(580, G - 40, lvl, 0.85)
    lab = (wtext(580, G - 300, "1 WEEK", 34, "#FFFFFF", ramp(t, 0.6, 0.9)) + wtext(580, G - 268, "BELOW 0°F", 26, "#9AD8FF", ramp(t, 0.6, 0.9))) if t < yr else \
          (wtext(580, G - 300, "1 YEAR", 34, "#FFFFFF", ramp(t, yr, yr + 0.3)) + wtext(580, G - 268, "−100°F", 34, "#9AD8FF", ramp(t, yr, yr + 0.3)))
    cam = (40, -40, lerp(1.15, 1.25, ramp(t, 0, D)), 0)
    return SS(park(t, night=1.0, frost=fr, lamps=1.0) + [(me + th + lab, 1.0, False)], cam, lights=(L_NIGHT,),
              overlay=tag_big("THE BIG FREEZE", 480, 110, ramp(t, 0.1, 0.4), 100, "#9AD8FF"))


@shot5(B[(5, 0)] - 0.1, "s08", "CLOSE: frozen dark park, only his flashlight; he swings it around then looks straight at us. WHERE DO YOU RUN? / PART 2 TOMORROW / FOLLOW OR FREEZE.")
def s08(t, D):
    sw = math.sin(t * 1.6) * 30 * (1 - ramp(t, 1.4, 2.0))
    J = F_SHIVER | dict(er=(80, -290), hr=(100, -300), face=fc(open=1.2, knit=0.8, lift=0.8, mouth="grit", look=(0, 0)))
    me = boy(J, "s08", BX, G, BS, L_TORCH)
    hx, hy = front_hand(J, BX, G, BS)
    o = me + torch(hx, hy, -20 + sw) + torch_beam(hx + 6, hy, -20 + sw, 380, 0.8) + breath(BX + 6, G - 400 * BS, t, 0.8)
    dark = f'<rect x="-800" y="-800" width="2560" height="2000" fill="#02030A" opacity="0.45"/>'
    cam = (0, G - 300 * BS - CY + 20, lerp(1.7, 1.95, eio(ramp(t, 0, D))), 0)
    return SS(park(t, night=1.0, frost=1.0, lamps=0.0) + [(dark, 1.0, False), (o, 1.0, False)], cam, lights=(L_TORCH,),
              overlay=tag_big("WHERE DO YOU RUN?", 480, 110, ramp(t, 0.05, 0.35), 96, "#FFFFFF")
              + badge("PART 2 TOMORROW", ramp(t, B[(5, 1)] - B[(5, 0)], B[(5, 1)] - B[(5, 0)] + 0.3), "#E8503A", 230)
              + tag_big("FOLLOW OR FREEZE", 480, 340, ramp(t, B[(5, 3)] - B[(5, 0)], B[(5, 3)] - B[(5, 0)] + 0.3), 90, "#9AD8FF"))
