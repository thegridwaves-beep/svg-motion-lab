"""Sandbox drawing kit.

Hard rule baked in: light, shadow and rim are never loose strokes. Every shaded object
is drawn with tt(), which renders base, shadow and rim INSIDE a mask of the object's
own silhouette, so nothing can spill past an edge. Strokes are only used for things
that really are lines (bike frames, glasses, strings, brows).
"""
import math, random, itertools

_ids = itertools.count()


def uid(p="m"):
    return f"{p}{next(_ids)}"


# ------------------------------------------------------------------ shape builders
def P(d):
    return lambda c: f'<path d="{d}" fill="{c}"/>'


def S(d, w):
    return lambda c: f'<path d="{d}" stroke="{c}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'


def E(cx, cy, rx, ry):
    return lambda c: f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{c}"/>'


def C(cx, cy, r):
    return lambda c: f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{c}"/>'


def R(x, y, w, h, rx=0):
    return lambda c: f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" fill="{c}"/>'


def U(*fns):
    return lambda c: "".join(f(c) for f in fns)


SOFT = 1.6   # terminator softness, in shape units per k; 0 = hard cel edge


def blur_f(sd):
    """Inline blur filter; returns (attr, defs)."""
    if sd <= 0.05:
        return "", ""
    fid = uid("sf")
    return (f' filter="url(#{fid})"',
            f'<filter id="{fid}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{sd:.2f}"/></filter>')


def tt(shape, base, shade, rim=None, k=1.0, sx=9, sy=8, rw=3.5, soft=None):
    """Two-tone + rim, all clipped to the shape. Key light top-left, rim light from the right.
    The inner terminators are softened with a small blur so tones blend; the silhouette stays crisp
    because everything sits inside one mask of the shape."""
    mid = uid("tt")
    rim = rim or shade
    soft = SOFT if soft is None else soft
    f1, d1 = blur_f(soft * k * 0.6)
    f2, d2 = blur_f(soft * k)
    return (f'{d1}{d2}<mask id="{mid}" maskUnits="userSpaceOnUse" x="-20000" y="-20000" width="40000" height="40000">{shape("#fff")}</mask>'
            f'<g mask="url(#{mid})">{shape(rim)}'
            f'<g{f1}><g transform="translate({-rw*k:.1f} 0)">{shape(shade)}</g></g>'
            f'<g{f2}><g transform="translate({-(rw+sx)*k:.1f} {-sy*k:.1f})">{shape(base)}</g></g></g>')


def inside(shape, content):
    """Draw arbitrary content clipped to a shape (for stripes, windows, textures)."""
    mid = uid("in")
    return f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-20000" y="-20000" width="40000" height="40000">{shape("#fff")}</mask><g mask="url(#{mid})">{content}</g>'


def g(content, x=0, y=0, k=1.0, rot=0, flip=False):
    sc = f"scale({-k if flip else k} {k})"
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) {sc}">{content}</g>'


def text(x, y, s, size, color="#2A1A4A", weight=700, anchor="start", family="Fredoka", op=1.0):
    return f'<text x="{x}" y="{y}" font-family="{family}, sans-serif" font-weight="{weight}" font-size="{size}" fill="{color}" text-anchor="{anchor}" opacity="{op}">{s}</text>'


def shade3(hexc, f_sh=0.72, f_rim=1.25):
    """Derive (base, shade, rim) from a base hex color."""
    h = hexc.lstrip("#")
    r, g_, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    def mix(t, to):
        return "#%02X%02X%02X" % tuple(int(max(0, min(255, c + (to - c) * t))) for c in (r, g_, b))
    sh = "#%02X%02X%02X" % tuple(int(c * f_sh) for c in (r, g_, b))
    # cool the shadow slightly toward violet
    sh_h = sh.lstrip("#"); sr, sg, sb = int(sh_h[0:2], 16), int(sh_h[2:4], 16), int(sh_h[4:6], 16)
    sh = "#%02X%02X%02X" % (int(sr * 0.95), int(sg * 0.9), min(255, int(sb * 1.08 + 8)))
    return hexc, sh, mix(0.3, 255)


# ------------------------------------------------------------------ palette
INK = "#2A1A4A"
PAPER = "#F7F1E8"
PAL = {
    "violet": "#5B3CD6", "plum": "#8A3E8E", "coral": "#FF6F61", "sunset": "#FF8A3A", "sun": "#FFC94A",
    "mint": "#3EE0B4", "teal": "#1FA98C", "sky": "#2FA6E8", "night": "#1B1240", "cream": "#FFF3E0",
}


# ------------------------------------------------------------------ people
class Look:
    def __init__(self, **kw):
        self.skin = "#E8B08A"; self.hair = "#2A2244"; self.hairstyle = "crop"
        self.top = "#2F8E70"; self.top_style = "sweater"; self.bottom = "#2E3F8E"; self.shoe = "#F4EDE6"
        self.glasses = False; self.scarf = None; self.beard = None; self.accent = "#FFC94A"
        self.height = 1.0; self.under = "#FFF3E0"
        self.__dict__.update(kw)


def _hair(look, part):
    """Return shape fns for hair (back or front), head-centered coords (head rx 50, ry 56)."""
    hs = look.hairstyle
    if part == "back":
        if hs == "bob":
            return P("M -63 34 Q -72 -72 0 -76 Q 72 -72 63 34 Q 52 40 44 34 L 44 0 L -44 0 L -44 34 Q -52 40 -63 34 Z")
        if hs == "long":
            return P("M -64 -16 Q -74 -80 0 -80 Q 74 -80 64 -16 Q 74 60 70 118 Q 50 126 30 112 L 28 20 L -28 20 L -30 112 Q -50 126 -70 118 Q -74 60 -64 -16 Z")
        return None
    if hs == "bob":
        return P("M -60 -2 Q -66 -74 0 -78 Q 66 -74 60 -2 Q 50 -30 26 -38 Q 4 -30 -14 -42 Q -40 -34 -60 -2 Z")
    if hs == "bun":
        return U(P("M -53 4 Q -60 -68 0 -66 Q 58 -68 53 2 Q 32 -34 2 -38 Q -30 -34 -53 4 Z"), C(4, -86, 30))
    if hs == "crop":
        return P("M -53 -6 Q -58 -70 2 -72 Q 56 -70 54 -8 Q 46 -40 22 -44 Q 10 -54 -8 -46 Q -40 -44 -53 -6 Z")
    if hs == "curly":
        bumps = [(-46, -18, 20), (-40, -46, 22), (-18, -64, 24), (10, -68, 24), (36, -56, 22), (50, -30, 20), (-56, 6, 14), (56, 2, 14)]
        return U(*[C(x, y, r) for x, y, r in bumps])
    if hs == "long":
        return P("M -62 -4 Q -68 -78 0 -80 Q 68 -78 62 -4 Q 52 -40 10 -46 Q -26 -40 -40 -24 Q -52 -14 -62 -4 Z")
    if hs == "bald":
        return U(P("M -51 -34 Q -62 -12 -52 10 Q -44 -10 -42 -32 Z"), P("M 51 -34 Q 62 -12 52 10 Q 44 -10 42 -32 Z"))
    return None


def face(expr, look):
    """Facial features, head-centered. Real features (eyes, brows, mouth) may use strokes."""
    o = []
    dark = "#1E1230"
    ey = -2
    if expr in ("neutral", "think", "sad", "angry", "talk"):
        lid = {"sad": 3, "angry": 4}.get(expr, 0)
        for sx in (-1, 1):
            ex = sx * 20
            look_dx = 4 if expr == "think" else 0
            look_dy = -4 if expr == "think" else 0
            o.append(f'<ellipse cx="{ex + look_dx}" cy="{ey + look_dy + lid}" rx="6.5" ry="{8.5 - lid}" fill="{dark}"/>')
            o.append(f'<circle cx="{ex + look_dx - 2}" cy="{ey + look_dy - 3 + lid}" r="2" fill="#FFFFFF"/>')
    if expr in ("happy", "laugh"):
        for sx in (-1, 1):
            ex = sx * 20
            o.append(f'<path d="M{ex-9} {ey+3} Q{ex} {ey-9} {ex+9} {ey+3}" stroke="{dark}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    if expr == "surprised":
        for sx in (-1, 1):
            ex = sx * 20
            o.append(f'<ellipse cx="{ex}" cy="{ey-2}" rx="10" ry="12" fill="#FFFFFF"/><circle cx="{ex}" cy="{ey-2}" r="5" fill="{dark}"/>')
    if expr == "sleepy":
        for sx in (-1, 1):
            ex = sx * 20
            o.append(f'<path d="M{ex-9} {ey} Q{ex} {ey+7} {ex+9} {ey}" stroke="{dark}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    # brows
    bw = {"neutral": [(-30, -24, -10, -26), (10, -26, 30, -24)],
          "happy": [(-30, -26, -10, -30), (10, -30, 30, -26)],
          "laugh": [(-30, -28, -10, -32), (10, -32, 30, -28)],
          "sad": [(-30, -22, -10, -30), (10, -30, 30, -22)],
          "surprised": [(-30, -34, -10, -38), (10, -38, 30, -34)],
          "think": [(-30, -24, -10, -24), (10, -32, 30, -28)],
          "angry": [(-30, -30, -10, -20), (10, -20, 30, -30)],
          "sleepy": [(-30, -20, -10, -20), (10, -20, 30, -20)],
          "talk": [(-30, -26, -10, -28), (10, -28, 30, -26)]}[expr]
    bc = look.hair if look.hairstyle != "bald" else "#C9C2D8"
    for x1, y1, x2, y2 in bw:
        o.append(f'<path d="M{x1} {y1} Q{(x1+x2)/2} {min(y1,y2)-3} {x2} {y2}" stroke="{bc}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    # nose
    o.append(f'<path d="M2 6 Q8 14 0 18" stroke="{shade3(look.skin)[1]}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    # mouth
    my = 30
    if expr == "neutral":
        o.append(f'<path d="M-9 {my} Q0 {my+6} 9 {my}" stroke="{dark}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    elif expr == "talk":
        o.append(f'<path d="M-10 {my-2} Q0 {my+14} 10 {my-2} Z" fill="{dark}"/>')
    elif expr == "happy":
        o.append(f'<path d="M-14 {my-3} Q0 {my+16} 14 {my-3} Z" fill="{dark}"/><path d="M-7 {my+5} Q0 {my+11} 7 {my+5} Z" fill="#FF7A8A"/>')
    elif expr == "laugh":
        o.append(f'<path d="M-18 {my-5} Q0 {my+24} 18 {my-5} Z" fill="{dark}"/><path d="M-9 {my+7} Q0 {my+17} 9 {my+7} Z" fill="#FF7A8A"/>')
    elif expr == "sad":
        o.append(f'<path d="M-10 {my+4} Q0 {my-5} 10 {my+4}" stroke="{dark}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    elif expr == "surprised":
        o.append(f'<ellipse cx="0" cy="{my+2}" rx="8" ry="10" fill="{dark}"/>')
    elif expr == "think":
        o.append(f'<path d="M-4 {my+1} Q6 {my-2} 12 {my+2}" stroke="{dark}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    elif expr == "angry":
        o.append(f'<path d="M-11 {my+3} Q0 {my-3} 11 {my+3}" stroke="{dark}" stroke-width="4.5" fill="none" stroke-linecap="round"/>')
    elif expr == "sleepy":
        o.append(f'<ellipse cx="0" cy="{my+1}" rx="5" ry="4" fill="{dark}"/>')
    # blush
    if expr in ("happy", "laugh", "surprised", "neutral", "talk"):
        o.append(f'<ellipse cx="-32" cy="16" rx="10" ry="5" fill="#FF6A86" opacity="0.4"/><ellipse cx="32" cy="16" rx="10" ry="5" fill="#FF6A86" opacity="0.4"/>')
    return "".join(o)


def head(look, expr="neutral", tilt=0):
    sk = shade3(look.skin)
    hr = shade3(look.hair)
    o = []
    back = _hair(look, "back")
    if back:
        o.append(tt(back, *hr))
    o.append(tt(U(E(-50, 2, 9, 13), E(50, 2, 9, 13)), *sk))                     # ears
    o.append(tt(E(0, 0, 50, 56), *sk))
    if look.beard:
        o.append(tt(P("M -42 10 Q -46 74 0 82 Q 46 74 42 10 Q 22 40 0 40 Q -22 40 -42 10 Z"), *shade3(look.beard)))
    front = _hair(look, "front")
    if front:
        o.append(tt(front, *hr))
    o.append(face(expr, look))
    if look.beard and expr != "laugh":
        pass
    if look.glasses:
        o.append('<circle cx="-20" cy="-2" r="16" fill="#FFFFFF" opacity="0.12"/><circle cx="20" cy="-2" r="16" fill="#FFFFFF" opacity="0.12"/>'
                 f'<circle cx="-20" cy="-2" r="16" fill="none" stroke="{INK}" stroke-width="4"/><circle cx="20" cy="-2" r="16" fill="none" stroke="{INK}" stroke-width="4"/>'
                 f'<path d="M-4 -4 Q0 -8 4 -4" stroke="{INK}" stroke-width="4" fill="none"/>')
    return f'<g transform="rotate({tilt})">{"".join(o)}</g>'


POSES = {
    #        L leg (hip, knee, foot)            R leg                                L arm (sh, el, hand)               R arm
    "stand": [((-22, -190), (-25, -100), (-26, -10)), ((22, -190), (25, -100), (26, -10)), ((-54, -332), (-76, -268), (-68, -200)), ((54, -332), (76, -268), (68, -200))],
    "walk":  [((-18, -190), (-36, -100), (-56, -12)), ((18, -190), (30, -104), (44, -22)), ((-54, -332), (-62, -268), (-40, -206)), ((54, -332), (86, -276), (96, -214))],
    "wave":  [((-22, -190), (-25, -100), (-26, -10)), ((22, -190), (25, -100), (26, -10)), ((-54, -332), (-76, -268), (-68, -200)), ((54, -332), (100, -378), (104, -452))],
    "cheer": [((-24, -190), (-34, -100), (-40, -10)), ((24, -190), (34, -100), (40, -10)), ((-54, -332), (-100, -380), (-108, -452)), ((54, -332), (100, -380), (108, -452))],
    "point": [((-22, -190), (-25, -100), (-26, -10)), ((22, -190), (25, -100), (26, -10)), ((-54, -332), (-76, -268), (-68, -200)), ((54, -332), (120, -350), (180, -380))],
    "think": [((-22, -190), (-25, -100), (-26, -10)), ((22, -190), (25, -100), (26, -10)), ((-54, -332), (-70, -262), (-20, -246)), ((54, -332), (74, -300), (24, -392))],
}


def person(look, pose="stand", expr="neutral", sit=False, tilt=0):
    """Full figure, feet at (0,0), ~ 490 units tall. Front view, key light top-left, rim right."""
    sk, top, bot, sh = shade3(look.skin), shade3(look.top), shade3(look.bottom), shade3(look.shoe)
    o = []
    dy = 60 if sit else 0                      # sitting lowers the upper body
    L, Rr, LA, RA = POSES.get(pose, POSES["stand"])
    hips = -190 + dy
    # long back hair first
    hc = (0, -424 + dy)
    if sit:
        # lap (foreshortened thighs) and shins
        o.append(tt(P(f"M -64 {hips-6} Q 0 {hips-16} 64 {hips-6} L 60 {hips+34} Q 0 {hips+44} -60 {hips+34} Z"), *bot))
        for sx in (-1, 1):
            o.append(tt(S(f"M {sx*28} {hips+30} L {sx*30} -12", 38), *bot, sx=6, sy=3, rw=3))
            o.append(tt(E(sx*32, -8, 26, 13), *sh))
    else:
        for (hp, kn, ft), sx in ((L, -1), (Rr, 1)):
            o.append(tt(S(f"M {hp[0]} {hp[1]} Q {kn[0]} {kn[1]} {ft[0]} {ft[1]}", 40), *bot, sx=6, sy=3, rw=3))
            o.append(tt(E(ft[0] + sx * 6, ft[1] + 4, 27, 13), *sh))
    # torso by style
    st = look.top_style
    ty0, ty1 = -342 + dy, hips + (8 if st != "coat" else 70)
    if sit and st == "coat":
        ty1 = hips + 20
    torso = P(f"M -62 {ty1} Q -72 {ty0+50} -52 {ty0+4} Q 0 {ty0-22} 52 {ty0+4} Q 72 {ty0+50} 62 {ty1} Q 0 {ty1+10} -62 {ty1} Z")
    if st == "hoodie":
        o.append(tt(E(0, ty0 + 10, 58, 30), *shade3(top[1])))
    o.append(tt(torso, *top))
    if st == "sweater":
        o.append(tt(R(-26, ty0 - 24, 52, 24, 10), *top))        # turtleneck
        o.append(inside(torso, "".join(f'<rect x="{-62+i*12}" y="{ty1-26}" width="5" height="30" fill="{top[1]}" opacity="0.6"/>' for i in range(11))))
    if st == "coat":
        o.append(tt(P(f"M -36 {ty0-4} L 0 {ty0+52} L 0 {ty0-4} Z"), top[1], top[1]))
        o.append(tt(P(f"M 36 {ty0-4} L 0 {ty0+52} L 0 {ty0-4} Z"), top[0], top[1], top[2]))
        o.append(inside(torso, f'<rect x="-2" y="{ty0+40}" width="4" height="400" fill="{top[1]}"/>'))
        for i in range(3):
            o.append(tt(C(-14, ty0 + 76 + i * 46, 6), *shade3("#8A4A1A")))
        o.append(tt(R(-54, ty0 + 150, 34, 10, 5), top[1], top[1]))
        o.append(tt(R(20, ty0 + 150, 34, 10, 5), top[1], top[1]))
    if st == "hoodie":
        o.append(tt(R(-40, ty0 + 120, 80, 44, 14), *shade3(top[1], 0.85)))
        o.append(f'<path d="M-12 {ty0+6} L-14 {ty0+60} M12 {ty0+6} L14 {ty0+60}" stroke="{look.under}" stroke-width="4" stroke-linecap="round"/>')
    if st == "cardigan":
        o.append(inside(torso, tt(R(-22, ty0 - 30, 44, 400), *shade3(look.under))))
        for i in range(4):
            o.append(tt(C(28, ty0 + 40 + i * 36, 5), *shade3("#E8E0D0")))
    if st == "raincoat":
        o.append(inside(torso, f'<rect x="-3" y="{ty0}" width="6" height="400" fill="{top[1]}"/>'))
        for i in range(3):
            o.append(tt(R(-16, ty0 + 60 + i * 44, 12, 18, 4), *shade3("#3A2A5A")))
    # arms (sleeves) and hands
    late = []
    for (shp, el, hd), sx in ((LA, -1), (RA, 1)):
        shp = (shp[0], shp[1] + dy); el = (el[0], el[1] + dy); hd = (hd[0], hd[1] + dy)
        sleeve = top if st != "tee" else sk
        tgt = late if (pose == "think" and sx == 1) else o
        o_ = o
        o = tgt
        o.append(tt(S(f"M {shp[0]} {shp[1]} Q {el[0]} {el[1]} {hd[0]} {hd[1]}", 30), *sleeve, sx=5, sy=4, rw=2.5))
        if st == "tee":
            o.append(tt(S(f"M {shp[0]} {shp[1]} L {shp[0] + (el[0]-shp[0])*0.45:.2f} {shp[1] + (el[1]-shp[1])*0.45:.2f}", 34), *top))
        o.append(tt(C(hd[0], hd[1], 15), *sk))
        o = o_
    # neck
    o.append(tt(R(-13, ty0 - 40, 26, 40, 6), sk[1], sk[1]))
    # scarf
    if look.scarf:
        scf = shade3(look.scarf)
        band = R(-56, ty0 - 30, 112, 32, 16)
        o.append(tt(band, *scf))
        o.append(tt(P(f"M 18 {ty0-4} L 42 {ty0-4} L 38 {ty0+86} L 16 {ty0+82} Z"), *scf))
        o.append(inside(U(band, P(f"M 18 {ty0-4} L 42 {ty0-4} L 38 {ty0+86} L 16 {ty0+82} Z")),
                        "".join(f'<rect x="{-56+i*22}" y="{ty0-40}" width="8" height="140" fill="{scf[1]}" transform="rotate(12 {-56+i*22} {ty0})"/>' for i in range(8))))
    # head
    o.append(g(head(look, expr, tilt), hc[0], hc[1]))
    o.extend(late)
    return "".join(o)


# ------------------------------------------------------------------ animals
def cat(expr="sleepy", color="#8E7EA2", sitting=False):
    c = shade3(color)
    o = []
    if sitting:
        body = P("M -44 0 Q -62 -56 -32 -94 Q 0 -112 32 -94 Q 62 -56 44 0 Q 0 8 -44 0 Z")
        o.append(tt(body, *c))
        o.append(inside(body, "".join(f'<path d="M{x} -70 q10 8 0 20 q-4 -10 0 -20 Z" fill="{c[1]}"/>' for x in (-30, -14, 14, 30))))
        o.append(tt(U(E(-22, -4, 16, 9), E(22, -4, 16, 9)), *shade3(c[0], 0.9)))
        o.append(tt(S("M 40 -6 Q 72 -4 62 6 Q 46 14 -6 8", 13), *c, sx=4, sy=3, rw=2))
        hx, hy = 0, -118
    else:
        o.append(tt(S("M -40 4 Q -74 12 -64 -18 Q -60 -30 -46 -18", 13), *c))
        o.append(tt(E(0, 0, 50, 28), *c))
        o.append(inside(E(0, 0, 50, 28), "".join(f'<path d="M{-24+i*16} -30 q6 14 0 30" stroke="{c[1]}" stroke-width="6" fill="none"/>' for i in range(4))))
        hx, hy = 34, -12
    hd = U(C(hx, hy, 26), P(f"M {hx-22} {hy-12} L {hx-18} {hy-40} L {hx-4} {hy-24} Z"), P(f"M {hx+22} {hy-12} L {hx+18} {hy-40} L {hx+4} {hy-24} Z"))
    o.append(tt(hd, *c))
    o.append(f'<path d="M{hx-17} {hy-28} L{hx-15} {hy-36} L{hx-9} {hy-27} Z" fill="#FFB0C0"/><path d="M{hx+17} {hy-28} L{hx+15} {hy-36} L{hx+9} {hy-27} Z" fill="#FFB0C0"/>')
    dk = "#1E1230"
    if expr == "sleepy":
        o.append(f'<path d="M{hx-16} {hy} q6 5 12 0 M{hx+4} {hy} q6 5 12 0" stroke="{dk}" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    else:
        o.append(f'<ellipse cx="{hx-10}" cy="{hy-2}" rx="5" ry="7" fill="{dk}"/><ellipse cx="{hx+10}" cy="{hy-2}" rx="5" ry="7" fill="{dk}"/>'
                 f'<circle cx="{hx-11}" cy="{hy-5}" r="1.8" fill="#fff"/><circle cx="{hx+9}" cy="{hy-5}" r="1.8" fill="#fff"/>')
    o.append(f'<path d="M{hx-3} {hy+8} L{hx+3} {hy+8} L{hx} {hy+12} Z" fill="#FF8AA0"/>')
    o.append(f'<path d="M{hx-6} {hy+16} q3 4 6 0 q3 4 6 0" stroke="{dk}" stroke-width="2.5" fill="none" stroke-linecap="round"/>')
    return "".join(o)


def duck(color="#F4EDE6", bill="#FF9A3A"):
    c = shade3(color)
    o = [tt(U(E(0, 0, 40, 24), P("M -38 -4 Q -54 -22 -44 -28 L -28 -12 Z")), *c),
         tt(C(30, -30, 18), *c), tt(P("M 44 -32 L 64 -27 L 44 -21 Z"), *shade3(bill)),
         tt(P("M -18 -10 Q 4 -22 22 -6 Q 4 4 -18 -10 Z"), *shade3(c[1], 0.9)),
         '<circle cx="34" cy="-34" r="3.6" fill="#1E1230"/><circle cx="33" cy="-35.4" r="1.2" fill="#fff"/>']
    return "".join(o)


def dog(color="#D99A5A"):
    c = shade3(color)
    o = [tt(S("M -46 -40 Q -70 -60 -62 -80", 12), *c),
         tt(R(-50, -66, 92, 42, 20), *c)]
    for x in (-40, -20, 18, 34):
        o.append(tt(R(x, -34, 12, 34, 5), *c))
    o.append(tt(U(C(48, -76, 26), E(66, -66, 18, 12)), *c))
    o.append(tt(P("M 30 -92 Q 20 -66 34 -58 Q 40 -78 36 -94 Z"), *shade3("#8A5A3A")))
    o.append('<circle cx="52" cy="-80" r="4.5" fill="#1E1230"/><circle cx="51" cy="-81.5" r="1.4" fill="#fff"/><ellipse cx="82" cy="-68" rx="6" ry="5" fill="#1E1230"/>')
    o.append('<path d="M68 -58 Q74 -52 80 -58" stroke="#1E1230" stroke-width="3" fill="none" stroke-linecap="round"/>')
    o.append(tt(R(28, -54, 36, 9, 4), *shade3("#E8504A")))
    return "".join(o)


CAST = {
    "Mira": Look(skin="#9A5E3E", hair="#1E2244", hairstyle="bob", top="#2F8E70", top_style="sweater", bottom="#2E3F8E", shoe="#F4EDE6", glasses=True),
    "June": Look(skin="#F2C3A0", hair="#A8442E", hairstyle="bun", top="#F2B132", top_style="coat", bottom="#5A2A6E", shoe="#2A1A3A", scarf="#2A8FC0"),
    "Remy": Look(skin="#C98B62", hair="#2A1A1A", hairstyle="crop", top="#FF6F61", top_style="hoodie", bottom="#5A6478", shoe="#2A2A4A", under="#FFF3E0"),
    "Ravi": Look(skin="#B07A52", hair="#ECE6F2", hairstyle="bald", beard="#ECE6F2", top="#1FA98C", top_style="cardigan", bottom="#7A5A3E", shoe="#4A2E1E", glasses=True, under="#FFF3E0"),
    "Leo": Look(skin="#E8B08A", hair="#6A3A1E", hairstyle="curly", top="#FFC94A", top_style="raincoat", bottom="#3E5ABE", shoe="#E8504A"),
}
