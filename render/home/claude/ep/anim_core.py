"""v5 animation core: beats with absolute start times (from the approved voice track, lines5/phrases5),
registered into the shot engine so each beat renders as its own clip. Locked kitchen layout lives here."""
import os, sys, math, random, json
sys.path.insert(0, "/home/claude/ep")
from board_props import *          # board_core + props (kitchen, mug, plate, ...)
import rig3 as R3
from rig3 import keys, mix, smooth, fc, ov

ANIM = []        # dict(name, t, fn)


def shot5(t0, name, desc=""):
    def deco(fn):
        ANIM[:] = [a for a in ANIM if a["name"] != name]      # a later definition replaces an earlier one
        ANIM.append(dict(name=name, t=t0, fn=fn, desc=desc))
        return fn
    return deco


def finalize(t_end):
    ANIM.sort(key=lambda a: a["t"])
    for a, b in zip(ANIM, ANIM[1:] + [dict(t=t_end)]):
        a["dur"] = (round(b["t"] * 30) - round(a["t"] * 30)) / 30.0
    for a in ANIM:
        engine.SHOTS[a["name"]] = (lambda fn: (lambda t, D, c: fn(t, D)))(a["fn"])
        engine.TL[a["name"]] = dict(name=a["name"], start=a["t"], dur=a["dur"], cues=[])
    return ANIM


def ramp(t, a, b):
    return max(0.0, min(1.0, (t - a) / max(1e-6, b - a)))


def eo(u):
    u = max(0.0, min(1.0, u)); return 1 - (1 - u) ** 3


def ei(u):
    u = max(0.0, min(1.0, u)); return u ** 3


def lerp(a, b, u):
    return a + (b - a) * u


def S_(svg, depth=1.0, static=False, blur=None, lid=None):
    return (lid or f"l{random.random():.6f}"[2:], depth, svg, static, blur)


def shot(layers, cam=(0, 0, 1.0), defs="", overlay="", pad=(260, 160)):
    named = []
    for k, l in enumerate(layers):
        named.append((f"L{k}",) + tuple(l[1:]))
    return dict(layers=named, defs=PROP_DEFS + KDEFS + defs, cam=cam, overlay=overlay, clock=False, pad=pad)


def haze(col="#4A2A9A", op=0.3):
    return f'<rect x="-900" y="-900" width="2760" height="2340" fill="{col}" opacity="{op}"/>'


def shake_free(*a):
    return 0.0


# ------------------------------------------------------------------ survival clock (story time, not playback time)
def survival(val, x=128, y=58, s=1.0, pop=1.0):
    k = s * (0.6 + 0.4 * eo(pop)) if pop < 1 else s
    body = (f'<rect x="-118" y="-36" width="236" height="74" rx="18" fill="#140A3A" opacity="0.9"/>'
            f'<rect x="-118" y="-36" width="236" height="74" rx="18" fill="none" stroke="#FF4F9A" stroke-width="3"/>'
            + text(0, -14, "SURVIVAL TIME", 13, "#FFB0D0", 700, "middle") + text(0, 22, val, 30, "#FFFFFF", 700, "middle"))
    return at(x, y, k, body)


def xmark(t, t0, x=880, y=70):
    """Brief, consistent elimination mark in the top-right corner (never over the action)."""
    if t < t0:
        return ""
    u = ramp(t, t0, t0 + 0.18)
    k = 0.45 * (0.6 + 0.4 * eo(u)) * (1 + 0.15 * math.sin(math.pi * u))
    return at(x, y, k, '<circle r="62" fill="#FF3D6E"/><circle r="62" fill="none" stroke="#FFFFFF" stroke-width="7"/>'
                       '<path d="M-26 -26 L26 26 M26 -26 L-26 26" stroke="#FFFFFF" stroke-width="14" stroke-linecap="round"/>', -10)


# ------------------------------------------------------------------ LOCKED KITCHEN LAYOUT (human scale, side-on, camera faces the wall)
TABLE_TOP = 420          # tabletop surface line
TABLE_X0, TABLE_X1 = 150, 1150
SEAT_X = 520             # where you sit, on the front edge
MUG_X = 600              # where the mug is set down (to your right)
PLATE_X = 840            # plate with toast (further right)
S0 = 0.55                # your normal scale in the wide
MUG_S = 0.125            # true-scale mug relative to you
CRUMBS = [(458, 0.9), (476, 1.3), (566, 1.0), (548, 0.7), (700, 1.2), (728, 0.8)]   # x, size on the tabletop


def kitchen_back():
    """Background room: crisp simple shapes, pushed back with scale + haze, not blur."""
    return (f'<g transform="translate(480 300) scale(0.86) translate(-480 -300)">{kitchen_room()}</g>'
            + haze("#3A1A86", 0.22) + '<rect x="-900" y="540" width="2760" height="600" fill="#2A1470"/>')


def table_front(top=TABLE_TOP):
    o = []
    for x in (TABLE_X0 + 40, TABLE_X1 - 70):
        o.append(f'<rect x="{x}" y="{top}" width="26" height="400" rx="6" fill="#A85E30"/><rect x="{x}" y="{top}" width="8" height="400" fill="#C47640"/>')
    o.append(f'<rect x="{TABLE_X0}" y="{top - 3}" width="{TABLE_X1 - TABLE_X0}" height="26" rx="8" fill="url(#wood)"/>')
    o.append(f'<rect x="{TABLE_X0}" y="{top - 3}" width="{TABLE_X1 - TABLE_X0}" height="4" rx="2" fill="#FFD6A8"/>')
    o.append(f'<rect x="{TABLE_X0}" y="{top + 17}" width="{TABLE_X1 - TABLE_X0}" height="6" fill="#8A4A22" opacity="0.6"/>')
    return "".join(o)


def table_items(top=TABLE_TOP, mug_on_table=True, crumbs=True):
    o = [plate(PLATE_X, top - 2, 0.14)]
    if mug_on_table:
        o.append(mug(MUG_X, top, MUG_S, steam=False))
    if crumbs:
        o.append("".join(f'<circle cx="{x}" cy="{top - 0.9*s:.2f}" r="{0.9*s:.2f}" fill="#E8A040"/>' for x, s in CRUMBS))
    return "".join(o)


def you_seated(J, s=S0, x=SEAT_X, top=TABLE_TOP, props=None):
    return at(x, top + 162 * s, s, R3.front(J, props=props))


def hand_mug(hx, hy, s=0.23):
    """A mug held by its handle at hand (hx, hy) in body units; mug body sits to the inside of the hand."""
    return f'<g transform="translate({hx - 30:.1f} {hy + 20:.1f})">{mug(0, 0, s, steam=False)}</g>'


# ------------------------------------------------------------------ tabletop at ant height (macro), same layout
def macro_world(hz=250, look=0.0, mug_x=760, mug_w=760, crumbs=True):
    """Camera on the tabletop near the front edge, looking toward the wall. Mug to the right, crumbs around you."""
    o = [f'<g transform="translate(480 {hz}) scale(1.5) translate(-480 -300)">{kitchen_room()}</g>' + haze("#3A1A86", 0.32)]
    o.append(wood_plane(hz))
    o.append(f'<rect x="-900" y="{hz - 2}" width="2760" height="5" fill="#FFE2C0" opacity="0.5"/>')
    o.append(giant_mug_base(mug_x, hz + 150, mug_w, 1100))
    if crumbs:
        rr = random.Random(3)
        for (x, y, s) in [(260, hz + 120, 0.6), (130, hz + 210, 1.1), (620, hz + 190, 0.5), (-40, hz + 260, 1.6), (380, hz + 70, 0.35)]:
            o.append(boulder(x, y, s, rr.randint(1, 9)))
    return "".join(o)


def macro_fg(hz=250):
    rr = random.Random(8)
    return boulder(870, hz + 330, 2.4, 4)


def floor_side(leg_x=150, top=380, chair=True):
    """Kitchen floor at ant height: table leg landmark, floor seams in perspective, chair leg in the distance."""
    o = ['<rect x="-900" y="-900" width="2760" height="2340" fill="#4A2A9A"/>']
    o.append(f'<g opacity="0.55"><rect x="-900" y="-900" width="2760" height="{top + 900}" fill="#5A2EB0"/>'
             + "".join(f'<rect x="{-400 + i*260}" y="{top - 330}" width="200" height="300" rx="14" fill="#6A3AC0"/>' for i in range(8)) + '</g>')
    if chair:
        o.append(f'<rect x="760" y="-900" width="40" height="{top + 900}" fill="#7A4A9A" opacity="0.7"/><rect x="900" y="-900" width="40" height="{top + 900}" fill="#7A4A9A" opacity="0.55"/>')
    o.append(f'<rect x="-900" y="{top}" width="2760" height="900" fill="#5A3AB8"/>')
    for i in range(-6, 16):
        o.append(f'<path d="M{480 + i*90} {top} L{480 + i*420} {top + 700}" stroke="#2A1870" stroke-width="5" opacity="0.8"/>')
    for k, y in enumerate((top + 30, top + 90, top + 190)):
        o.append(f'<path d="M-900 {y} L1860 {y}" stroke="#2A1870" stroke-width="{4 + k}" opacity="0.8"/>')
    o.append(f'<rect x="{leg_x}" y="-900" width="140" height="{top + 906}" fill="#A85E30"/><rect x="{leg_x}" y="-900" width="34" height="{top + 906}" fill="#C47640"/>'
             f'<ellipse cx="{leg_x + 70}" cy="{top + 6}" rx="110" ry="14" fill="#1A0A40" opacity="0.4"/>')
    return "".join(o)


def floor_crumb(x, y, s=1.0):
    return soft_shadow(x, y, 26 * s, 6 * s, 0.4) + crumb(x, y - 14 * s, 22 * s, 3)
