"""Ep 3 core: timing (lines.json / phrases.json), landscape shot helper, and the locked sets.
World is 960x540 (wide). Reuses the mosquito, swarm and props from the mosquito reel (mosq/mcore, mprops).

Locked geography (keep continuity across cuts):
  HOME     the boy's house: blue-grey two-storey, red door, centre of the street; big front window = living room.
  LIVING   couch facing the TV (camera side), window behind the couch (shows the street sky), kitchen doorway at right.
  KITCHEN  fridge-freezer (left), counter with the box fan (centre), wall clock above, back door with a fly screen (right).
  BACKYARD pool to the right of the back door, lounger, fence, the same dusk sky.
"""
import sys, json, math, random, re
sys.path[:0] = ["/home/claude/ep3", "/home/claude/mosq", "/home/claude/ep2x", "/home/claude/ep", "/home/claude/bible"]
from mprops import *
import mprops as MP
import geo

D3 = "/home/claude/ep3"
_L = json.load(open(f"{D3}/lines.json"))
LINES = _L["lines"]; TEND = _L["total"]
PH = {int(k): v for k, v in json.load(open(f"{D3}/phrases.json")).items()}


def Ln(i):
    return LINES[i]["start"]


def LEn(i):
    return LINES[i]["end"]


def Pn(i, k):
    ph = PH[i]
    return ph[min(k, len(ph) - 1)]["t"]


W, H = 960, 540
LW, LC = LD["dusk"], LD["cool"]
LI = Light("indoor", amb=(1.0, 0.94, 0.9), sat=1.0, key="#FFD8A0", key_op=0.35, ang=-40, spread=0.8, shade="#2A1440", shade_op=0.35, rim="#FFE0B0", rim_op=0.45, rim_w=7)
LIC = Light("indoorDark", amb=(0.74, 0.7, 0.84), sat=0.85, key="#FFB070", key_op=0.25, ang=-40, shade="#0A0620", shade_op=0.45, rim="#9AB8FF", rim_op=0.35, rim_w=7)
LICE = Light("ice", amb=(0.86, 0.94, 1.04), sat=0.8, key="#E8F4FF", key_op=0.4, ang=-60, spread=0.8, shade="#1A3060", shade_op=0.35, rim="#FFFFFF", rim_op=0.55, rim_w=8)

EXTRA_DEFS = (
    lin("lroomW", [(0, "#F0D6C4"), (1, "#E0BCA8")]) + lin("lroomF", [(0, "#B07A5A"), (1, "#8A5A40")])
    + lin("couch", [(0, "#4A6AC8"), (1, "#2E4690")]) + lin("kitW", [(0, "#DCEFE8"), (1, "#BCD8D0")])
    + lin("fridge", [(0, "#F4F6FA"), (1, "#C8CCD8")], 0, 0, 1, 0) + lin("street", [(0, "#4A4458"), (1, "#2E2A3A")])
    + lin("houseB", [(0, "#8AA4C8"), (1, "#6A84A8")]) + lin("houseP", [(0, "#E8B4A0"), (1, "#C89480")]) + lin("houseY", [(0, "#F0D890"), (1, "#C8B070")])
    + lin("space", [(0, "#05030F"), (1, "#0A0828")]) + rad("atmo", [(0.86, "#5AB8FF", 0), (0.93, "#5AB8FF", 0.55), (1, "#5AB8FF", 0)])
    + rad("nightSide", [(0, "#0A1430", 0), (0.7, "#0A1430", 0.2), (1, "#05081A", 0.85)], 0.35, 0.4, 0.75)
    + lin("ocean", [(0, "#1E4A9A"), (1, "#0E2A6A")]) + lin("titleBg", [(0, "#1A0E4A"), (1, "#3A1A6A")])
)


def S3(layers, cam=(0, 0, 1.0), defs="", overlay="", lights=(), pad=(260, 160)):
    named = [(f"L{k}", l[1], l[0], l[2] if len(l) > 2 else False, l[3] if len(l) > 3 else None) for k, l in enumerate(layers)]
    return dict(layers=named, defs=MP.BASE_DEFS + EXTRA_DEFS + light_defs(*lights) + defs, cam=cam, overlay=overlay, clock=False, pad=pad)


def ui(svg):
    return (svg, 0.0, False)


def chip(txt, x, y, u=1.0, size=22, sub=None, edge=PINK):
    return pill(txt, x, y, u, size, sub=sub, edge=edge)


def label(txt, x, y, size=18, col="#FFFFFF", anchor="middle", u=1.0):
    if u <= 0:
        return ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="Fredoka" font-weight="700" font-size="{size}" fill="{col}" '
            f'stroke="{INK}" stroke-width="{size / 6:.1f}" paint-order="stroke" stroke-linejoin="round" opacity="{clamp(u * 3):.2f}">{txt}</text>')


def leader(x0, y0, x1, y1, u=1.0, col="#FFFFFF"):
    if u <= 0:
        return ""
    x = lerp(x0, x1, eo(u)); y = lerp(y0, y1, eo(u))
    return f'<path d="M{x0:.1f} {y0:.1f} L{x:.1f} {y:.1f}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/><path d="M{x0:.1f} {y0:.1f} L{x:.1f} {y:.1f}" stroke="{col}" stroke-width="2.4" stroke-linecap="round"/><circle cx="{x0:.1f}" cy="{y0:.1f}" r="4" fill="{col}" stroke="{INK}" stroke-width="2"/>'


# ------------------------------------------------------------------ brand
_LOGO = None


def logo(x, y, s=1.0):
    global _LOGO
    if _LOGO is None:
        src = open("/home/claude/brand/out/profile_picture.min.svg").read()
        body = re.sub(r"^<svg[^>]*>", "", src.strip()); body = re.sub(r"</svg>\s*$", "", body)
        body = body.replace('id="sky"', 'id="mlSky3"').replace("url(#sky)", "url(#mlSky3)")
        _LOGO = f'<clipPath id="mlClip3"><rect x="0" y="0" width="800" height="800" rx="180"/></clipPath><g clip-path="url(#mlClip3)">{body}</g>'
    return f'<g transform="translate({x - 400 * s:.1f} {y - 400 * s:.1f}) scale({s:.4f})">{_LOGO}</g>'


# ------------------------------------------------------------------ space
def gpt(cx, cy, r, lon, lat, lon0, lat0):
    x, y, c = geo.globe_pt(cx, cy, r, lon, lat, lon0, lat0)
    return (x, y) if c > 0.05 else None


def earth(cx, cy, r, lon0, lat0=15, night=0.0, t=0.0, land="#3E8A4A"):
    o = [f'<circle cx="{cx}" cy="{cy}" r="{r * 1.08:.1f}" fill="url(#atmo)"/>', f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#ocean)"/>',
         geo.globe_land(cx, cy, r, lon0, lat0, fill=land)]
    if night > 0:
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#060A20" opacity="{0.62 * night:.2f}"/>')
        r_ = random.Random(9)
        for i in range(260):
            lon = r_.uniform(-180, 180); lat = r_.uniform(-40, 60)
            p = gpt(cx, cy, r, lon, lat, lon0, lat0)
            if p:
                o.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r_.uniform(0.8, 1.8):.1f}" fill="#FFD890" opacity="{0.85 * night:.2f}"/>')
    return "".join(o)


def space_bg(seed=5):
    return '<rect x="-600" y="-600" width="2160" height="1800" fill="url(#space)"/>' + FX.stars(seed, 260, -500, 1460, -400, 940, 0.9)


# ------------------------------------------------------------------ the street (wide, dusk)
HOME_X, STREET_Y = 480, 400


def house2(x, y, s=1.0, wall="url(#houseB)", roof="#4A2A4A", door="#C83A3A", dark=0.0, lit_=1.0, seed=0):
    o = [f'<rect x="-110" y="-200" width="220" height="200" fill="{wall}"/>', f'<path d="M-128 -200 L0 -280 L128 -200 Z" fill="{roof}"/>',
         f'<rect x="-28" y="-86" width="56" height="86" rx="4" fill="{door}"/><circle cx="16" cy="-42" r="3" fill="#FFD890"/>',
         '<rect x="-20" y="-96" width="40" height="8" fill="#5A3A4A" opacity="0.5"/>']
    for wx, wy, ww in ((-92, -170, 60), (32, -170, 60), (-96, -84, 56)):
        o.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="48" rx="3" fill="#FFD890" opacity="{0.35 + 0.65 * lit_:.2f}"/><rect x="{wx + ww / 2 - 2}" y="{wy}" width="4" height="48" fill="#E8E0D4"/>'
                 f'<rect x="{wx - 4}" y="{wy + 46}" width="{ww + 8}" height="6" fill="#E8E0D4"/>')
    o.append('<rect x="44" y="-80" width="52" height="70" rx="4" fill="#FFD890" opacity="0.9"/><rect x="44" y="-80" width="52" height="70" rx="4" fill="none" stroke="#E8E0D4" stroke-width="5"/>')
    if dark > 0:
        o.append(f'<rect x="-130" y="-282" width="260" height="284" fill="#0A0418" opacity="{0.5 * dark:.2f}"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{"".join(o)}</g>'


def street_scene(t=0.0, dark=0.0, sun=True, swarm_k=0.0):
    """Front view of the street: dusk sky, far roofs, 3 houses (his in the middle), lawns, sidewalk, road."""
    o = [dusk_sky(dark, t, sun).replace('cx="560" cy="300"', 'cx="760" cy="250"')]
    o.append(far_roofs(300, mixc("#3A1A4A", "#120818", dark), seed=4, x0=-300, x1=1260))
    if swarm_k > 0:
        o.append(cloud_mass(480, lerp(-160, 90, swarm_k), lerp(200, 900, swarm_k), lerp(60, 260, swarm_k), t, 3, "#0A0610", min(1, swarm_k * 1.4), 10))
    for x, wall, roof, door in ((170, "url(#houseP)", "#6A2A3A", "#3A6A9A"), (HOME_X, "url(#houseB)", "#4A2A4A", "#C83A3A"), (790, "url(#houseY)", "#5A3A2A", "#2A8A5A")):
        o.append(house2(x, STREET_Y - 30, 0.9 if x != HOME_X else 1.0, wall, roof, door, dark, 1.0))
    o.append(f'<rect x="-600" y="{STREET_Y - 30}" width="2160" height="40" fill="{mixc("#3E8A4A", "#14281E", dark)}"/>')
    o.append(f'<rect x="-600" y="{STREET_Y + 10}" width="2160" height="16" fill="{mixc("#C8C0D0", "#3A3448", dark)}"/>')
    o.append(f'<rect x="-600" y="{STREET_Y + 26}" width="2160" height="300" fill="url(#street)"/>')
    for k in range(-6, 16):
        o.append(f'<rect x="{k * 90}" y="{STREET_Y + 80}" width="46" height="6" fill="#E8E0A0" opacity="{0.7 - 0.4 * dark:.2f}"/>')
    for lx in (40, 330, 640, 920):
        on = 1.0 if dark > 0.3 else 0.3
        o.append(f'<rect x="{lx - 3}" y="{STREET_Y - 160}" width="6" height="176" fill="#2A2436"/><path d="M{lx} {STREET_Y - 160} q16 -6 26 4" stroke="#2A2436" stroke-width="5" fill="none"/>'
                 f'<circle cx="{lx + 26}" cy="{STREET_Y - 152}" r="6" fill="#FFE8B0" opacity="{0.4 + 0.6 * on:.2f}"/>' + glow(lx + 26, STREET_Y - 148, 40, "#FFD890", 0.35 * on, 10))
    return "".join(o)


# ------------------------------------------------------------------ living room (front view, camera at the TV)
FLOOR_L = 470


def living_room(t=0.0, sky_dark=0.0, swarm_k=0.0, tv=True):
    o = ['<rect x="-600" y="-600" width="2160" height="1800" fill="url(#lroomW)"/>']
    # window behind the couch, showing the street sky
    wx0, wy0, ww, wh = 250, 70, 400, 210
    o.append(f'<rect x="{wx0 - 14}" y="{wy0 - 14}" width="{ww + 28}" height="{wh + 28}" rx="10" fill="#FFFFFF"/>')
    o.append(f'<svg x="{wx0}" y="{wy0}" width="{ww}" height="{wh}" viewBox="250 100 400 210">{dusk_sky(sky_dark, t)}{far_roofs(300, mixc("#3A1A4A", "#120818", sky_dark), 6, 200, 760)}'
             + (cloud_mass(450, lerp(60, 200, swarm_k), lerp(80, 400, swarm_k), lerp(30, 160, swarm_k), t, 4, "#0A0610", min(1, 1.5 * swarm_k), 8) if swarm_k > 0 else "") + '</svg>')
    o.append(f'<rect x="{wx0 + ww / 2 - 4}" y="{wy0}" width="8" height="{wh}" fill="#FFFFFF"/><rect x="{wx0}" y="{wy0 + wh / 2 - 4}" width="{ww}" height="8" fill="#FFFFFF"/>')
    # curtains
    for cx, s in ((wx0 - 40, 1), (wx0 + ww + 40, -1)):
        o.append(f'<path d="M{cx - 36 * s} {wy0 - 30} Q{cx} {wy0 + 100} {cx - 30 * s} {wy0 + wh + 40} L{cx + 30 * s} {wy0 + wh + 40} Q{cx + 20 * s} {wy0 + 100} {cx + 36 * s} {wy0 - 30} Z" fill="#E86A5A"/>')
    # kitchen doorway at the right with fan and freezer visible
    o.append('<rect x="760" y="60" width="170" height="420" fill="url(#kitW)"/><rect x="752" y="52" width="186" height="10" fill="#FFFFFF"/><rect x="752" y="52" width="10" height="430" fill="#FFFFFF"/><rect x="930" y="52" width="10" height="430" fill="#FFFFFF"/>')
    o.append('<rect x="780" y="140" width="80" height="330" rx="8" fill="url(#fridge)"/><path d="M780 260 L860 260" stroke="#A8ACB8" stroke-width="3"/><rect x="848" y="170" width="5" height="60" rx="2" fill="#A8ACB8"/>')
    o.append(box_fan(900, 300, 0.42, t, spin=0.0))
    # floor, rug, couch
    o.append(f'<rect x="-600" y="{FLOOR_L}" width="2160" height="600" fill="url(#lroomF)"/>')
    o.append(f'<ellipse cx="450" cy="{FLOOR_L + 40}" rx="330" ry="38" fill="#C85A6A" opacity="0.6"/>')
    o.append(couch(450, FLOOR_L - 4))
    # lamp + plant
    o.append('<path d="M120 470 L120 250" stroke="#4A3A3A" stroke-width="6"/><path d="M80 250 L160 250 L140 196 L100 196 Z" fill="#FFE0A0"/>' + glow(120, 240, 70, "#FFD890", 0.35, 18))
    o.append('<rect x="660" y="420" width="50" height="50" rx="6" fill="#C86A4A"/>' + "".join(f'<ellipse cx="{685 + 22 * math.cos(a)}" cy="{400 + 30 * math.sin(a) - 30}" rx="10" ry="28" fill="#3E8A4A" transform="rotate({math.degrees(a) + 90} {685 + 22 * math.cos(a)} {400 + 30 * math.sin(a) - 30})"/>' for a in (-2.6, -2.0, -1.5, -1.0, -0.5)))
    return "".join(o)


def couch(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-230" y="-150" width="460" height="110" rx="34" fill="url(#couch)"/>'
            '<rect x="-250" y="-90" width="70" height="100" rx="26" fill="#3A56A8"/><rect x="180" y="-90" width="70" height="100" rx="26" fill="#3A56A8"/>'
            '<rect x="-190" y="-62" width="380" height="62" rx="20" fill="#5A7AD8"/><path d="M0 -60 L0 -4" stroke="#3A56A8" stroke-width="4"/>'
            '<rect x="-200" y="0" width="12" height="16" fill="#2A2030"/><rect x="188" y="0" width="12" height="16" fill="#2A2030"/></g>')


def box_fan(x, y, s=1.0, t=0.0, spin=0.0, wind=0.0):
    """Square box fan facing camera; spin 0..1 = blade speed (motion-blurred disc when fast)."""
    a = (t * 1400 * spin) % 360
    o = ['<rect x="-110" y="-110" width="220" height="220" rx="22" fill="#E8ECF4"/><rect x="-96" y="-96" width="192" height="192" rx="14" fill="#2A3040"/>']
    if spin > 0.6:
        o.append('<circle r="86" fill="#8A94A8" opacity="0.55"/><circle r="60" fill="#A8B0C0" opacity="0.4"/>')
    else:
        for k in range(5):
            o.append(f'<path d="M0 0 Q40 -30 80 -12 Q60 20 0 0 Z" fill="#9AA4B8" transform="rotate({a + k * 72:.1f})"/>')
    o.append('<circle r="16" fill="#C8CCD8"/>')
    for k in range(-4, 5):
        o.append(f'<path d="M{k * 22} -96 L{k * 22} 96" stroke="#E8ECF4" stroke-width="2" opacity="0.8"/>')
    o.append('<rect x="70" y="80" width="26" height="12" rx="4" fill="#FF4F7A"/><rect x="-10" y="110" width="20" height="16" fill="#C8CCD8"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{"".join(o)}</g>'


def cereal_bowl(x, y, s=1.0, t=0.0, ripple=0.0):
    o = ['<path d="M-60 -10 Q-56 40 0 46 Q56 40 60 -10 Z" fill="#FFFFFF"/><path d="M-60 -10 Q-56 40 0 46 Q56 40 60 -10 Z" fill="#5AE8FF" opacity="0.25"/>',
         '<ellipse cx="0" cy="-10" rx="60" ry="14" fill="#F8F4EC"/>']
    for k in range(10):
        o.append(f'<circle cx="{-44 + k * 10}" cy="{-12 + 3 * math.sin(k * 2.1) + ripple * 2 * math.sin(t * 30 + k)}" r="5" fill="#F0B04A" stroke="#C8803A" stroke-width="1.5"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{"".join(o)}</g>'


# ------------------------------------------------------------------ kitchen (front view)
def kitchen(t=0.0, fan_spin=0.0, dark=0.0, freezer_open=0.0, clock_min=20.0):
    o = ['<rect x="-600" y="-600" width="2160" height="1800" fill="url(#kitW)"/>']
    for i in range(-6, 20):
        for j in range(4):
            o.append(f'<rect x="{-40 + i * 56}" y="{160 + j * 40}" width="52" height="36" rx="5" fill="#FFFFFF" opacity="0.55"/>')
    # wall clock with the countdown face
    o.append('<circle cx="560" cy="80" r="48" fill="#FFFFFF" stroke="#2A2436" stroke-width="6"/>')
    a = math.radians(-90 + 360 * (clock_min / 60.0))
    o.append(f'<path d="M560 80 L{560 + 34 * math.cos(a):.1f} {80 + 34 * math.sin(a):.1f}" stroke="#E83A4A" stroke-width="4" stroke-linecap="round"/><path d="M560 80 L560 52" stroke="#2A2436" stroke-width="5" stroke-linecap="round"/><circle cx="560" cy="80" r="5" fill="#2A2436"/>')
    # fridge-freezer, left
    fo = eo(freezer_open)
    o.append('<rect x="100" y="40" width="200" height="450" rx="14" fill="url(#fridge)"/><path d="M100 200 L300 200" stroke="#A8ACB8" stroke-width="4"/>'
             '<rect x="270" y="80" width="8" height="90" rx="4" fill="#A8ACB8"/><rect x="270" y="230" width="8" height="120" rx="4" fill="#A8ACB8"/>')
    if fo > 0:
        o.append(f'<rect x="104" y="44" width="192" height="152" rx="10" fill="#CFEFFF"/>' + glow(200, 120, 90, "#E8FAFF", 0.7 * fo, 14)
                 + f'<path d="M300 40 L{300 + 150 * fo:.0f} {30 - 10 * fo:.0f} L{300 + 150 * fo:.0f} {206 + 10 * fo:.0f} L300 200 Z" fill="#E8ECF4"/>')
        for k in range(int(10 * fo)):
            o.append(f'<path d="M{200 + 30 * math.sin(k * 1.7 + t)} {200 - (t * 40 + k * 23) % 120}" stroke="#FFFFFF" opacity="0.5"/>')
    o.append(label("FREEZER", 200, 140, 16, "#3A4A6A") if fo < 0.2 else "")
    # counter with the fan
    o.append('<rect x="-600" y="330" width="2160" height="20" rx="6" fill="#C8B0A0"/><rect x="-600" y="348" width="2160" height="300" fill="#7A9A90"/>')
    for k in range(-4, 14):
        o.append(f'<rect x="{-20 + k * 120}" y="364" width="108" height="140" rx="10" fill="#6A8A80"/><rect x="{30 + k * 120}" y="378" width="18" height="7" rx="3" fill="#E8E0D4"/>')
    o.append(box_fan(560, 236, 0.85, t, fan_spin))
    # back door with fly screen, right
    o.append('<rect x="760" y="60" width="150" height="290" rx="6" fill="#8A6A5A"/><rect x="774" y="74" width="122" height="150" fill="#3A4A5A" opacity="0.6"/>'
             + "".join(f'<path d="M{774 + k * 8} 74 L{774 + k * 8} 224" stroke="#8A9AB0" stroke-width="0.8" opacity="0.6"/>' for k in range(16)))
    if dark > 0:
        o.append(f'<rect x="-600" y="-600" width="2160" height="1800" fill="#0A0418" opacity="{0.4 * dark:.2f}"/>')
    return "".join(o)


def countdown(txt, x, y, u=1.0, urgent=0.0, t=0.0):
    if u <= 0:
        return ""
    pulse = 1 + 0.06 * urgent * math.sin(t * 10)
    o = (f'<rect x="-82" y="-28" width="164" height="56" rx="16" fill="{INK}" opacity="0.92"/><rect x="-82" y="-28" width="164" height="56" rx="16" fill="none" stroke="#FF3A4A" stroke-width="3"/>'
         f'<circle cx="-56" cy="0" r="7" fill="#FF3A4A" opacity="{0.6 + 0.4 * math.sin(t * 8):.2f}"/>' + text(14, 11, txt, 32, "#FFFFFF", 700, "middle"))
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({pulse * (0.7 + 0.3 * eo(u)):.3f})" opacity="{clamp(u * 3):.2f}">{o}</g>'
