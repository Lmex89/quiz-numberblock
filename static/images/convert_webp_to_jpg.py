"""
Convierte imágenes WebP/PNG a JPG en static/images/.
Ejecutar: python convert_webp_to_jpg.py

Corrige archivos con extensión .jpg que en realidad son WebP o PNG.
Escala todas las imágenes a 200x200 px con object-fit cover.
"""
import os
from PIL import Image

DIR = os.path.dirname(os.path.abspath(__file__))
SIZE = (200, 200)
SRC_EXTS = (".webp", ".png")

converted = 0
errors = 0

files = sorted(os.listdir(DIR), key=lambda x: int(x.split(".")[0]) if x.split(".")[0].isdigit() else 999)

for fname in files:
    low = fname.lower()

    is_mislabeled_jpg = low.endswith(".jpg") and not low.endswith(".webp")
    is_webp_file = low.endswith(".webp")

    if not (is_mislabeled_jpg or is_webp_file or any(low.endswith(e) for e in SRC_EXTS)):
        continue

    path = os.path.join(DIR, fname)
    if not os.path.isfile(path):
        continue

    try:
        img = Image.open(path)
    except Exception as e:
        print(f"  SKIP {fname}: {e}")
        continue

    if img.format == "JPEG" and low.endswith(".jpg"):
        continue

    dst = os.path.splitext(fname)[0] + ".jpg"
    dst_path = os.path.join(DIR, dst)
    old_fmt = img.format or "unknown"

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
