"""Character v3: fully pose-able body (front and profile) with an expressive face.
Same design as rig2 (sweater, trousers, mitten hands, fringe), but every joint, brow, eye and mouth is a parameter,
so poses can be keyed and interpolated. Feet rest at y=0, hips at y=-200, head centre at y=-438 (front)."""
import math, sys
sys.path.insert(0, "/home/claude/bible"); sys.path.insert(0, "/home/claude/ant2"); sys.path.insert(0, "/home/claude/ep")
from kit import inside, P, S, E, C, R, U, g
import scene_people as SP
import rig2, kit3
from rig2 import _limb, _hand, _arm as _arm_front, _neck, TORSO, DARK, _soft
import assets as A

rim = SP.rimmed
YOU = A.YOU

# ------------------------------------------------------------------ pose maths
def mix(a, b, u):
    if isinstance(a, dict):
        return {k: mix(a[k], b.get(k, a[k]), u) if k in b else a[k] for k in a} | {k: b[k] for k in b if k not in a}
    if isinstance(a, (tuple, list)):
        return tuple(mix(x, y, u) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a + (b - a) * u
    return b if u >= 0.5 else a


def smooth(u):
    u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)


def keys(t, ks, ease=smooth):
    """ks = [(time, pose), ...] sorted; returns the interpolated pose at t."""
    if t <= ks[0][0]:
        return ks[0][1]
    for (t0, a), (t1, b) in zip(ks, ks[1:]):
        if t <= t1:
            return mix(a, b, ease((t - t0) / max(1e-6, t1 - t0)))
    return ks[-1][1]


def ov(base, **kw):
    """Copy of a pose with fields overridden (face fields via face=dict)."""
    d = dict(base)
    for k, v in kw.items():
        if k == "face":
            d["face"] = dict(base["face"]) | v
        else:
            d[k] = v
    return d


# ------------------------------------------------------------------ faces
FACE = dict(lift=0.0, knit=0.0, open=1.0, look=(0.0, 0.0), mouth="smile", mo=0.0, turn=0.0, blink=0.0, blush=0.45)


def _mouth(kind, mo, x0=0.0, y0=0.0):
    x, y = x0, y0
    if kind == "smile":
        return f'<path d="M{x-9:.1f} {y+30:.1f} Q{x:.1f} {y+37 + 3*mo:.1f} {x+9:.1f} {y+30:.1f}" stroke="#5A1E2E" stroke-width="4" fill="none" stroke-linecap="round"/>'
    if kind == "grin":
        m = P(f"M {x-14:.1f} {y+26:.1f} Q {x:.1f} {y+28:.1f} {x+14:.1f} {y+26:.1f} Q {x+12:.1f} {y+44:.1f} {x:.1f} {y+44:.1f} Q {x-12:.1f} {y+44:.1f} {x-14:.1f} {y+26:.1f} Z")
        return m("#5A1E2E") + inside(m, f'<ellipse cx="{x:.1f}" cy="{y+44:.1f}" rx="9" ry="6" fill="#FF7A8A"/>')
    if kind in ("o", "gasp", "scream"):
        rx, ry = {"o": (5, 6), "gasp": (8, 11), "scream": (13, 17)}[kind]
        rx += 3 * mo; ry += 4 * mo
        cy = y + 33 + (ry - 6) * 0.4
        return (f'<ellipse cx="{x:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#5A1E2E"/>'
                + (f'<ellipse cx="{x:.1f}" cy="{cy + ry*0.55:.1f}" rx="{rx*0.6:.1f}" ry="{ry*0.3:.1f}" fill="#FF7A8A"/>' if kind == "scream" else ""))
    if kind == "worried":
        return f'<path d="M{x-10:.1f} {y+35:.1f} Q{x-5:.1f} {y+30:.1f} {x:.1f} {y+33:.1f} Q{x+5:.1f} {y+36:.1f} {x+10:.1f} {y+31:.1f}" stroke="#5A1E2E" stroke-width="4" fill="none" stroke-linecap="round"/>'
    if kind == "frown":
        return f'<path d="M{x-9:.1f} {y+36:.1f} Q{x:.1f} {y+29:.1f} {x+9:.1f} {y+36:.1f}" stroke="#5A1E2E" stroke-width="4" fill="none" stroke-linecap="round"/>'
    if kind == "flat":
        return f'<path d="M{x-8:.1f} {y+33:.1f} L{x+8:.1f} {y+33:.1f}" stroke="#5A1E2E" stroke-width="4" stroke-linecap="round"/>'
    if kind == "smirk":
        return f'<path d="M{x-8:.1f} {y+33:.1f} Q{x+2:.1f} {y+35:.1f} {x+11:.1f} {y+27:.1f}" stroke="#5A1E2E" stroke-width="4" fill="none" stroke-linecap="round"/>'
    if kind == "grit":
        w = 12 + 2 * mo
        return (f'<rect x="{x-w:.1f}" y="{y+27:.1f}" width="{2*w:.1f}" height="11" rx="5" fill="#FFFFFF" stroke="#5A1E2E" stroke-width="3"/>'
                f'<path d="M{x-w+3:.1f} {y+32.5:.1f} L{x+w-3:.1f} {y+32.5:.1f}" stroke="#5A1E2E" stroke-width="2"/>')
    if kind == "sip":
        return f'<ellipse cx="{x:.1f}" cy="{y+32:.1f}" rx="5" ry="3.5" fill="#5A1E2E"/>'
    return ""


def face_front(f=None, p=YOU, tilt=0.0):
    f = FACE | (f or {})
    sk, hr = p.skin, p.hair
    tr = f["turn"] * 12
    o = []
    back_hair = P("M -60 22 Q -72 -72 0 -82 Q 72 -72 60 22 Q 52 30 45 20 L 46 -8 Q 0 -30 -46 -8 L -45 20 Q -52 30 -60 22 Z")
    o.append(rim(back_hair, hr[1], hr[1], hr[2], 5))
    o.append(rim(U(E(-50 + tr * 0.4, 4, 9, 12), E(50 + tr * 0.4, 4, 9, 12)), sk[0], sk[1], sk[2], 3))
    face = P("M -50 -8 Q -52 -60 0 -62 Q 52 -60 50 -8 Q 49 34 24 50 Q 0 60 -24 50 Q -49 34 -50 -8 Z")
    o.append(rim(face, *sk, 6))
    o.append(inside(face, _soft(f'<ellipse cx="{-27 + tr:.1f}" cy="20" rx="11" ry="7" fill="#FF6F8A" opacity="{f["blush"]:.2f}"/><ellipse cx="{27 + tr:.1f}" cy="20" rx="11" ry="7" fill="#FF6F8A" opacity="{f["blush"]:.2f}"/>', 3)))
    ey = 2
    op = max(0.08, f["open"] * (1 - f["blink"]))
    lx, ly = f["look"]
    for sx in (-1, 1):
        ex = sx * 20 + tr
        if op < 0.2:
            o.append(f'<path d="M{ex-9:.1f} {ey:.1f} Q{ex:.1f} {ey+5:.1f} {ex+9:.1f} {ey:.1f}" stroke="{DARK}" stroke-width="4.5" fill="none" stroke-linecap="round"/>')
        else:
            rx, ry = 8.5 + 1.8 * max(0, op - 1), 10 * op
            o.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#FFFFFF"/>')
            pr = min(6.2, ry * 0.75) * (0.85 if op > 1.15 else 1)
            o.append(f'<circle cx="{ex + lx*3.5:.1f}" cy="{ey + ly*3.5 + 1:.1f}" r="{pr:.1f}" fill="{DARK}"/>')
            o.append(f'<circle cx="{ex + lx*3.5 - 2:.1f}" cy="{ey + ly*3.5 - 2:.1f}" r="2" fill="#FFFFFF"/>')
            # upper lid for tension / tiredness
            if op < 0.85:
                o.append(f'<path d="M{ex-11:.1f} {ey - ry - 3:.1f} L{ex+11:.1f} {ey - ry - 3:.1f} L{ex+11:.1f} {ey - ry + 2:.1f} Q{ex:.1f} {ey - ry - 1:.1f} {ex-11:.1f} {ey - ry + 2:.1f} Z" fill="{sk[0]}"/>')
    lift, knit = f["lift"], f["knit"]
    for sx in (-1, 1):
        x_in, x_out = sx * 11 + tr, sx * 30 + tr
        y_in = -28 - 6 * lift - 7 * knit
        y_out = -27 - 6 * lift + 3 * knit
        o.append(f'<path d="M{x_out:.1f} {y_out:.1f} Q{(x_in + x_out)/2:.1f} {min(y_in, y_out) - 3:.1f} {x_in:.1f} {y_in:.1f}" stroke="{hr[0]}" stroke-width="5.5" fill="none" stroke-linecap="round"/>')
    o.append(_soft(f'<ellipse cx="{1 + tr:.1f}" cy="13" rx="5" ry="4" fill="{sk[1]}" opacity="0.8"/>', 1))
    o.append(_mouth(f["mouth"], f["mo"], tr, 0))
    fringe = P("M -56 -10 Q -62 -78 0 -84 Q 64 -80 57 -14 Q 44 -42 18 -44 Q 24 -32 10 -26 Q -10 -42 -36 -32 Q -48 -26 -56 -10 Z")
    o.append(rim(fringe, *hr, 5))
    o.append(inside(fringe, _soft(f'<ellipse cx="-12" cy="-66" rx="24" ry="7" fill="{hr[2]}" opacity="0.6" transform="rotate(-12 -12 -66)"/>', 3)))
    return f'<g transform="rotate({tilt:.2f})">{"".join(o)}</g>'


def face_side(f=None, p=YOU):
    f = FACE | (f or {})
    sk, hr = p.skin, p.hair
    o = []
    back_hair = P("M -58 34 Q -72 -66 4 -74 Q 60 -72 58 -22 Q 34 -44 8 -38 Q -12 -10 -22 36 Z")
    o.append(rim(back_hair, hr[1], hr[1], hr[2], 5))
    face = P("M -38 -2 Q -40 -56 10 -58 Q 52 -56 54 -14 Q 64 -4 66 6 Q 64 14 54 16 Q 52 44 22 54 Q -12 58 -30 34 Q -40 18 -38 -2 Z")
    o.append(rim(face, *sk, 6))
    o.append(rim(E(-10, 6, 10, 13), sk[1], sk[1], sk[2], 3))
    fringe = P("M -60 4 Q -68 -72 6 -78 Q 62 -74 60 -20 Q 44 -40 26 -42 Q 22 -30 6 -28 Q -20 -30 -30 -6 Q -44 -2 -60 4 Z")
    o.append(rim(fringe, *hr, 5))
    o.append(inside(fringe, f'<path d="M-30 -62 Q4 -76 38 -60 L37 -55 Q4 -70 -29 -57 Z" fill="{hr[2]}" opacity="0.8"/>'))
    o.append(f'<ellipse cx="26" cy="16" rx="11" ry="7" fill="#FF7A8A" opacity="{f["blush"] * 0.8:.2f}"/>')
    op = max(0.08, f["open"] * (1 - f["blink"]))
    lx, ly = f["look"]
    if op < 0.2:
        o.append('<path d="M28 -6 Q36 -1 44 -6" stroke="#2A1430" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    else:
        o.append(f'<ellipse cx="37" cy="-6" rx="{7 + max(0, op - 1) * 3:.1f}" ry="{9 * op:.1f}" fill="#FFFFFF"/>')
        o.append(f'<circle cx="{40 + lx*2.5:.1f}" cy="{-5 + ly*3:.1f}" r="{min(5.5, 9*op*0.62):.1f}" fill="#2A1430"/><circle cx="{42 + lx*2.5:.1f}" cy="{-8 + ly*3:.1f}" r="1.6" fill="#FFFFFF"/>')
    lift, knit = f["lift"], f["knit"]
    yi = -22 - 6 * lift - 7 * knit
    yo = -22 - 6 * lift + 3 * knit
    o.append(f'<path d="M24 {yo:.1f} Q36 {min(yi, yo) - 5:.1f} 48 {yi:.1f}" stroke="{hr[0]}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    m, mo = f["mouth"], f["mo"]
    if m in ("o", "gasp", "scream"):
        rx, ry = {"o": (4, 5), "gasp": (6, 8), "scream": (9, 13)}[m]
        o.append(f'<ellipse cx="48" cy="{32 + ry*0.3:.1f}" rx="{rx + 2*mo:.1f}" ry="{ry + 3*mo:.1f}" fill="#5A1E2E"/>')
    elif m in ("smile", "grin"):
        o.append('<path d="M38 26 Q48 35 56 26" stroke="#5A1E2E" stroke-width="4" fill="none" stroke-linecap="round"/>')
    elif m in ("grit", "flat"):
        o.append('<path d="M40 30 L56 29" stroke="#5A1E2E" stroke-width="4" stroke-linecap="round"/>' + ('<path d="M42 30 L54 30" stroke="#FFFFFF" stroke-width="2"/>' if m == "grit" else ""))
    elif m in ("worried", "frown"):
        o.append('<path d="M40 33 Q47 27 55 32" stroke="#5A1E2E" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    else:
        o.append('<path d="M42 30 Q48 32 54 29" stroke="#5A1E2E" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    return "".join(o)


# ------------------------------------------------------------------ front body
FRONT = dict(lean=0.0, hip=(0.0, 0.0), shr=0.0, head=(0.0, 0.0, 0.0),
             kl=(-24.0, -100.0), fl=(-26.0, 0.0), kr=(24.0, -100.0), fr=(26.0, 0.0),
             el=(-84.0, -290.0), hl=(-88.0, -214.0), er=(84.0, -290.0), hr=(88.0, -214.0),
             face=dict(FACE), sit=0.0, back_l=False, back_r=False)


def _leg_front(hip, knee, foot, p, far):
    col = (p.bottom[1], p.bottom[1], p.bottom[0]) if far else p.bottom
    leg = _limb(hip[0], hip[1], knee[0], knee[1], foot[0], foot[1] - 8, 46, 34)
    fx, fy = foot
    shoe = P(f"M {fx-24:.1f} {fy+14:.1f} Q {fx-26:.1f} {fy-6:.1f} {fx-6:.1f} {fy-10:.1f} Q {fx+20:.1f} {fy-10:.1f} {fx+24:.1f} {fy+8:.1f} Q {fx+24:.1f} {fy+16:.1f} {fx+14:.1f} {fy+16:.1f} L {fx-16:.1f} {fy+16:.1f} Q {fx-24:.1f} {fy+16:.1f} {fx-24:.1f} {fy+14:.1f} Z")
    return rim(leg, *col, 5) + rim(shoe, p.shoe[0], p.shoe[1], "#FFFFFF", 3) + inside(shoe, f'<rect x="{fx-30:.1f}" y="{fy+9:.1f}" width="60" height="9" fill="#FF4F9A" opacity="0.85"/>')


def front(J=None, p=YOU, props=None):
    """props: dict(l=svg, r=svg) drawn at the hands (in torso frame, already positioned by caller via hand coords)."""
    J = FRONT | (J or {})
    hx, hy = J["hip"]
    o = []
    hip_y = -200 + hy
    if J["sit"] > 0.5:
        # cross-legged on a surface, facing camera: thighs out to the knees, shins crossing back in front
        col_far = (p.bottom[1], p.bottom[1], p.bottom[0])
        for side, kn in ((-1, J["kl"]), (1, J["kr"])):
            hp = (hx + side * 24, hip_y)
            th = _limb(hp[0], hp[1], (hp[0] + kn[0] + hx) / 2, hip_y - 6, kn[0] + hx, kn[1] + hy, 48, 40)
            o.append(rim(th, *(col_far if side < 0 else p.bottom), 5))
        for side, kn, ft in ((1, J["kr"], J["fr"]), (-1, J["kl"], J["fl"])):
            k_ = (kn[0] + hx, kn[1] + hy); f_ = (ft[0] + hx, ft[1] + hy)
            sh_ = _limb(k_[0], k_[1], (k_[0] + f_[0]) / 2, k_[1] + 12, f_[0], f_[1], 40, 32)
            o.append(rim(sh_, *p.bottom, 5))
            shoe = E(f_[0] - side * 14, f_[1] + 2, 20, 14)
            o.append(rim(shoe, p.shoe[0], p.shoe[1], "#FFFFFF", 3))
    else:
        o.append(_leg_front((hx - 24, hip_y), (J["kl"][0] + hx * 0.5, J["kl"][1] + hy * 0.5), J["fl"], p, True))
        o.append(_leg_front((hx + 24, hip_y), (J["kr"][0] + hx * 0.5, J["kr"][1] + hy * 0.5), J["fr"], p, False))
    shr = J["shr"]
    up = []
    sx, sy = 46, -340 - 16 * shr
    arms_back, arms_front = [], []
    for side, el, hd, bk in ((-1, J["el"], J["hl"], J["back_l"]), (1, J["er"], J["hr"], J["back_r"])):
        piece = _arm_front(p, side * sx, sy, el[0], el[1], hd[0], hd[1], side < 0, side)
        infront = J.get("front_l" if side < 0 else "front_r", False) or (abs(hd[0]) < 66 and -380 < hd[1] < -190) or hd[1] < -400 and abs(hd[0]) < 70
        (arms_back if (bk or not infront) else arms_front).append(piece)
    up.extend(arms_back)
    up.append(_neck(p))
    t = P(TORSO)
    up.append(rim(t, *p.top, 8))
    up.append(inside(t, "".join(f'<rect x="{-58 + i*10}" y="-222" width="4" height="26" fill="{p.top[1]}" opacity="0.65"/>' for i in range(12))))
    collar = P("M -30 -374 Q 0 -356 30 -374 Q 34 -366 26 -360 Q 0 -346 -26 -360 Q -34 -366 -30 -374 Z")
    up.append(rim(collar, p.top[1], p.top[1], p.top[2], 3))
    hdx, hdy, tilt = J["head"]
    up.append(g(face_front(J["face"], p, tilt), hdx, -438 + hdy + 12 * shr))
    up.extend(arms_front)
    if props:
        up.extend(props)
    o.append(f'<g transform="translate({hx:.1f} {hy:.1f}) rotate({J["lean"]:.2f} 0 -200)">{"".join(up)}</g>')
    return "".join(o)


# ------------------------------------------------------------------ profile body (faces right)
SIDE = dict(lean=0.0, hip=(0.0, 0.0), head=(0.0, 0.0, 0.0), shr=0.0,
            k1=(16.0, -110.0), f1=(-10.0, 0.0), k2=(16.0, -110.0), f2=(10.0, 0.0),
            e1=(-14.0, -280.0), h1=(0.0, -214.0), e2=(0.0, -280.0), h2=(12.0, -214.0),
            face=dict(FACE))


def side(J=None, p=YOU, props=None):
    """1 = far limbs, 2 = near limbs. Hip-relative leg joints are absolute in body coords; arm joints in torso frame."""
    J = SIDE | (J or {})
    hx, hy = J["hip"]
    hip = (hx, -200 + hy)
    o = [kit3._leg(hip, J["k1"], J["f1"], p, True)]
    up_far = []
    sh = (6.0, -342.0 - 14 * J["shr"])
    up_far.append(kit3._arm(sh, J["e1"], J["h1"], p, True))
    up = []
    torso = P("M -42 -196 Q -50 -330 -8 -370 Q 42 -378 46 -316 L 44 -196 Q 0 -186 -42 -196 Z")
    up.append(rim(R(-10, -394, 26, 32, 10), p.skin[1], p.skin[1], p.skin[0], 3))
    up.append(rim(torso, *p.top, 8))
    up.append(inside(torso, "".join(f'<rect x="{-44 + i*10}" y="-222" width="4" height="26" fill="{p.top[1]}" opacity="0.7"/>' for i in range(10))))
    collar = P("M -18 -370 Q 2 -380 22 -372 Q 24 -362 16 -358 Q 0 -366 -16 -360 Z")
    up.append(rim(collar, p.top[1], p.top[1], p.top[2], 3))
    hdx, hdy, tilt = J["head"]
    up.append(f'<g transform="translate({4 + hdx:.1f} {-438 + hdy + 12 * J["shr"]:.1f}) rotate({tilt:.2f})">{face_side(J["face"], p)}</g>')
    up.append(kit3._arm(sh, J["e2"], J["h2"], p, False))
    if props:
        up.extend(props)
    rot = f'translate({hx:.1f} {hy:.1f}) rotate({J["lean"]:.2f} 0 -200)'
    o.append(f'<g transform="{rot}">{"".join(up_far)}</g>')
    o.append(kit3._leg(hip, J["k2"], J["f2"], p, False))
    o.append(f'<g transform="{rot}">{"".join(up)}</g>')
    return "".join(o)


# ------------------------------------------------------------------ pose library
F = FACE
def fc(**kw):
    return dict(FACE) | kw


# front
F_STAND = dict(FRONT)
F_SIT = FRONT | dict(sit=1.0, kl=(-104, -182), fl=(26, -176), kr=(104, -182), fr=(-26, -172))
F_ALARM = FRONT | dict(shr=0.6, el=(-92, -300), hl=(-70, -360), er=(92, -300), hr=(70, -360), kl=(-30, -96), fl=(-40, 0), kr=(30, -96), fr=(40, 0), hip=(0, 8),
                       face=fc(lift=1.0, knit=0.6, open=1.3, mouth="gasp"))
F_COWER = FRONT | dict(shr=1.0, lean=-6, hip=(-10, 22), el=(-70, -300), hl=(-30, -400), er=(70, -300), hr=(30, -400), kl=(-40, -86), fl=(-46, 0), kr=(20, -86), fr=(30, 0),
                       head=(-8, 10, -8), face=fc(lift=0.6, knit=1.0, open=1.25, mouth="grit", look=(-1, -0.5)))
F_SHIVER = FRONT | dict(shr=1.0, el=(-60, -260), hl=(30, -300), er=(60, -260), hr=(-30, -300), back_l=False, kl=(-12, -100), fl=(-14, 0), kr=(12, -100), fr=(14, 0),
                        head=(0, 12, 0), face=fc(knit=0.9, open=0.7, mouth="grit", blush=0.15))
