"""Character v2: one connected body. Neck sits behind the collar, arms grow out of the sweater's shoulders,
mitten hands with a thumb and a cuff, slimmer trousers. Patches rig.person and kit2.back in place."""
import math, sys
sys.path.insert(0, "/home/claude/bible"); sys.path.insert(0, "/home/claude/ant2"); sys.path.insert(0, "/home/claude/ep")
import kit as K
from kit import inside, P, S, E, C, R, U, g
import scene_people as SP
import rig, kit2

rim = SP.rimmed
TORSO = "M -60 -196 C -64 -262 -70 -318 -58 -344 C -46 -368 -22 -374 0 -374 C 22 -374 46 -368 58 -344 C 70 -318 64 -262 60 -196 Q 0 -184 -60 -196 Z"
SHOULDER = (46, -340)


def _hand(hx, hy, ex, ey, sk, side):
    ang = math.degrees(math.atan2(hy - ey, hx - ex)) - 90
    mit = P("M -13 -6 Q -14 14 0 17 Q 14 14 13 -6 Q 10 -14 0 -14 Q -10 -14 -13 -6 Z")
    th = E(-12 * side, -2, 6, 9)
    body = rim(U(mit, th), *sk, 3)
    return f'<g transform="translate({hx:.1f} {hy:.1f}) rotate({ang:.1f})">{body}</g>'


def _limb(x0, y0, cx, cy, x1, y1, w0, w1, n=18):
    """A tapered tube along a quadratic curve, with round ends, as one closed shape."""
    L_, R_ = [], []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        dx = 2 * (1 - t) * (cx - x0) + 2 * t * (x1 - cx)
        dy = 2 * (1 - t) * (cy - y0) + 2 * t * (y1 - cy)
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        w = (w0 + (w1 - w0) * t) / 2
        L_.append((x + nx * w, y + ny * w)); R_.append((x - nx * w, y - ny * w))
    pts = L_ + R_[::-1]
    d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts) + " Z"
    return U(P(d), C(x0, y0, w0 / 2), C(x1, y1, w1 / 2))


def _arm(p, sx, sy, ex, ey, hx, hy, far, side):
    col = (p.top[1], p.top[1], p.top[0]) if far else p.top
    sk = (p.skin[1], p.skin[1], p.skin[0]) if far else p.skin
    dx, dy = hx - ex, hy - ey
    L = math.hypot(dx, dy) or 1
    wx, wy = hx - dx / L * 13, hy - dy / L * 13
    sleeve = _limb(sx, sy, ex, ey, wx, wy, 34, 26)
    cuff = f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="15" fill="{p.top[1]}" opacity="0.55"/>'
    return _hand(hx, hy, ex, ey, sk, side) + rim(sleeve, *col, 5) + inside(sleeve, _soft(cuff, 2))


def _legs(p, legs, back=False):
    o = []
    for i, (hx, hy, fx, fy) in enumerate(legs):
        far = (i == 1) if back else (i == 0)
        col = (p.bottom[1], p.bottom[1], p.bottom[0]) if far else p.bottom
        shape = P(f"M {hx-21:.1f} {hy:.1f} L {hx+21:.1f} {hy:.1f} L {fx+14:.1f} {fy-6:.1f} Q {fx:.1f} {fy:.1f} {fx-14:.1f} {fy-6:.1f} Z")
        o.append(rim(shape, *col, 5))
        if back:
            shoe = P(f"M {fx-22:.1f} {fy+14:.1f} Q {fx-22:.1f} {fy-6:.1f} {fx:.1f} {fy-8:.1f} Q {fx+22:.1f} {fy-6:.1f} {fx+22:.1f} {fy+14:.1f} Z")
        else:
            shoe = P(f"M {fx-24:.1f} {fy+14:.1f} Q {fx-26:.1f} {fy-6:.1f} {fx-6:.1f} {fy-10:.1f} Q {fx+20:.1f} {fy-10:.1f} {fx+24:.1f} {fy+8:.1f} Q {fx+24:.1f} {fy+16:.1f} {fx+14:.1f} {fy+16:.1f} L {fx-16:.1f} {fy+16:.1f} Q {fx-24:.1f} {fy+16:.1f} {fx-24:.1f} {fy+14:.1f} Z")
        o.append(rim(shoe, p.shoe[0], p.shoe[1], "#FFFFFF", 3))
        o.append(inside(shoe, f'<rect x="{fx-30:.1f}" y="{fy+9:.1f}" width="60" height="9" fill="#FF4F9A" opacity="0.85"/>'))
    return o


def _torso(p, back=False):
    t = P(TORSO)
    o = [rim(t, *p.top, 8)]
    rib = "".join(f'<rect x="{-58 + i*10}" y="-222" width="4" height="26" fill="{p.top[1]}" opacity="0.65"/>' for i in range(12))
    o.append(inside(t, rib))
    if not back:
        # crew neck: a soft rolled collar that sits over the base of the neck
        collar = P("M -30 -374 Q 0 -356 30 -374 Q 34 -366 26 -360 Q 0 -346 -26 -360 Q -34 -366 -30 -374 Z")
        o.append(rim(collar, p.top[1], p.top[1], p.top[2], 3))
    return o


def _neck(p):
    nk = R(-14, -396, 28, 30, 10)
    return rim(nk, p.skin[1], p.skin[1], p.skin[0], 3) + inside(nk, _soft(f'<rect x="-20" y="-398" width="40" height="14" fill="#000" opacity="0.22"/>', 2))


def _in_front(hx, hy):
    return abs(hx) < 62 and -372 < hy < -190


def person(p, arms, legs, expr="neutral", tilt=0.0, blink=False, prop=None):
    o = _legs(p, legs)
    front_arms = []
    for j, (sx, sy, ex, ey, hx, hy) in enumerate(arms):
        side = -1 if j == 0 else 1
        sx2, sy2 = side * SHOULDER[0], SHOULDER[1]
        piece = _arm(p, sx2, sy2, ex, ey, hx, hy, j == 0, side)
        (front_arms if _in_front(hx, hy) else o).append(piece)
    o.append(_neck(p))
    o.extend(_torso(p))
    hd = g(SP.head(p, "sleepy" if blink else expr, tilt), 0, -438)
    raised_front = []
    o.append(hd)
    o.extend(front_arms)
    if prop:
        o.append(prop)
    return "".join(o)


def back(arms="stand", legs="stand", tilt=0):
    a = rig.ARMS[arms] if isinstance(arms, str) else arms
    l = rig.LEGS[legs] if isinstance(legs, str) else legs
    p = kit2.YOU
    o = _legs(p, l, back=True)
    over = []
    for j, (sx, sy, ex, ey, hx, hy) in enumerate(a):
        side = -1 if j == 0 else 1
        piece = _arm(p, side * SHOULDER[0], SHOULDER[1], ex, ey, hx, hy, j == 1, side)
        (over if hy < -360 else o).append(piece)
    o.append(_neck(p))
    o.extend(_torso(p, back=True))
    hair = P("M -58 -398 Q -70 -506 0 -514 Q 70 -506 58 -398 Q 50 -380 28 -378 L -28 -378 Q -50 -380 -58 -398 Z")
    o.append(f'<g transform="rotate({tilt} 0 -444)">' + rim(E(-52, -444, 9, 13), *p.skin, 3) + rim(E(52, -444, 9, 13), *p.skin, 3) +
             rim(hair, *p.hair, 6) + inside(hair, _soft(f'<ellipse cx="0" cy="-486" rx="34" ry="9" fill="{p.hair[2]}" opacity="0.55"/>', 4)) + '</g>')
    o.extend(over)
    return "".join(o)


def install():
    rig.person = person
    kit2.back = back
    rig.LEGS["stand"] = [(-22, -204, -24, -16), (22, -204, 24, -16)]


install()


# ------------------------------------------------------------------ head v2: fuller hair with a swept fringe, real eyes
DARK = "#24112E"


def _soft(svg, b=3):
    f, d = K.blur_f(b)
    return d + f'<g{f}>{svg}</g>'


def head2(p, expr="neutral", tilt=0):
    sk, hr = p.skin, p.hair
    o = []
    back_hair = P("M -60 22 Q -72 -72 0 -82 Q 72 -72 60 22 Q 52 30 45 20 L 46 -8 Q 0 -30 -46 -8 L -45 20 Q -52 30 -60 22 Z")
    o.append(rim(back_hair, hr[1], hr[1], hr[2], 5))
    o.append(rim(U(E(-50, 4, 9, 12), E(50, 4, 9, 12)), sk[0], sk[1], sk[2], 3))
    face = P("M -50 -8 Q -52 -60 0 -62 Q 52 -60 50 -8 Q 49 34 24 50 Q 0 60 -24 50 Q -49 34 -50 -8 Z")
    o.append(rim(face, *sk, 6))
    o.append(inside(face, _soft(f'<ellipse cx="-27" cy="20" rx="11" ry="7" fill="#FF6F8A" opacity="0.45"/><ellipse cx="27" cy="20" rx="11" ry="7" fill="#FF6F8A" opacity="0.45"/>', 3)))
    # eyes
    ey = 2
    for sx in (-1, 1):
        ex = sx * 20
        if expr in ("happy", "laugh"):
            o.append(f'<path d="M{ex-9} {ey+3} Q{ex} {ey-8} {ex+9} {ey+3}" stroke="{DARK}" stroke-width="4.5" fill="none" stroke-linecap="round"/>')
        elif expr == "sleepy":
            o.append(f'<path d="M{ex-9} {ey} Q{ex} {ey+6} {ex+9} {ey}" stroke="{DARK}" stroke-width="4.5" fill="none" stroke-linecap="round"/>')
        else:
            big = expr in ("surprised", "scared")
            rx, ry, ir = (10.5, 12.5, 5.5) if big else (8.5, 10, 6.2)
            o.append(f'<ellipse cx="{ex}" cy="{ey}" rx="{rx}" ry="{ry}" fill="#FFFFFF"/>')
            o.append(f'<circle cx="{ex + (2 if expr == "think" else 0)}" cy="{ey + (0 if big else 1.5) - (3 if expr == "think" else 0)}" r="{ir}" fill="{DARK}"/>')
            o.append(f'<circle cx="{ex - 2}" cy="{ey - 3}" r="2.2" fill="#FFFFFF"/>')
            if expr in ("sad", "angry"):
                lid = P(f"M {ex-12} {ey-14} L {ex+12} {ey-14} L {ex+12} {ey - (2 if expr == 'sad' else 0) + (sx * 3 if expr == 'angry' else 0)} Q {ex} {ey-6} {ex-12} {ey - (2 if expr == 'sad' else 0) - (sx * 3 if expr == 'angry' else 0)} Z")
                o.append(lid(sk[0]))
    bw = {"neutral": (-26, -27), "happy": (-29, -31), "laugh": (-30, -33), "sad": (-22, -30), "surprised": (-34, -38),
          "think": (-25, -31), "angry": (-30, -20), "sleepy": (-21, -21), "scared": (-30, -36), "strain": (-24, -20)}.get(expr, (-26, -27))
    for sx in (-1, 1):
        x1, x2 = sx * 30, sx * 11
        o.append(f'<path d="M{x1} {bw[0]} Q{(x1 + x2) / 2} {min(bw) - 3} {x2} {bw[1]}" stroke="{hr[0]}" stroke-width="5.5" fill="none" stroke-linecap="round"/>')
    o.append(_soft(f'<ellipse cx="1" cy="13" rx="5" ry="4" fill="{sk[1]}" opacity="0.8"/>', 1))
    m = expr
    if m in ("happy", "laugh"):
        mouth = P("M -14 26 Q 0 28 14 26 Q 12 44 0 44 Q -12 44 -14 26 Z")
        o.append(mouth("#5A1E2E") + inside(mouth, '<ellipse cx="0" cy="44" rx="9" ry="6" fill="#FF7A8A"/>'))
    elif m in ("surprised", "scared"):
        o.append('<ellipse cx="0" cy="33" rx="7" ry="9" fill="#5A1E2E"/>')
    elif m == "sad":
        o.append(f'<path d="M-9 35 Q0 28 9 35" stroke="#5A1E2E" stroke-width="4" fill="none" stroke-linecap="round"/>')
    elif m in ("angry", "strain"):
        o.append(f'<path d="M-9 32 L9 32" stroke="#5A1E2E" stroke-width="4" stroke-linecap="round"/>')
    elif m == "think":
        o.append(f'<path d="M-4 32 Q4 34 10 29" stroke="#5A1E2E" stroke-width="4" fill="none" stroke-linecap="round"/>')
    else:
        o.append(f'<path d="M-8 30 Q0 36 8 30" stroke="#5A1E2E" stroke-width="4" fill="none" stroke-linecap="round"/>')
    fringe = P("M -56 -10 Q -62 -78 0 -84 Q 64 -80 57 -14 Q 44 -42 18 -44 Q 24 -32 10 -26 Q -10 -42 -36 -32 Q -48 -26 -56 -10 Z")
    o.append(rim(fringe, *hr, 5))
    o.append(inside(fringe, _soft(f'<ellipse cx="-12" cy="-66" rx="24" ry="7" fill="{hr[2]}" opacity="0.6" transform="rotate(-12 -12 -66)"/>', 3)))
    return f'<g transform="rotate({tilt})">{"".join(o)}</g>'


def _install_head():
    SP.head = head2
    kit2.face_close = lambda expr="neutral", tilt=0, blink=False: head2(kit2.YOU, "sleepy" if blink else expr, tilt)
    if hasattr(kit2, "SP"):
        kit2.SP.head = head2


_install_head()
