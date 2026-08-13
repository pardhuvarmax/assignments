"""
Procedurally draws a small set of synthetic images with Pillow, so this
experiment has no external image assets, no licensing/provenance questions,
and known ground truth for every visual detail (exact counts, colors,
labels) that the QA step can be checked against.

Run directly to (re)generate images/*.png.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(HERE, "images")

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)


def font(size):
    return ImageFont.load_default(size=size)


def quarterly_revenue():
    img = Image.new("RGB", (600, 400), WHITE)
    d = ImageDraw.Draw(img)
    d.text((20, 15), "Quarterly Revenue ($M)", fill=BLACK, font=font(24))

    bars = [("Q1", 60, (70, 110, 220)), ("Q2", 90, (70, 110, 220)),
            ("Q3", 75, (70, 110, 220)), ("Q4", 140, (230, 140, 40))]
    base_y = 350
    x = 80
    width = 90
    for label, height, color in bars:
        d.rectangle([x, base_y - height * 2, x + width, base_y], fill=color)
        d.text((x + width // 2 - 10, base_y + 8), label, fill=BLACK, font=font(18))
        x += width + 40
    img.save(os.path.join(IMAGES_DIR, "quarterly_revenue.png"))


def network_diagram():
    img = Image.new("RGB", (600, 400), WHITE)
    d = ImageDraw.Draw(img)
    d.text((20, 15), "Network Diagram", fill=BLACK, font=font(24))

    nodes = {
        "Server": (300, 100),
        "Database": (300, 320),
        "Client A": (100, 250),
        "Client B": (500, 250),
    }
    edges = [("Server", "Database"), ("Server", "Client A"), ("Server", "Client B")]
    for a, b in edges:
        d.line([nodes[a], nodes[b]], fill=(120, 120, 120), width=3)
    for name, (x, y) in nodes.items():
        d.ellipse([x - 40, y - 40, x + 40, y + 40], fill=(90, 170, 220), outline=BLACK, width=2)
        d.text((x - 30, y - 8), name, fill=BLACK, font=font(14))
    img.save(os.path.join(IMAGES_DIR, "network_diagram.png"))


def traffic_scene():
    img = Image.new("RGB", (600, 400), (210, 235, 250))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 300, 600, 400], fill=(90, 90, 90))  # road
    d.rectangle([280, 340, 320, 360], fill=(255, 255, 255))  # lane marking

    d.rectangle([460, 120, 480, 300], fill=(60, 60, 60))  # pole
    d.rectangle([440, 60, 500, 240], fill=(30, 30, 30))  # housing
    d.ellipse([450, 70, 490, 110], fill=(200, 30, 30))    # red -- lit
    d.ellipse([450, 130, 490, 170], fill=(90, 70, 20))    # yellow -- off
    d.ellipse([450, 190, 490, 230], fill=(30, 90, 40))    # green -- off

    d.rectangle([80, 250, 220, 300], fill=(200, 60, 60))  # car body
    d.ellipse([95, 290, 125, 320], fill=BLACK)
    d.ellipse([175, 290, 205, 320], fill=BLACK)
    img.save(os.path.join(IMAGES_DIR, "traffic_scene.png"))


def weather_icons():
    img = Image.new("RGB", (600, 400), WHITE)
    d = ImageDraw.Draw(img)
    d.text((20, 15), "Weather Icons", fill=BLACK, font=font(24))

    # Sun
    d.ellipse([100, 90, 180, 170], fill=(250, 200, 40))
    # Cloud
    d.ellipse([380, 100, 460, 160], fill=(190, 190, 200))
    d.ellipse([420, 90, 500, 150], fill=(190, 190, 200))
    # Rain (cloud + lines)
    d.ellipse([100, 260, 180, 320], fill=(180, 180, 190))
    for lx in (110, 130, 150):
        d.line([lx, 320, lx - 10, 360], fill=(60, 110, 220), width=4)
    # Snow (cloud + flakes)
    d.ellipse([380, 260, 460, 320], fill=(190, 190, 200))
    for fx, fy in ((400, 350), (420, 360), (440, 350)):
        d.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], fill=(120, 180, 230))

    img.save(os.path.join(IMAGES_DIR, "weather_icons.png"))


def warehouse_plan():
    img = Image.new("RGB", (600, 400), WHITE)
    d = ImageDraw.Draw(img)
    d.text((20, 10), "Warehouse Floor Plan", fill=BLACK, font=font(22))

    zones = [
        ("Receiving", (30, 60, 210, 380), (170, 220, 170)),
        ("Storage", (220, 60, 400, 380), (170, 190, 230)),
        ("Shipping", (410, 60, 590, 380), (230, 190, 140)),
    ]
    for label, box, color in zones:
        d.rectangle(box, fill=color, outline=BLACK, width=2)
        d.text((box[0] + 10, box[1] + 10), label, fill=BLACK, font=font(16))

    # 5 boxes scattered in the Storage zone
    box_positions = [(240, 120), (280, 160), (320, 120), (240, 220), (320, 260)]
    for x, y in box_positions:
        d.rectangle([x, y, x + 30, y + 30], fill=(150, 100, 60), outline=BLACK, width=2)

    img.save(os.path.join(IMAGES_DIR, "warehouse_plan.png"))


def build_all():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    quarterly_revenue()
    network_diagram()
    traffic_scene()
    weather_icons()
    warehouse_plan()


if __name__ == "__main__":
    build_all()
    print(f"Generated images in {IMAGES_DIR}")
