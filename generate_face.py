"""
generate_face.py
Roda via GitHub Actions e gera face_output.svg a partir de foto.jpg
"""
from PIL import Image, ImageEnhance
import numpy as np
import random, os

IMG_PATH = "foto.jpg"
OUT_PATH = "face_output.svg"

if not os.path.exists(IMG_PATH):
    print(f"ERRO: {IMG_PATH} não encontrado no repositório.")
    exit(1)

img = Image.open(IMG_PATH).convert("RGBA")
w, h = img.size
side = min(w, h)
img = img.crop(((w-side)//2, (h-side)//2, (w+side)//2, (h+side)//2))

SIZE = 200
img = img.resize((SIZE, SIZE), Image.LANCZOS)
img_gray = img.convert("L")
img_gray = ImageEnhance.Contrast(img_gray).enhance(2.2)
pixels = np.array(img_gray)

particles = []
random.seed(42)
CANVAS = 280

for y in range(0, SIZE, 4):
    for x in range(0, SIZE, 4):
        brightness = pixels[y, x]
        density = (255 - brightness) / 255.0
        if random.random() < density * 0.7:
            jx = 10 + (x / SIZE) * CANVAS + random.uniform(-1.2, 1.2)
            jy = 10 + (y / SIZE) * CANVAS + random.uniform(-1.2, 1.2)
            r  = random.uniform(0.8, 1.6)
            op = 0.5 + density * 0.45
            particles.append((jx, jy, r, op))

colors = ["#ff69b4","#ff1493","#ff85c2","#ffb6d9","#e91e8c","#ff4da6"]
groups = {c: [] for c in colors}
for p in particles:
    groups[random.choice(colors)].append(p)

svg = [
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="300" height="300">',
    '<defs><filter id="g"><feGaussianBlur stdDeviation="0.8" result="b"/>',
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>',
    '<rect width="300" height="300" fill="#0d0117" rx="10"/>',
]
for c, pts in groups.items():
    svg.append(f'<g fill="{c}" filter="url(#g)">')
    for (x, y, r, op) in pts:
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" opacity="{op:.2f}"/>')
    svg.append('</g>')
svg.append('</svg>')

with open(OUT_PATH, "w") as f:
    f.write("\n".join(svg))

print(f"✅ {OUT_PATH} gerado com {len(particles)} partículas.")