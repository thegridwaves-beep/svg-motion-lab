"""A posable version of the Sandbox person: arm/leg poses blend smoothly, head tilts, eyes blink, body squashes."""
import sys
sys.path.insert(0, "/home/claude/bible")
import kit as K
from kit import inside, P, S, E, C, R, U, g
import scene_people as SP
from scene_people import rimmed, head, LEGS, ARMS

ARMS = dict(ARMS)
ARMS.update({
    "brace": [(-58, -350, -110, -300, -120, -230), (58, -350, 110, -300, 120, -230)],
    "shiver": [(-58, -350, -40, -300, 26, -300), (58, -350, 40, -300, -26, -300)],
    "thumbs": [(-58, -350, -84, -280, -76, -214), (58, -350, 120, -330, 92, -410)],
    "fall": [(-58, -350, -130, -380, -170, -440), (58, -350, 130, -380, 170, -440)],
    "head": [(-58, -350, -110, -420, -40, -470), (58, -350, 110, -420, 40, -470)],
    "fist": [(-58, -350, -84, -280, -76, -214), (58, -350, 100, -300, 60, -330)],
})
LEGS = dict(LEGS)
LEGS["crouch"] = [(-24, -190, -40, -16), (24, -190, 40, -16)]
LEGS["fall"] = [(-20, -204, -50, -40), (20, -204, 36, -10)]


def lerp_pose(a, b, u):
    return [tuple(x + (y - x) * u for x, y in zip(pa, pb)) for pa, pb in zip(a, b)]


def person(p, arms, legs, expr="neutral", tilt=0.0, blink=False, prop=None):
    o = []
    for i, (hx, hy, fx, fy) in enumerate(legs):
        col = (p.bottom[0], p.bottom[1], p.bottom[0]) if i == 0 else (p.bottom[1], p.bottom[1], p.bottom[2])
        shape = P(f"M {hx-22:.1f} {hy:.1f} L {hx+22:.1f} {hy:.1f} L {fx+16:.1f} {fy:.1f} Q {fx:.1f} {fy+6:.1f} {fx-16:.1f} {fy:.1f} Z")
        o.append(rimmed(shape, *col, 5))
        shoe = P(f"M {fx-26:.1f} {fy+16:.1f} Q {fx-28:.1f} {fy-6:.1f} {fx-6:.1f} {fy-8:.1f} Q {fx+20:.1f} {fy-8:.1f} {fx+26:.1f} {fy+10:.1f} Q {fx+26:.1f} {fy+18:.1f} {fx+16:.1f} {fy+18:.1f} L {fx-18:.1f} {fy+18:.1f} Q {fx-26:.1f} {fy+18:.1f} {fx-26:.1f} {fy+16:.1f} Z")
        o.append(rimmed(shoe, p.shoe[0], p.shoe[1], "#FFFFFF", 3))
    torso = P("M -66 -196 Q -76 -330 -10 -370 Q 58 -372 64 -300 L 60 -196 Q 0 -184 -66 -196 Z")
    o.append(rimmed(torso, *p.top, 8))
    o.append(inside(torso, "".join(f'<rect x="{-62+i*10}" y="-222" width="4" height="26" fill="{p.top[1]}" opacity="0.7"/>' for i in range(13))))
    o.append(rimmed(R(-26, -388, 52, 26, 11), *p.top, 4))
    o.append(inside(R(-13, -400, 26, 36, 6), f'<rect x="-20" y="-410" width="40" height="60" fill="{p.skin[1]}"/>'))
    hd = g(head(p, "sleepy" if blink else expr, tilt), 0, -444)
    late = []
    for j, (sx, sy, ex, ey, hx, hy) in enumerate(arms):
        arm = S(f"M {sx:.1f} {sy:.1f} Q {ex:.1f} {ey:.1f} {hx:.1f} {hy:.1f}", 30)
        col = (p.top[0], p.top[1], p.top[0]) if j == 0 else (p.top[1], p.top[1], p.top[2])
        sk = (p.skin[0], p.skin[1], p.skin[0]) if j == 0 else p.skin
        piece = rimmed(arm, *col, 5) + rimmed(C(hx, hy, 15), *sk, 3)
        (late if hy < -380 and abs(hx) < 60 else o).append(piece)
    o.append(hd)
    o.extend(late)
    if prop:
        o.append(prop)
    return "".join(o)
