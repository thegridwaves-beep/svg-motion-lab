"""Props and sets for the rebuilt mosquito reel: close-up arm and slap hand, the swarm wall and hole, carrier and scale,
the neighbourhood flood, pool sets, the landing diagram, the lounger, Spain at night, the follow card."""
from mcore import *
import geo

SK = R3.YOU.skin; TP = R3.YOU.top; HR = R3.YOU.hair
LD["cool"] = Light("cool", amb=(0.7, 0.74, 0.92), sat=0.85, key="#8AB0FF", key_op=0.3, ang=-150, shade="#0A0A30", shade_op=0.5, rim="#9AC0FF", rim_op=0.45, rim_w=7)
LD["sickly"] = Light("sickly", amb=(0.86, 0.9, 0.86), sat=0.35, key="#C8FFD8", key_op=0.2, ang=-60, shade="#102018", shade_op=0.45, rim="#B8E8C8", rim_op=0.3, rim_w=6)


# ------------------------------------------------------------------ close-up arm + slap hand
def forearm(x, y, s=1.0, ang=0.0, dark=0.0):
    """Forearm entering from the right edge, wrist at (x, y). Sleeve cuff at the right."""
    sk = mixc(SK[0], "#5A4A6A", dark * 0.5); sk2 = mixc(SK[1], "#3A2A4A", dark * 0.5)
    o = [f'<path d="M0 -46 Q180 -62 420 -70 L420 74 Q180 66 0 46 Q-24 0 0 -46 Z" fill="{sk}"/>',
         f'<path d="M0 20 Q180 40 420 50 L420 74 Q180 66 0 46 Z" fill="{sk2}" opacity="0.7"/>',
         f'<path d="M20 -30 Q160 -46 380 -54" stroke="{SK[2]}" stroke-width="8" fill="none" opacity="0.45" stroke-linecap="round"/>']
    for k, (hx, hy) in enumerate(((70, -20), (120, 4), (170, -26), (210, 12), (260, -14), (300, 20), (340, -30))):
        o.append(f'<path d="M{hx} {hy} q6 -10 14 -12" stroke="{SK[1]}" stroke-width="2" fill="none" opacity="0.6"/>')
    o.append(f'<path d="M330 -80 L470 -90 L470 92 L330 84 Q312 0 330 -80 Z" fill="{TP[0]}"/>')
    o += [f'<path d="M{340 + i * 18} -78 L{344 + i * 18} 82" stroke="{TP[1]}" stroke-width="6" opacity="0.6"/>' for i in range(6)]
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})">{"".join(o)}</g>'


def slap_hand(x, y, s=1.0, ang=0.0, curl=0.0, dark=0.0):
    """Open palm facing down/forward with four fingers and a thumb; wrist at (x, y), fingers toward -y. curl 0..1 grips."""
    sk = mixc(SK[0], "#5A4A6A", dark * 0.5); sk2 = mixc(SK[1], "#3A2A4A", dark * 0.5)
    o = [f'<path d="M-60 0 Q-70 -70 -50 -120 L50 -120 Q70 -70 60 0 Q0 30 -60 0 Z" fill="{sk}"/>']
    for k in range(4):
        fx = -42 + k * 28
        L_ = (96, 110, 104, 86)[k] * (1 - 0.55 * curl)
        o.append(f'<rect x="{fx - 12}" y="{-120 - L_:.1f}" width="24" height="{L_ + 14:.1f}" rx="12" fill="{sk}" stroke="{sk2}" stroke-width="2.5"/>')
        o.append(f'<path d="M{fx - 6} {-128 - L_ * 0.55:.1f} q6 -3 12 0" stroke="{sk2}" stroke-width="2" fill="none" opacity="0.7"/>')
    o.append(f'<path d="M58 -40 Q120 -70 130 -110 Q138 -132 118 -134 Q98 -110 52 -90 Z" fill="{sk}" stroke="{sk2}" stroke-width="2.5"/>')
    o.append(f'<path d="M-40 -30 Q0 -10 40 -30" stroke="{sk2}" stroke-width="3" fill="none" opacity="0.6"/>')
    o.append(f'<path d="M-70 0 L70 0 L76 120 L-76 120 Z" fill="{TP[0]}"/>' + "".join(f'<path d="M{-60 + i * 24} 6 L{-62 + i * 24} 118" stroke="{TP[1]}" stroke-width="6" opacity="0.6"/>' for i in range(6)))
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})">{"".join(o)}</g>'


def hand_grip(x, y, s=1.0, grip=1.0):
    """Hand gripping a horizontal chair rail at (x, y), seen from the side; grip 0 opens the fingers."""
    o = [f'<path d="M-90 30 Q-40 0 10 -8 L20 34 Q-40 50 -90 60 Z" fill="{TP[0]}"/>',
         f'<path d="M0 -30 Q60 -50 90 -20 Q100 10 80 30 Q40 44 0 34 Z" fill="{SK[0]}"/>']
    for k in range(4):
        a = lerp(80, 10, grip)
        fx = 30 + k * 16
        o.append(f'<g transform="translate({fx} -30) rotate({a:.0f})"><rect x="-7" y="-6" width="14" height="{46 - 6 * k}" rx="7" fill="{SK[0]}" stroke="{SK[1]}" stroke-width="2"/></g>')
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{"".join(o)}</g>'


# ------------------------------------------------------------------ swarm shapes
def mosq_silhouette_path(cx, cy, s):
    """A big mosquito silhouette (for the 'hole' in the sunset)."""
    p = (f"M{-120} 0 Q-60 -26 10 -20 Q40 -50 70 -20 Q90 -24 100 -10 L170 30 L96 6 Q60 30 10 14 Q-60 26 -120 0 Z")
    legs = "".join(f'<path d="M{a} 10 L{b} 70 L{c} 120" stroke-width="7" fill="none" stroke-linecap="round"/>' for a, b, c in ((0, -40, -80), (20, 10, -10), (40, 70, 90)))
    wings = '<ellipse cx="-10" cy="-50" rx="80" ry="22" transform="rotate(-20 -10 -50)"/><ellipse cx="0" cy="-40" rx="70" ry="18" transform="rotate(-8 0 -40)"/>'
    return f'<g transform="translate({cx} {cy}) scale({s})"><path d="{p}"/>{wings}<g stroke="currentColor">{legs}</g></g>'


def swarm_hole(cx, cy, s, t, op=1.0):
    """The 'hole' in the sunset: a giant mosquito silhouette made of swarm, its edges fraying into individual specks."""
    m = mosq(cx, cy, s, t * 0.25, rot=-6, flip=True, seed=11, flap=0.4)
    m = re.sub(r'(fill|stroke)="#[0-9A-Fa-f]{6}"', r'\1="#07040C"', m)
    m = re.sub(r'opacity="0\.[0-9]+"', 'opacity="0.97"', m)
    edge = swarm(cx - 10 * s, cy - 6 * s, 50 * s, 22 * s, 160, t, 33, 1.2 + 0.25 * s, "#07040C")
    return f'<g opacity="{op:.2f}"><g filter="url(#b1)">{m}</g>{edge}</g>'


def wall(x0, x1, top, bottom, t, seed=5, dense=1.0):
    """Towering packed wall of mosquitoes: a dark mass with a churning surface of individual bodies."""
    o = [f'<rect x="{x0}" y="{top + 20}" width="{x1 - x0}" height="{bottom - top}" fill="#0A0610" opacity="{0.92 * dense:.2f}" filter="url(#b6)"/>']
    r = random.Random(seed)
    for i in range(int(260 * dense)):
        px = r.uniform(x0, x1) + 4 * math.sin(t * 3 + i); py = r.uniform(top, bottom) + 3 * math.cos(t * 4 + i)
        o.append(speck(px, py, r.uniform(1.8, 2.8), t, i, "#2A2036", 0.95))
    for i in range(int(40 * dense)):
        px = r.uniform(x0, x1) + 10 * math.sin(t * 2 + i); py = top + r.uniform(-30, 30) + 6 * math.sin(t * 5 + i)
        o.append(speck(px, py, 2.4, t, i + 99, "#0A0610"))
    return "".join(o)


def flow_around_text(t, y, h, n=120, seed=8, x0=280, x1=680, speed=80):
    """Specks streaming right-to-left that bulge over and under a text band [y-h/2, y+h/2]."""
    r = random.Random(seed); o = []
    for i in range(n):
        lane = r.uniform(-1, 1)
        x = x1 - ((t * speed * r.uniform(0.8, 1.3) + r.uniform(0, 600)) % (x1 - x0 + 80))
        mid = (x - 480) / 160
        bulge = math.exp(-mid * mid) * (h * 0.6 + 10)
        yy = y + lane * (h * 0.5 + 18) + (bulge if lane > 0 else -bulge) * (1 if abs(lane) < 0.9 else 0.4)
        o.append(speck(x, yy + 4 * math.sin(t * 6 + i), 2.6, t, i, "#3A2E4A"))
    return "".join(o)


# ------------------------------------------------------------------ carrier and scale
def carrier(x, y, s=1.0):
    o = ['<path d="M-150 -6 L150 -6 L132 26 L-126 26 Z" fill="#5A6478"/>',
         '<path d="M-160 -16 L170 -16 L150 -4 L-154 -4 Z" fill="#7A8498"/>',
         '<path d="M-130 -12 L60 -12" stroke="#E8ECF4" stroke-width="2" stroke-dasharray="10 7"/><path d="M-60 -10 L120 -14" stroke="#FFD23F" stroke-width="1.5"/>',
         '<path d="M70 -16 L70 -54 L100 -54 L104 -16 Z" fill="#4A5468"/><rect x="80" y="-74" width="6" height="22" fill="#4A5468"/><rect x="74" y="-48" width="22" height="6" fill="#9AA4B8"/>',
         '<path d="M-120 26 L120 26" stroke="#2A3448" stroke-width="3"/>']
    for k in range(4):
        o.append(f'<path d="M{-100 + k * 40} -22 l12 -4 l12 4 Z" fill="#AAB4C8"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{"".join(o)}</g>'


def scale_rig(t, tilt, pour=0.0, heap=0.0, carrier_on=1.0, last=None):
    """Balance at fulcrum (480, 230); left pan carries the carrier, right pan the mosquito heap. tilt deg (+ = right pan down)."""
    o = ['<path d="M480 600 L480 230" stroke="#C8B0E8" stroke-width="12"/><path d="M420 610 L540 610 L516 580 L444 580 Z" fill="#C8B0E8"/>']
    arm = [f'<path d="M330 230 L630 230" stroke="#E8DCF8" stroke-width="10" stroke-linecap="round"/><circle cx="480" cy="230" r="13" fill="{GOLD}"/>']
    pans = []
    for px, side in ((345, -1), (615, 1)):
        a = math.radians(tilt)
        ax = 480 + (px - 480) * math.cos(a); ay = 230 + (px - 480) * math.sin(a)
        pans.append((ax, ay))
    o.append(f'<g transform="rotate({tilt:.2f} 480 230)">{"".join(arm)}</g>')
    for k, (ax, ay) in enumerate(pans):
        o.append(f'<path d="M{ax:.1f} {ay:.1f} L{ax - 44:.1f} {ay + 90:.1f} M{ax:.1f} {ay:.1f} L{ax + 44:.1f} {ay + 90:.1f}" stroke="#E8DCF8" stroke-width="2.5"/>'
                 f'<path d="M{ax - 58:.1f} {ay + 90:.1f} Q{ax:.1f} {ay + 116:.1f} {ax + 58:.1f} {ay + 90:.1f} Z" fill="#E8DCF8"/>')
    (lx, ly), (rx, ry) = pans
    o.append(carrier(lx, ly + 80, 0.44 * carrier_on))
    r = random.Random(3)
    for i in range(int(260 * heap)):
        hx = rx + r.gauss(0, 17); hy = ry + 92 - abs(r.gauss(0, 12)) - i * 0.06
        o.append(speck(hx, hy, 2.2, t, i, "#140C18"))
    if pour > 0:
        o.append(swarm(rx, ry - 160, 50, 150, int(140 * pour), t, 6, 2.0, "#0A0610", drift=(0, 0)))
    if last is not None:
        o.append(last)
    return "".join(o), pans


# ------------------------------------------------------------------ neighbourhood, 3/4 aerial
def iso_house(x, y, s, c_wall, c_roof, lit_=0.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M-30 0 L0 15 L30 0 L30 -26 L0 -11 L-30 -26 Z" fill="{c_wall}"/>'
            f'<path d="M-30 -26 L0 -11 L0 15 L-30 0 Z" fill="#00000033"/><path d="M-34 -26 L0 -46 L34 -26 L0 -8 Z" fill="{c_roof}"/>'
            f'<rect x="6" y="-12" width="8" height="8" fill="#FFD890" opacity="{0.3 + 0.7 * lit_:.2f}"/></g>')


HOME_ISO = (480, 330)


def neighbourhood(t, dark=0.0, seed=4):
    """3/4 aerial over rows of houses along diagonal streets; his house at HOME_ISO."""
    r = random.Random(seed)
    o = [f'<rect x="-400" y="-400" width="1760" height="1400" fill="{mixc("#4A8A4A", "#14241A", dark)}"/>']
    for k in range(-6, 8):
        y = 330 + k * 60
        o.append(f'<path d="M-200 {y + 140} L1200 {y - 560}" stroke="{mixc("#8A8498", "#2A2834", dark)}" stroke-width="22"/>')
    for k in range(-8, 10):
        x = 480 + k * 90
        o.append(f'<path d="M{x - 500} {-200} L{x + 500} {800}" stroke="{mixc("#8A8498", "#2A2834", dark)}" stroke-width="16" opacity="0.8"/>')
    cols = [("#F4D8C0", "#8A4A5A"), ("#E8E0F4", "#4A5A8A"), ("#F0E0B0", "#9A5A3A"), ("#D8E8D8", "#5A3A6A")]
    pts = []
    for i in range(-5, 7):
        for j in range(-6, 9):
            x = 480 + i * 64 + j * 32; y = 330 + j * 36 - i * 30
            if (i, j) == (0, 0):
                continue
            pts.append((y, x))
    for y, x in sorted(pts):
        cw, cr = r.choice(cols)
        o.append(iso_house(x, y, 0.9, mixc(cw, "#2A2434", dark * 0.8), mixc(cr, "#1A1424", dark * 0.8), dark))
    return "".join(o)


def flood_streams(t, prog, seed=3):
    """Dark rivers of mosquitoes flowing along the streets into HOME_ISO; prog 0..1 how far the front has reached."""
    o = []
    hx, hy = HOME_ISO
    for k, (sx, sy) in enumerate(((-120, 760), (1080, -180), (-160, -120), (1120, 760), (480, -260), (480, 860))):
        L_ = prog
        mx, my = (sx + hx) / 2 + (40 if k % 2 else -40), (sy + hy) / 2
        ex = sx + (hx - sx) * L_; ey = sy + (hy - sy) * L_
        o.append(f'<path d="M{sx} {sy} Q{mx} {my} {ex:.0f} {ey:.0f}" stroke="#07040C" stroke-width="{38 * (0.5 + 0.5 * L_):.0f}" fill="none" stroke-linecap="round" opacity="0.85" filter="url(#b6)"/>')
        r = random.Random(seed + k)
        for j in range(30):
            u = r.random() * L_
            px = (1 - u) ** 2 * sx + 2 * (1 - u) * u * mx + u * u * hx
            py = (1 - u) ** 2 * sy + 2 * (1 - u) * u * my + u * u * hy
            o.append(speck(px + r.gauss(0, 12), py + r.gauss(0, 12), 2.2, t, j + k * 40, "#07040C"))
    return "".join(o)


# ------------------------------------------------------------------ pool sets
def coping(x0, x1, y, h=26):
    return (f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{h}" fill="#E8E0D4"/><rect x="{x0}" y="{y + h - 5}" width="{x1 - x0}" height="5" fill="#B8AEA4"/>'
            + "".join(f'<path d="M{x} {y} L{x} {y + h}" stroke="#C8C0B4" stroke-width="2"/>' for x in range(int(x0), int(x1), 60)))


def larva(x, y, t, k=0, s=1.0):
    sw = 7 * math.sin(t * 4 + k)
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.2f})"><path d="M0 0 L-2 10" stroke="#4A3A2A" stroke-width="3"/><circle cx="-3" cy="15" r="6" fill="#5A4834"/>'
            f'<path d="M-3 18 Q{sw:.1f} 40 -4 64 Q{-sw:.1f} 82 0 98" stroke="#6A5440" stroke-width="6" fill="none" stroke-linecap="round"/></g>')


def pov_surface(t, feet=1.0, seed=2):
    """Looking straight up from under water: bright rippling surface, a canopy of mosquito feet dimpling it."""
    o = ['<rect x="-400" y="-400" width="1760" height="1400" fill="url(#deep)"/>',
         f'<rect x="200" y="-100" width="560" height="760" fill="#9AF0FF" opacity="{0.35 * (1 - 0.6 * feet):.2f}"/>']
    o.append(rays(480, 270, 30, 600, 14, t, "#DFFFFF", 0.06, 0.04, 3, t * 3))
    r = random.Random(seed)
    for i in range(int(380 * feet)):
        px = r.uniform(290, 670); py = r.uniform(-60, 600)
        sz = r.uniform(0.8, 1.6)
        o.append(f'<g transform="translate({px:.0f} {py:.0f}) scale({sz:.2f})"><ellipse rx="7" ry="2.6" fill="#0A0610" opacity="0.8"/>'
                 + "".join(f'<circle cx="{dx}" cy="{dy}" r="2.4" fill="#BFF8FF" opacity="0.65"/><circle cx="{dx}" cy="{dy}" r="1" fill="#0A0610"/>' for dx, dy in ((-9, -5), (-9, 5), (0, -7), (0, 7), (9, -5), (9, 5)))
                 + "</g>")
    return "".join(o)


# ------------------------------------------------------------------ landing diagram
STAR = None


def star_body():
    global STAR
    if STAR is None:
        J = F_STAND | dict(el=(-130, -330), hl=(-200, -390), er=(130, -330), hr=(200, -390), kl=(-60, -100), fl=(-100, 0), kr=(60, -100), fr=(100, 0), face=fc(open=1.1, lift=0.6, mouth="worried"))
        STAR = R3.front(J)
    return STAR


def spots(fill, seed=1, x0=318, x1=642, y0=96, y1=500, step=13):
    """Landing spots on the body (masked later): empty rings fill with landed mosquitoes as fill rises 0..1."""
    r = random.Random(seed); o = []
    for gy in range(y0, y1, step):
        for gx in range(x0, x1, step):
            on = r.random() < fill
            if on:
                o.append(speck(gx + r.uniform(-1.5, 1.5), gy + r.uniform(-1.5, 1.5), 1.6, 0.0, gx * 7 + gy, "#140C18").replace('<g transform="', f'<g transform="rotate({r.uniform(-30, 30):.0f} {gx} {gy}) ', 1))
            else:
                o.append(f'<circle cx="{gx}" cy="{gy}" r="3" fill="none" stroke="#5AE8FF" stroke-width="0.8" opacity="0.55"/>')
    return "".join(o)


def lounger_side(x, y, s=1.0, flip=False):
    sx = -s if flip else s
    return (f'<g transform="translate({x} {y}) scale({sx} {s})"><path d="M-110 -26 L60 -26 L110 -96" stroke="#FFFFFF" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            '<path d="M-110 -26 L60 -26 L110 -96" stroke="#5AC8E8" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            '<path d="M-96 -26 L-102 0 M44 -26 L50 0" stroke="#C8C0D0" stroke-width="6" stroke-linecap="round"/></g>')


def pool_lights(t, smear=0.0):
    o = []
    for k, (x, y) in enumerate(((330, 470), (420, 500), (540, 500), (630, 470))):
        o.append(glow(x, y, 16 + 50 * smear, "#7FF4FF", 0.6, 6 + int(16 * smear)))
        if smear > 0:
            o.append(f'<ellipse cx="{x + 30 * smear}" cy="{y}" rx="{10 + 60 * smear:.0f}" ry="6" fill="#BFF8FF" opacity="{0.4 * smear:.2f}" filter="url(#b8)"/>')
        o.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#DFFFFF"/>')
    return "".join(o)


# ------------------------------------------------------------------ Spain at night
SP_BOX = (300, 30, 360, 360)
SP_P = geo.MapProj(SP_BOX, -10.0, 4.6, 35.4, 44.2)
CITIES = [("Madrid", -3.70, 40.42, 6.5), ("Barcelona", 2.17, 41.39, 5.5), ("Valencia", -0.38, 39.47, 4.2), ("Seville", -5.98, 37.39, 4.0),
          ("Zaragoza", -0.89, 41.65, 3.4), ("Málaga", -4.42, 36.72, 3.6), ("Bilbao", -2.93, 43.26, 3.4), ("Murcia", -1.13, 37.99, 3.0),
          ("Valladolid", -4.72, 41.65, 2.6), ("Vigo", -8.72, 42.24, 2.6), ("A Coruña", -8.41, 43.36, 2.4), ("Granada", -3.60, 37.18, 2.6),
          ("Alicante", -0.48, 38.35, 3.0), ("Córdoba", -4.78, 37.89, 2.6), ("Palma", 2.65, 39.57, 2.8), ("Oviedo", -5.85, 43.36, 2.2),
          ("Pamplona", -1.64, 42.81, 2.2), ("Santander", -3.80, 43.46, 2.2), ("Salamanca", -5.66, 40.97, 2.0), ("Toledo", -4.02, 39.86, 1.8),
          ("Cádiz", -6.29, 36.53, 2.2), ("Almería", -2.46, 36.84, 2.2), ("Badajoz", -6.97, 38.88, 1.8), ("Tarragona", 1.25, 41.12, 2.2),
          ("Girona", 2.82, 41.98, 1.8), ("León", -5.57, 42.60, 1.8), ("Burgos", -3.70, 42.34, 1.8), ("Albacete", -1.86, 38.99, 1.8)]


def spain_night(t, front_lon, seed=6):
    o = ['<rect x="-400" y="-400" width="1760" height="1400" fill="#04081A"/>']
    o.append(geo.land_map(SP_P, ["France", "Portugal", "Morocco", "Algeria", "Andorra"], fill="#0E1830", stroke="#22385A", sw=1.4))
    o.append(geo.land_map(SP_P, ["Spain"], fill="#16284A", stroke="#6A9ADA", sw=2.2))
    r = random.Random(seed)
    lights = list(CITIES)
    for i in range(110):
        lon = r.uniform(-9.2, 3.2); lat = r.uniform(36.2, 43.6)
        lights.append(("", lon, lat, r.uniform(0.8, 1.6)))
    for nm, lon, lat, sz in lights:
        if nm == "" and not _in_spain(lon, lat):
            continue
        x, y = SP_P(lon, lat)
        on = clamp((lon - front_lon) / 0.4)
        if on <= 0:
            continue
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{sz * 0.6:.1f}" fill="#FFE0A0" opacity="{0.95 * on:.2f}"/>' + glow(x, y, sz * 2.2, "#FFC870", 0.45 * on, 3))
    return "".join(o)


_SP = None


def _in_spain(lon, lat):
    global _SP
    if _SP is None:
        _SP = [ring for nm, ring in geo.rings(["Spain"])]
    for ring in _SP:
        inside = False
        for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
            if (y1 > lat) != (y2 > lat) and lon < x1 + (lat - y1) * (x2 - x1) / (y2 - y1):
                inside = not inside
        if inside:
            return True
    return False


def swarm_front(t, front_lon, seed=7):
    """A dense swarm edge advancing west→east (lon); darkness behind it."""
    x, _ = SP_P(front_lon, 40)
    o = [f'<rect x="-400" y="-400" width="{x + 400 - 30:.0f}" height="1400" fill="#000000" opacity="0.72"/>',
         f'<g filter="url(#b10)"><rect x="{x - 70:.0f}" y="-200" width="90" height="1000" fill="#000000" opacity="0.7"/></g>',
         swarm(x - 10, 230, 40, 300, 160, t, seed, 1.6, "#000000")]
    return "".join(o)


# ------------------------------------------------------------------ follow card
def follow_card(t, pressed=False, press_k=0.0, u=1.0):
    from mreel import logo
    k = eo(u)
    o = [logo(480, 140, 0.24 * (0.6 + 0.4 * k)) if u > 0 else "",
         big_num("SANDBOX", 480, 282, ramp(u, 0.3, 0.8) if u < 1 else 1.0, 38, "#FFFFFF")]
    sc = 1 - 0.1 * press_k
    col = PINK if not pressed else "#3A2A6A"
    o.append(f'<g transform="translate(480 362) scale({sc:.3f})" opacity="{clamp(u * 2):.2f}"><rect x="-118" y="-32" width="236" height="64" rx="32" fill="{col}"/>'
             + text(0, 11, "FOLLOWING" if pressed else "FOLLOW", 30, "#FFFFFF", 700, "middle") + "</g>")
    return "".join(o)
