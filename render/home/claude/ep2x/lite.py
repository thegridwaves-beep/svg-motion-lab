"""Scene lighting for rigged characters: ambient tint + desaturation, a directional key gradient, a shade gradient
on the far side, and a rim light on the edge that faces the light. Every effect is masked to the character's own
silhouette (a <use> of the drawn body), so it reads as light falling on him rather than a glow pasted over him.

lit(body_svg, uid, x, y, s, L, ang=None) -> svg      body drawn in rig coords (feet at y=0, head top near y=-525)
light_defs(*lights)                                  defs for the lights used in a shot
"""
import math

WHITE = '<filter id="Lwht" x="-30%" y="-30%" width="160%" height="160%"><feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1 0"/></filter>'


class Light:
    def __init__(self, name, amb=(1, 1, 1), sat=1.0, key="#FFFFFF", key_op=0.0, ang=-135, spread=0.85,
                 shade="#1A1040", shade_op=0.0, rim="#FFFFFF", rim_op=0.0, rim_w=9, lift=0.0, bounce="#8AD0FF", bounce_op=0.0, bounce_ang=90):
        self.name, self.amb, self.sat, self.key, self.key_op, self.ang = name, amb, sat, key, key_op, ang
        self.spread, self.shade, self.shade_op, self.rim, self.rim_op, self.rim_w, self.lift = spread, shade, shade_op, rim, rim_op, rim_w, lift
        self.bounce, self.bounce_op, self.bounce_ang = bounce, bounce_op, bounce_ang

    def at(self, **kw):
        d = dict(self.__dict__); d.update(kw); n = Light(d.pop("name")); n.__dict__.update(d); n.name = kw.get("name", self.name); return n


def _mat(amb, sat, lift):
    r, g, b = amb
    lw = (0.2126, 0.7152, 0.0722)
    rows = []
    for i, k in enumerate((r, g, b)):
        row = [(1 - sat) * lw[j] + (sat if i == j else 0) for j in range(3)]
        rows.append(" ".join(f"{k * v:.4f}" for v in row) + f" 0 {lift:.3f}")
    return "  ".join(rows) + "  0 0 0 1 0"


def _qa(a):
    return int(round(a / 15.0)) * 15 % 360


def light_defs(*lights):
    out = [WHITE]
    seen = set()
    for L0 in lights:
        if L0 is None:
            continue
        for L in (L0, L0.at(ang=180 - L0.ang)):
            out.append(_one_light(L, seen))
    return "".join(out)


def _one_light(L, seen):
    out = []
    if True:
        a = _qa(L.ang)
        key = (L.name, a)
        if key in seen:
            return ""
        seen.add(key)
        nm = f"{L.name}_{a}"
        out.append(f'<filter id="La_{L.name}" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="{_mat(L.amb, L.sat, L.lift)}"/></filter>')
        # light comes FROM angle a (degrees, 0 = from the right, 90 = from below, -90/270 = from above)
        lx, ly = math.cos(math.radians(a)), math.sin(math.radians(a))
        x1, y1, x2, y2 = 0.5 + 0.5 * lx, 0.5 + 0.5 * ly, 0.5 - 0.5 * lx, 0.5 - 0.5 * ly
        out.append(f'<linearGradient id="Lk_{nm}" x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}">'
                   f'<stop offset="0" stop-color="{L.key}" stop-opacity="{L.key_op:.3f}"/><stop offset="{L.spread:.2f}" stop-color="{L.key}" stop-opacity="0"/></linearGradient>')
        out.append(f'<linearGradient id="Ls_{nm}" x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}">'
                   f'<stop offset="0.35" stop-color="{L.shade}" stop-opacity="0"/><stop offset="1" stop-color="{L.shade}" stop-opacity="{L.shade_op:.3f}"/></linearGradient>')
        if L.bounce_op > 0:
            bx_, by_ = math.cos(math.radians(L.bounce_ang)), math.sin(math.radians(L.bounce_ang))
            out.append(f'<linearGradient id="Lb_{nm}" x1="{0.5 + 0.5 * bx_:.3f}" y1="{0.5 + 0.5 * by_:.3f}" x2="{0.5 - 0.5 * bx_:.3f}" y2="{0.5 - 0.5 * by_:.3f}">'
                       f'<stop offset="0" stop-color="{L.bounce}" stop-opacity="{L.bounce_op:.3f}"/><stop offset="0.45" stop-color="{L.bounce}" stop-opacity="0"/></linearGradient>')
        d = L.rim_w
        out.append(f'<filter id="Le_{nm}" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
                   f'<feOffset in="SourceAlpha" dx="{-lx * d:.2f}" dy="{-ly * d:.2f}" result="o"/>'
                   f'<feComposite in="SourceAlpha" in2="o" operator="out" result="e"/><feGaussianBlur in="e" stdDeviation="{d * 0.38:.2f}" result="eb"/>'
                   f'<feComposite in="eb" in2="SourceAlpha" operator="in" result="ec"/>'
                   f'<feColorMatrix in="ec" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1 0"/></filter>')
    return "".join(out)


def lit(body, uid, x, y, s, L, flip=False, box=(-190, -560, 380, 600)):
    """Character `body` (rig coords) placed at (x, y) scale s, lit by L. `uid` must be unique within the frame."""
    fx = -s if flip else s
    if L is None:
        return f'<g transform="translate({x:.1f} {y:.1f}) scale({fx:.4f} {s:.4f})">{body}</g>'
    a = _qa(L.ang if not flip else 180 - L.ang)
    nm = f"{L.name}_{a}"
    bx, by, bw, bh = box
    o = [f'<g id="{uid}" filter="url(#La_{L.name})">{body}</g>']
    o.append(f'<mask id="M{uid}" maskUnits="userSpaceOnUse" x="{bx - 60}" y="{by - 60}" width="{bw + 120}" height="{bh + 120}"><use href="#{uid}" filter="url(#Lwht)"/></mask>')
    if L.shade_op > 0:
        o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="url(#Ls_{nm})" mask="url(#M{uid})" style="mix-blend-mode:multiply"/>')
    if L.key_op > 0:
        o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="url(#Lk_{nm})" mask="url(#M{uid})" style="mix-blend-mode:screen"/>')
    if L.bounce_op > 0:
        o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="url(#Lb_{nm})" mask="url(#M{uid})" style="mix-blend-mode:screen"/>')
    if L.rim_op > 0:
        o.append(f'<mask id="R{uid}" maskUnits="userSpaceOnUse" x="{bx - 60}" y="{by - 60}" width="{bw + 120}" height="{bh + 120}"><use href="#{uid}" filter="url(#Le_{nm})"/></mask>'
                 f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{L.rim}" opacity="{L.rim_op:.3f}" mask="url(#R{uid})"/>')
    # flip handled outside the light maths: the light angle is mirrored so it still comes from the same screen side
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({fx:.4f} {s:.4f})">{"".join(o)}</g>'


def contact(x, y, w, L=None, op=0.45, col="#05030F", k=1.0):
    """Contact shadow ellipse under feet, pushed away from the light."""
    dx = 0.0
    if L is not None:
        dx = -math.cos(math.radians(L.ang)) * w * 0.25
    return (f'<ellipse cx="{x + dx:.1f}" cy="{y:.1f}" rx="{w:.1f}" ry="{w * 0.16 * k:.1f}" fill="{col}" opacity="{op * 0.55:.2f}"/>'
            f'<ellipse cx="{x + dx * 0.5:.1f}" cy="{y:.1f}" rx="{w * 0.55:.1f}" ry="{w * 0.09 * k:.1f}" fill="{col}" opacity="{op:.2f}"/>')


# ------------------------------------------------------------------ the light plan, one per location / event state
LT = dict(
    kitchen=Light("kitchen", amb=(0.86, 0.82, 1.0), sat=1.0, key="#7FF4FF", key_op=0.5, ang=180, spread=0.75, shade="#1A0E4A", shade_op=0.4, rim="#B8FBFF", rim_op=0.55, rim_w=8),
    kitchen_warm=Light("kitchen_warm", amb=(0.96, 0.9, 0.96), key="#FFC890", key_op=0.25, ang=-40, shade="#2A1260", shade_op=0.3, rim="#FFE0B0", rim_op=0.35),
    lava=Light("lava", amb=(0.88, 0.74, 0.8), sat=1.0, key="#FF7A2E", key_op=0.62, ang=90, spread=0.5, shade="#1A0C30", shade_op=0.45, rim="#FFB060", rim_op=0.55, rim_w=8),
    impact=Light("impact", amb=(1.05, 0.88, 0.8), key="#FFF4D0", key_op=0.8, ang=-20, spread=0.85, shade="#3A0A1A", shade_op=0.5, rim="#FFFFFF", rim_op=0.65, rim_w=10),
    moonnight=Light("moonnight", amb=(0.72, 0.68, 0.86), sat=0.9, key="#FFC8A0", key_op=0.45, ang=-35, shade="#140A30", shade_op=0.45, rim="#FFB070", rim_op=0.5, rim_w=8, bounce="#FF7A2E", bounce_op=0.35),
    arch=Light("arch", amb=(1.0, 0.9, 0.84), sat=0.95, key="#FFC070", key_op=0.42, ang=200, spread=0.8, shade="#5A2A3A", shade_op=0.32, rim="#FFD8A0", rim_op=0.5, rim_w=8, bounce="#8AD0E0", bounce_op=0.2),
    ice=Light("ice", amb=(0.97, 1.0, 1.06), sat=0.95, key="#FFFFFF", key_op=0.25, ang=-130, shade="#2E4E8E", shade_op=0.45, rim="#FFFFFF", rim_op=0.45, rim_w=7, bounce="#9AD4FF", bounce_op=0.32),
    kpg=Light("kpg", amb=(1.0, 0.97, 0.93), key="#FFE8B0", key_op=0.32, ang=-50, shade="#2A3A6A", shade_op=0.3, rim="#FFF4D8", rim_op=0.45, rim_w=7, bounce="#F0D8A0", bounce_op=0.18),
    flash=Light("flash", amb=(1.1, 1.06, 1.0), key="#FFFFFF", key_op=0.9, ang=0, spread=0.9, shade="#1A1040", shade_op=0.6, rim="#FFFFFF", rim_op=0.8, rim_w=12, lift=0.02),
    redsky=Light("redsky", amb=(1.0, 0.72, 0.64), sat=0.85, key="#FF6A3A", key_op=0.5, ang=-90, shade="#2A0610", shade_op=0.5, rim="#FFB070", rim_op=0.6, rim_w=8),
    winter=Light("winter", amb=(0.74, 0.72, 0.74), sat=0.55, key="#B0A8A0", key_op=0.2, ang=-110, shade="#1A1820", shade_op=0.42, rim="#C8C0B8", rim_op=0.3),
    toba=Light("toba", amb=(1.0, 0.98, 0.95), key="#FFF0C0", key_op=0.3, ang=-40, shade="#203A5A", shade_op=0.3, rim="#FFF8E0", rim_op=0.4, bounce="#C8E8A0", bounce_op=0.15),
    ashday=Light("ashday", amb=(0.78, 0.74, 0.72), sat=0.55, key="#D8C8B0", key_op=0.2, ang=-100, shade="#1A1618", shade_op=0.42, rim="#E0D0C0", rim_op=0.3),
    fire=Light("fire", amb=(0.62, 0.54, 0.72), sat=0.95, key="#FF9A3A", key_op=0.55, ang=0, spread=0.6, shade="#0A0620", shade_op=0.55, rim="#FFC070", rim_op=0.6, rim_w=8),
    portal=Light("portal", amb=(0.78, 0.8, 0.98), key="#7FF4FF", key_op=0.5, ang=0, shade="#0A0A3A", shade_op=0.45, rim="#C8FFFF", rim_op=0.55, rim_w=8),
)
