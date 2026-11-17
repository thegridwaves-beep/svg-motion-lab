"""Review fixes: glossy raindrop, clock shot in the new grass, a readable bird, a rebuilt ending that shows
exactly what the narration says, and diagram scenes set inside the world instead of an empty purple void."""
import math, random, sys
sys.path.insert(0, "/home/claude/ant"); sys.path.insert(0, "/home/claude/ant2")
from engine import shot, W, H
import vivid as V
from kit import inside, P, S, E, C, R, U, g, text
import kit as K
import assets as A
from assets import ant, glow, sh, GREENS, sparkle, splash, label
from kit2 import *
import kit2, rig
from kit3 import side, silhouette, SIL_DEFS, topdown, top_contact
from shots_a import eo, ei
from shots_b import GAR, LOW, garden_layers, fg
import shots_c, hook

ease = V.ease
ramp = A.ramp


def soft(svg, b=4):
    f, d = K.blur_f(b)
    return d + f'<g{f}>{svg}</g>'


# ---------------------------------------------------------------- diagrams live inside the world now
WORLD_BG = (sky("gold", (760, 140)) + f'<g filter="url(#b8)">{forest(GAR, 901)}{ground(GAR, "gold", seed=900)}{blades(GAR, 902, 26, 0.02, 0.45, 260, 520)}</g>'
            + '<rect x="-300" y="-300" width="1560" height="1140" fill="#1A0A4A" opacity="0.58"/>')
shots_c.DIAG_BG = WORLD_BG
shots_c.DIAG = shots_c.DIAG + sky_defs("gold")


# ---------------------------------------------------------------- RAIN: a glossy drop slamming down beside you
def glossy_drop(cx, cy, r, squash=1.0):
    ry = r * squash
    body = P(f"M{cx:.1f} {cy - ry * 1.9:.1f} C{cx + r * 0.25:.1f} {cy - ry * 1.3:.1f} {cx + r:.1f} {cy - ry * 0.55:.1f} {cx + r:.1f} {cy:.1f} "
             f"A{r:.1f} {ry:.1f} 0 1 1 {cx - r:.1f} {cy:.1f} C{cx - r:.1f} {cy - ry * 0.55:.1f} {cx - r * 0.25:.1f} {cy - ry * 1.3:.1f} {cx:.1f} {cy - ry * 1.9:.1f} Z")
    gid = K.uid("dg")
    grad = (f'<radialGradient id="{gid}" cx="0.38" cy="0.62" r="0.75"><stop offset="0" stop-color="#E9FBFF"/><stop offset="0.45" stop-color="#8FDCFF"/>'
            f'<stop offset="0.85" stop-color="#3D8FE0"/><stop offset="1" stop-color="#2A5FC0"/></radialGradient>')
    inner = (soft(f'<ellipse cx="{cx + r * 0.18:.1f}" cy="{cy + ry * 0.35:.1f}" rx="{r * 0.62:.1f}" ry="{ry * 0.34:.1f}" fill="#2D4FB0" opacity="0.45"/>', r * 0.08) +   # refracted ground
             soft(f'<ellipse cx="{cx - r * 0.38:.1f}" cy="{cy - ry * 0.25:.1f}" rx="{r * 0.16:.1f}" ry="{ry * 0.42:.1f}" fill="#FFFFFF" opacity="0.92" transform="rotate(18 {cx - r * 0.38:.1f} {cy - ry * 0.25:.1f})"/>', r * 0.025) +
             soft(f'<ellipse cx="{cx + r * 0.42:.1f}" cy="{cy + ry * 0.48:.1f}" rx="{r * 0.2:.1f}" ry="{ry * 0.08:.1f}" fill="#FFFFFF" opacity="0.55"/>', r * 0.03) +
             soft(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 1.02:.1f}" fill="none" stroke="#DFF8FF" stroke-width="{r * 0.09:.1f}" opacity="0.5"/>', r * 0.04))
    return grad + body(f"url(#{gid})") + inside(body, inner)


def crown(cx, cy, s, u):
    """Milk-drop crown: a ring of thin jets that rise, throw droplets from their tips, and fall back."""
    if u <= 0 or u >= 1:
        return ""
    o = []
    rise = math.sin(math.pi * min(1, u * 1.15))
    o.append(soft(f'<ellipse cx="{cx:.1f}" cy="{cy - s * 0.2 * rise:.1f}" rx="{s * 0.8 * (0.6 + u):.1f}" ry="{s * 0.45 * rise:.1f}" fill="#9ADFFF" opacity="{0.55 * (1 - u):.2f}"/>', 6))
    ring = f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{s * (0.9 + 0.5 * u):.1f}" ry="{s * 0.2 * (1 + 0.5 * u):.1f}" fill="#7FCBFF" opacity="{0.7 * (1 - u):.2f}"/>'
    o.append(soft(ring, 2))
    n = 7
    for k in range(n):
        f = k / (n - 1)
        a = math.pi * f
        bx = cx - math.cos(a) * s * (0.85 + 0.4 * u)
        by = cy - math.sin(a) * s * 0.18
        h = s * (0.55 + 0.2 * math.sin(k * 2.3)) * rise
        lean = -math.cos(a) * s * 0.35 * rise
        tx, ty = bx + lean, by - h
        w = s * 0.13 * (1 - 0.4 * u)
        jet = P(f"M{bx - w:.1f} {by:.1f} Q{bx + lean * 0.4 - w * 0.6:.1f} {by - h * 0.55:.1f} {tx:.1f} {ty:.1f} Q{bx + lean * 0.4 + w * 0.6:.1f} {by - h * 0.55:.1f} {bx + w:.1f} {by:.1f} Z")
        for j in range(2):
            v = u
            sp = 1.0 + 0.35 * j
            dx = bx - math.cos(a) * s * 1.1 * v * sp
            dy = by - s * (3.6 + 0.8 * math.sin(k * 1.7 + j)) * v * sp + s * 3.4 * v * v
            o.append(glossy_drop(dx, dy, s * (0.09 - 0.03 * j) * (1 - 0.35 * v)))
    return "".join(o)


@shot("o_rain")
def _(t, D, c):
    """Low and close: a drop the size of a car comes down beside you and explodes into a crown."""
    cam = LOW
    L = [("sky", 0.1, sky("storm", None), True, None), ("forest", 0.25, forest(cam, 931), True, 2),
         ("gnd", 0.6, ground(cam, "storm", seed=930) + blades(cam, 932, 22, 0.03, 0.5, 300, 700, avoid=(230, 860, 0.15)), True, None)]
    yy = cam.gy(0.55)
    hit = 0.62
    u = min(1.0, t / hit)
    dy = 40 + (yy - 120 - 40) * u ** 1.4
    trail = soft("".join(f'<ellipse cx="640" cy="{dy - 180 - k * 70:.1f}" rx="{30 - k * 5:.1f}" ry="{60 - k * 6:.1f}" fill="#BFEFFF" opacity="{0.35 - k * 0.07:.2f}"/>' for k in range(4)), 8)
    act = contact(330, yy, 46) + g(front("head" if t > hit else "brace", "crouch" if t > hit else "stand", "surprised"), 330, yy, 0.34)
    if t < hit:
        act += trail + glossy_drop(640, dy, 120, 1.0)
    else:
        v = ramp(t, hit, hit + 0.9)
        act += crown(640, yy - 4, 150, v)
        act += f'<rect x="-300" y="-300" width="1560" height="1140" fill="#DFF6FF" opacity="{0.55 * max(0, 1 - (t - hit) / 0.18):.2f}"/>'
    L.append(("act", 0.85, act, False, None))
    shake = 0.0
    ov = kinetic("RAIN", 480, 120, t, hit + 0.02, 80, "#FFFFFF")
    return dict(layers=L, defs=sky_defs("storm"), cam=(0, 0, 1.04 + 0.05 * ease(t / D)), overlay=ov + f'<rect width="{W}" height="{H}" fill="#14123A" opacity="0.15"/>')


# ---------------------------------------------------------------- the clock, in the new grass
@shot("o_clock")
def _(t, D, c):
    cam = GAR
    L = garden_layers(cam, "gold", 950, sun=(740, 150))
    yy = cam.gy(0.55)
    act = contact(480, yy, 30) + g(front("brace" if t < 1.2 else "stand", "stand", "surprised" if t < 1.2 else "neutral", 0, (t % 2.6) < 0.1), 480, yy, 0.22)
    L.append(("act", 0.75, act, False, None))
    L.append(fg(cam, 951))
    secs = max(0.0, (t - 1.2)) if t > 1.2 else 0.0
    pop = A.out_back(ramp(t, 0.0, 0.45))
    clock = (f'<g transform="translate(480 150) scale({0.2 + 0.8 * pop:.3f})"><rect x="-170" y="-46" width="340" height="92" rx="24" fill="#140A3A" opacity="0.92"/>'
             f'<rect x="-170" y="-46" width="340" height="92" rx="24" fill="none" stroke="#FF4F9A" stroke-width="4"/>'
             f'<circle cx="-136" cy="0" r="7" fill="#FF4F7A" opacity="{0.5 + 0.5 * math.sin(t * 6):.2f}"/>' + text(14, 20, f"00:{secs:05.2f}", 56, "#FFFFFF", 700, "middle") + '</g>')
    ov = clock + kinetic("How long would you last?", 480, 492, t, 1.4, 34)
    return dict(layers=L, defs=sky_defs("gold"), cam=(0, 50, 1.25 + 0.12 * ease(t / D)), overlay=ov, clock=False)


# ---------------------------------------------------------------- a bird you can actually read
def bird(flap, col=("#2A1A4A", "#160C2C", "#FFD9A0")):
    up = math.sin(flap)
    wing = lambda s: P(f"M0 -6 Q{s * 60:.1f} {-50 - 40 * up:.1f} {s * 170:.1f} {-30 - 70 * up:.1f} Q{s * 110:.1f} {4 - 20 * up:.1f} {s * 20:.1f} 12 Z")
    body = P("M-70 0 Q-40 -26 20 -22 Q70 -18 92 -4 Q70 8 20 16 Q-40 18 -70 0 Z")
    head = C(86, -10, 18)
    beak = P("M100 -14 L132 -4 L100 0 Z")
    tail = P("M-66 -2 L-112 -24 L-104 4 L-114 26 L-66 8 Z")
    return (rim_(wing(-1), col) + rim_(tail, col) + rim_(body, col) + rim_(head, col) + beak("#FFB13A") +
            '<circle cx="92" cy="-14" r="3.2" fill="#FFFFFF"/>' + rim_(wing(1), col))


def rim_(shape, col):
    import scene_people as SP
    return SP.rimmed(shape, col[0], col[1], col[2], 4)


@shot("l_bird")
def _(t, D, c):
    """Low angle, looking up past you: a bird folds its wings and dives at you."""
    cam = LOW
    L = [("sky", 0.1, sky("gold", (700, 140)), True, None), ("forest", 0.25, forest(cam, 961), True, 2),
         ("gnd", 0.6, ground(cam, "gold", seed=960) + blades(cam, 962, 22, 0.03, 0.5, 300, 700, avoid=(300, 700, 0.15)), True, None)]
    yy = cam.gy(0.6)
    u = ease(ramp(t, 0.0, D * 0.9))
    bx, by = 900 - 420 * u, -40 + 330 * u
    sc = 0.6 + 1.3 * u
    b = g(bird(t * 9 * (1 - u) + 1.2 * u), bx, by, sc, 32 * u + 12, flip=True)
    act = contact(400, yy, 40) + g(front("head", "crouch", "surprised"), 400, yy, 0.3)
    L.append(("act", 0.85, act, False, None))
    L.append(("bird", 1.0, silhouette(b) if u < 0.4 else b, False, None))
    return dict(layers=L, defs=sky_defs("gold") + SIL_DEFS, cam=(0, 0, 1.0 + 0.06 * t), overlay=kinetic("snack", 480, 112, t, 0.3, 54, "#FF4F9A"))


# ---------------------------------------------------------------- THE TRUTH: "None of them. Remember, we cheated."
@shot("t_none")
def _(t, D, c):
    """Rewind to the moment you shrank: you grow back in reverse, the clock runs backwards to zero."""
    u = ease(ramp(t, 0.2, D - 0.6))
    body = hook.macro_world(t)
    k = 0.06 + 0.12 * u
    you = hook.you_at(rig.ARMS["stand"], "stand", "surprised", 0, False, k, 480, 432)
    world = f'<g transform="translate(480 432) scale({1.6 - 0.6 * u:.3f}) translate(-480 -432)">{body}{you}</g>'
    secs = (25 * 60 + 41) * (1 - u)
    val = f"00:{int(secs) // 60:02d}:{int(secs) % 60:02d}"
    rw = "".join(f'<path d="M{x} 230 L{x + 40} 205 L{x + 40} 255 Z" fill="#FFFFFF" opacity="{0.55 + 0.45 * math.sin(t * 10 + i):.2f}"/>' for i, x in enumerate((70, 112)))
    ov = (f'<rect width="{W}" height="{H}" fill="#2A0A6A" opacity="0.25"/>' +
          f'<g transform="translate(480 90)"><rect x="-150" y="-40" width="300" height="80" rx="22" fill="#140A3A" opacity="0.9"/>'
          f'<rect x="-150" y="-40" width="300" height="80" rx="22" fill="none" stroke="#FF4F9A" stroke-width="4"/>' + text(0, 18, val, 50, "#FFFFFF", 700, "middle") + '</g>' +
          f'<g transform="translate(40 0)">{rw}</g>' + kinetic("WE CHEATED", 480, 480, t, D * 0.45, 58, "#FFD23A"))
    L = [("world", 1.0, world, False, None)]
    return dict(layers=L, defs=hook.MACRO_DEFS if hasattr(hook, "MACRO_DEFS") else "", cam=(0, 0, 1.0), overlay=ov, clock=False)


# ---------------------------------------------------------------- "No thoughts. No memories. No you."
@shot("t_vanish")
def _(t, D, c):
    import shots_d
    L = shots_d.side_layers("dawn", 440, ks=(0,), sun=(480, 330), avoid=(330, 640, 0.0))
    L[0] = ("sky", 0.04, sky("dawn", (480, 330)) + glow(480, 330, 200, "#FFE6C8", 0.75, 30), True, None)
    yy = shots_d.yy_side()
    hx, hy = 480, yy - 0.5 * 470
    icons = [("thought", 0.10, 0.30), ("memory", 0.22, 0.42), ("you", 0.40, 0.62)]
    a = []
    for i, (kind, t_in, t_out) in enumerate(icons):
        ti, to = D * t_in, D * t_out
        if t < ti: continue
        x = hx - 150 + i * 150; y = hy - 70 - 20 * math.sin(t * 2 + i)
        op = min(1, (t - ti) / 0.3) * (1 - ramp(t, to, to + 0.6))
        sc = 1 - 0.5 * ramp(t, to, to + 0.6)
        if kind == "thought":
            ic = (sh(C(0, 0, 34), "#FFFFFF", "#D8D0F0", "#FFFFFF", 1) + '<circle cx="-22" cy="30" r="8" fill="#FFFFFF"/><circle cx="-32" cy="44" r="5" fill="#FFFFFF"/>'
                  + '<path d="M-12 -4 Q0 -18 12 -4 Q14 8 0 12 Q-14 8 -12 -4 Z" fill="#FFD23A"/>')
        elif kind == "memory":
            ic = (sh(R(-34, -28, 68, 56, 8), "#FFFFFF", "#D8D0F0", "#FFFFFF", 1) + '<rect x="-26" y="-20" width="52" height="34" rx="4" fill="#7AC8FF"/>'
                  + '<path d="M-26 14 L-8 -2 L4 8 L14 0 L26 14 Z" fill="#3FD68A"/><circle cx="14" cy="-10" r="5" fill="#FFE27A"/>')
        else:
            ic = sh(P("M0 26 Q-34 4 -30 -12 Q-26 -30 0 -16 Q26 -30 30 -12 Q34 4 0 26 Z"), "#FF6F9A", "#D83F70", "#FFC0D8", 1)
        a.append(f'<g opacity="{op:.2f}" transform="translate({x:.1f} {y:.1f}) scale({sc:.3f})">{ic}</g>')
    dis = ease(ramp(t, D * 0.62, D * 0.95))
    body = g(side("stand", 0, "neutral", (t % 2.6) < 0.1), 480, yy, 0.5)
    a.insert(0, contact(480, yy, 40, 0.45 * (1 - dis)) + f'<g opacity="{1 - dis:.2f}">{silhouette(body)}</g>')
    if dis > 0:
        rr = random.Random(2)
        for k in range(160):
            x0, y0 = 480 + rr.uniform(-24, 30), yy - rr.uniform(0, 230)
            uu = max(0.0, min(1.0, dis * 1.5 - rr.uniform(0, 0.5)))
            x, y = x0 + rr.uniform(-40, 140) * uu, y0 - 160 * uu
            a.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{2.6 * (1 - uu) + 0.4:.2f}" fill="{rr.choice(["#FFE6C8", "#FFC79A", "#FFFFFF", "#FF9AC0"])}" opacity="{(1 - uu) * min(1, dis * 4):.2f}"/>')
    L.append(("act", 1.0, "".join(a), False, None))
    L.append(shots_d.side_fg(441, ks=(0,)))
    ov = (kinetic("no thoughts", 260, 470, t, D * 0.12, 30, "#FFFFFF", out_t=D * 0.33) + kinetic("no memories", 480, 470, t, D * 0.24, 30, "#FFFFFF", out_t=D * 0.45)
          + kinetic("no you", 700, 470, t, D * 0.42, 34, "#FF6F9A"))
    return dict(layers=L, defs=sky_defs("dawn") + SIL_DEFS, cam=(0, 10, 1.25 + 0.15 * ease(t / D)), overlay=ov, clock=False)


# ---------------------------------------------------------------- ENDING
BLUE_BG = ('<rect x="-300" y="-300" width="1560" height="1140" fill="#123A8A"/>' +
           "".join(f'<rect x="{-300 + k * 40}" y="-300" width="1.4" height="1140" fill="#9AC8FF" opacity="0.18"/>' for k in range(40)) +
           "".join(f'<rect x="-300" y="{-300 + k * 40}" width="1560" height="1.4" fill="#9AC8FF" opacity="0.18"/>' for k in range(29)) +
           '<rect x="-300" y="-300" width="1560" height="1140" fill="url(#bpv)"/>')
BP_DEFS = '<radialGradient id="bpv" cx="0.5" cy="0.5" r="0.7"><stop offset="0.5" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#06123A" stop-opacity="0.7"/></radialGradient>'


def ant_parts(t, show):
    """The ant built up piece by piece: show is 0..5 (abdomen, thorax, head, legs, antennae, eyes)."""
    full = ant(t, 0.0)
    if show >= 5:
        return full
    # reveal by clipping a widening window across the drawing, back to front
    mid = K.uid("ap")
    w = [0, 70, 105, 140, 140, 140][int(show)] + 35 * (show - int(show))
    return f'<clipPath id="{mid}"><rect x="-80" y="-120" width="{w + 10:.1f}" height="200"/></clipPath><g clip-path="url(#{mid})">{full}</g>'


@shot("e_nature")
def _(t, D, c):
    """Left: shrinking a human (crossed out). Right: life starting over, an ant drawn from scratch on a blueprint."""
    a = []
    a.append('<rect x="-300" y="-300" width="780" height="1140" fill="#2A1470"/>')
    shrink = ease(ramp(t, 0.6, D * 0.45))
    a.append(contact(240, 440, 40 * (1 - 0.8 * shrink)) + g(front("stand", "stand", "neutral"), 240, 440, 0.62 - 0.52 * shrink))
    if t > D * 0.42:
        x = A.out_back(ramp(t, D * 0.42, D * 0.42 + 0.4))
        a.append(f'<g transform="translate(240 300) scale({x:.3f})" opacity="0.92"><path d="M-110 -110 L110 110 M110 -110 L-110 110" stroke="#FF4F7A" stroke-width="26" stroke-linecap="round"/></g>')
    a.append(chip(240, 90, "shrink a big animal", t, 0.4, "#FF4F7A"))
    bp = ramp(t, D * 0.55, D * 0.98) * 5
    if t > D * 0.5:
        a.append(f'<g transform="translate(720 430) scale(3.2)">' + ant_parts(t, bp) + '</g>')
        a.append(chip(720, 90, "start over", t, D * 0.55, "#46E0D0", "#0A0420"))
    L = [("bp", 1.0, BLUE_BG, True, None), ("act", 1.0, "".join(a), False, None)]
    return dict(layers=L, defs=BP_DEFS, cam=(0, 0, 1.0), overlay='<rect x="478" y="0" width="4" height="540" fill="#FFFFFF" opacity="0.5"/>', clock=False)


@shot("e_anatomy")
def _(t, D, c):
    """You and the ant side by side; each feature lights up on both as it is named."""
    a = []
    a.append(contact(250, 470, 60) + g(front("stand", "stand", "neutral"), 250, 470, 0.8))
    a.append(f'<ellipse cx="690" cy="476" rx="220" ry="20" fill="#0A0420" opacity="0.35"/>' + g(ant(t, 0.0), 690, 470, 3.4))
    pairs = [("skin", "armor", (300, 300), (690 - 40 * 3.4, 470 - 44 * 3.4), "#FF8A3A"),
             ("lungs", "tubes", (250, 245), (690 + 8 * 3.4, 470 - 30 * 3.4), "#2EA6C8"),
             ("2 eyes", "thousands of eyes", (250, 122), (690 + 42 * 3.4, 470 - 40 * 3.4), "#46E0D0"),
             ("big brain", "packed brain", (250, 88), (690 + 34 * 3.4, 470 - 32 * 3.4), "#FF4F9A")]
    times = [0.03, 0.22, 0.42, 0.68]
    for i, ((hn, an, hp, ap, col), tf) in enumerate(zip(pairs, times)):
        t0 = D * tf
        if t < t0: continue
        on = 1 - 0.55 * ramp(t, t0 + D * 0.2, t0 + D * 0.24) if i < 3 else 1.0
        pulse = 0.6 + 0.4 * math.sin((t - t0) * 6)
        a.append(f'<g opacity="{on:.2f}">' + soft(f'<circle cx="{hp[0]}" cy="{hp[1]}" r="{26 + 6 * pulse:.1f}" fill="{col}" opacity="0.6"/>', 6) +
                 soft(f'<circle cx="{ap[0]:.1f}" cy="{ap[1]:.1f}" r="{26 + 6 * pulse:.1f}" fill="{col}" opacity="0.6"/>', 6) + '</g>')
        y = 60 + i * 0
    names = [("armor, not skin", 0.03), ("tubes, not lungs", 0.22), ("thousands of eyes, not two", 0.42), ("a brain packed tighter than ours", 0.68)]
    cur = max([n for n in names if t >= D * n[1]] or [names[0]], key=lambda n: n[1])
    ov = chip(480, 70, cur[0], t, D * cur[1], "#FF4F9A") if t >= D * cur[1] else ""
    L = [("bg", 1.0, WORLD_BG, True, None), ("act", 1.0, "".join(a), False, None)]
    return dict(layers=L, defs=shots_c.DIAG, cam=(0, 0, 1.0), overlay=ov, clock=False)


@shot("e_end")
def _(t, D, c):
    cam = GAR
    L = garden_layers(cam, "gold", 260, sun=(640, 250))
    yy = cam.gy(0.55)
    act = contact(580, yy, 36) + g(ant(t, 0.0), 580, yy, 0.62, 0, flip=True) + g(back("stand", "stand", 0), 330, 560, 0.5)
    L.append(("act", 0.75, act, False, None))
    return dict(layers=L, defs=sky_defs("gold"), cam=(30, 60, 1.6 + 0.25 * ease(t / D)), overlay="", clock=False)


@shot("e_become")
def _(t, D, c):
    """Close: you turn into an ant in a burst of light, then the end card."""
    cam = GAR
    L = garden_layers(cam, "gold", 262, sun=(480, 230))
    yy = cam.gy(0.55)
    m = ease(ramp(t, 0.5, 1.3))
    act = (f'<g opacity="{1 - m:.2f}">' + contact(480, yy, 24) + g(front("stand", "stand", "happy"), 480, yy, 0.17 * (1 - 0.6 * m)) + '</g>' +
           f'<g opacity="{m:.2f}">' + contact(480, yy, 36) + g(ant(t, 0.0), 480, yy, 0.62 * (0.5 + 0.5 * A.out_back(m))) + '</g>')
    if 0.4 < t < 1.9:
        rr = random.Random(5); u = ramp(t, 0.4, 1.9)
        act += soft(f'<circle cx="480" cy="{yy - 40}" r="{30 + 60 * u:.1f}" fill="#FFF2D8" opacity="{0.8 * (1 - u):.2f}"/>', 8)
        for k in range(40):
            an = rr.uniform(0, 6.28)
            act += f'<circle cx="{480 + math.cos(an) * 70 * u:.1f}" cy="{yy - 40 + math.sin(an) * 70 * u:.1f}" r="1.8" fill="#FFF2D8" opacity="{1 - u:.2f}"/>'
    L.append(("act", 0.75, act, False, None))
    L.append(fg(cam, 263))
    endc = ease(ramp(t, D - 1.8, D - 1.0))
    ov = ""
    if endc > 0:
        ov = (f'<rect width="{W}" height="{H}" fill="#14084A" opacity="{0.78 * endc:.2f}"/>' +
              f'<g opacity="{endc:.2f}">' + text(480, 262, "Sandbox", 76, "#FFFFFF", 700, "middle") + text(480, 306, "big questions, small worlds", 22, "#C8B8FF", 600, "middle", "Inter") + '</g>')
    return dict(layers=L, defs=sky_defs("gold"), cam=(0, 95, 3.3 - 0.5 * ease(t / D)), overlay=ov, clock=False)
