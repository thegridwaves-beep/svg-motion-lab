"""Grass v2: blades grow in clumps from a rooted base (soft occlusion + a little soil mound hides every root),
each blade is a curved, tapering leaf that arcs and droops toward its tip, and near blades sway with the wind.
Patches kit2.pblade / kit2.blades / kit2.forest in place, so every scene picks it up."""
import math, random, sys
sys.path.insert(0, "/home/claude/ant"); sys.path.insert(0, "/home/claude/bible"); sys.path.insert(0, "/home/claude/ep")
import kit as K
from kit import inside, P, E, g
import kit2
from assets import sh, GREENS

T_NOW = [0.0]          # set by the engine each frame (for swaying dynamic layers)


def _blur(svg, b):
    f, d = K.blur_f(b)
    return d + f'<g{f}>{svg}</g>'


def leaf_blade(bx, by, ux, uy, h, w, col, bend=0.25, droop=0.1, sway=0.0, simple=False):
    """A curved grass leaf rooted at (bx, by), growing along (ux, uy), arching sideways by bend*h."""
    nx, ny = -uy, ux
    b = (bend + sway) * h
    # spine: base -> mid (pushed sideways a little) -> tip (pushed sideways more, and drooping back toward the ground)
    mx, my = bx + ux * h * 0.55 + nx * b * 0.35, by + uy * h * 0.55 + ny * b * 0.35
    tx, ty = bx + ux * h * (1 - droop) + nx * b, by + uy * h * (1 - droop) + ny * b
    root = 0.12 * w
    d = (f"M{bx - nx * w / 2:.1f} {by - ny * w / 2 + root:.1f} "
         f"Q{mx - nx * w * 0.42:.1f} {my - ny * w * 0.42:.1f} {tx:.1f} {ty:.1f} "
         f"Q{mx + nx * w * 0.5:.1f} {my + ny * w * 0.5:.1f} {bx + nx * w / 2:.1f} {by + ny * w / 2 + root:.1f} Z")
    shape = P(d)
    if simple or w < 3:
        half = (f"M{bx:.1f} {by + root:.1f} Q{mx + nx * w * 0.5:.1f} {my + ny * w * 0.5:.1f} {tx:.1f} {ty:.1f} "
                f"Q{mx + nx * w * 0.1:.1f} {my + ny * w * 0.1:.1f} {bx + nx * w / 2:.1f} {by + ny * w / 2 + root:.1f} Z")
        return shape(col[0]) + f'<path d="{half}" fill="{col[1]}" opacity="0.55"/>'
    return sh(shape, col[0], col[1], col[2], max(0.3, w / 22))


def tuft(cam, x, y, h, w, rr, cols, sway_t=None, n=None, lean=0.0, ao=None, simple=False):
    vx, vy = cam.vp
    dx, dy = vx - x, vy - y
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    if vy > y:
        ux, uy = -ux, -uy
    n = n or rr.randint(3, 5)
    col = rr.choice(cols)
    aos = f'<ellipse cx="{x:.1f}" cy="{y + w * 0.1:.1f}" rx="{w * 2.6:.1f}" ry="{max(1.5, w * 0.55):.1f}" fill="#120830" opacity="0.5"/>'
    o = []
    if ao is not None: ao.append(aos)
    else: o.append(_blur(aos, max(0.8, w * 0.25)))
    blades_ = []
    for i in range(n):
        f = (i - (n - 1) / 2) / max(1, (n - 1) / 2)          # -1 .. 1 across the clump
        hh = h * rr.uniform(0.55, 1.0) * (1 - 0.25 * abs(f))
        ww = w * rr.uniform(0.75, 1.05)
        bend = 0.34 * f + rr.uniform(-0.1, 0.1) + lean
        sw = 0.0
        if sway_t is not None:
            ph = rr.uniform(0, 6.28)
            sw = 0.035 * math.sin(sway_t * 1.3 + ph) + 0.015 * math.sin(sway_t * 2.9 + ph * 1.7)
        c = col if rr.random() < 0.7 else rr.choice(cols)
        blades_.append((abs(f), leaf_blade(x + f * w * 0.9, y, ux, uy, hh, ww, c, bend, rr.uniform(0.06, 0.2), sw, simple)))
    blades_.sort(key=lambda a: -a[0])                         # outer blades behind, centre blades in front
    o += [s for _, s in blades_]
    # a little soil lip over the roots so nothing floats
    o.append(f'<ellipse cx="{x:.1f}" cy="{y + w * 0.3:.1f}" rx="{w * 1.6:.1f}" ry="{max(1.0, w * 0.3):.1f}" fill="#2A1450" opacity="0.45"/>')
    return "".join(o)


def pblade(cam, bx, by, h, w, col, lean=0.0, sway=0.0, shadow=True):
    rr = random.Random(int(bx * 7 + by * 13))
    return tuft(cam, bx, by, h, w * 0.8, rr, [col], None, n=3, lean=lean + sway)


def blades(cam, seed, n, dmin, dmax, hmin, hmax, wmul=1.0, avoid=None, umin=-1.1, umax=1.1, t=0.0, sway=0.0, cols=GREENS, tuft_n=None):
    rr = random.Random(seed)
    items = []
    ao = []
    # tall clumps, gathered into loose patches instead of evenly sprinkled spikes
    centers = [(rr.uniform(umin, umax), rr.uniform(dmin, dmax)) for _ in range(max(2, n // 4))]
    for k in range(n):
        cu, cd = centers[k % len(centers)]
        d = min(dmax, max(dmin, cd + rr.gauss(0, (dmax - dmin) * 0.12)))
        u = min(umax, max(umin, cu + rr.gauss(0, 0.18)))
        x, y = cam.gx(u, d), cam.gy(d)
        if avoid and avoid[0] < x < avoid[1] and d > avoid[2]:
            continue
        sc = cam.scale(d)
        h = rr.uniform(hmin, hmax) * sc * 1.35
        w = h * rr.uniform(0.05, 0.075) * wmul
        items.append((d, tuft(cam, x, y, h, w, rr, cols, (t if sway else None), n=tuft_n, ao=ao)))
    # a carpet of short tufts between the patches, so the ground reads as a meadow floor
    for k in range(int(n * 1.2) if dmax <= 0.6 else 0):
        d = rr.uniform(max(dmin, 0.04), min(1.0, dmax + 0.15))
        u = rr.uniform(umin, umax)
        x, y = cam.gx(u, d), cam.gy(d)
        if avoid and avoid[0] < x < avoid[1] and d > avoid[2]:
            continue
        sc = cam.scale(d)
        h = rr.uniform(40, 110) * sc
        w = h * rr.uniform(0.07, 0.1)
        items.append((d, tuft(cam, x, y, h, w, rr, cols, None, n=rr.randint(3, 5), ao=ao, simple=True)))
    items.sort(key=lambda a: a[0])
    return f'<g filter="url(#b4)">{"".join(ao)}</g>' + "".join(s for _, s in items)


def forest(cam, seed, n=60, haze=0.55, mood_col=None):
    rr = random.Random(seed)
    items = []
    for k in range(n):
        d = rr.uniform(0.0, 0.12)
        x, y = cam.gx(rr.uniform(-1.2, 1.2), d), cam.gy(d) + 90   # roots run down behind the ground layer
        h = rr.uniform(2200, 4200) * cam.scale(d) * 1.9 + 90
        w = h * rr.uniform(0.05, 0.08)
        items.append((d, tuft(cam, x, y, h, w, rr, GREENS, None, n=rr.randint(3, 4), ao=[], simple=True)))
    items.sort(key=lambda a: a[0])
    return f'<g opacity="{haze}">{"".join(s for _, s in items)}</g>'


def install():
    kit2.pblade = pblade
    kit2.blades = blades
    kit2.forest = forest


install()


# ------------------------------------------------------------------ flat (side-on) versions for the hook / ep1 code paths
UP = kit2.Cam(hz=-100000, vp=(480, -10_000_000), near=600)


def grass_field_flat(rnd, x0, x1, y, hmin, hmax, wmin, wmax, n, t, cols=GREENS, wind=1.0, haze=None):
    items = []
    for i in range(max(2, int(n * 0.7))):
        x = rnd.uniform(x0, x1); h = rnd.uniform(hmin, hmax); w = rnd.uniform(wmin, wmax) * 0.55
        cam = kit2.Cam(hz=-100000, vp=(x, -10_000_000), near=600)
        items.append(tuft(cam, x, y + rnd.uniform(0, 6), h, w, rnd, cols, (t if wind else None), n=rnd.randint(3, 5), ao=[]))
    s = "".join(items)
    return f'<g opacity="{haze}">{s}</g>' if haze else s


def blade_flat(x, y, h, w, bend, col, sway=0.0):
    nb = (bend + sway) / max(h, 1)
    return leaf_blade(x, y, 0.0, -1.0, h, w * 0.8, col, nb, 0.08, 0.0)


def install_flat():
    import ep1, assets
    ep1.grass_field = grass_field_flat
    assets.grass_field = grass_field_flat
    try:
        import hook
        hook.blade = blade_flat
    except Exception:
        pass


install_flat()
