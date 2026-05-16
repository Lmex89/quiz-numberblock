"""
Genera placeholders 1.jpg a 20.jpg (200x200 px).
Ejecutar con: python generate_placeholders.py
Requiere: pip install Pillow
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
W, H = 200, 200

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


def main():
    font = None
    for size in (90, 72, 60, 48):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
            break
        except (IOError, OSError):
            continue
    if font is None:
        font = ImageFont.load_default()

    for i in range(1, 21):
        img = Image.new("RGB", (W, H), COLORS[(i - 1) % len(COLORS)])
        draw = ImageDraw.Draw(img)

        text = str(i)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (W - tw) / 2 - bbox[0]
        y = (H - th) / 2 - bbox[1]

        draw.text((x, y), text, fill="white", font=font)
        img.save(os.path.join(OUT_DIR, f"{i}.jpg"), "JPEG", quality=85)

    print(f"✓ Generados {100} placeholders en {OUT_DIR}")


if __name__ == "__main__":
    main()
