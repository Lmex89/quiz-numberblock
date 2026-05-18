"""
Genera placeholders 1.jpg a N.jpg (200x200 px) según config.json.
No sobrescribe archivos .jpg/.jpeg existentes.

Uso:
  python generate_placeholders.py                          # solo placeholders para los que falten
  python generate_placeholders.py --source /ruta/imagenes/  # importa imágenes desde otra carpeta
Requiere: pip install Pillow cairosvg (cairosvg solo para SVG)
"""
import argparse
import io
import json
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
W, H = 200, 200

CONFIG_PATH = os.path.join(OUT_DIR, "..", "..", "config.json")
DEFAULT_TOTAL = 32
try:
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    TOTAL = cfg.get("TOTAL_IMAGES", DEFAULT_TOTAL)
except (FileNotFoundError, json.JSONDecodeError):
    TOTAL = DEFAULT_TOTAL

COLORS = [
    (255, 99, 132), (54, 162, 235), (255, 206, 86), (75, 192, 192),
    (153, 102, 255), (255, 159, 64), (255, 182, 193), (135, 206, 250),
    (144, 238, 144), (255, 218, 185), (221, 160, 221), (175, 238, 238),
    (240, 128, 128), (152, 251, 152), (255, 228, 181), (173, 216, 230),
    (255, 182, 193), (238, 130, 238), (0, 206, 209), (255, 215, 0),
    (250, 128, 114), (147, 112, 219), (60, 179, 113), (255, 140, 0),
    (100, 149, 237), (218, 165, 32), (46, 139, 87), (210, 105, 30),
    (72, 61, 139), (205, 92, 92), (0, 191, 255), (50, 205, 50),
    (255, 69, 0), (218, 112, 214), (34, 139, 34), (255, 160, 122),
    (123, 104, 238), (0, 255, 127), (255, 105, 180), (173, 255, 47),
    (138, 43, 226), (127, 255, 212), (255, 20, 147), (0, 255, 255),
    (255, 99, 71), (250, 250, 210), (189, 183, 107), (244, 164, 96),
    (102, 205, 170), (106, 90, 205),
]


def _open_image(path: str) -> Image.Image | None:
    low = path.lower()
    if low.endswith(".svg"):
        try:
            import cairosvg
            with open(path, "rb") as f:
                svg_data = f.read()
            png_data = cairosvg.svg2png(bytestring=svg_data, output_width=W, output_height=H)
            return Image.open(io.BytesIO(png_data)).convert("RGB")
        except ImportError:
            print(f"  SKIP {os.path.basename(path)}: cairosvg no instalado (pip install cairosvg)")
            return None
        except Exception as e:
            print(f"  SKIP {os.path.basename(path)}: SVG error: {e}")
            return None
    try:
        return Image.open(path)
    except Exception:
        return None


def _import_from_source(src_dir: str) -> int:
    imported = 0
    for i in range(1, TOTAL + 1):
        dst = os.path.join(OUT_DIR, f"{i}.jpg")
        if os.path.exists(dst):
            continue
        found = None
        for ext in (".jpg", ".jpeg", ".png", ".webp", ".svg"):
            candidate = os.path.join(src_dir, f"{i}{ext}")
            if os.path.isfile(candidate):
                found = candidate
                break
        if found is None:
            continue
        img = _open_image(found)
        if img is None:
            continue
        img.thumbnail((W, H), Image.LANCZOS)
        canvas = Image.new("RGB", (W, H), (255, 255, 255))
        x = (W - img.width) // 2
        y = (H - img.height) // 2
        canvas.paste(img, (x, y))
        canvas.save(dst, "JPEG", quality=90)
        imported += 1
        print(f"  Importado {found} → {dst}")
    return imported


def _generate_placeholder(i: int, font):
    dst = os.path.join(OUT_DIR, f"{i}.jpg")
    if os.path.exists(dst) or os.path.exists(os.path.join(OUT_DIR, f"{i}.jpeg")):
        return False
    img = Image.new("RGB", (W, H), COLORS[(i - 1) % len(COLORS)])
    draw = ImageDraw.Draw(img)
    text = str(i)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (W - tw) / 2 - bbox[0]
    y = (H - th) / 2 - bbox[1]
    draw.text((x, y), text, fill="white", font=font)
    img.save(dst, "JPEG", quality=85)
    return True


def main():
    parser = argparse.ArgumentParser(description="Genera placeholders o importa imágenes")
    parser.add_argument("--source", help="Carpeta con imágenes fuente (1.jpg, 2.jpg, …)")
    args = parser.parse_args()

    imported = 0
    if args.source:
        if not os.path.isdir(args.source):
            print(f"Error: no existe la carpeta '{args.source}'")
            return
        imported = _import_from_source(args.source)

    font = None
    for size in (90, 72, 60, 48):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
            break
        except (IOError, OSError):
            continue
    if font is None:
        font = ImageFont.load_default()

    placeholders = 0
    for i in range(1, TOTAL + 1):
        if _generate_placeholder(i, font):
            placeholders += 1

    total = imported + placeholders
    parts = []
    if imported:
        parts.append(f"{imported} importadas")
    if placeholders:
        parts.append(f"{placeholders} placeholders generados")
    if not parts:
        print(f"✓ Todo al día — {TOTAL} imágenes ya existen en {OUT_DIR}")
    else:
        print(f"✓ Hecho: {', '.join(parts)} en {OUT_DIR}")


if __name__ == "__main__":
    main()
