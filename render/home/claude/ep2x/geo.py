"""Real coastlines (Natural Earth 110m via johan/world.geo.json, public domain) for maps and globes.
mercator map:   land_map(box, lon0, lon1, lat0, lat1) -> svg paths
globe:          globe_land(cx, cy, r, lon0, lat0) -> svg paths (orthographic, far side folded to the limb)"""
import json, math
_D = json.load(open("/home/claude/geo/world.geo.json/countries.geo.json"))
FEAT = {f["properties"]["name"]: f for f in _D["features"]}


def rings(names=None):
    for f in _D["features"]:
        if names and f["properties"]["name"] not in names:
            continue
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in polys:
            yield f["properties"]["name"], poly[0]


def _merc_y(lat):
    lat = max(-85, min(85, lat))
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


class MapProj:
    """Mercator into the screen box (x, y, w, h) covering lon0..lon1 and lat0 (south)..lat1 (north); keeps aspect by width."""
    def __init__(self, box, lon0, lon1, lat0, lat1):
        self.x, self.y, self.w, self.h = box
        self.lon0, self.lon1 = lon0, lon1
        self.y0, self.y1 = _merc_y(lat0), _merc_y(lat1)
        self.k = self.w / math.radians(lon1 - lon0)
        cy = (self.y0 + self.y1) / 2
        self.cy_scr = self.y + self.h / 2; self.cy = cy

    def __call__(self, lon, lat):
        return self.x + math.radians(lon - self.lon0) * self.k, self.cy_scr - (_merc_y(lat) - self.cy) * self.k


def land_map(P, names=None, fill="#6AA86A", stroke=None, sw=1.2, exclude=(), op=1.0):
    o = []
    for nm, ring in rings(names):
        if nm in exclude:
            continue
        pts = [P(lon, lat) for lon, lat in ring]
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"
        o.append(f'<path d="{d}"/>')
    st = f' stroke="{stroke or fill}" stroke-width="{sw}" stroke-linejoin="round"'
    return f'<g fill="{fill}"{st} opacity="{op}">{"".join(o)}</g>'


def ortho(lon, lat, lon0, lat0):
    l, p, l0, p0 = map(math.radians, (lon, lat, lon0, lat0))
    x = math.cos(p) * math.sin(l - l0)
    y = math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(l - l0)
    c = math.sin(p0) * math.sin(p) + math.cos(p0) * math.cos(p) * math.cos(l - l0)
    return x, -y, c


def globe_land(cx, cy, r, lon0, lat0, names=None, fill="#4AA86A", stroke=None, sw=0.8, densify=2.0):
    o = []
    for nm, ring in rings(names):
        if nm == "Antarctica" and lat0 > 20:
            continue
        pts, vis = [], 0
        prev = None
        for lon, lat in ring:
            # densify long edges so folding to the limb stays smooth
            if prev is not None:
                n = int(max(abs(lon - prev[0]), abs(lat - prev[1])) / densify)
                for k in range(1, n):
                    u = k / n
                    pts.append(ortho(prev[0] + (lon - prev[0]) * u, prev[1] + (lat - prev[1]) * u, lon0, lat0))
            q = ortho(lon, lat, lon0, lat0); pts.append(q); prev = (lon, lat)
            vis += q[2] > 0
        if vis == 0:
            continue
        sp = []
        for x, y, c in pts:
            if c < 0:
                m = math.hypot(x, y) or 1e-6; x, y = x / m, y / m
            sp.append((cx + r * x, cy + r * y))
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in sp) + "Z"
        o.append(f'<path d="{d}"/>')
    st = f' stroke="{stroke or fill}" stroke-width="{sw}" stroke-linejoin="round"'
    return f'<g fill="{fill}"{st}>{"".join(o)}</g>'


def globe_pt(cx, cy, r, lon, lat, lon0, lat0):
    x, y, c = ortho(lon, lat, lon0, lat0)
    return cx + r * x, cy + r * y, c


PLACES = dict(chicxulub=(-89.5, 21.4), toba=(98.83, 2.6), pinnacle=(22.09, -34.21), mexico_city=(-99.1, 19.4),
              delhi=(77.2, 28.6), nagpur=(79.1, 21.1))
