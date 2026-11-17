"""Storyboard core: each beat is a function returning a shot dict (layers/defs/cam/overlay), rendered as a keyframe.
Same dict format as engine shots, so the approved boards become the animated shots later."""
import os, sys, math, random, json
sys.path.insert(0, "/home/claude/ep")
import engine, rig2, grass2
rig2.install(); grass2.install_flat() if hasattr(grass2, "install_flat") else None
import shots_a, shots_b, shots_c, shots_d, shots_e
from engine import W, H, layer_tf
import vivid as V
import render
from kit import inside, P, S, E, C, R, U, g, text
import assets as A
from assets import drop, ant, glow, sh, GREENS, sparkle, raindrop, crumb, spider, label, bird_shadow, shrew, mosquito, neuron
from kit2 import *
from kit3 import side, pov_arm, silhouette, SIL_DEFS, topdown, top_contact, dof
from shots_a import KDEFS, kitchen_far
from shots_e import WORLD_BG, glossy_drop, crown, BLUE_BG, BP_DEFS, bird, soft
from shots_c import DIAG_BG, big_clock

BEATS = []   # (id, t_abs, vo, shot_label, motion_note, fn, key_t)


def beat(t, vo, shot, motion, key=0.6):
    def deco(fn):
        BEATS.append(dict(id=len(BEATS) + 1, t=t, vo=vo, shot=shot, motion=motion, fn=fn, key=key))
        return fn
    return deco


def frame(out):
    cam = out.get("cam", (0, 0, 1.0))
    body = []
    for (lid, depth, svg, static, blur) in out["layers"]:
        f = f' filter="url(#b{blur})"' if blur else ""
        body.append(f'<g transform="{layer_tf(cam, depth)}"{f}>{svg}</g>')
    body.append(out.get("overlay", ""))
    return V.svg("".join(body), out.get("defs", ""))


def one(svg, defs="", cam=(0, 0, 1.0), overlay=""):
    return dict(layers=[("all", 1.0, svg, False, None)], defs=defs, cam=cam, overlay=overlay)


def at(x, y, s, body, rot=0, flip=False):
    fx = -s if flip else s
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({fx:.4f} {s:.4f})">{body}</g>'


def bg(col1, col2, id_="bgg", vert=True):
    d = f'<linearGradient id="{id_}" x1="0" y1="0" x2="{0 if vert else 1}" y2="{1 if vert else 0}"><stop offset="0" stop-color="{col1}"/><stop offset="1" stop-color="{col2}"/></linearGradient>'
    return f'<rect x="-600" y="-600" width="2160" height="1740" fill="url(#{id_})"/>', d


def vignette(op=0.55, id_="vig2"):
    d = f'<radialGradient id="{id_}" cx="0.5" cy="0.5" r="0.75"><stop offset="0.55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#080320" stop-opacity="{op}"/></radialGradient>'
    return f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#{id_})"/>', d


def speed_lines(cx, cy, n=26, r0=180, r1=620, seed=3, col="#FFFFFF", op=0.5, vertical=False):
    rr = random.Random(seed); o = []
    for k in range(n):
        if vertical:
            x = rr.uniform(-40, 1000); y = rr.uniform(-60, 600); L = rr.uniform(60, 200)
            o.append(f'<path d="M{x:.0f} {y:.0f} L{x:.0f} {y - L:.0f}" stroke="{col}" stroke-width="{rr.uniform(1.5, 4):.1f}" stroke-linecap="round" opacity="{op * rr.uniform(0.4, 1):.2f}"/>')
        else:
            a = rr.uniform(0, 2 * math.pi); ra = rr.uniform(r0, r0 + 80); rb = rr.uniform(r1 * 0.7, r1)
            o.append(f'<path d="M{cx + ra*math.cos(a):.0f} {cy + ra*math.sin(a):.0f} L{cx + rb*math.cos(a):.0f} {cy + rb*math.sin(a):.0f}" stroke="{col}" stroke-width="{rr.uniform(1.5, 5):.1f}" stroke-linecap="round" opacity="{op * rr.uniform(0.4, 1):.2f}"/>')
    return "".join(o)


def dust_puff(cx, cy, s=1.0, seed=2, col="#E8D8FF", op=0.8):
    rr = random.Random(seed); o = []
    for k in range(9):
        a = math.pi + k * math.pi / 8
        d = rr.uniform(40, 80) * s
        o.append(f'<circle cx="{cx + d*math.cos(a)*1.4:.0f}" cy="{cy + d*math.sin(a)*0.45:.0f}" r="{rr.uniform(14, 26)*s:.0f}" fill="{col}" opacity="{op*rr.uniform(0.5, 0.9):.2f}"/>')
    return f'<g filter="url(#b3)">{"".join(o)}</g>'


def big_text(x, y, s, size=64, col="#FFFFFF", anchor="middle", stroke="#120836"):
    return (f'<text x="{x}" y="{y + 4}" font-family="Fredoka, sans-serif" font-weight="700" font-size="{size}" fill="{stroke}" opacity="0.55" text-anchor="{anchor}">{s}</text>'
            + text(x, y, s, size, col, 700, anchor))


def pill(x, y, s, bgc="#FF4F9A", fg="#FFFFFF", size=26, pad=18):
    w = len(s) * size * 0.56 + pad * 2
    return (f'<rect x="{x - w/2:.0f}" y="{y - size*0.95:.0f}" width="{w:.0f}" height="{size*1.45:.0f}" rx="{size*0.72:.0f}" fill="{bgc}"/>'
            + text(x, y, s, size, fg, 700, "middle"))


def xstamp(x, y, s=1.0, rot=-12):
    return at(x, y, s, '<circle r="62" fill="#FF3D6E" opacity="0.92"/><circle r="62" fill="none" stroke="#FFFFFF" stroke-width="6"/>'
              '<path d="M-28 -28 L28 28 M28 -28 L-28 28" stroke="#FFFFFF" stroke-width="14" stroke-linecap="round"/>', rot)


def clock_chip(val, x=480, y=60, s=1.0, col="#FF4F9A"):
    body = (f'<rect x="-120" y="-30" width="240" height="60" rx="18" fill="#140A3A" opacity="0.9"/>'
            f'<rect x="-120" y="-30" width="240" height="60" rx="18" fill="none" stroke="{col}" stroke-width="3"/>'
            f'<circle cx="-94" cy="0" r="7" fill="{col}"/>' + text(12, 12, val, 34, "#FFFFFF", 700, "middle"))
    return at(x, y, s, body)


def person(arms="stand", legs="stand", expr="neutral", tilt=0, blink=False):
    return front(arms, legs, expr, tilt, blink)


def render_beats(beats, outdir="/home/claude/ep/board", only=None):
    from playwright.sync_api import sync_playwright
    os.makedirs(outdir, exist_ok=True)
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1920, "height": 1080})
        for b in beats:
            if only and b["id"] not in only:
                continue
            try:
                svg = frame(b["fn"](b["key"]))
            except Exception as e:
                import traceback; traceback.print_exc(); print("FAIL", b["id"], repr(e)); continue
            pg.set_content(f"<!doctype html><html><head><meta charset='utf-8'><style>{render.FONTS} body{{margin:0}}</style></head><body>{svg}</body></html>")
            pg.wait_for_timeout(30)
            pg.screenshot(path=f"{outdir}/b{b['id']:03d}.jpg", type="jpeg", quality=88)
        br.close()
