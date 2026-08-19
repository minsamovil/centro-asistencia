from math import cos, sin, pi

from PIL import Image, ImageDraw


def radial_gradient(img, cx, cy, radius, c1, c2):
    d = ImageDraw.Draw(img)
    steps = 120
    for i in range(steps, 0, -1):
        r = radius * i / steps
        t = 1 - i / steps
        color = tuple(int(c1[j] + (c2[j] - c1[j]) * t) for j in range(3))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


W, H = 800, 600
img = Image.new("RGB", (W, H), (11, 19, 43))
d = ImageDraw.Draw(img)

# wing gradient colors
wing_a1, wing_a2 = (255, 159, 243), (142, 68, 173)
wing_b1, wing_b2 = (254, 202, 87), (238, 82, 83)

# radial gradients
radial_gradient(img, 300, 230, 140, wing_a1, wing_a2)
radial_gradient(img, 500, 230, 140, wing_a1, wing_a2)
radial_gradient(img, 290, 380, 130, wing_b1, wing_b2)
radial_gradient(img, 510, 380, 130, wing_b1, wing_b2)

# wing spots
for cx, cy, r in [
    (300, 230, 12), (500, 230, 12), (340, 205, 7), (460, 205, 7),
    (280, 275, 8), (520, 275, 8), (290, 380, 9), (510, 380, 9),
    (260, 350, 6), (540, 350, 6),
]:
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))

# body
d.ellipse([386, 210, 414, 390], fill=(26, 26, 46), outline=(226, 226, 226), width=2)
# head
d.ellipse([378, 173, 422, 217], fill=(26, 26, 46), outline=(226, 226, 226), width=3)

# antennae (line segments approximating curve)
for base, direction in [(392, 1), (408, -1)]:
    pts = []
    for t in range(0, 41):
        ang = t * 0.05
        pts.append((base + direction * (t * 1.8 * cos(ang * 0.6)), 180 - t * 1.2))
    d.line(pts, fill=(226, 226, 226), width=3)
    tip = pts[-1]
    d.ellipse([tip[0] - 6, tip[1] - 6, tip[0] + 6, tip[1] + 6], fill=(254, 202, 87))

# text
img.save("mariposa.png")
print("mariposa.png generado")