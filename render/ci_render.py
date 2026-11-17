"""CI render worker. Plans the full shot list (balanced by duration across N chunks), renders this chunk's shots
with P parallel processes into /home/claude/ep/shots5/.
Usage: python3 ci_render.py plan N            -> prints JSON matrix
       python3 ci_render.py run  CHUNK N P [names...]"""
import sys, os, json, subprocess
sys.path.insert(0, "/home/claude/ep")
TEND = float(os.environ.get("TEND", "312.129"))
MOD = os.environ.get("ANIM_MOD", "anim_g")
if "ANIM_MOD" not in os.environ or "TEND" not in os.environ:     # never fall back to another episode silently
    print("Error: ANIM_MOD/TEND not set in the environment", flush=True); sys.exit(1)
print("module", MOD, "tend", TEND, "vert", os.environ.get("VERT", ""), flush=True)


def shots():
    import importlib, anim_core
    importlib.import_module(MOD)
    return anim_core.finalize(TEND)


def groups(A, n, only=None):
    items = [a for a in A if not only or a["name"] in only]
    items.sort(key=lambda a: -a["dur"] * (2.0 if a["name"][0] in "cdefghj" else 1.0))   # garden-heavy shots weigh more
    g = [[] for _ in range(n)]; tot = [0.0] * n
    for a in items:
        k = tot.index(min(tot)); g[k].append(a["name"]); tot[k] += a["dur"] * (2.0 if a["name"][0] in "cdefghj" else 1.0)
    return g


if sys.argv[1] == "plan":
    n = int(sys.argv[2])
    print(json.dumps({"chunk": list(range(n))}))
elif sys.argv[1] == "run":
    chunk, n, p = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    only = set(sys.argv[5:]) or None
    A = shots()
    mine = groups(A, n, only)[chunk]
    print("chunk", chunk, "shots", mine, flush=True)
    sub = [mine[i::p] for i in range(p)]
    procs = [subprocess.Popen([sys.executable, "/home/claude/ep/render_one.py"] + s) for s in sub if s]
    rc = [q.wait() for q in procs]
    print("done", rc, flush=True)
    sys.exit(max(rc) if rc else 0)
