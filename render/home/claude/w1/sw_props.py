"""Screwworm Short props: 3D screwworm fly, eggs, screw maggots, campsite at night/dawn, x-ray head, clinic, plane, map."""
import math, random
from wcore import *
from botfly import skin_macro, bokeh, SURF, skin_xsec
from botfly_mt import fg_hairs, dust, flare, streaks, hstreaks, flashw
import geo

L_NIGHT = Light("swNight", amb=(0.55, 0.62, 0.9), sat=0.8, key="#FF9A4A", key_op=0.45, ang=-20, spread=0.7, shade="#05081A", shade_op=0.55, rim="#9AB8FF", rim_op=0.5, rim_w=7)
L_DAY = Light("swDay", amb=(1.0, 0.95, 0.88), sat=1.0, key="#FFE0A0", key_op=0.35, ang=-60, spread=0.8, shade="#2A1A3A", shade_op=0.3, rim="#FFF0C8", rim_op=0.45, rim_w=7)
L_CLIN = Light("swClin", amb=(0.96, 0.99, 1.02), sat=0.95, key="#E8F4FF", key_op=0.3, ang=-80, spread=0.9, shade="#2A3A5A", shade_op=0.3, rim="#FFFFFF", rim_op=0.4, rim_w=6)
SHADE = "#05030F"


# ------------------------------------------------------------------ 3D screwworm fly (same projection idea as mosq3d)
def fly3d(ox, oy, s=1.0, yaw_deg=0.0, t=0.0, flap=0.0, legs="land", glow_eyes=0.0):
    """New World screwworm fly: metallic blue-green body with three dark stripes on the thorax, big orange-red eyes.
    Model: head at +x, ~90 units long at s=1. yaw 0 = side view facing right, -90 = head-on."""
    yaw = math.radians(yaw_deg); c, si = math.cos(yaw), math.sin(yaw)
    items = []

    def P(p):
        x, y, z = p
        return ox + (x * c - z * si) * s, oy + y * s, x * si + z * c

    def dk(Z):
        return max(0.0, min(0.45, Z / 60.0 * 0.25))

    def ell(p, rx, ry, rz, col, hl=0.18, op=1.0):
        X, Y, Z = P(p); prx = math.sqrt((rx * c) ** 2 + (rz * si) ** 2)
        items.append((Z, f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{prx * s:.1f}" ry="{ry * s:.1f}" fill="{mixc(col, SHADE, dk(Z))}" opacity="{op:.2f}"/>'
                         f'<ellipse cx="{X - 0.25 * prx * s:.1f}" cy="{Y - 0.45 * ry * s:.1f}" rx="{0.45 * prx * s:.1f}" ry="{0.25 * ry * s:.1f}" fill="#E8FFF8" opacity="{hl:.2f}"/>'))

    def line(pts, col, w, op=1.0):
        q = [P(p) for p in pts]; Z = sum(z for *_, z in q) / len(q)
        items.append((Z, f'<path d="M{" L".join(f"{x:.1f} {y:.1f}" for x, y, _ in q)}" stroke="{col}" stroke-width="{w * s:.1f}" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="{op:.2f}"/>'))

    def poly(pts, col, op=1.0, stroke=None):
        q = [P(p) for p in pts]; Z = sum(z for *_, z in q) / len(q)
        st = f' stroke="{stroke}" stroke-width="{1.0 * s:.1f}"' if stroke else ""
        items.append((Z, f'<path d="M{" L".join(f"{x:.1f} {y:.1f}" for x, y, _ in q)} Z" fill="{col}" opacity="{op:.2f}"{st}/>'))

    ell((-18, 2, 0), 22, 17, 16, "#1E7A7A", 0.25)                 # abdomen
    ell((-18, 2, 0), 14, 9, 10, "#2AA8A0", 0.0, 0.5)
    ell((8, -2, 0), 16, 15, 14, "#1E8A88", 0.22)                   # thorax
    for zz in (-6, 0, 6):                                          # the 3 dark stripes
        line([(-2, -15, zz), (8, -17, zz * 1.05), (20, -13, zz)], "#0E2A2E", 3.0, 0.9)
    ell((28, 0, 0), 8, 9, 10, "#2A5A5A")                           # head
    for zz in (-6.5, 6.5):
        X, Y, Z = P((31, -2, zz)); rr = (7.5 - 2.5 * abs(si)) * s
        items.append((Z - 0.5, f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{rr:.1f}" fill="{mixc("#E8502A", SHADE, dk(Z))}"/><circle cx="{X - 2 * s:.1f}" cy="{Y - 2.5 * s:.1f}" r="{2 * s:.1f}" fill="#FFD0A0" opacity="0.8"/>'
                            + (glow(X, Y, 9 * s, "#FF6A2A", 0.35 * glow_eyes, 3) if glow_eyes > 0 else "")))
    line([(34, 6, 0), (38, 12, 0)], "#1A1414", 3.0)
    for k, hx in enumerate((2, 8, 14)):
        for side in (-1, 1):
            knee = (hx + (-18, 0, 18)[k], 18, side * (16 + 4 * k)) if legs == "land" else (hx - 8, 16, side * 8)
            foot = (hx + (-34, -2, 34)[k], 32, side * (26 + 5 * k)) if legs == "land" else (hx - 20, 30, side * 12)
            line([(hx, 8, side * 4), knee, foot], "#141414", 2.4)
    fl = math.sin(t * 40) * flap
    for side in (-1, 1):
        lift = 20 * fl if flap > 0 else 0
        poly([(8, -14, side * 4), (-10, -26 - lift, side * (16 + 8 * flap)), (-42, -18 - lift, side * (20 + 6 * flap)), (-30, -8, side * 8)], "#E8F4FF", 0.35, "#B8D0E0")
    items.sort(key=lambda it: -it[0])
    return "".join(v for _, v in items)


# ------------------------------------------------------------------ eggs and screw maggots
def egg_rice(x, y, s=1.0, rot=0.0, hatch=0.0):
    o = f'<ellipse cx="0" cy="0" rx="2.4" ry="6.5" fill="#FFF8EC" stroke="#D8C8A8" stroke-width="0.6"/><ellipse cx="-0.6" cy="-2" rx="0.8" ry="2.4" fill="#FFFFFF"/>'
    if hatch > 0:
        o = f'<g opacity="{1 - 0.6 * hatch:.2f}">{o}</g><path d="M0 -6 L0 {-6 - 6 * hatch:.1f}" stroke="#F4E4D0" stroke-width="2.6" stroke-linecap="round"/>'
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">{o}</g>'


def egg_shingles(cx, cy, length, n, laid=1.0, s=1.0, hatch=0.0, seed=4, ang=0.0):
    """Eggs stacked like roof shingles along a line (the cut's edge). laid 0..1 = how many are down."""
    r = random.Random(seed); o = []
    m = int(n * laid)
    for k in range(m):
        u = k / max(1, n - 1)
        x = cx - length / 2 + length * u + r.uniform(-3, 3); y = cy + r.uniform(-6, 6)
        o.append(egg_rice(x, y, s, ang + 60 + r.uniform(-10, 10), hatch))
    return "".join(o)


def cut(x, y, L=160, w=10, s=1.0, open_=0.0, wet=1.0, ang=0.0):
    """A small cut seen from above: a thin red slit with a wet glint; open_ widens it into a wound."""
    ww = w + 60 * open_
    o = (f'<ellipse cx="0" cy="0" rx="{L / 2 + 30 * open_:.0f}" ry="{ww / 2 + 10:.0f}" fill="#E8907A" opacity="0.6"/>'
         f'<path d="M{-L / 2} 0 Q0 {-ww / 2:.1f} {L / 2} 0 Q0 {ww / 2:.1f} {-L / 2} 0 Z" fill="#B8202E"/>'
         f'<path d="M{-L / 2 + 10} 0 Q0 {-ww / 4:.1f} {L / 2 - 10} 0" stroke="#7A0E1A" stroke-width="{3 + 10 * open_:.1f}" fill="none"/>'
         f'<path d="M{-L / 3} {-ww / 4:.1f} Q0 {-ww / 2.4:.1f} {L / 3} {-ww / 4:.1f}" stroke="#FFFFFF" stroke-width="2.4" fill="none" opacity="{0.6 * wet:.2f}"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})">{o}</g>'


def screw_maggot(x, y, s=1.0, t=0.0, rot=0.0, spin=1.0, wig=1.0):
    """Screwworm larva: white, tapered to a pointed head (+x), with rings of dark spines that spiral as it turns (spin)."""
    o = []; n = 11
    for k in range(n, -1, -1):
        u = k / n
        w = 4 + 14 * math.sin(math.pi * (0.15 + 0.7 * (1 - u))) if u < 0.92 else 3.5
        px = -36 + 76 * u; py = 3 * wig * math.sin(t * 8 - k * 0.8)
        o.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="5.5" ry="{w:.1f}" fill="{mixc("#FFF8F0", "#EAD8C8", u * 0.6)}" stroke="#D8C0A8" stroke-width="1"/>')
        if 1 <= k <= 9:
            ph = (t * 6 * spin + k * 0.7) % 1.0
            yy = py - w + 2 * w * ph
            o.append(f'<path d="M{px - 3:.1f} {yy:.1f} l6 -2" stroke="#2A1408" stroke-width="2.2" stroke-linecap="round" opacity="0.85"/>')
            yy2 = py - w + 2 * w * ((ph + 0.5) % 1.0)
            o.append(f'<path d="M{px - 3:.1f} {yy2:.1f} l6 -2" stroke="#2A1408" stroke-width="2.2" stroke-linecap="round" opacity="0.5"/>')
    hy = 3 * wig * math.sin(t * 8)
    o.append(f'<path d="M40 {hy - 2:.1f} l7 -3 M40 {hy + 2:.1f} l7 3" stroke="#14080A" stroke-width="2.4" stroke-linecap="round"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">{"".join(o)}</g>'


# ------------------------------------------------------------------ campsite
def sky(t, day=0.0):
    top = mixc("#060A24", "#5AB0F0", day); mid = mixc("#1A1A4A", "#FFB070", clamp(day * 1.6) * (1 - clamp((day - 0.6) * 2.5)) + clamp((day - 0.6) * 2.5) * 0.0)
    bot = mixc("#3A2A5A", "#FFE0A0", day)
    r = random.Random(7)
    st = "".join(f'<circle cx="{r.uniform(-300, 1260):.0f}" cy="{r.uniform(-500, 260):.0f}" r="{r.uniform(1, 2.6):.1f}" fill="#FFFFFF" opacity="{(1 - day) * r.uniform(0.4, 1) * (0.7 + 0.3 * math.sin(t * 3 + _)):.2f}"/>' for _ in range(120))
    moon = f'<circle cx="640" cy="-120" r="44" fill="#F4F0DC" opacity="{1 - day:.2f}"/>' + glow(640, -120, 140, "#CFE0FF", 0.3 * (1 - day), 20)
    sun = ""
    if day > 0.05:
        sy = lerp(330, -60, day)
        sun = glow(300, sy, 220, "#FFD890", 0.7 * day, 30) + f'<circle cx="300" cy="{sy:.0f}" r="46" fill="#FFF0B0" opacity="{day:.2f}"/>'
    return (f'<rect x="-600" y="-700" width="2160" height="1200" fill="{top}"/>'
            f'<rect x="-600" y="-100" width="2160" height="500" fill="{mid}" opacity="0.6" filter="url(#b40)"/>'
            f'<rect x="-600" y="200" width="2160" height="200" fill="{bot}" opacity="0.6" filter="url(#b30)"/>' + st + moon + sun)


def trees(day=0.0, seed=5, y0=330):
    r = random.Random(seed); o = []
    col = mixc("#0A1024", "#2E5A3A", day)
    for k in range(16):
        x = -300 + k * 110 + r.uniform(-30, 30); h = r.uniform(160, 280)
        o.append(f'<path d="M{x} {y0} L{x + 46} {y0 - h} L{x + 92} {y0} Z" fill="{col}"/><path d="M{x + 10} {y0 - h * 0.45} L{x + 46} {y0 - h * 1.05} L{x + 82} {y0 - h * 0.45} Z" fill="{col}"/>')
    return "".join(o)


def campfire(x, y, t, s=1.0, out=0.0):
    f = 1 - out
    flames = "".join(f'<path d="M{-14 + 14 * k} 0 Q{-24 + 14 * k + 6 * math.sin(t * 9 + k)} {-30 - 18 * f} {-4 + 10 * k} {-60 * f - 10 * math.sin(t * 7 + k)} Q{12 + 10 * k} -30 {10 + 12 * k} 0 Z" fill="{("#FF8A2A", "#FFD03A", "#FF5A2A")[k]}" opacity="{0.9 * f:.2f}"/>' for k in range(3))
    logs = '<rect x="-40" y="-8" width="80" height="14" rx="7" fill="#5A3A22" transform="rotate(12)"/><rect x="-40" y="-8" width="80" height="14" rx="7" fill="#6A4A2A" transform="rotate(-12)"/>'
    smoke = "".join(f'<circle cx="{6 * math.sin(t + k):.1f}" cy="{-60 - ((t * 30 + k * 30) % 120):.1f}" r="{8 + k * 3}" fill="#8A8A9A" opacity="{0.25 * out:.2f}" filter="url(#b6)"/>' for k in range(4))
    return f'<g transform="translate({x} {y}) scale({s})">' + glow(0, -20, 120, "#FF8A3A", 0.5 * f, 20) + logs + flames + smoke + '</g>'


def tent(x, y, s=1.0, day=0.0):
    c1, c2 = mixc("#3A4A8A", "#E8703A", day), mixc("#2A3466", "#C8502A", day)
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M-120 0 L0 -150 L120 0 Z" fill="{c1}"/><path d="M0 -150 L120 0 L60 0 Z" fill="{c2}"/>'
            f'<path d="M-22 0 L0 -70 L22 0 Z" fill="#14101C"/><path d="M0 -150 L0 -170" stroke="#AAAAAA" stroke-width="3"/></g>')


def sleeper(t, x=480, y=410, s=1.0, Lt=None, face=None, zip_=0.0, ankle=True, uid="slp", bag="#C83A5A"):
    """The boy asleep on his back in a sleeping bag, head to the left, bare ankle poking out of the bag at the right."""
    Lt = Lt or L_NIGHT
    fc_ = face or fc(open=0.0, mouth="smile", lift=0.1, look=(0, 0))
    J = R3.FRONT | dict(face=fc_)
    head = (f'<g transform="translate({x - 150 * s:.1f} {y - 18 * s:.1f}) rotate(-90) scale({0.55 * s:.3f})"><clipPath id="hc{uid}"><circle cx="0" cy="-6" r="92"/></clipPath>'
            f'<g clip-path="url(#hc{uid})">{boy(J, uid, 0, 438, 1.0, Lt)}</g></g>')
    breathe = 3 * math.sin(t * 1.6) * s
    bagp = (f'<path d="M{x - 150 * s:.1f} {y - 38 * s - breathe:.1f} Q{x:.1f} {y - 70 * s - breathe:.1f} {x + 170 * s:.1f} {y - 40 * s:.1f} Q{x + 200 * s:.1f} {y - 20 * s:.1f} {x + 170 * s:.1f} {y + 10 * s:.1f} L{x - 160 * s:.1f} {y + 14 * s:.1f} Z" fill="{bag}"/>'
            f'<path d="M{x - 140 * s:.1f} {y - 10 * s:.1f} Q{x:.1f} {y - 30 * s - breathe:.1f} {x + 160 * s:.1f} {y - 12 * s:.1f}" stroke="#FFFFFF" stroke-width="{3 * s:.1f}" opacity="0.3" fill="none"/>')
    if zip_ > 0:
        bagp += f'<path d="M{x - 150 * s:.1f} {y - 40 * s:.1f} L{x - 150 * s - 90 * zip_ * s:.1f} {y - 50 * s:.1f} L{x - 150 * s - 90 * zip_ * s:.1f} {y + 14 * s:.1f} L{x - 150 * s:.1f} {y + 14 * s:.1f} Z" fill="{bag}"/>'
    ank = ""
    if ankle:
        ax, ay = x + 190 * s, y - 14 * s
        ank = (f'<path d="M{ax - 30 * s:.1f} {ay - 12 * s:.1f} L{ax + 40 * s:.1f} {ay - 16 * s:.1f} Q{ax + 64 * s:.1f} {ay - 18 * s:.1f} {ax + 66 * s:.1f} {ay:.1f} L{ax + 70 * s:.1f} {ay + 14 * s:.1f} L{ax - 30 * s:.1f} {ay + 14 * s:.1f} Z" fill="{R3.YOU.skin[0]}"/>'
               + cut(ax + 14 * s, ay - 2 * s, 18, 2, s, 0, 1.0, -8))
    pad = f'<ellipse cx="{x:.1f}" cy="{y + 16 * s:.1f}" rx="{260 * s:.1f}" ry="{20 * s:.1f}" fill="#05030F" opacity="0.35" filter="url(#b6)"/>'
    pillow = f'<ellipse cx="{x - 190 * s:.1f}" cy="{y - 4 * s:.1f}" rx="{70 * s:.1f}" ry="{26 * s:.1f}" fill="#E8E4F4"/>'
    return pad + pillow + bagp + head + ank


def ground(day=0.0, y0=330):
    return (f'<rect x="-600" y="{y0}" width="2160" height="900" fill="{mixc("#141E2A", "#5A8A4A", day)}"/>'
            + "".join(f'<path d="M{-300 + k * 37} {y0 + 30 + (k * 53) % 300} q4 -14 10 -20" stroke="{mixc("#24323E", "#3E6A3A", day)}" stroke-width="3" fill="none"/>' for k in range(60)))


def campsite(t, day=0.0, fire_out=0.0, sleeper_on=True, zip_=0.0, face=None):
    return (sky(t, day) + trees(day) + ground(day) + tent(250, 390, 1.0, day) + campfire(660, 420, t, 1.0, fire_out)
            + (sleeper(t, 480, 470, 0.78, L_DAY if day > 0.5 else L_NIGHT, face=face, zip_=zip_) if sleeper_on else ""))


# ------------------------------------------------------------------ x-ray head (side) with the nose-to-brain path
def xray_head(t, prog=0.0, hot=0.0):
    o = ['<rect x="-600" y="-600" width="2160" height="1800" fill="url(#xskin)"/>']
    o += [f'<path d="M-600 {y} L1560 {y}" stroke="#1A3A7A" stroke-width="1" opacity="0.4"/>' for y in range(-600, 1200, 40)]
    o.append('<path d="M330 520 Q300 380 330 260 Q350 110 480 70 Q620 40 680 150 Q700 210 690 250 L740 300 L712 314 Q720 336 712 350 L726 372 Q700 400 700 430 Q690 470 640 476 L600 480 Q596 520 600 600" fill="#0E2A5A" stroke="#7AE8FF" stroke-width="3"/>')
    o.append(f'<path d="M360 250 Q360 120 470 96 Q590 76 650 160 Q670 220 600 236 Q480 250 360 250 Z" fill="{mixc("#C8A8E8", "#FF3A4A", hot)}" opacity="0.55" stroke="#E8D0FF" stroke-width="2"/>')
    o.append(''.join(f'<path d="M{400 + 40 * k} {120 + 10 * (k % 2)} q20 30 0 60 q-20 30 0 60" stroke="#E8D0FF" stroke-width="2" fill="none" opacity="0.5"/>' for k in range(6)))
    o.append('<path d="M712 330 Q660 320 620 300 Q590 280 600 250" stroke="#7AE8FF" stroke-width="18" fill="none" opacity="0.6" stroke-linecap="round"/>')
    if prog > 0:
        pts = [(712, 330), (660, 318), (620, 298), (598, 262), (580, 230), (540, 200)]
        n = len(pts) - 1; f = min(prog * n, n - 1e-6); i = int(f); v = f - i
        trail = "M" + " L".join(f"{x} {y}" for x, y in pts[:i + 1]) + f" L{lerp(pts[i][0], pts[i + 1][0], v):.1f} {lerp(pts[i][1], pts[i + 1][1], v):.1f}"
        o.append(f'<path d="{trail}" stroke="#FF3A4A" stroke-width="10" fill="none" stroke-linecap="round" opacity="0.85"/>')
        hx, hy = lerp(pts[i][0], pts[i + 1][0], v), lerp(pts[i][1], pts[i + 1][1], v)
        o.append(glow(hx, hy, 40, "#FF5A3A", 0.8, 6) + screw_maggot(hx, hy, 0.5, t, math.degrees(math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])), 1.5))
    return "".join(o)


# ------------------------------------------------------------------ clinic, plane, map
def clinic(t):
    return ('<rect x="-600" y="-600" width="2160" height="1800" fill="url(#hospW)"/>'
            '<rect x="-600" y="420" width="2160" height="600" fill="#C8D8E4"/><rect x="-600" y="416" width="2160" height="8" fill="#A8B8C8"/>'
            '<rect x="560" y="120" width="160" height="200" rx="8" fill="#FFFFFF" stroke="#A8C0D8" stroke-width="6"/><path d="M640 150 L640 290 M590 220 L690 220" stroke="#E84A5A" stroke-width="18"/>'
            '<rect x="250" y="300" width="300" height="24" rx="8" fill="#E8EEF4"/><rect x="262" y="324" width="12" height="100" fill="#A8B0BC"/><rect x="528" y="324" width="12" height="100" fill="#A8B0BC"/>')


def jar(x, y, s=1.0, n=0, t=0.0):
    o = ['<rect x="-30" y="-60" width="60" height="70" rx="10" fill="#CFF4FF" opacity="0.5" stroke="#FFFFFF" stroke-width="3"/>', '<rect x="-34" y="-70" width="68" height="14" rx="5" fill="#5A7AA8"/>']
    for k in range(n):
        o.append(screw_maggot(-18 + (k * 9) % 36, -10 - (k * 7) % 40, 0.22, t + k, (k * 47) % 360, 0.2, 0.3))
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{"".join(o)}</g>'


def tweezers(x, y, s=1.0, ang=0.0, pinch=0.0):
    g = 6 * (1 - pinch)
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})"><path d="M0 0 L120 {-g:.1f}" stroke="#C8CCD8" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M0 0 L120 {g:.1f}" stroke="#A8ACB8" stroke-width="7" stroke-linecap="round"/></g>')


def plane(x, y, s=1.0, t=0.0, door=0.0):
    """1960s twin-prop cargo plane, side view facing left."""
    p = 70 * math.sin(t * 60)
    o = ['<path d="M-160 0 Q-170 -30 -120 -36 L150 -30 Q190 -28 210 -60 L230 -60 L220 -10 Q200 10 150 12 L-120 14 Q-168 12 -160 0 Z" fill="#D8DCE4"/>',
         '<path d="M-150 4 L200 2" stroke="#A8ACB8" stroke-width="3"/>', '<path d="M-20 -6 L60 -6 L110 46 L80 46 Z" fill="#B8BCC8"/>',
         '<ellipse cx="-30" cy="-6" rx="34" ry="12" fill="#9AA0AC"/>', f'<ellipse cx="-66" cy="-6" rx="4" ry="{abs(p) * 0.6 + 6:.0f}" fill="#5A5A6A" opacity="0.6"/>',
         ''.join(f'<rect x="{-110 + 26 * k}" y="-28" width="14" height="10" rx="3" fill="#5AB0E8"/>' for k in range(8))]
    if door > 0:
        o.append(f'<rect x="60" y="6" width="50" height="{14 * door:.0f}" fill="#2A2A34"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{"".join(o)}</g>'


AM_BOX = (300, 20, 360, 520)
AM_P = geo.MapProj(AM_BOX, -125.0, -60.0, 0.0, 50.0)
SPREAD = [("Panama", 0.0), ("Costa Rica", 0.12), ("Nicaragua", 0.25), ("Honduras", 0.35), ("El Salvador", 0.42), ("Guatemala", 0.5), ("Belize", 0.55), ("Mexico", 0.68)]


def americas(t, prog=0.0, pin=0.0):
    o = ['<rect x="-600" y="-600" width="2160" height="1800" fill="#081A3A"/>']
    o.append(geo.land_map(AM_P, ["United States of America", "Canada", "Cuba", "Colombia", "Venezuela"], fill="#1A3A5A", stroke="#4A7AAA", sw=1.4))
    for nm, at in SPREAD:
        u = clamp((prog - at) / 0.12)
        o.append(geo.land_map(AM_P, [nm], fill=mixc("#1A3A5A", "#E83A3A", u), stroke=mixc("#4A7AAA", "#FF8A8A", u), sw=1.4))
    if pin > 0:
        x, y = AM_P(-76.6, 39.0)
        o.append(glow(x, y, 50 * pin, "#FF3A4A", 0.7, 6) + f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{lerp(30, 7, pin):.1f}" fill="none" stroke="#FFFFFF" stroke-width="3" opacity="{pin:.2f}"/>'
                 + f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#FF3A4A" opacity="{pin:.2f}"/>')
    return "".join(o)
