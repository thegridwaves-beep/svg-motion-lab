"""Mosquito reel core: voice timing, vertical window, the mosquito, swarms, the backyard world at dusk, UI.
Everything is laid out for the portrait window x 300..660, y -50..590 (engine VERT, VFRAME default (480, 270))."""
import os, sys, json, math, random, re
sys.path[:0] = ["/home/claude/mosq", "/home/claude/ep2x", "/home/claude/ep", "/home/claude/bible"]
import anim_core as AC
from anim_core import shot5, finalize
import engine
from board_core import at, text
import rig3 as R3
from pose2 import *
from lite import LT, Light, lit, light_defs, contact
from fx import *
import fx as FX

DM = "/home/claude/mosq"
_L = json.load(open(f"{DM}/lines.json"))
LINES = _L["lines"]; TEND = _L["total"]
PH = {int(k): v for k, v in json.load(open(f"{DM}/phrases.json")).items()}


def Ln(i):
    return LINES[i]["start"]


def LEn(i):
    return LINES[i]["end"]


def Pn(i, k):
    ph = PH[i]
    return ph[min(k, len(ph) - 1)]["t"]


X0, X1, Y0, Y1 = 300, 660, -50, 590          # portrait window in world units
CX = 480
FONT = "Fredoka"
INK, PINK, CYAN, GOLD, CREAM = "#140A3A", "#FF4F9A", "#5AE8FF", "#FFD23F", "#FFF5E4"

# lights
LD = dict(
    dusk=Light("dusk", amb=(0.98, 0.86, 0.88), sat=1.0, key="#FFB070", key_op=0.45, ang=-30, spread=0.8, shade="#2A1440", shade_op=0.4, rim="#FFC890", rim_op=0.55, rim_w=8),
    dark=Light("dark", amb=(0.62, 0.58, 0.74), sat=0.85, key="#FF9A5A", key_op=0.2, ang=-30, shade="#0A0620", shade_op=0.5, rim="#FFB070", rim_op=0.35, rim_w=7),
    water=Light("water", amb=(0.7, 0.86, 1.0), sat=0.9, key="#9AF0FF", key_op=0.45, ang=-90, spread=0.7, shade="#06204A", shade_op=0.45, rim="#C8FFFF", rim_op=0.5, rim_w=7),
    pale=Light("pale", amb=(0.9, 0.9, 0.98), sat=0.45, key="#FFD0A0", key_op=0.25, ang=-30, shade="#1A1030", shade_op=0.45, rim="#FFC890", rim_op=0.3, rim_w=7),
)

BASE_DEFS = blurf(1, 2, 3, 4, 6, 8, 10, 12, 16, 20, 24, 30, 40, 60) + (
    '<radialGradient id="vigD" cx="0.5" cy="0.5" r="0.72"><stop offset="0.55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#05030F" stop-opacity="0.55"/></radialGradient>'
    + lin("duskSky", [(0, "#2A1670"), (0.42, "#7A2E9E"), (0.72, "#FF6F61"), (1, "#FFB070")])
    + lin("nightSky", [(0, "#0A0620"), (0.6, "#2A1450"), (1, "#5A2A5A")])
    + lin("lawn", [(0, "#3E8A4A"), (1, "#24603A")]) + lin("lawnDark", [(0, "#22402E"), (1, "#14281E")])
    + lin("water", [(0, "#5AE8FF"), (1, "#1A7AC8")]) + lin("deep", [(0, "#1A9AD8"), (0.5, "#0E5A9A"), (1, "#062A5A")])
    + lin("wallH", [(0, "#F4D8C0"), (1, "#D8B49A")]) + lin("roofH", [(0, "#7A3A5A"), (1, "#4A1E3A")])
    + lin("can", [(0, "#8A1020"), (0.3, "#E8283A"), (0.55, "#FF6A6A"), (0.7, "#D8202E"), (1, "#7A0E1A")], 0, 0, 1, 0)
    + lin("blood", [(0, "#FF3A4A"), (1, "#A8101E")]) + lin("steel", [(0, "#8A94A8"), (1, "#4A5268")])
    + rad("sunG", [(0, "#FFF4C0", 1), (0.5, "#FFC870", 0.6), (1, "#FF8A5A", 0)])
    + rad("eyeR", [(0, "#FF6A6A", 1), (1, "#FF2A3A", 0)])
    + '<filter id="toWhite" x="-20%" y="-20%" width="140%" height="140%"><feFlood flood-color="#FFFFFF"/><feComposite in2="SourceAlpha" operator="in"/></filter>'
)


def S2(layers, cam=(0, 0, 1.0), defs="", overlay="", lights=(), pad=(260, 160)):
    named = [(f"L{k}", l[1], l[0], l[2] if len(l) > 2 else False, l[3] if len(l) > 3 else None) for k, l in enumerate(layers)]
    return dict(layers=named, defs=BASE_DEFS + light_defs(*lights) + defs, cam=cam, overlay=overlay, clock=False, pad=pad)


def you(J, uid, x, y, s, Lt, side=False, flip=False, backv=False):
    body = R3.side(J) if side else (back(J) if backv else R3.front(J))
    return lit(body, uid, x, y, s, Lt, flip=flip)


def cam_keys(t, ks):
    if t <= ks[0][0]:
        return ks[0][1]
    for (t0, a), (t1, b) in zip(ks, ks[1:]):
        if t <= t1:
            u = eio((t - t0) / max(1e-6, t1 - t0))
            return tuple(lerp(x, y, u) for x, y in zip(a, b))
    return ks[-1][1]


def shake(t, amp=3.0, f=17.0):
    return (amp * math.sin(t * f), amp * 0.7 * math.cos(t * f * 1.3))


# ------------------------------------------------------------------ UI (screen space, inside the portrait window)
def pill(txt, x, y, u=1.0, size=26, col="#FFFFFF", bg=INK, edge=PINK, sub=None, w=None):
    if u <= 0:
        return ""
    k = 0.7 + 0.3 * eo(u) + 0.1 * math.sin(math.pi * clamp(u * 1.4))
    ww = w or (max(len(txt) * size * 0.58, len(sub) * size * 0.36 if sub else 0) + 40)
    hh = size * 1.75 + (size * 0.75 if sub else 0)
    o = (f'<rect x="{-ww / 2:.0f}" y="{-hh / 2:.0f}" width="{ww:.0f}" height="{hh:.0f}" rx="{hh / 2.6:.0f}" fill="{bg}" opacity="0.9"/>'
         f'<rect x="{-ww / 2:.0f}" y="{-hh / 2:.0f}" width="{ww:.0f}" height="{hh:.0f}" rx="{hh / 2.6:.0f}" fill="none" stroke="{edge}" stroke-width="2.5"/>')
    if sub:
        o += text(0, -hh / 2 + size * 1.3, txt, size, col, 700, "middle") + text(0, -hh / 2 + size * 2.25, sub, size * 0.58, edge, 600, "middle")
    else:
        o += text(0, size * 0.36, txt, size, col, 700, "middle")
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})" opacity="{clamp(u * 3):.2f}">{o}</g>'


def big_num(txt, x, y, u=1.0, size=40, col=GOLD, sub=None, subcol="#FFFFFF"):
    if u <= 0:
        return ""
    k = 0.6 + 0.4 * eo(u) + 0.14 * math.sin(math.pi * clamp(u * 1.3))
    o = (f'<text x="0" y="0" text-anchor="middle" font-family="Fredoka" font-weight="700" font-size="{size}" fill="{col}" stroke="{INK}" '
         f'stroke-width="{size / 7:.1f}" paint-order="stroke" stroke-linejoin="round">{txt}</text>')
    if sub:
        o += (f'<text x="0" y="{size * 0.75:.0f}" text-anchor="middle" font-family="Fredoka" font-weight="700" font-size="{size * 0.42:.0f}" fill="{subcol}" stroke="{INK}" '
              f'stroke-width="{size / 14:.1f}" paint-order="stroke">{sub}</text>')
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})" opacity="{clamp(u * 3):.2f}">{o}</g>'


def fmt_int(v):
    return f"{int(round(v)):,}"


def roll_count(t, t0, t1, a, b, ease=eo):
    u = ease(ramp(t, t0, t1))
    return a + (b - a) * u


def fade(t, t0, t1, col="#05030F", rev=False):
    u = ramp(t, t0, t1)
    if rev:
        u = 1 - u
    if u <= 0:
        return ""
    return f'<rect x="-200" y="-200" width="1360" height="1000" fill="{col}" opacity="{u:.3f}"/>'


def flash(t, t0, dur=0.22, col="#FFFFFF"):
    u = 1 - ramp(t, t0, t0 + dur) if t >= t0 else 0
    return f'<rect x="-200" y="-200" width="1360" height="1000" fill="{col}" opacity="{0.8 * u:.2f}"/>' if u > 0 else ""


# ------------------------------------------------------------------ the mosquito
def mosq(x, y, s=1.0, t=0.0, rot=0.0, flip=False, male=False, full=0.0, land=False, red_eye=0.0, seed=0, flap=1.0, shadow=None):
    """Side view, facing right. Body ~100 units long at s=1. full 0..1 swells the abdomen with blood; land splays the legs down."""
    r = random.Random(seed)
    ph = t * 38 + seed * 1.7
    o = []
    # legs (6), banded
    hips = [(18, 4), (22, 5), (26, 4)]
    for k, (hx, hy) in enumerate(hips):
        if land:
            kx, ky = hx + (-20, 4, 26)[k], hy + 26 + 3 * math.sin(t * 2 + k)
            fx_, fy = hx + (-46, -2, 50)[k], 44
        else:
            sw = 3 * math.sin(t * 3 + k + seed)
            kx, ky = hx - 10 - 8 * k, hy + 18 + sw
            fx_, fy = hx - 34 - 14 * k, hy + 40 + sw
        d = f"M{hx} {hy} L{kx:.1f} {ky:.1f} L{fx_:.1f} {fy:.1f}"
        o.append(f'<path d="{d}" stroke="#241C2C" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        o.append(f'<path d="{d}" stroke="#F4F0FF" stroke-width="2.4" fill="none" stroke-dasharray="2 7" opacity="0.8"/>')
    # abdomen: tapered, banded; swells and reddens when fed
    sw_ = 1 + 0.9 * full
    ab = f"M10 -2 Q-10 {-8 * sw_:.1f} -50 {2 - 2 * full:.1f} Q-54 {6 + 2 * full:.1f} -48 {9 + 3 * full:.1f} Q-10 {12 + 10 * full:.1f} 10 8 Z"
    o.append(f'<path d="{ab}" fill="{mixc("#2E2634", "#C8202E", full)}"/>')
    if full > 0.05:
        o.append(f'<path d="{ab}" fill="#FF5A5A" opacity="{0.35 * full:.2f}" transform="translate(-2 -2) scale(0.92)"/>')
    for k in range(5):
        bx = 2 - k * 10
        o.append(f'<path d="M{bx} {-6 * sw_ + k * 0.5:.1f} Q{bx - 2} 2 {bx} {9 + 8 * full:.1f}" stroke="#F4F0FF" stroke-width="2" fill="none" opacity="{0.75 * (1 - 0.6 * full):.2f}"/>')
    # thorax (hump) with scale pattern
    o.append('<ellipse cx="22" cy="-3" rx="15" ry="12" fill="#3A3044"/><path d="M14 -12 Q22 -18 30 -10" stroke="#F4F0FF" stroke-width="2.4" fill="none" opacity="0.85"/>'
             '<path d="M20 -8 L22 4" stroke="#F4F0FF" stroke-width="1.6" opacity="0.6"/>')
    # wings: flapping fan
    fl = math.sin(ph) * flap
    for wk, dy in ((0, 0), (1, 3)):
        a = -150 + 26 * fl + wk * 10
        o.append(f'<g transform="translate(20 -12) rotate({a:.1f})"><ellipse cx="30" cy="0" rx="32" ry="7" fill="#DFF2FF" opacity="0.38"/>'
                 f'<path d="M0 0 L58 0" stroke="#B8D8F0" stroke-width="1" opacity="0.6"/></g>')
    if flap > 0.3:
        o.append(f'<path d="M20 -12 L-36 -46 Q-20 -30 -40 -8 Z" fill="#DFF2FF" opacity="{0.12 * flap:.2f}"/>')
    # head, eye, proboscis, palps, antennae
    o.append('<circle cx="40" cy="2" r="8" fill="#2A2232"/>')
    o.append(f'<circle cx="42" cy="0" r="6" fill="{mixc("#120C18", "#E8202E", red_eye)}"/><circle cx="44" cy="-2" r="1.8" fill="#FFFFFF" opacity="0.9"/>')
    if red_eye > 0:
        o.append(f'<circle cx="42" cy="0" r="12" fill="url(#eyeR)" opacity="{0.6 * red_eye:.2f}"/>')
    o.append('<path d="M46 6 L84 22" stroke="#1C1420" stroke-width="2.2" stroke-linecap="round"/><path d="M46 5 L62 12" stroke="#F4F0FF" stroke-width="1.4" opacity="0.7"/>')
    if male:
        o.append('<path d="M44 -4 Q58 -20 66 -30" stroke="#2A2232" stroke-width="1.6" fill="none"/>')
        for k in range(9):
            u = k / 8; ax, ay = 44 + 22 * u, -4 - 26 * u
            o.append(f'<path d="M{ax - 6:.1f} {ay - 4:.1f} L{ax + 6:.1f} {ay + 4:.1f} M{ax - 5:.1f} {ay + 5:.1f} L{ax + 5:.1f} {ay - 5:.1f}" stroke="#4A3E54" stroke-width="1.2" opacity="0.8"/>')
    else:
        o.append('<path d="M44 -4 Q56 -16 70 -18" stroke="#2A2232" stroke-width="1.4" fill="none"/><path d="M44 -2 Q58 -8 72 -6" stroke="#2A2232" stroke-width="1.2" fill="none"/>')
    body = "".join(o)
    sx = -s if flip else s
    sh = ""
    if shadow is not None:
        sh = f'<ellipse cx="{x:.1f}" cy="{shadow:.1f}" rx="{40 * s:.1f}" ry="{6 * s:.1f}" fill="#05030F" opacity="0.25"/>'
    return sh + f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx:.4f} {s:.4f})">{body}</g>'


def speck(x, y, s, t, seed, col="#0E0812", op=1.0):
    """A far mosquito: dark body, two flicking wing strokes, dangling legs."""
    w = math.sin(t * 40 + seed)
    a = 20 + 25 * w
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.2f})" opacity="{op:.2f}"><ellipse cx="0" cy="0" rx="3.4" ry="1.0" fill="{col}"/>'
            f'<path d="M0 -0.5 l{-3 * math.cos(math.radians(a)):.2f} {-3 * math.sin(math.radians(a)):.2f} M0.6 -0.5 l{-2.4 * math.cos(math.radians(a + 25)):.2f} {-3 * math.sin(math.radians(a + 25)):.2f}" stroke="#B8C8E0" stroke-width="0.7" opacity="0.7"/>'
            f'<path d="M-0.5 0.6 l-2 2.6 M0.6 0.6 l-0.6 3 M1.4 0.4 l1.4 2.4" stroke="{col}" stroke-width="0.45"/></g>')


def swarm(cx, cy, rx, ry, n, t, seed=1, s=1.0, col="#140C18", drift=(0, 0), op=1.0, swirl=1.0):
    r = random.Random(seed)
    o = []
    for i in range(n):
        a = r.random() * TAU; d = math.sqrt(r.random())
        sp = r.uniform(0.6, 1.6) * swirl
        px = cx + rx * d * math.cos(a + t * 0.25 * sp) + 6 * math.sin(t * 5 * sp + i) + drift[0] * t
        py = cy + ry * d * math.sin(a + t * 0.25 * sp) + 5 * math.cos(t * 6.3 * sp + i * 0.7) + drift[1] * t
        o.append(speck(px, py, s * r.uniform(0.7, 1.3), t, i + seed, col, op))
    return "".join(o)


def cloud_mass(cx, cy, rx, ry, t, seed=3, col="#0E0816", op=0.95, blur=8):
    """A dense far swarm reading as a dark, writhing cloud."""
    o = [f'<g filter="url(#b{blur})" opacity="{op:.2f}">']
    r = random.Random(seed)
    for k in range(9):
        a = r.random() * TAU; d = r.uniform(0.0, 0.55)
        d_ = blob(cx + rx * d * math.cos(a), cy + ry * d * math.sin(a), min(rx, ry) * r.uniform(0.55, 0.85), seed + k, 0.28, 11, t * 0.6, 0.12, rx / min(rx, ry), ry / min(rx, ry))
        o.append(f'<path d="{d_}" fill="{col}"/>')
    o.append("</g>")
    return "".join(o)


# ------------------------------------------------------------------ world: dusk backyard
HOUSE_X = 470
GROUND = 430


def dusk_sky(dark=0.0, t=0.0, sun=True):
    o = ['<rect x="-400" y="-400" width="1760" height="1400" fill="url(#duskSky)"/>']
    if sun:
        o.append(f'<circle cx="560" cy="300" r="120" fill="url(#sunG)" opacity="{1 - 0.8 * dark:.2f}"/><circle cx="560" cy="300" r="34" fill="#FFF0C0" opacity="{1 - 0.9 * dark:.2f}"/>')
    for k, (x, y, w) in enumerate(((360, 60, 90), (600, 20, 120), (420, 160, 70), (700, 120, 100))):
        o.append(f'<ellipse cx="{x + 6 * math.sin(t * 0.2 + k)}" cy="{y}" rx="{w}" ry="{w * 0.18}" fill="#FFB0A0" opacity="{0.35 * (1 - dark):.2f}"/>')
    if dark > 0:
        o.append(f'<rect x="-400" y="-400" width="1760" height="1400" fill="#0A0418" opacity="{0.82 * dark:.2f}"/>')
    return "".join(o)


def far_roofs(y=300, col="#3A1A4A", seed=4, x0=200, x1=760):
    r = random.Random(seed); o = []
    x = x0
    while x < x1:
        w = r.uniform(50, 90); h = r.uniform(30, 60)
        o.append(f'<path d="M{x:.0f} {y} L{x:.0f} {y - h:.0f} L{x + w / 2:.0f} {y - h - 26:.0f} L{x + w:.0f} {y - h:.0f} L{x + w:.0f} {y} Z" fill="{col}"/>')
        if r.random() < 0.6:
            o.append(f'<rect x="{x + w * 0.3:.0f}" y="{y - h * 0.6:.0f}" width="9" height="11" fill="#FFD890" opacity="0.8"/>')
        if r.random() < 0.4:
            tx = x + w + 6
            o.append(f'<ellipse cx="{tx:.0f}" cy="{y - 40:.0f}" rx="22" ry="34" fill="#2A1238"/><rect x="{tx - 3:.0f}" y="{y - 12:.0f}" width="6" height="14" fill="#2A1238"/>')
        x += w + r.uniform(4, 30)
    return "".join(o)


def fence(y, x0=200, x1=760, col="#C8946A", dark=0.0):
    c = mixc(col, "#3A2430", dark)
    o = [f'<rect x="{x0}" y="{y - 60}" width="{x1 - x0}" height="8" fill="{c}"/><rect x="{x0}" y="{y - 30}" width="{x1 - x0}" height="8" fill="{c}"/>']
    for x in range(x0, x1, 22):
        o.append(f'<path d="M{x} {y} L{x} {y - 74} L{x + 9} {y - 82} L{x + 18} {y - 74} L{x + 18} {y} Z" fill="{c}" stroke="{mixc("#8A5A3A", "#1A1018", dark)}" stroke-width="1.2"/>')
    return "".join(o)


def house(x, y, s=1.0, dark=0.0, lit_=1.0):
    o = []
    o.append(f'<rect x="-120" y="-150" width="240" height="150" fill="url(#wallH)"/><path d="M-140 -150 L0 -240 L140 -150 Z" fill="url(#roofH)"/>')
    o.append('<rect x="-30" y="-90" width="60" height="90" rx="4" fill="#6A3A4A"/><circle cx="18" cy="-44" r="3" fill="#FFD890"/>')
    for wx in (-90, 50):
        o.append(f'<rect x="{wx}" y="-120" width="44" height="40" rx="3" fill="#FFD890" opacity="{0.4 + 0.6 * lit_:.2f}"/><rect x="{wx + 20}" y="-120" width="4" height="40" fill="#C89A7A"/>')
    o.append('<rect x="60" y="-226" width="22" height="50" fill="#8A4A5A"/>')
    if dark > 0:
        o.append(f'<rect x="-145" y="-245" width="290" height="250" fill="#0A0418" opacity="{0.55 * dark:.2f}"/>')
        for wx in (-90, 50):
            o.append(f'<rect x="{wx}" y="-120" width="44" height="40" rx="3" fill="#FFD890" opacity="{0.7 * lit_ * dark:.2f}"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{"".join(o)}</g>'


def lawn(y=GROUND, dark=0.0):
    return (f'<rect x="-400" y="{y}" width="1760" height="700" fill="url(#lawn)"/>'
            + (f'<rect x="-400" y="{y}" width="1760" height="700" fill="url(#lawnDark)" opacity="{dark:.2f}"/>' if dark > 0 else ""))


def grass_tufts(y, x0=280, x1=680, seed=7, col="#2E7A3E", n=26, dark=0.0):
    r = random.Random(seed); c = mixc(col, "#14281E", dark); o = []
    for i in range(n):
        x = r.uniform(x0, x1); yy = y + r.uniform(4, 140); h = r.uniform(6, 14)
        o.append(f'<path d="M{x - 4:.0f} {yy:.0f} Q{x - 2:.0f} {yy - h:.0f} {x:.0f} {yy - h - 3:.0f} Q{x + 1:.0f} {yy - h:.0f} {x + 4:.0f} {yy:.0f} Z" fill="{c}"/>')
    return "".join(o)


def pool(x, y, w=300, h=70, t=0.0, dark=0.0, specks=0.0, seed=5):
    """Pool seen from the side-ish (low ellipse-ish rounded rect); specks 0..1 = mosquitoes resting on the surface."""
    o = [f'<rect x="{x - w / 2 - 10}" y="{y - 8}" width="{w + 20}" height="{h + 16}" rx="16" fill="#E8E0D4"/>',
         f'<rect x="{x - w / 2}" y="{y}" width="{w}" height="{h}" rx="12" fill="url(#water)"/>']
    o.append(waves(x - w / 2 + 10, x + w / 2 - 10, y + 14, t, 2, 40, 30, "#FFFFFF", 0.4 * (1 - dark), 1.4, seed, 3, 16, 0.3))
    if dark > 0:
        o.append(f'<rect x="{x - w / 2}" y="{y}" width="{w}" height="{h}" rx="12" fill="#06142A" opacity="{0.55 * dark:.2f}"/>')
    if specks > 0:
        r = random.Random(seed)
        for i in range(int(160 * specks)):
            px = r.uniform(x - w / 2 + 8, x + w / 2 - 8); py = r.uniform(y + 4, y + h - 4)
            o.append(speck(px, py, 1.3, t, i, "#140C18", 0.95))
    return "".join(o)


def lounger(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M-80 -20 L40 -20 L80 -70" stroke="#FFFFFF" stroke-width="10" fill="none" stroke-linecap="round"/>'
            '<path d="M-80 -20 L40 -20 L80 -70" stroke="#5AC8E8" stroke-width="6" fill="none" stroke-linecap="round"/>'
            '<path d="M-70 -20 L-74 0 M30 -20 L34 0" stroke="#C8C0D0" stroke-width="5" stroke-linecap="round"/></g>')


def string_lights(x0, x1, y, sag=24, t=0.0, on=1.0):
    o = [f'<path d="M{x0} {y} Q{(x0 + x1) / 2} {y + sag * 2} {x1} {y}" stroke="#2A1A30" stroke-width="1.6" fill="none"/>']
    for k in range(1, 9):
        u = k / 9; bx = x0 + (x1 - x0) * u; by = y + sag * 2 * 2 * u * (1 - u)
        o.append(f'<circle cx="{bx:.0f}" cy="{by + 5:.0f}" r="4" fill="#FFE0A0" opacity="{0.5 + 0.5 * on:.2f}"/>' + glow(bx, by + 5, 10, "#FFD890", 0.5 * on, 4))
    return "".join(o)


def backyard(t=0.0, dark=0.0, pool_specks=0.0, sun=True, roofs=True):
    """The locked backyard: sky, far roofs, fence at y 360, house left-back, lawn from 430, pool right-front."""
    o = [dusk_sky(dark, t, sun)]
    if roofs:
        o.append(far_roofs(330, mixc("#3A1A4A", "#120818", dark)))
    o.append(fence(372, dark=dark))
    o.append(house(380, 372, 0.9, dark))
    o.append(lawn(372, dark))
    o.append(string_lights(300, 660, 250, 18, t, 1.0))
    o.append(grass_tufts(372, dark=dark))
    return "".join(o)


def soda_can(x, y, s=1.0, level=0.0, t=0.0):
    """Generic red soda can, see-through window showing the blood level (0..1)."""
    o = ['<rect x="-40" y="-120" width="80" height="140" rx="10" fill="url(#can)"/>',
         '<ellipse cx="0" cy="-120" rx="40" ry="8" fill="#C8CCD8"/><ellipse cx="0" cy="-121" rx="30" ry="5" fill="#9AA0B0"/>',
         '<rect x="-12" y="-125" width="24" height="6" rx="3" fill="#E8ECF4"/>',
         '<ellipse cx="0" cy="20" rx="40" ry="8" fill="#9AA0B0"/>']
    # glass window
    o.append('<rect x="-26" y="-100" width="52" height="108" rx="8" fill="#FFF5E4" opacity="0.9"/>')
    lv = 104 * clamp(level)
    if lv > 0:
        o.append(f'<rect x="-24" y="{6 - lv:.1f}" width="48" height="{lv:.1f}" rx="6" fill="url(#blood)"/>'
                 f'<path d="M-24 {6 - lv:.1f} Q-12 {2 - lv + 2 * math.sin(t * 6):.1f} 0 {6 - lv:.1f} Q12 {10 - lv - 2 * math.sin(t * 6):.1f} 24 {6 - lv:.1f}" stroke="#FF8A8A" stroke-width="2" fill="none"/>')
    for k in range(1, 3):
        yy = 6 - 104 * k / 3
        o.append(f'<path d="M-26 {yy:.1f} L-16 {yy:.1f}" stroke="#7A0E1A" stroke-width="2"/>')
    o.append(text(0, 40, "SODA", 18, "#FFFFFF", 700, "middle") if False else "")
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{"".join(o)}</g>'


def drop(x, y, s=1.0, col="#E8283A"):
    return f'<path transform="translate({x} {y}) scale({s})" d="M0 -16 Q10 -2 10 4 A10 10 0 0 1 -10 4 Q-10 -2 0 -16 Z" fill="{col}" stroke="{INK}" stroke-width="2"/>'


def blood_meter(x, y, frac, u=1.0, h=170):
    """Vertical meter: body silhouette-free bar with a drop on top; frac 1 = full blood."""
    if u <= 0:
        return ""
    col = mixc("#E8283A", "#8A6A7A", 1 - frac) if frac < 0.6 else "#E8283A"
    o = [f'<rect x="-16" y="0" width="32" height="{h}" rx="16" fill="{INK}" opacity="0.88"/><rect x="-16" y="0" width="32" height="{h}" rx="16" fill="none" stroke="{PINK}" stroke-width="2.5"/>',
         f'<rect x="-10" y="{6 + (h - 12) * (1 - frac):.1f}" width="20" height="{(h - 12) * frac:.1f}" rx="10" fill="{col}"/>',
         drop(0, -16, 1.1)]
    return f'<g transform="translate({x} {y})" opacity="{clamp(u * 3):.2f}">{"".join(o)}</g>'


def vig(op=0.55):
    return f'<rect x="-200" y="-200" width="1360" height="1000" fill="url(#vigD)" opacity="{op}"/>'
