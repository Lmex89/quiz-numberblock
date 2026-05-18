"""
Convierte imágenes WebP/PNG/SVG/JPEG a JPG en static/images/.
Ejecutar: python convert_webp_to_jpg.py

Corrige archivos con extensión .jpg que en realidad son WebP/PNG/SVG.
Convierte .jpeg a .jpg y escala todas a 200x200 px con object-fit cover.
Requiere: pip install Pillow cairosvg
"""
import io
import os
from PIL import Image

DIR = os.path.dirname(os.path.abspath(__file__))
SIZE = (200, 200)
SRC_EXTS = (".webp", ".png", ".jpeg", ".svg")

converted = 0
errors = 0


def _open_image(path: str) -> Image.Image | None:
    low = path.lower()
    if low.endswith(".svg"):
        try:
            import cairosvg
            with open(path, "rb") as f:
                svg_data = f.read()
            png_data = cairosvg.svg2png(bytestring=svg_data, output_width=SIZE[0], output_height=SIZE[1])
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


files = sorted(os.listdir(DIR), key=lambda x: int(x.split(".")[0]) if x.split(".")[0].isdigit() else 999)

for fname in files:
    low = fname.lower()

    is_mislabeled_jpg = low.endswith(".jpg") and not low.endswith(".webp")
    is_svg_file = low.endswith(".svg")

    if not (is_mislabeled_jpg or is_svg_file or any(low.endswith(e) for e in SRC_EXTS)):
        continue

    path = os.path.join(DIR, fname)
    if not os.path.isfile(path):
        continue

    if is_svg_file:
        img = _open_image(path)
        if img is None:
            errors += 1
            continue
        old_fmt = "SVG"
    else:
        img = _open_image(path)
        if img is None:
            print(f"  SKIP {fname}: no se pudo abrir")
            errors += 1
            continue
        if img.format == "JPEG" and low.endswith(".jpg"):
            continue
        old_fmt = img.format or "unknown"

    dst = os.path.splitext(fname)[0] + ".jpg"
    dst_path = os.path.join(DIR, dst)
    print(f"  {fname} ({old_fmt}) → {dst}")

    try:
        img = img.convert("RGB")
        img.thumbnail(SIZE, Image.LANCZOS)

        canvas = Image.new("RGB", SIZE, (255, 255, 255))
        x = (SIZE[0] - img.width) // 2
        y = (SIZE[1] - img.height) // 2
        canvas.paste(img, (x, y))

        canvas.save(dst_path, "JPEG", quality=90)
        if fname != dst:
            os.remove(path)
        converted += 1
    except Exception as e:
        print(f"  ERROR {fname}: {e}")
        errors += 1

if not converted and not errors:
    print("  No se encontraron imágenes para convertir.")

print(f"\n✓ {converted} convertidas, {errors} errores")
