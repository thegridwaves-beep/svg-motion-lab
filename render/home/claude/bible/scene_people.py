"""Characters drawn exactly in the bench-scene style: organic filled shapes, warm rim light
clipped inside each shape, cool shadows, same heads and faces. Feet at (0,0), front view.
Light: warm sun from behind-right (rim on the right edge), soft fill from the left."""
import math
import kit as K
from kit import tt, inside, P, S, E, C, R, U, g

DK = "#1E1230"


class Person:
    def __init__(self, **kw):
        self.__dict__.update(kw)


MIRA = Person(name="Mira", skin=("#9A5E3E", "#7A4630", "#C9865E"), hair=("#1E2244", "#141634", "#46518A"), hairstyle="bob", glasses=True,
             top=("#2F8E70", "#21705A", "#FFB27A"), top_style="sweater", bottom=("#2E3F8E", "#22306E", "#5A70C8"),
             shoe=("#F4EDE6", "#C9BFD8"), accent=None)
JUNE = Person(name="June", skin=("#F2C3A0", "#D89A78", "#FFE2C8"), hair=("#A8442E", "#7E2E1E", "#E07850"), hairstyle="bun", glasses=False,
              top=("#F2B132", "#C9861C", "#FFE3A8"), top_style="coat", bottom=("#5A2A6E", "#43205A", "#8A4AA0"),
              shoe=("#2A1A3A", "#14101E"), accent=("#2A8FC0", "#1E6E98", "#7FD0F0"))


def rimmed(shape, base, shade, rim, rim_w=7, split=0.55):
    """Base + cool shadow on the right part + warm rim on the right edge, all clipped inside."""
    content = (f'<rect x="-400" y="-900" width="800" height="1200" fill="{base}"/>'
               f'<g transform="translate({rim_w} 0)">{shape(shade)}</g>')
    inner = inside(shape, content)
    # shadow half: the shape shifted left leaves the right portion; we want shade on right side
    f1, d1 = K.blur_f(rim_w * 0.45)
    f2, d2 = K.blur_f(rim_w * 0.25)
    return (d1 + d2 + inside(shape, f'<rect x="-400" y="-900" width="800" height="1200" fill="{shade}"/>'
                          f'<g{f1}><g transform="translate({-rim_w*2.2:.1f} -4)">{shape(base)}</g></g>') +
            inside(shape, f'<g opacity="0.95"{f2}>{_rim_band(shape, rim, rim_w)}</g>'))


def _rim_band(shape, rim, w):
    mid = K.uid("rb")
    return (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-2000" y="-2000" width="4000" height="4000">'
            f'<rect x="-2000" y="-2000" width="4000" height="4000" fill="#fff"/><g transform="translate({-w} 0)">{shape("#000")}</g></mask>'
            f'<g mask="url(#{mid})">{shape(rim)}</g>')


def head(p, expr="neutral", tilt=0):
    sk, hr = p.skin, p.hair
    o = []
    if p.hairstyle == "bob":
        o.append(rimmed(P("M -60 34 Q -70 -70 0 -74 Q 68 -70 60 30 L 44 30 Q 40 -20 4 -30 Q -30 -20 -40 34 Z"), *hr, 5))
    o.append(rimmed(U(E(-50, 4, 9, 13), E(50, 4, 9, 13)), sk[0], sk[1], sk[2], 3))
    o.append(rimmed(E(0, 0, 50, 56), *sk, 6))
    if p.hairstyle == "bob":
        o.append(rimmed(P("M -58 -4 Q -64 -72 0 -76 Q 66 -72 58 -6 Q 40 -36 6 -40 Q -30 -34 -58 -4 Z"), *hr, 5))
        o.append(inside(P("M -58 -4 Q -64 -72 0 -76 Q 66 -72 58 -6 Q 40 -36 6 -40 Q -30 -34 -58 -4 Z"),
                        '<path d="M-26 -60 Q6 -72 34 -58 L33 -54 Q6 -66 -25 -55 Z" fill="#46518A"/>'))
    if p.hairstyle == "bun":
        cap = P("M -52 4 Q -58 -66 0 -62 Q 56 -64 52 2 Q 30 -34 0 -36 Q -30 -34 -52 4 Z")
        o.append(rimmed(C(4, -84, 30), *hr, 6))
        o.append(inside(C(4, -84, 30), '<path d="M-18 -100 Q4 -114 28 -96 L26 -88 Q4 -104 -16 -92 Z" fill="#E07850"/>'))
        o.append(rimmed(cap, *hr, 5))
        o.append(inside(cap, '<path d="M-18 -50 Q12 -60 36 -44 L35 -40 Q12 -55 -17 -46 Z" fill="#D2633F"/>'))
    o.append(K.face(expr, K.Look(skin=sk[0], hair=hr[0], hairstyle="bob")))
    if p.glasses:
        o.append('<circle cx="-20" cy="-2" r="16" fill="#FFFFFF" opacity="0.12"/><circle cx="20" cy="-2" r="16" fill="#FFFFFF" opacity="0.12"/>'
                 f'<circle cx="-20" cy="-2" r="16" fill="none" stroke="#2A1A3A" stroke-width="4"/><circle cx="20" cy="-2" r="16" fill="none" stroke="#2A1A3A" stroke-width="4"/>'
                 f'<path d="M-4 -4 Q0 -8 4 -4" stroke="#2A1A3A" stroke-width="4" fill="none"/>')
    return f'<g transform="rotate({tilt})">{"".join(o)}</g>'


LEGS = {
    "stand": [(-24, -204, -26, -16), (24, -204, 26, -16)],
    "walk": [(-20, -204, -58, -20), (20, -204, 44, -28)],
}
ARMS = {
    "stand": [(-58, -350, -84, -280, -76, -214), (58, -350, 84, -280, 76, -214)],
    "walk": [(-58, -350, -70, -280, -46, -220), (58, -350, 94, -290, 104, -232)],
    "wave": [(-58, -350, -84, -280, -76, -214), (58, -350, 110, -400, 112, -470)],
    "point": [(-58, -350, -84, -280, -76, -214), (58, -350, 130, -380, 190, -420)],
    "think": [(-58, -350, -76, -276, -22, -262), (58, -350, 84, -320, 26, -406)],
    "cheer": [(-58, -350, -110, -400, -118, -470), (58, -350, 110, -400, 118, -470)],
    "hold": [(-58, -350, -84, -290, -30, -262), (58, -350, 84, -290, 30, -262)],
}


def person(p, pose="stand", expr="neutral", prop=None):
    o = []
    legs = LEGS["walk" if pose == "walk" else "stand"]
    # legs as filled tapered trouser shapes, one leg in shadow
    for i, (hx, hy, fx, fy) in enumerate(legs):
        col = (p.bottom[0], p.bottom[1], p.bottom[0]) if i == 0 else (p.bottom[1], p.bottom[1], p.bottom[2])
        shape = P(f"M {hx-22} {hy} L {hx+22} {hy} L {fx+16} {fy} Q {fx} {fy+6} {fx-16} {fy} Z")
        o.append(rimmed(shape, *col, 5))
        shoe = P(f"M {fx-26} {fy+16} Q {fx-28} {fy-6} {fx-6} {fy-8} Q {fx+20} {fy-8} {fx+26} {fy+10} Q {fx+26} {fy+18} {fx+16} {fy+18} L {fx-18} {fy+18} Q {fx-26} {fy+18} {fx-26} {fy+16} Z")
        o.append(rimmed(shoe, p.shoe[0], p.shoe[1], "#FFFFFF", 3))
        o.append(inside(shoe, f'<rect x="{fx-30}" y="{fy+12}" width="60" height="8" fill="{p.shoe[1]}"/>'))
    # torso
    if p.top_style == "coat":
        torso = P("M -66 -150 Q -78 -330 -8 -370 Q 64 -372 70 -296 L 70 -150 Q 0 -138 -66 -150 Z")
    else:
        torso = P("M -66 -196 Q -76 -330 -10 -370 Q 58 -372 64 -300 L 60 -196 Q 0 -184 -66 -196 Z")
    o.append(rimmed(torso, *p.top, 8))
    if p.top_style == "sweater":
        o.append(inside(torso, "".join(f'<rect x="{-62+i*10}" y="-222" width="4" height="26" fill="{p.top[1]}" opacity="0.7"/>' for i in range(13))))
        o.append(rimmed(R(-26, -388, 52, 26, 11), *p.top, 4))
    if p.top_style == "coat":
        o.append(inside(torso, f'<rect x="2" y="-372" width="4" height="240" fill="{p.top[1]}"/>'
                               f'<path d="M -30 -370 L 4 -326 L 4 -370 Z" fill="{p.top[1]}"/>'
                               f'<rect x="-56" y="-200" width="34" height="8" rx="4" fill="{p.top[1]}"/><rect x="24" y="-200" width="34" height="8" rx="4" fill="{p.top[1]}"/>'))
        for i in range(3):
            o.append(rimmed(C(-12, -300 + i * 44, 6), "#8A4A1A", "#6A3410", "#C88A5A", 2))
    # neck
    o.append(inside(R(-13, -400, 26, 36, 6), f'<rect x="-20" y="-410" width="40" height="60" fill="{p.skin[1]}"/>'))
    # scarf (June)
    if p.accent:
        band = R(-54, -398, 108, 32, 16)
        tail = P("M 22 -374 L 46 -374 L 42 -286 L 20 -290 Z")
        o.append(rimmed(U(band, tail), *p.accent, 5))
        o.append(inside(U(band, tail), "".join(f'<rect x="{-50+i*20}" y="-420" width="5" height="160" fill="{p.accent[1]}" transform="rotate(14 {-50+i*20} -380)"/>' for i in range(9))))
    # head
    hd = g(head(p, expr, -6 if expr == "laugh" else 0), 0, -444)
    arms = ARMS.get(pose, ARMS["stand"])
    late = []
    for j, (sx, sy, ex, ey, hx, hy) in enumerate(arms):
        arm = S(f"M {sx} {sy} Q {ex} {ey} {hx} {hy}", 30)
        col = (p.top[0], p.top[1], p.top[0]) if j == 0 else (p.top[1], p.top[1], p.top[2])
        sk = (p.skin[0], p.skin[1], p.skin[0]) if j == 0 else p.skin
        piece = rimmed(arm, *col, 5) + rimmed(C(hx, hy, 15), *sk, 3)
        (late if pose == "think" and j == 1 else o).append(piece)
    o.append(hd)
    o.extend(late)
    if prop == "book":
        o.append(g(_book(), 0, -258))
    if prop == "cup":
        o.append(g(_cup(), 0, -236))
    return "".join(o)


def _book():
    cover = P("M -70 0 L 0 12 L 70 0 L 64 50 L 0 62 L -64 50 Z")
    return (rimmed(cover, "#D8483E", "#A83030", "#FF8A70", 4) +
            inside(P("M -62 -6 L 0 6 L 0 54 L -58 44 Z"), '<rect x="-80" y="-20" width="90" height="90" fill="#FFF6EA"/>' +
                   "".join(f'<rect x="-52" y="{4+i*9}" width="40" height="2.5" fill="#C9B8A8" transform="rotate(8 -52 {4+i*9})"/>' for i in range(4))) +
            inside(P("M 62 -6 L 0 6 L 0 54 L 58 44 Z"), '<rect x="-10" y="-20" width="90" height="90" fill="#F0E2D0"/>'))


def _cup():
    body = P("M -24 -60 L 24 -60 L 19 0 Q 0 4 -19 0 Z")
    return (rimmed(body, "#FFF3F6", "#E8D8DE", "#FFFFFF", 3) + inside(body, '<rect x="-30" y="-36" width="60" height="16" fill="#5A7AE0"/>') +
            rimmed(R(-28, -72, 56, 14, 6), "#7A3A2A", "#5A2418", "#A85A40", 2) +
            '<path d="M-6 -82 q-10 -16 0 -30 q10 -14 0 -28 M10 -84 q-8 -12 0 -24" stroke="#FFFFFF" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.6"/>')
