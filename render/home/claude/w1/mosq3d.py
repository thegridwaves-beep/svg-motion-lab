"""A mosquito built in 3D (parts with real depth), drawn from any yaw angle so camera orbits turn it properly.
Model space: body axis along +x (head at +x), y down, z toward the viewer's left. yaw 0 = right-facing side view
(same as the 2D mosq), yaw -90 = head-on toward the camera, yaw -180 = left-facing side view."""
import math
from fx import mixc

SHADE = "#05030F"


def _proj(p, yaw, s, ox, oy):
    x, y, z = p
    c, si = math.cos(yaw), math.sin(yaw)
    X = x * c - z * si
    Z = x * si + z * c          # larger Z = farther from camera
    return ox + X * s, oy + y * s, Z


def mosq3d(ox, oy, s=1.0, yaw_deg=0.0, t=0.0, eggs=True, full=0.0, flap=0.0, legs="land", seed=0):
    yaw = math.radians(yaw_deg)
    c, si = math.cos(yaw), math.sin(yaw)
    items = []        # (depth, svg)

    def P(p):
        return _proj(p, yaw, s, ox, oy)

    def sphere(p, r, col, hl=True, op=1.0):
        X, Y, Z = P(p)
        dk = max(0.0, min(0.45, (Z / (60.0)) * 0.25))
        cc = mixc(col, SHADE, dk)
        o = f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r * s:.1f}" fill="{cc}" opacity="{op:.2f}"/>'
        if hl:
            o += f'<circle cx="{X - 0.3 * r * s:.1f}" cy="{Y - 0.35 * r * s:.1f}" r="{0.35 * r * s:.1f}" fill="#FFFFFF" opacity="0.10"/>'
        items.append((Z, o))

    def ellipsoid(p, rx, ry, rz, col, op=1.0):
        X, Y, Z = P(p)
        prx = math.sqrt((rx * c) ** 2 + (rz * si) ** 2)
        dk = max(0.0, min(0.45, (Z / 60.0) * 0.25))
        items.append((Z, f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{prx * s:.1f}" ry="{ry * s:.1f}" fill="{mixc(col, SHADE, dk)}" opacity="{op:.2f}"/>'
                         f'<ellipse cx="{X - 0.25 * prx * s:.1f}" cy="{Y - 0.4 * ry * s:.1f}" rx="{0.35 * prx * s:.1f}" ry="{0.22 * ry * s:.1f}" fill="#FFFFFF" opacity="0.10"/>'))

    def ring(p, r, col, w=2.0, op=0.8):
        """A band around the body axis: seen side-on it's a line, head-on it's a full circle."""
        X, Y, Z = P(p)
        rx = abs(r * si)
        items.append((Z - 0.5, f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{max(0.4, rx * s):.1f}" ry="{r * s:.1f}" fill="none" stroke="{col}" stroke-width="{w * s:.1f}" opacity="{op:.2f}"/>'))

    def line(pts, col, w, op=1.0, dash=None, cap="round"):
        q = [P(p) for p in pts]
        Z = sum(z for _, _, z in q) / len(q)
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y, _ in q)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        items.append((Z, f'<path d="{d}" stroke="{col}" stroke-width="{w * s:.1f}" fill="none" stroke-linecap="{cap}" stroke-linejoin="round" opacity="{op:.2f}"{da}/>'))

    def poly(pts, col, op=1.0, stroke=None):
        q = [P(p) for p in pts]
        Z = sum(z for _, _, z in q) / len(q)
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y, _ in q) + " Z"
        st = f' stroke="{stroke}" stroke-width="{1.0 * s:.1f}"' if stroke else ""
        items.append((Z, f'<path d="{d}" fill="{col}" opacity="{op:.2f}"{st}/>'))

    # abdomen: overlapping spheres along the axis with white bands
    sw = 1 + 0.9 * full
    for k in range(6):
        x0, x1 = 6 - 9.5 * k, 6 - 9.5 * (k + 1)
        r = (7.5 - 0.55 * k) * sw if k < 5 else 4.5
        line([(x0, 3 - 0.6 * k, 0), (x1, 3 - 0.6 * (k + 1), 0)], mixc("#2E2634", "#C8202E", full), 2 * r, 1.0)
    for k in range(7):
        x = 6 - 9.5 * k
        r = (7.5 - 0.55 * k) * sw if k < 6 else 3.5
        col = mixc("#2E2634", "#C8202E", full)
        sphere((x, 3 - 0.6 * k, 0), r, col, hl=(k % 2 == 0))
        if 0 < k < 6:
            ring((x + 4.5, 3 - 0.6 * k, 0), r * 0.98, "#F4F0FF", 1.8, 0.75 * (1 - 0.6 * full))
    # thorax + scutum stripe
    ellipsoid((22, -3, 0), 15, 12, 10, "#3A3044")
    line([(13, -13, 0), (22, -15.5, 0), (31, -10, 0)], "#F4F0FF", 2.4, 0.85)
    # head, eyes
    sphere((40, 2, 0), 8, "#2A2232")
    for zz in (-4.5, 4.5):
        sphere((43, 0, zz), 5.2, "#120C18", hl=True)
    # proboscis + palps
    line([(46, 6, 0), (66, 14, 0), (86, 22, 0)], "#1C1420", 2.4)
    line([(46, 5, 0), (62, 11, 0)], "#F4F0FF", 1.4, 0.7)
    # antennae
    for zz in (-3, 3):
        line([(45, -4, zz), (56, -13, zz * 2.2), (70, -18, zz * 3.0)], "#2A2232", 1.4)
    # legs (3 pairs), banded
    hips = [(18, 4), (22, 5), (26, 4)]
    for k, (hx, hy) in enumerate(hips):
        for side in (-1, 1):
            if legs == "land":
                knee = (hx + (-24, 2, 26)[k], hy + 22 + 2 * math.sin(t * 2 + k), side * (20 + 4 * k))
                foot = (hx + (-50, -4, 52)[k], 44, side * (36 + 6 * k))
            else:
                knee = (hx - 10 - 8 * k, hy + 18, side * 10)
                foot = (hx - 34 - 14 * k, hy + 40, side * 16)
            pts = [(hx, hy, side * 3), knee, foot]
            line(pts, "#241C2C", 2.2)
            line(pts, "#F4F0FF", 2.4, 0.8, dash="2 7", cap="butt")
    # wings (folded back over the abdomen when landed, or flapping)
    fl = math.sin(t * 38) * flap
    for side in (-1, 1):
        lift = 14 + 26 * fl if flap > 0 else 0
        base = (20, -12, side * 3)
        tip = (-38, -16 - lift, side * (12 + 6 * flap))
        mid1 = (-6, -22 - lift * 0.6, side * (9 + 4 * flap))
        mid2 = (-8, -8 - lift * 0.4, side * (5 + 4 * flap))
        poly([base, mid1, tip, mid2], "#DFF2FF", 0.38, stroke="#B8D8F0")
    # eggs glued under the abdomen
    if eggs:
        for k in range(7):
            x = -36 + 9 * k
            for zz in ((-2.5,) if k % 2 else (2.5,)):
                p = (x, 12 + 0.6 * math.sin(k * 1.7), zz)
                X, Y, Z = P(p)
                rx = math.sqrt((4.5 * c) ** 2 + (4.5 * si) ** 2)
                items.append((Z - 0.2, f'<ellipse cx="{X:.1f}" cy="{Y + 5 * s:.1f}" rx="{max(2.2, 4.2 * s * (0.55 + 0.45 * abs(si))):.1f}" ry="{7 * s:.1f}" fill="#FFF4DC" stroke="#C8A878" stroke-width="{0.9 * s:.1f}"/>'
                                    f'<ellipse cx="{X - 1.2 * s:.1f}" cy="{Y + 2.5 * s:.1f}" rx="{1.4 * s:.1f}" ry="{3 * s:.1f}" fill="#FFFFFF" opacity="0.75"/>'))
    items.sort(key=lambda it: -it[0])
    return "".join(svg for _, svg in items)
