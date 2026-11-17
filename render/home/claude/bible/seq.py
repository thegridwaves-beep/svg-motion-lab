"""One continuous sequence: a camera moving through connected scenes.

Shot grammar used here
- camera keys per scene: (time, zoom, focus_x, focus_y); focus point sits at screen centre
- linked zoom transition: the outgoing camera dives into a point while the incoming scene
  grows out of that same point at the same zoom rate, so motion never breaks
- cut on action: a hard cut to a new angle (close-up) right after a fast move
"""
import math, os, sys, shutil, subprocess
from playwright.sync_api import sync_playwright
import vivid as V
import render

FPS = 24
W, H = V.W, V.H


def ease_io(x):
    x = max(0.0, min(1.0, x))
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_in(x):
    x = max(0.0, min(1.0, x))
    return x ** 3


def lerp(a, b, u):
    return a + (b - a) * u


def cam_at(keys, t):
    """keys: [(t, zoom, fx, fy)]. Cubic Hermite spline through the keys (zoom in log space).
    Velocity is continuous through interior keys, and eases to rest only at the first and last key,
    so the camera never stutters."""
    if t <= keys[0][0]:
        return keys[0][1:]
    if t >= keys[-1][0]:
        return keys[-1][1:]
    P = [(k[0], math.log(k[1]), k[2], k[3]) for k in keys]
    n = len(P)
    def tan(i, d):
        if i == 0 or i == n - 1:
            return 0.0
        return (P[i + 1][d] - P[i - 1][d]) / (P[i + 1][0] - P[i - 1][0])
    for i in range(n - 1):
        if P[i][0] <= t <= P[i + 1][0]:
            h = P[i + 1][0] - P[i][0]
            u = (t - P[i][0]) / h
            h00, h10, h01, h11 = 2*u**3 - 3*u**2 + 1, u**3 - 2*u**2 + u, -2*u**3 + 3*u**2, u**3 - u**2
            out = [h00 * P[i][d] + h10 * h * tan(i, d) + h01 * P[i + 1][d] + h11 * h * tan(i + 1, d) for d in (1, 2, 3)]
            return math.exp(out[0]), out[1], out[2]


def clamp_focus(z, fx, fy):
    """Keep the camera inside the scene so its edge never shows."""
    hx, hy = W / 2 / z, H / 2 / z
    return min(max(fx, hx), W - hx), min(max(fy, hy), H - hy)


def place(scene_svg, z, fx, fy, op=1.0, blur=0.0, anchor=(W / 2, H / 2)):
    f = f' filter="url(#mb{int(blur)})"' if blur >= 1 else ""
    return (f'<g opacity="{op:.3f}"{f}><g transform="translate({anchor[0]:.2f} {anchor[1]:.2f}) scale({z:.4f}) translate({-fx:.2f} {-fy:.2f})">'
            f'{scene_svg}</g></g>')


# ---------------------------------------------------------------- the shot list
# each shot: name, scene fn, start, end, camera keys (local time)
SHOTS = [
    # 1. hook: open tight on the rocket already flying, pull out to reveal the planet
    dict(name="space", fn=V.f_space, t0=0.0, t1=3.4,
         keys=[(0.0, 2.5, 220, 392), (1.7, 1.05, 500, 290), (2.6, 1.0, 495, 290)]),
    # 2. CONTINUITY zoom: the tiny Earth in shot 1 grows into this Earth (same object, so it earns the zoom)
    dict(name="earth", fn=V.f_earth, t0=2.6, t1=5.4,
         keys=[(0.8, 1.3, 480, 290), (2.8, 1.12, 470, 292)]),
    # 3. CUT ON MOTION: hard cut, camera already gliding, new place
    dict(name="island", fn=V.f_island, t0=5.4, t1=8.3,
         keys=[(0.0, 1.32, 440, 300), (2.9, 1.08, 500, 290)]),
    # 4. WHIP PAN: fast sideways move with motion blur into a new location
    dict(name="room", fn=V.f_room, t0=7.95, t1=10.6,
         keys=[(0.35, 1.06, 480, 320), (2.65, 1.18, 420, 325)]),
    # 5. CUT TO A NEW ANGLE: close-up reaction
    dict(name="mira", fn=V.f_ava, t0=10.6, t1=13.2,
         keys=[(0.0, 1.14, 520, 292), (2.6, 1.03, 480, 280)]),
]

# transitions: "zoom" = linked continuity zoom through a portal; "whip" = sideways whip pan.
# Anything not listed is a straight cut.
TRANS = [
    dict(kind="zoom", a="space", b="earth", t0=2.6, t1=3.4, dive=(150, 300), s1=21.7, i1=1.3, portal=("circle", 9)),
    dict(kind="whip", a="island", b="room", t0=7.95, t1=8.3),
]


def frame_at(t, cache=None):
    layers = []
    for sh in SHOTS:
        if not (sh["t0"] <= t < sh["t1"]):
            continue
        tl = t - sh["t0"]
        V.T = tl
        z, fx, fy = cam_at(sh["keys"], tl)
        op = 1.0
        tr_out = next((tr for tr in TRANS if tr["a"] == sh["name"] and tr["t0"] <= t < tr["t1"]), None)
        tr_in = next((tr for tr in TRANS if tr["b"] == sh["name"] and tr["t0"] <= t < tr["t1"]), None)
        whip = tr_out if (tr_out and tr_out["kind"] == "whip") else (tr_in if (tr_in and tr_in["kind"] == "whip") else None)
        if whip:
            u = (t - whip["t0"]) / (whip["t1"] - whip["t0"])
            sp = ease_io(u)
            if whip is tr_in:
                z, fx, fy = cam_at(sh["keys"], whip["t1"] - sh["t0"])
                dx = W * (1 - sp)
            else:
                z, fx, fy = cam_at(sh["keys"], whip["t0"] - sh["t0"])
                dx = -W * sp
            fx, fy = clamp_focus(z, fx, fy)
            amt = 1 - abs(2 * u - 1)          # blur peaks mid-whip
            V.BARE = True
            mid = f"wb{len(layers)}"
            layers.append(f'<filter id="{mid}" x="-20%" y="0" width="140%" height="100%"><feGaussianBlur stdDeviation="{18*amt:.1f} 0"/></filter>'
                          f'<g filter="url(#{mid})">{place(sh["fn"](), z, fx, fy, 1.0, anchor=(W/2 + dx, H/2))}</g>')
            continue
        blur = 0
        if tr_out:
            u = ease_in((t - tr_out["t0"]) / (tr_out["t1"] - tr_out["t0"]))
            z0, x0, y0 = cam_at(sh["keys"], tr_out["t0"] - sh["t0"])
            z = math.exp(lerp(math.log(z0), math.log(tr_out["s1"]), u))
            pf = ease_io(min(1.0, (t - tr_out["t0"]) / (tr_out["t1"] - tr_out["t0"]) * 1.7))
            fx, fy = lerp(x0, tr_out["dive"][0], pf), lerp(y0, tr_out["dive"][1], pf)
            blur = 2 if 0.3 < u < 0.9 else 0
        if not tr_in:
            fx, fy = clamp_focus(z, fx, fy)
        if tr_in:
            tro = tr_in
            u = ease_in((t - tro["t0"]) / (tro["t1"] - tro["t0"]))
            # outgoing zoom at start of the transition
            a = next(s for s in SHOTS if s["name"] == tro["a"])
            za0 = cam_at(a["keys"], tro["t0"] - a["t0"])[0]
            i0 = tro["i1"] * za0 / tro["s1"]
            z = math.exp(lerp(math.log(i0), math.log(tro["i1"]), u))
            fx, fy = cam_at(sh["keys"], 0.8)[1:]
            # portal: reveal through the shape the camera dives into, growing with the outgoing zoom
            zo = math.exp(lerp(math.log(za0), math.log(tro["s1"]), u))
            # where the dive point sits on screen right now (outgoing camera, clamped)
            pf = ease_io(min(1.0, (t - tro["t0"]) / (tro["t1"] - tro["t0"]) * 1.7))
            ax0, ay0 = cam_at(a["keys"], tro["t0"] - a["t0"])[1:]
            ofx, ofy = clamp_focus(zo, lerp(ax0, tro["dive"][0], pf), lerp(ay0, tro["dive"][1], pf))
            anc = (W / 2 + (tro["dive"][0] - ofx) * zo, H / 2 + (tro["dive"][1] - ofy) * zo)
            pt = tro["portal"]
            base_r = pt[1] if pt[0] == "circle" else max(pt[1], pt[2]) / 2
            grow = 1 + max(0.0, 640 / (base_r * tro["s1"]) - 1) * u ** 3
            op = min(1.0, u / 0.12)
            if pt[0] == "circle":
                r_ = pt[1] * zo * grow
                shape = f'<circle cx="{anc[0]:.2f}" cy="{anc[1]:.2f}" r="{r_:.2f}" fill="#fff"/>'
            else:
                w_, h_ = pt[1] * zo * grow, pt[2] * zo * grow
                shape = f'<rect x="{anc[0] - w_/2:.2f}" y="{anc[1] - h_/2:.2f}" width="{w_:.2f}" height="{h_:.2f}" rx="{min(w_, h_)*0.08:.2f}" fill="#fff"/>'
            V.BARE = True
            mid = f"pm{len(layers)}"
            layers.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#000"/>'
                          f'<g filter="url(#mb2)">{shape}</g></mask><g mask="url(#{mid})">{place(sh["fn"](), z, fx, fy, op, anchor=(lerp(anc[0], W / 2, u ** 2), lerp(anc[1], H / 2, u ** 2)))}</g>')
            continue
        V.BARE = True
        layers.append(place(sh["fn"](), z, fx, fy, op, blur))
    V.BARE = False
    defs = ('<filter id="mb2" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="2.2"/></filter>'
            '<radialGradient id="ovig" cx="0.5" cy="0.5" r="0.75"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#0A0420" stop-opacity="0.4"/></radialGradient>'
            '<filter id="ograin"><feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.9 -0.4"/></filter>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 {W} {H}"><defs>{defs}</defs>'
            f'<rect width="{W}" height="{H}" fill="#0A0628"/>{"".join(layers)}'
            f'<rect width="{W}" height="{H}" fill="url(#ovig)"/><rect width="{W}" height="{H}" filter="url(#ograin)" opacity="0.06" style="mix-blend-mode:overlay"/></svg>')


def render_seq(name="seq_test", t_start=0.0, t_end=None, step=1):
    t_end = t_end or max(s["t1"] for s in SHOTS)
    tmp = os.path.join(render.OUT, f"_{name}")
    shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    V.ANIM = True
    n = int((t_end - t_start) * FPS)
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1920, "height": 1080})
        for i in range(0, n, step):
            html = os.path.join(tmp, "f.html")
            open(html, "w").write(f"<!doctype html><html><head><style>{render.FONTS}</style></head><body>{frame_at(t_start + i / FPS)}</body></html>")
            pg.goto("file://" + html)
            pg.screenshot(path=os.path.join(tmp, f"{i//step:04d}.png"))
        br.close()
    V.ANIM = False
    return tmp


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode == "contact":       # quick check: a frame every 1/3 s
        tmp = render_seq("seq_contact", step=8)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(tmp, "%04d.png"),
                        "-vf", "scale=480:-1,tile=6x8", "-frames:v", "1", os.path.join(render.OUT, "seq_contact.jpg")], check=True)
        print("contact ok")
    else:
        tmp = render_seq("seq_test")
        out = os.path.join(render.OUT, "seq_test.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "%04d.png"),
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], check=True)
        print("wrote", out)
