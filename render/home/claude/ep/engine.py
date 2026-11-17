"""Shot engine: layered 2D shots with parallax camera; static layers cached as images when rendering."""
import os, sys, json, time, math, subprocess
sys.path.insert(0, "/home/claude/bible")
import vivid as V
V.ANIM = True
import render

W, H = 960, 540
FPS = 30
TL = {s["name"]: s for s in json.load(open("/home/claude/ep/timeline.json"))}
ORDER = [s["name"] for s in json.load(open("/home/claude/ep/timeline.json"))]
SHOTS = {}
CACHE = "/home/claude/ep/cache"; OUT = "/home/claude/ep/shots"
STATIC_K = 2.2   # raster scale of cached static layers; shows with in-shot punch-ins raise it
os.makedirs(CACHE, exist_ok=True); os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ vertical (9:16) mode: same shots, a portrait window that follows the subject
VERT = os.environ.get("VERT") == "1"
VW, VH = 360, 640                 # portrait window in screen units (shows 1080x1920 at 3 px per unit)
VFRAME = {}                       # shot name -> (cx, cy) or fn(t, D) -> (cx, cy): centre of the portrait window in 960x540 screen space


def vwin(name, t):
    """Portrait window (x0, y0, w, h); a VFRAME entry may add a third value k > 1 to widen the window (zoom out)."""
    f = VFRAME.get(name, (480, 270))
    v = f(t, TL[name]["dur"]) if callable(f) else f
    cx, cy, k = (v + (1.0,))[:3] if len(v) == 2 else v
    w, h = VW * k, VH * k
    return cx - w / 2, cy - h / 2, w, h


def vert_overlay(ov, x0, y0, w=VW, h=VH, top=62, bottom=150):
    """Screen-space overlay (drawn for 960x540) mapped into the portrait window: its top half sits under the top safe margin,
    its bottom half above the bottom safe margin, both scaled to the window width."""
    if not ov:
        return ""
    k = w / W; top *= w / VW; bottom *= w / VW
    yt = y0 + top; yb = y0 + h - bottom - k * H
    return (f'<clipPath id="ovT"><rect x="-50" y="-200" width="1060" height="470"/></clipPath><clipPath id="ovB"><rect x="-50" y="270" width="1060" height="470"/></clipPath>'
            f'<g transform="translate({x0:.2f} {yt:.2f}) scale({k:.4f})"><g clip-path="url(#ovT)">{ov}</g></g>'
            f'<g transform="translate({x0:.2f} {yb:.2f}) scale({k:.4f})"><g clip-path="url(#ovB)">{ov}</g></g>')


# survival clock per section
SECTION_CLOCK = [("f_", "00:00:01"), ("s_", "00:00:10"), ("c_", "00:01:00"), ("d_", "00:05:00"), ("r_", "00:15:00"), ("v_", "00:20:00"), ("l_", "00:25:00")]


def shot(name):
    def deco(fn):
        SHOTS[name] = fn
        return fn
    return deco


def layer_tf(cam, depth):
    """cam = (dx, dy, z): look at (480+dx, 270+dy) on the main plane (depth 1) with zoom z; other depths parallax."""
    dx, dy, z = cam[:3]
    roll = cam[3] if len(cam) > 3 else 0.0
    zl = 1 + (z - 1) * depth
    return f"translate({W/2} {H/2}) rotate({roll:.3f}) scale({zl:.5f}) translate({-(W/2 + dx*depth):.3f} {-(H/2 + dy*depth):.3f})"


def clock_overlay(name, t):
    pref = name[:2]
    val, idx = None, None
    for i, (p, v) in enumerate(SECTION_CLOCK):
        if pref == p:
            val, idx = v, i
    if val is None:
        return ""
    first = TL[name]["start"] == min(TL[n]["start"] for n in ORDER if n.startswith(pref))
    k = 1.0
    roll = ""
    if first:
        u = min(1, t / 0.6)
        k = 1 + 0.25 * math.sin(math.pi * u) if t < 0.6 else 1.0
    from kit import text
    body = (f'<rect x="-92" y="-24" width="184" height="48" rx="14" fill="#140A3A" opacity="0.85"/>'
            f'<rect x="-92" y="-24" width="184" height="48" rx="14" fill="none" stroke="#FF4F9A" stroke-width="2"/>'
            f'<circle cx="-70" cy="0" r="5" fill="#FF4F7A" opacity="{0.55 + 0.45*math.sin(t*6):.2f}"/>' + text(10, 10, val, 28, "#FFFFFF", 700, "middle"))
    return f'<g transform="translate(130 56) scale({k:.3f})">{body}</g>'


def compose(name, t):
    s = TL[name]
    out = SHOTS[name](t, s["dur"], [c["t"] for c in s["cues"]])
    return out


def frame_svg(name, t):
    out = compose(name, t)
    cam = out.get("cam", (0, 0, 1.0))
    body = []
    for (lid, depth, svg, static, blur) in out["layers"]:
        f = f' filter="url(#b{blur})"' if blur else ""
        body.append(f'<g transform="{layer_tf(cam, depth)}"{f}>{svg}</g>')
    body.append(out.get("overlay", ""))
    if out.get("clock", True):
        body.append(clock_overlay(name, t))
    return V.svg("".join(body), out.get("defs", ""))


# ------------------------------------------------------------------ fast renderer with cached static layers
def build_cache(pg, name, out):
    files = {}
    pad_x, pad_y = out.get("pad", (260, 160))
    vb = (-pad_x, -pad_y, W + 2 * pad_x, H + 2 * pad_y)
    k = min(3.3 if VERT else STATIC_K, 9000 / vb[2], 9000 / vb[3])
    pw, ph = int(vb[2] * k), int(vb[3] * k)
    for (lid, depth, svg, static, blur) in out["layers"]:
        if not static:
            continue
        f = f' filter="url(#b{blur})"' if blur else ""
        doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{pw}" height="{ph}" viewBox="{vb[0]} {vb[1]} {vb[2]} {vb[3]}">'
               f'<defs>{V.defs()}{out.get("defs", "")}</defs><g{f}>{svg}</g></svg>')
        html = os.path.join(CACHE, f"{name}_{lid}.html")
        open(html, "w").write(f"<!doctype html><html><head><meta charset='utf-8'><style>html,body{{margin:0;background:transparent}}{render.FONTS}</style></head><body>{doc}</body></html>")
        pg.set_viewport_size({"width": pw, "height": ph})
        pg.goto("file://" + html)
        png = os.path.join(CACHE, f"{name}_{lid}.png")
        pg.screenshot(path=png, omit_background=True, timeout=600000)
        files[lid] = (png, vb)
    return files


def render_shot(br, name):
    s = TL[name]
    n = int(round(s["dur"] * FPS))
    PW, PH = (1080, 1920) if VERT else (1920, 1080)
    pg = br.new_page(viewport={"width": PW, "height": PH})
    t0 = time.time()
    out0 = compose(name, 0.0)
    files = build_cache(pg, name, out0)
    pg.set_viewport_size({"width": PW, "height": PH})
    groups = []
    for (lid, depth, svg, static, blur) in out0["layers"]:
        if static:
            png, vb = files[lid]
            groups.append(f'<g id="L_{lid}"><image href="file://{png}" x="{vb[0]}" y="{vb[1]}" width="{vb[2]}" height="{vb[3]}" preserveAspectRatio="none"/></g>')
        else:
            f = f' filter="url(#b{blur})"' if blur else ""
            groups.append(f'<g id="L_{lid}"{f}></g>')
    vbw, vbh = (VW, VH) if VERT else (W, H)
    page = (f'<svg id="root" xmlns="http://www.w3.org/2000/svg" width="{PW}" height="{PH}" viewBox="0 0 {vbw} {vbh}"><defs id="defs">{V.defs()}{out0.get("defs", "")}</defs>'
            f'{"".join(groups)}<g id="ov"></g>'
            f'<rect id="vigr" width="{vbw}" height="{vbh}" fill="url(#vig)"/>'
            f'<image id="grn" href="file:///home/claude/ant/grain.png" width="{vbw}" height="{vbh}" opacity="0.05" preserveAspectRatio="xMidYMid slice" style="mix-blend-mode:overlay"/></svg>')
    html = os.path.join(CACHE, f"{name}_frame.html")
    open(html, "w").write(f"<!doctype html><html><head><meta charset='utf-8'><style>html,body{{margin:0}}{render.FONTS}</style></head><body>{page}</body></html>")
    pg.goto("file://" + html)
    pg.wait_for_timeout(200)
    tmp = os.path.join(OUT, f"_{name}.tmp.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    tc = time.time()
    for i in range(n):
        t = i / FPS
        out = out0 if i == 0 else compose(name, t)
        cam = out.get("cam", (0, 0, 1.0))
        upd = []
        for (lid, depth, svg, static, blur) in out["layers"]:
            upd.append([f"L_{lid}", layer_tf(cam, depth), "" if static else svg, static])
        ov = out.get("overlay", "") + (clock_overlay(name, t) if out.get("clock", True) else "")
        win = None
        if VERT:
            x0, y0, ww, wh = vwin(name, t)
            ov = vert_overlay(ov, x0, y0, ww, wh) + out.get("voverlay", "")
            win = [x0, y0, ww, wh]
        pg.evaluate("""([u, ov, win]) => {
            for (const [id, tf, svg, st] of u) { const e = document.getElementById(id); if (!e) continue; e.setAttribute('transform', tf); if (!st) e.innerHTML = svg; }
            document.getElementById('ov').innerHTML = ov;
            if (win) { document.getElementById('root').setAttribute('viewBox', win.join(' '));
                       for (const id of ['vigr', 'grn']) { const e = document.getElementById(id); e.setAttribute('x', win[0]); e.setAttribute('y', win[1]); e.setAttribute('width', win[2]); e.setAttribute('height', win[3]); } } }""", [upd, ov, win])
        ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
    ff.stdin.close()
    if ff.wait() == 0:
        os.replace(tmp, os.path.join(OUT, f"{name}.mp4"))
    pg.close()
    print(f"{name}: cache {tc - t0:.0f}s, {n} frames {time.time() - tc:.0f}s ({(time.time() - tc)/max(n,1):.2f}s/f)", flush=True)


def stills(items, path="/home/claude/ep/stills"):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    os.makedirs(path, exist_ok=True)
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1920, "height": 1080})
        for name, t in items:
            html = os.path.join(path, "f.html")
            open(html, "w").write(f"<!doctype html><html><head><meta charset='utf-8'><style>{render.FONTS}</style></head><body>{frame_svg(name, t)}</body></html>")
            pg.goto("file://" + html); pg.screenshot(path=os.path.join(path, f"{name}_{t:05.2f}.jpg"), type="jpeg", quality=85)
        br.close()
    ims = [Image.open(os.path.join(path, f"{n}_{t:05.2f}.jpg")).resize((640, 360)) for n, t in items]
    sheet = Image.new("RGB", (3 * 645, ((len(ims) + 2) // 3) * 365), (10, 6, 30))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 3) * 645, (i // 3) * 365))
    sheet.save(os.path.join(path, "sheet.jpg"), quality=85)
