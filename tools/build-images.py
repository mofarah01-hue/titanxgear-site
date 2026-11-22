"""Build web images for the site from source-img/ into img/.

App screens: the sheet background around each device is keyed out (flood fill from the
corners), so the phones sit on the black page. Photos are resized. The logo is pulled
from the pitch deck PDF with its transparency mask.
Run: python -I tools/build-images.py   (from the repo root)
Prints one line per file and exits 1 if any source is missing.
"""
import sys, pathlib
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "source-img", ROOT / "img"
DECK = pathlib.Path(r"C:\Users\mo_fa\OneDrive\Documents\Consulting\Titan X\Titan_X_Pitch_Deck_V1.0.pdf")
OUT.mkdir(exist_ok=True)
failed = []

def key_corners(im, thresh=40):
    """Make the light sheet background transparent, starting from the four corners."""
    im = im.convert("RGBA")
    marker = (255, 0, 255, 0)
    w, h = im.size
    for xy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1)]:
        r, g, b, a = im.getpixel(xy)
        if r > 150 and g > 150 and b > 150:  # only flood a light background, never the device
            ImageDraw.floodfill(im, xy, marker, thresh=thresh)
    px = im.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == marker:
                px[x, y] = (0, 0, 0, 0)
    return im

def save(im, name, widths, q=80):
    for wd in widths:
        if wd > im.width:
            wd = im.width
        r = im.resize((wd, round(im.height * wd / im.width)), Image.LANCZOS)
        p = OUT / f"{name}-{wd}.webp"
        r.save(p, "WEBP", quality=q, method=6)
        print(f"{p.name}  {r.size[0]}x{r.size[1]}  {p.stat().st_size // 1024} KB")

def src(name):
    p = SRC / name
    if not p.exists():
        failed.append(name)
        return None
    return Image.open(p)

for n in ["floor", "after", "progress", "today-phone", "plan", "assistant"]:
    im = src(f"app-{n}.png")
    if im:
        save(key_corners(im), f"app-{n}", [560, 1000, 1600] if n == "floor" else [480, 900])

for n, widths in [("deck-hero", [960, 1600, 2425]), ("deck-headgear", [600, 1091]), ("deck-headgear-worn", [600, 836])]:
    im = src(f"{n}.jpg")
    if im:
        save(im.convert("RGB"), n, widths, q=76)

# Logo with its transparency mask, straight from the deck (page 1, image 2).
try:
    import pymupdf
    d = pymupdf.open(DECK)
    x = d[0].get_images(full=True)[1]
    import io
    base = Image.open(io.BytesIO(d.extract_image(x[0])["image"])).convert("RGB")
    mask = Image.open(io.BytesIO(d.extract_image(x[1])["image"])).convert("L").resize(base.size)
    logo = base.convert("RGBA")
    logo.putalpha(mask)
    logo = logo.crop(logo.getbbox())
    save(logo, "logo", [240, 480], q=88)
    logo.resize((180, round(180 * logo.height / logo.width))).save(OUT / "logo-180.png")
except Exception as e:  # watchdog: say what failed, do not hide it
    failed.append(f"logo from deck: {e}")

# Open Graph card: hero photo, 1200x630, JPEG (social sites want JPEG/PNG).
im = src("deck-hero.jpg")
if im:
    w, h = im.size
    ch = round(w * 630 / 1200)
    og = im.convert("RGB").crop((0, (h - ch) // 2, w, (h - ch) // 2 + ch)).resize((1200, 630), Image.LANCZOS)
    og.save(OUT / "og.jpg", quality=82)
    print("og.jpg  1200x630")

if failed:
    print("FAILED:", "; ".join(failed))
    sys.exit(1)
print("images OK")
