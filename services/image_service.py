import hashlib
import io
import time
from urllib.parse import quote

import requests
from PIL import Image, ImageDraw, ImageFont


def generate_cover_image(prompt: str) -> Image.Image:
    seed = int(time.time())
    short_prompt = quote(prompt[:300])
    urls = [
        f"https://image.pollinations.ai/prompt/{short_prompt}?width=600&height=600&nologo=true&nofeed=true&seed={seed}",
        f"https://image.pollinations.ai/prompt/{short_prompt}?width=512&height=512&nologo=true&seed={seed}",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=45, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and len(r.content) > 1000:
                return Image.open(io.BytesIO(r.content)).convert("RGB")
        except Exception:
            continue
    return _make_placeholder(prompt)


def _make_placeholder(prompt: str) -> Image.Image:
    h = hashlib.md5(prompt.encode()).hexdigest()
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    img = Image.new("RGB", (600, 600), color=(r, g, b))
    draw = ImageDraw.Draw(img)

    for i in range(600):
        a = i / 600
        draw.line(
            [(0, i), (600, i)],
            fill=(int(r * (1 - a * 0.5)), int(g * (1 - a * 0.3)), int(b * (1 - a * 0.2))),
        )

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except Exception:
        font = ImageFont.load_default()

    draw.text((300, 300), "Album Cover", fill=(255, 255, 255), anchor="mm", font=font)
    return img
