"""Week-1 Shorts core. Portrait window x 300..660, y -50..590 (centre 480, 270). Captions later sit y 380..440,
Instagram UI covers y > 465 and the top band y < 30: keep faces and key action inside y 40..380.
Reuses the show's boy (rig3), lights, FX, mosquito and sets (mosq/mcore, mprops, ep3/core3)."""
import os, sys, json, math, random, re
sys.path[:0] = ["/home/claude/w1", "/home/claude/sneeze", "/home/claude/ep3", "/home/claude/mosq", "/home/claude/ep2x", "/home/claude/ep", "/home/claude/bible"]
import core3 as C3
from core3 import couch, kitchen, living_room, box_fan, EXTRA_DEFS, LI, LIC, FLOOR_L, chip, label, leader
from mprops import *
import mprops as MP

SHORT = os.environ.get("SHORT", "botfly")
DW = f"/home/claude/w1/{SHORT}"
_L = json.load(open(f"{DW}/lines.json"))
LINES = _L["lines"]; TEND = _L["total"]
PH = {int(k): v for k, v in json.load(open(f"{DW}/phrases.json")).items()}


def Ln(i):
    return LINES[i]["start"]


def LEn(i):
    return LINES[i]["end"]


def Pn(i, k):
    ph = PH[i]
    return ph[min(k, len(ph) - 1)]["t"]


CX, CY = 480, 270
W_DEFS = EXTRA_DEFS + (lin("skinG", [(0, "#F2C2A2"), (1, "#E0A486")]) + lin("dermis", [(0, "#F0A08E"), (1, "#C86A62")])
                       + lin("jungle", [(0, "#0E3A2A"), (1, "#05180F")]) + lin("bacon", [(0, "#C8402E"), (1, "#8A2418")])
                       + rad("pocketG", [(0, "#FFD8C0", 1), (1, "#C8504A", 0)]) + lin("xskin", [(0, "#0A1E46"), (1, "#05102A")]))


def SV(layers, cam=(0, 0, 1.0), defs="", overlay="", lights=()):
    named = [(f"L{k}", l[1], l[0], l[2] if len(l) > 2 else False, l[3] if len(l) > 3 else None) for k, l in enumerate(layers)]
    return dict(layers=named, defs=MP.BASE_DEFS + W_DEFS + light_defs(*lights) + defs, cam=cam, overlay=overlay, clock=False, pad=(260, 160))


def ui(svg):
    return (svg, 0.0, False)


def cam_orbit(t, D, cx, cy, z0, z1, ang0=-8, ang1=8):
    """Fake 2D orbit: the camera drifts sideways and rolls a little while pushing in (pair with a parallax background)."""
    u = eio(ramp(t, 0, D))
    return (cx - CX + lerp(-60, 60, u), cy - CY, lerp(z0, z1, u), lerp(ang0, ang1, u))


def whip(t, t0, d=0.22):
    """0..1..0 blur strength around a whip pan at t0 (use as an overlay smear)."""
    return clamp(1 - abs(t - t0) / d)


def smear(u, col="#FFFFFF"):
    if u <= 0:
        return ""
    return "".join(f'<path d="M200 {40 + 30 * k} L760 {40 + 30 * k + 10}" stroke="{col}" stroke-width="{6 + 4 * (k % 3)}" opacity="{0.08 * u * (1 + k % 2):.2f}" filter="url(#b8)"/>' for k in range(20))


def tag_big(txt, x, y, u, size=58, col="#FFFFFF", edge=INK):
    """Short punchy word on screen (max 2-3 words), Fredoka with a thick outline."""
    if u <= 0:
        return ""
    k = 0.6 + 0.4 * eo(min(1, u * 1.6)) + 0.08 * math.sin(math.pi * clamp(u * 1.6))
    o = text(0, 0, txt, size, col, 700, "middle").replace("<text ", f'<text stroke="{edge}" stroke-width="{size / 5:.1f}" paint-order="stroke" stroke-linejoin="round" ')
    return f'<g transform="translate({x} {y}) scale({k:.3f})" opacity="{clamp(u * 3):.2f}">{o}</g>'


# ------------------------------------------------------------------ the boy
def boy(J, uid, x, y, s, Lt, side=False, flip=False, backv=False):
    return you(J, uid, x, y, s, Lt, side=side, flip=flip, backv=backv)
