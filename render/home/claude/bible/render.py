import os, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
FONTS = """@font-face{font-family:Fredoka;font-weight:700;src:url('file:///root/.fonts/fredoka-latin-700-normal.ttf')}
@font-face{font-family:Fredoka;font-weight:600;src:url('file:///root/.fonts/fredoka-latin-600-normal.ttf')}
html,body{margin:0}"""


def render(items, w=1920, h=1080):
    """items: list of (name, svg_string)."""
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
        for name, svg in items:
            path = os.path.join(OUT, name + ".html")
            open(path, "w").write(f"<!doctype html><html><head><style>{FONTS}</style></head><body>{svg}</body></html>")
            pg.goto("file://" + path)
            pg.wait_for_timeout(250)
            png = os.path.join(OUT, name + "_2x.png")
            pg.screenshot(path=png)
            from PIL import Image
            Image.open(png).convert("RGB").resize((w, h), Image.LANCZOS).save(os.path.join(OUT, name + ".jpg"), quality=93)
            os.remove(png)
            print("rendered", name)
        br.close()
