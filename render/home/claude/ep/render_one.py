"""Render the named shots (current anim module) into /home/claude/ep/shots5/. Used by CI and locally."""
import sys, os, importlib
sys.path.insert(0, "/home/claude/ep")
import anim_core, engine
importlib.import_module(os.environ.get("ANIM_MOD", "anim_g"))
for m in os.environ.get("EXTRA_MODS", "").split(","):
    if m: importlib.import_module(m)
anim_core.finalize(float(os.environ.get("TEND", "312.129")))
engine.OUT = os.environ.get("OUT_DIR", "/home/claude/ep/shots5"); os.makedirs(engine.OUT, exist_ok=True)
engine.CACHE = "/home/claude/ep/cache_" + str(os.getpid()); os.makedirs(engine.CACHE, exist_ok=True)
from playwright.sync_api import sync_playwright
bad = 0
with sync_playwright() as p:
    br = p.chromium.launch()
    for n in sys.argv[1:]:
        for attempt in range(2):
            try:
                engine.render_shot(br, n); break
            except Exception as e:
                print("FAIL", n, attempt, repr(e), flush=True)
                if attempt == 1: bad += 1
    br.close()
print("DONE", flush=True)
sys.exit(1 if bad else 0)
