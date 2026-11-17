"""Modern adults on the same rig as the boy (rig3): identical construction, outlines, shading, faces and hands, so
they belong to the same show. Taller (h ~1.3), own outfits, hairstyles, skin tones, optional beard and glasses."""
import math, sys
sys.path[:0] = ["/home/claude/ep2x", "/home/claude/ep", "/home/claude/bible"]
import rig3 as R3
from kit import P as KP, E as KE
from scene_people import Person
from pose2 import *
from lite import lit


def mk(skin, hair, top, bottom, shoe, style="short", h=1.3, beard=False, glasses=False):
    p = Person(name="adult", skin=skin, hair=hair, hairstyle="bob", glasses=glasses, top=top, top_style="sweater", bottom=bottom, shoe=shoe, accent=None)
    p.style, p.h, p.beard = style, h, beard
    return p


SKINS = [("#E8B896", "#C8946E", "#FFDCC0"), ("#8A5A3A", "#6A4228", "#B07A54"), ("#C98B62", "#A86E48", "#F0B890"), ("#5A3A28", "#40281A", "#7A5440"), ("#F2C8A8", "#D8A080", "#FFE6D0")]
DARKH, BROWN, BLOND, GREY = ("#1A1210", "#0E0A08", "#4A3A3A"), ("#5A3A2A", "#3A2418", "#8A6046"), ("#D8A850", "#B0843A", "#F4D488"), ("#B8B0A8", "#8A847C", "#E8E4E0")

ADULTS = [
    mk(SKINS[0], BROWN, ("#3A6AC8", "#2A50A0", "#9AC0FF"), ("#2A2A3A", "#1A1A28", "#5A5A70"), ("#2A2A2A", "#141414"), "short", 1.3),
    mk(SKINS[1], DARKH, ("#C83A5A", "#9A2A44", "#FF9AB0"), ("#2A2A2A", "#1A1A1A", "#5A5A5A"), ("#3A2A2A", "#1A1414"), "curly", 1.32, beard=True),
    mk(SKINS[4], BLOND, ("#7AB86A", "#5A9A4E", "#C8F0B8"), ("#3A4A6A", "#2A3650", "#6A80A8"), ("#3A2A2A", "#1A1414"), "long", 1.26),
    mk(SKINS[3], DARKH, ("#E8A03A", "#C07A20", "#FFD890"), ("#4A3A5A", "#342844", "#7A6A8A"), ("#2A1A1A", "#141010"), "bun", 1.28, glasses=True),
    mk(SKINS[2], GREY, ("#E8E0D4", "#C0B8AC", "#FFFFFF"), ("#5A5A6A", "#40404E", "#8A8A9A"), ("#2A2A2A", "#141414"), "short", 1.3, beard=True),
]
ATTENDANT = mk(SKINS[0], DARKH, ("#1A3A7A", "#122A5A", "#5A7AC8"), ("#1A2A4A", "#121E36", "#4A5A7A"), ("#14101C", "#0A0810"), "bun", 1.3)


def _hair_over_front(p):
    hr = p.hair
    if p.style == "curly":
        return "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{hr[0]}"/>' for x, y, r in ((-46, -50, 26), (-20, -74, 28), (14, -78, 28), (44, -56, 26), (-56, -22, 18), (58, -26, 18)))
    if p.style == "short":
        return R3.rim(KP("M -56 -16 Q -60 -84 0 -86 Q 60 -84 56 -16 Q 44 -50 0 -54 Q -44 -50 -56 -16 Z"), *hr, 4)
    if p.style == "long":
        return R3.rim(KP("M -60 -6 Q -66 -86 0 -90 Q 66 -86 60 -6 Q 48 -50 4 -54 Q -40 -54 -60 -6 Z"), *hr, 5)
    if p.style == "bun":
        return R3.rim(KE(0, -98, 24, 20), *hr, 4) + R3.rim(KP("M -56 -12 Q -60 -82 0 -86 Q 60 -82 56 -12 Q 40 -48 0 -52 Q -40 -48 -56 -12 Z"), *hr, 5)
    return ""


def _hair_back_front(p):
    if p.style == "long":
        return R3.rim(KP("M -64 -10 Q -76 -84 0 -90 Q 76 -84 64 -10 L 70 90 Q 0 110 -70 90 Z"), *p.hair, 6)
    return ""


def _hair_over_side(p):
    hr = p.hair
    if p.style == "curly":
        return "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{hr[0]}"/>' for x, y, r in ((-40, -40, 26), (-10, -70, 28), (24, -70, 24), (-50, -6, 20)))
    if p.style == "short":
        return R3.rim(KP("M -48 2 Q -52 -72 10 -78 Q 58 -72 56 -30 Q 32 -50 2 -48 Q -30 -40 -48 2 Z"), *hr, 4)
    if p.style == "long":
        return R3.rim(KP("M -66 70 Q -80 -70 6 -80 Q 56 -76 54 -36 Q 30 -56 -2 -50 Q -30 -40 -32 70 Z"), *hr, 5)
    if p.style == "bun":
        return R3.rim(KE(-44, -60, 22, 20), *hr, 4) + R3.rim(KP("M -50 4 Q -56 -72 8 -78 Q 58 -72 56 -26 Q 32 -48 2 -46 Q -30 -38 -50 4 Z"), *hr, 4)
    return ""


def _glasses_front():
    return '<g fill="none" stroke="#14101C" stroke-width="3.5"><circle cx="-20" cy="2" r="13"/><circle cx="20" cy="2" r="13"/><path d="M-7 2 L7 2"/></g>'


def _beard_front(p):
    return R3.rim(KP("M -44 10 Q -40 60 0 66 Q 40 60 44 10 Q 30 40 0 44 Q -30 40 -44 10 Z"), *p.hair, 4) if p.beard else ""


def adult_front(J, p):
    J = dict(R3.FRONT) | J
    hx, hy = J["hip"]; hdx, hdy, tilt = J["head"]
    tf = f'translate({hx:.1f} {hy:.1f}) rotate({J["lean"]:.2f} 0 -200) translate({hdx:.1f} {-438 + hdy + 12 * J["shr"]:.1f}) rotate({tilt:.2f})'
    body = R3.front(J, p)
    over = _hair_over_front(p) + _beard_front(p) + (_glasses_front() if p.glasses else "")
    return f'<g transform="scale({p.h:.3f})"><g transform="{tf}">{_hair_back_front(p)}</g>{body}<g transform="{tf}">{over}</g></g>'


def adult_side(J, p):
    J = dict(R3.SIDE) | J
    hx, hy = J["hip"]; hdx, hdy, tilt = J["head"]
    tf = f'translate({hx:.1f} {hy:.1f}) rotate({J["lean"]:.2f} 0 -200) translate({4 + hdx:.1f} {-438 + hdy + 12 * J["shr"]:.1f}) rotate({tilt:.2f})'
    body = R3.side(J, p)
    beard = R3.rim(KP("M 20 20 Q 30 60 56 50 Q 60 30 54 16 Z"), *p.hair, 3) if p.beard else ""
    gl = '<g fill="none" stroke="#14101C" stroke-width="3.5"><circle cx="36" cy="2" r="12"/><path d="M24 2 L-6 -2"/></g>' if p.glasses else ""
    return f'<g transform="scale({p.h:.3f})">{body}<g transform="{tf}">{_hair_over_side(p)}{beard}{gl}</g></g>'


def adult(J, p, uid, x, y, s, Lt, side=False, flip=False):
    body = adult_side(J, p) if side else adult_front(J, p)
    return lit(body, uid, x, y, s, Lt, flip=flip, box=(-260, -700, 520, 740))
