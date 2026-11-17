"""Ep2 pose library on rig3: investigation, hesitation, testing ground, startle, bracing, shielding, coughing,
breath-holding, shivering, slipping, running, crouching, sitting, relief. Front poses (F_*) and profile poses (S_*)."""
import math, sys
sys.path[:0] = ["/home/claude/ep2x", "/home/claude/ep", "/home/claude/bible"]
import rig3 as R3
from rig3 import keys, mix, smooth, fc, FRONT, SIDE

TAU = 2 * math.pi

# ------------------------------------------------------------------ extra mouth / face states
_mouth0 = R3._mouth


def _mouth(kind, mo, x0=0.0, y0=0.0):
    x, y = x0, y0
    if kind == "puff":      # held breath: lips pressed, cheeks ballooned
        return (f'<ellipse cx="{x - 30:.1f}" cy="{y + 22:.1f}" rx="{14 + 3 * mo:.1f}" ry="{11 + 2 * mo:.1f}" fill="#FF8A8A" opacity="0.45"/>'
                f'<ellipse cx="{x + 30:.1f}" cy="{y + 22:.1f}" rx="{14 + 3 * mo:.1f}" ry="{11 + 2 * mo:.1f}" fill="#FF8A8A" opacity="0.45"/>'
                f'<path d="M{x - 6:.1f} {y + 33:.1f} Q{x:.1f} {y + 31:.1f} {x + 6:.1f} {y + 33:.1f}" stroke="#5A1E2E" stroke-width="4" fill="none" stroke-linecap="round"/>')
    if kind == "chatter":   # teeth chattering: open/close driven by mo (0..1)
        h = 3 + 6 * mo
        return (f'<rect x="{x - 12:.1f}" y="{y + 28:.1f}" width="24" height="{h:.1f}" rx="3" fill="#5A1E2E"/>'
                f'<rect x="{x - 11:.1f}" y="{y + 28:.1f}" width="22" height="3.2" fill="#FFFFFF"/>'
                f'<rect x="{x - 11:.1f}" y="{y + 25 + h:.1f}" width="22" height="3.2" fill="#FFFFFF"/>')
    if kind == "cough":
        return f'<ellipse cx="{x:.1f}" cy="{y + 33:.1f}" rx="{9 + 2 * mo:.1f}" ry="{7 + 3 * mo:.1f}" fill="#5A1E2E"/>'
    return _mouth0(kind, mo, x0, y0)


R3._mouth = _mouth
_face_side0 = R3.face_side


def _face_side(f=None, p=R3.YOU):
    f = R3.FACE | (f or {})
    o = _face_side0(f, p)
    m = f["mouth"]
    if m == "puff":
        o += '<ellipse cx="34" cy="20" rx="17" ry="14" fill="#FF8A8A" opacity="0.45"/><path d="M44 30 Q50 29 56 30" stroke="#5A1E2E" stroke-width="4" fill="none" stroke-linecap="round"/>'
    elif m == "chatter":
        mo = f["mo"]
        o += f'<rect x="42" y="27" width="14" height="{3 + 5 * mo:.1f}" rx="2" fill="#5A1E2E"/><rect x="43" y="27" width="12" height="2.6" fill="#FFF"/>'
    elif m == "cough":
        o += f'<ellipse cx="50" cy="32" rx="{6 + 2 * f["mo"]:.1f}" ry="{6 + 3 * f["mo"]:.1f}" fill="#5A1E2E"/>'
    return o


R3.face_side = _face_side


# ------------------------------------------------------------------ front poses (feet at y=0; hands in torso frame)
F_STAND = dict(FRONT)
F_RELAX = FRONT | dict(el=(-80, -288), hl=(-78, -212), er=(80, -288), hr=(78, -212), face=fc(mouth="smile"))
F_ALARM = R3.F_ALARM
F_COWER = R3.F_COWER
F_SHIVER = R3.F_SHIVER | dict(face=fc(knit=1.0, open=0.75, mouth="chatter", blush=0.1, lift=0.4))
F_SHIELD = FRONT | dict(er=(96, -372), hr=(18, -478), el=(-82, -292), hl=(-86, -216), head=(0, 6, -4), lean=-3,
                        face=fc(open=0.45, knit=0.8, lift=0.2, mouth="grit", look=(-0.4, -0.6)))
F_BRACE = FRONT | dict(lean=-9, hip=(10, 18), shr=0.7, el=(-92, -342), hl=(-24, -432), er=(74, -322), hr=(12, -408),
                       kl=(-46, -92), fl=(-62, 0), kr=(40, -94), fr=(58, 0), head=(-6, 10, -10),
                       face=fc(open=0.35, knit=1.0, lift=0.3, mouth="grit", look=(-1, 0)))
F_INHALE = FRONT | dict(shr=0.9, el=(-90, -296), hl=(-96, -226), er=(90, -296), hr=(96, -226), head=(0, -6, 0),
                        face=fc(open=1.0, lift=0.5, mouth="o", mo=0.6, look=(0, -0.4)))
F_HOLD = FRONT | dict(shr=0.75, el=(-88, -294), hl=(-92, -222), er=(88, -294), hr=(92, -222), head=(0, -2, 0),
                      face=fc(open=1.25, lift=0.9, knit=0.2, mouth="puff", mo=0.6, look=(0, 0), blush=0.9))
F_GASP = FRONT | dict(shr=0.4, lean=4, hip=(0, 14), el=(-60, -300), hl=(-10, -360), er=(84, -280), hr=(70, -200),
                      kl=(-30, -96), fl=(-34, 0), kr=(30, -96), fr=(34, 0), head=(4, 12, 6),
                      face=fc(open=0.6, knit=0.9, lift=0.1, mouth="gasp", mo=0.6, look=(0.3, 0.6)))
F_COUGH = FRONT | dict(shr=0.6, lean=5, hip=(0, 10), el=(-50, -300), hl=(-6, -404), er=(76, -296), hr=(40, -300), head=(0, 18, 8),
                       face=fc(open=0.12, knit=1.0, mouth="cough", mo=0.8))
F_LOOKUP = FRONT | dict(head=(0, -8, 0), el=(-86, -292), hl=(-90, -214), er=(86, -292), hr=(90, -214),
                        face=fc(open=1.2, lift=0.8, mouth="o", mo=0.4, look=(0, -1)))
F_POINTUP = FRONT | dict(head=(0, -8, 4), er=(112, -400), hr=(150, -508), el=(-86, -292), hl=(-90, -214),
                         face=fc(open=1.25, lift=0.9, mouth="o", mo=0.6, look=(0.8, -1)))
F_NERVOUS = FRONT | dict(er=(96, -330), hr=(46, -452), el=(-80, -290), hl=(-82, -214), head=(4, 4, 6), shr=0.3,
                         face=fc(open=1.1, lift=0.8, knit=0.6, mouth="worried", look=(-0.6, 0.2)))
F_SIT_THINK = R3.F_SIT | dict(er=(82, -300), hr=(26, -392), el=(-84, -282), hl=(-60, -224), head=(6, 6, 8),
                              face=fc(open=0.9, lift=0.3, knit=0.5, mouth="flat", look=(0.6, -0.3)))
F_HOPE = FRONT | dict(el=(-110, -300), hl=(-150, -360), er=(110, -300), hr=(150, -360), head=(0, -2, -5),
                      face=fc(open=1.15, lift=0.9, knit=-0.2, mouth="smile", mo=0.5, look=(0, 0)))
F_RELIEF = FRONT | dict(shr=-0.2, el=(-84, -290), hl=(-80, -214), er=(84, -290), hr=(80, -214), head=(0, 4, 0),
                        face=fc(open=0.12, lift=0.4, mouth="smile", mo=0.2))
F_HANDS = FRONT | dict(el=(-70, -280), hl=(-40, -330), er=(70, -280), hr=(40, -330), head=(0, 14, 0),
                       face=fc(open=1.1, lift=0.6, knit=0.4, mouth="o", look=(0, 1)))


# ------------------------------------------------------------------ profile poses (faces right)
S_STAND = dict(SIDE)
S_TEST = SIDE | dict(lean=-6, hip=(-6, 6), f1=(-26, 0), k1=(-4, -108), f2=(58, -4), k2=(44, -104),
                     e1=(-60, -300), h1=(-110, -260), e2=(56, -300), h2=(104, -270), head=(4, 6, 10),
                     face=fc(open=1.1, lift=0.6, knit=0.4, mouth="flat", look=(0.6, 1)))
S_WITHDRAW = SIDE | dict(lean=-14, hip=(-14, 4), f1=(-30, 0), k1=(-10, -108), f2=(4, -46), k2=(46, -122),
                         e1=(-80, -320), h1=(-140, -330), e2=(70, -330), h2=(130, -360), head=(-6, 0, -8),
                         face=fc(open=1.35, lift=1.0, knit=0.6, mouth="gasp", look=(0.4, 1)))
S_STARTLE = SIDE | dict(lean=-12, hip=(-10, 6), shr=0.7, f1=(-40, 0), k1=(-20, -104), f2=(26, 0), k2=(26, -106),
                        e1=(-30, -320), h1=(10, -380), e2=(40, -320), h2=(70, -390), head=(-8, 8, -10),
                        face=fc(open=1.4, lift=1.0, knit=0.5, mouth="gasp", mo=0.6, look=(0.6, -0.4)))
S_LOOKUP = SIDE | dict(lean=-6, head=(-4, -6, -24), e1=(-14, -282), h1=(-4, -216), e2=(4, -282), h2=(16, -216),
                       face=fc(open=1.25, lift=0.9, mouth="o", mo=0.4, look=(0.6, -1)))
S_POINT = S_LOOKUP | dict(e2=(56, -400), h2=(110, -500), face=fc(open=1.3, lift=1.0, mouth="o", mo=0.6, look=(0.8, -1)))
S_SHIELD = SIDE | dict(lean=-8, head=(-2, 6, -12), e2=(60, -380), h2=(70, -470), e1=(-20, -290), h1=(-10, -220),
                       face=fc(open=0.45, knit=0.9, lift=0.2, mouth="grit", look=(0.8, -0.6)))
S_BRACE = SIDE | dict(lean=14, hip=(0, 26), f1=(-70, 0), k1=(-36, -96), f2=(46, 0), k2=(58, -84),
                      e1=(40, -350), h1=(80, -420), e2=(60, -340), h2=(96, -440), head=(6, 14, 10),
                      face=fc(open=0.3, knit=1.0, lift=0.2, mouth="grit", look=(1, 0)))
S_CROUCH = SIDE | dict(hip=(-10, 118), lean=34, k1=(56, -50), f1=(-26, 0), k2=(70, -48), f2=(14, 0),
                       e1=(60, -330), h1=(20, -440), e2=(80, -330), h2=(30, -460), head=(10, 36, 20),
                       face=fc(open=0.15, knit=1.0, mouth="grit"))
S_KNEEL = SIDE | dict(hip=(-6, 92), lean=16, f1=(-92, -4), k1=(-4, -6), f2=(46, 0), k2=(70, -96),
                      e1=(20, -290), h1=(60, -220), e2=(60, -280), h2=(126, -196), head=(8, 14, 16),
                      face=fc(open=1.1, lift=0.5, mouth="o", mo=0.2, look=(0.8, 1)))
S_KNEEL_POKE = S_KNEEL | dict(e2=(86, -250), h2=(162, -150), face=fc(open=1.2, lift=0.7, knit=0.2, mouth="flat", look=(1, 1)))
S_DIG = S_KNEEL | dict(lean=30, e1=(70, -250), h1=(130, -130), e2=(90, -250), h2=(160, -120), head=(14, 22, 24),
                       face=fc(open=1.0, knit=0.6, mouth="flat", look=(0.6, 1)))
S_SHIVER = SIDE | dict(shr=1.0, head=(4, 14, 6), e1=(30, -270), h1=(40, -310), e2=(36, -268), h2=(46, -306),
                       face=fc(open=0.75, knit=1.0, mouth="chatter", blush=0.1))
S_PUSH = SIDE | dict(lean=16, hip=(-10, 10), f1=(-74, 0), k1=(-40, -100), f2=(34, 0), k2=(46, -100),
                     e1=(54, -320), h1=(116, -330), e2=(64, -318), h2=(124, -326), face=fc(open=1.0, knit=0.6, mouth="grit", look=(1, 0)))
S_HANDS_KNEES = SIDE | dict(lean=44, hip=(-16, 24), f1=(-34, 0), k1=(16, -100), f2=(22, 0), k2=(46, -98),
                            e1=(46, -260), h1=(50, -170), e2=(60, -262), h2=(70, -172), head=(16, 30, 26),
                            face=fc(open=0.3, knit=0.6, mouth="gasp", mo=0.4))
S_SIT = SIDE | dict(hip=(-20, 160), lean=-4, k1=(60, -120), f1=(80, 0), k2=(76, -116), f2=(100, 0),
                    e1=(-10, -290), h1=(-40, -190), e2=(56, -280), h2=(70, -170), face=fc(open=1.0, mouth="flat"))
S_SIT_CHIN = S_SIT | dict(lean=10, e2=(70, -260), h2=(66, -380), head=(10, 20, 14), face=fc(open=0.85, lift=0.3, knit=0.4, mouth="flat", look=(1, 0.2)))
S_SIT_HUG = S_SIT | dict(lean=16, e1=(40, -280), h1=(80, -200), e2=(60, -278), h2=(92, -196), head=(10, 20, 14),
                         face=fc(open=0.9, lift=0.4, knit=0.3, mouth="smile", look=(1, 0)))


def walk_J(ph, run=False, **kw):
    """Walk / run cycle in profile. ph in cycles. Run has a flight phase, forward lean, pumping arms."""
    s, cz = math.sin(TAU * ph), math.cos(TAU * ph)
    amp, lift, arm = (88, 62, 78) if run else (46, 20, 40)
    bob = (-18 * abs(math.sin(TAU * ph)) + 8) if run else -6 * abs(cz)
    J = dict(SIDE)
    for k, sign in ((1, 1), (2, -1)):
        u = sign * s
        fx = amp * u
        up = max(0.0, sign * cz) * lift
        J[f"f{k}"] = (fx, -up)
        J[f"k{k}"] = (fx * 0.55 + 20 + (16 if up > 4 else 0) + (14 if run else 0), -108 - up * (0.9 if run else 0.6) + bob * 0.5)
    for k, sign in ((1, -1), (2, 1)):
        u = sign * s
        if run:
            J[f"h{k}"] = (40 + arm * u, -270 - u * 40); J[f"e{k}"] = (-20 + arm * u * 0.2, -286 + 10 * u)
        else:
            J[f"h{k}"] = (6 + arm * u, -215 - abs(u) * 18); J[f"e{k}"] = (-14 + arm * u * 0.3, -280)
    J["hip"] = (0, bob)
    J["lean"] = 16 if run else 3
    if run:
        J["face"] = fc(open=1.3, lift=0.9, knit=0.6, mouth="scream", mo=0.3, look=(1, 0))
    for k, v in kw.items():
        J[k] = (J["face"] | v) if k == "face" else v
    return J


def blink(face, t, period=3.1, phase=0.0):
    u = ((t + phase) % period) / period
    b = 1.0 if u > 0.955 else 0.0
    return face | dict(blink=b)


def talk(face, t, amt=1.0):
    return face | dict(mo=amt * (0.5 + 0.5 * math.sin(t * 17)) * (0.6 + 0.4 * math.sin(t * 5.3)))


def jitter(J, t, amp=3.0, f=23.0):
    """Shiver: tiny fast whole-body tremble + chatter."""
    hx, hy = J.get("hip", (0, 0))
    d = dict(J); d["hip"] = (hx + amp * math.sin(t * f), hy + 0.5 * amp * math.sin(t * f * 1.3))
    d["face"] = dict(J["face"]) | dict(mo=0.5 + 0.5 * math.sin(t * 31))
    return d


front = R3.front
side = R3.side


# ------------------------------------------------------------------ back view: same body, the head seen from behind
_face_front0 = R3.face_front


def _face_front(f=None, p=R3.YOU, tilt=0.0):
    if f and f.get("back"):
        hr = p.hair; sk = p.skin
        from kit import P as _P, E as _E
        o = [R3.rim(_E(-50, 6, 9, 12), sk[1], sk[1], sk[2], 3), R3.rim(_E(50, 6, 9, 12), sk[1], sk[1], sk[2], 3)]
        o.append(R3.rim(_P("M -60 30 Q -70 -80 0 -86 Q 70 -80 60 30 Q 40 58 0 60 Q -40 58 -60 30 Z"), *hr, 6))
        o.append(f'<path d="M-30 -60 Q0 -74 34 -58" stroke="{hr[2]}" stroke-width="7" fill="none" opacity="0.6" stroke-linecap="round"/>'
                 f'<path d="M-6 -40 Q4 -20 -2 0" stroke="{hr[0]}" stroke-width="4" fill="none" opacity="0.5"/>')
        return f'<g transform="rotate({tilt:.2f})">{"".join(o)}</g>'
    return _face_front0(f, p, tilt)


R3.face_front = _face_front


def back(J):
    """Body from behind (front rig with the back of the head); arms read the same from both sides in this style."""
    J = dict(J); J["face"] = dict(J.get("face", R3.FACE)) | dict(back=True)
    return R3.front(J)
