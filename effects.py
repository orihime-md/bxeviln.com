"""Pillow-based image effects with a hacker/terminal aesthetic."""

import hashlib
import os
import random
from io import BytesIO

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

EFFECT_NAMES = {
    "glitch": "Glitch",
    "matrix": "Matrix Rain",
    "terminal": "Terminal Scan",
    "cyber": "Cyber Punk",
    "invert": "Invert",
    "deepfry": "Deep Fry",
    "vhs": "VHS",
    "encrypt": "Encrypted Slices",
}

def load_image(data: bytes) -> Image.Image:
    img = Image.open(BytesIO(data))
    return img.convert("RGB")

def to_bytes(img: Image.Image, filename: str = "output.png") -> BytesIO:
    fmt = "PNG" if filename.lower().endswith(".png") else "JPEG"
    buf = BytesIO()
    if fmt == "JPEG":
        img.save(buf, format=fmt, quality=92)
    else:
        img.save(buf, format=fmt)
    buf.seek(0)
    return buf

def _load_font(size: int):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()

def effect_glitch(img: Image.Image) -> Image.Image:
    """RGB channel shifts plus random horizontal slice displacement."""
    img = img.convert("RGB")
    width, height = img.size
    result = img.copy()
    shift = max(4, width // 60)
    r, g, b = img.split()
    result = Image.merge("RGB", (
        r.transform(r.size, Image.AFFINE, (1, 0, shift, 0, 1, 0)),
        g,
        b.transform(b.size, Image.AFFINE, (1, 0, -shift, 0, 1, 0)),
    ))
    draw_count = random.randint(4, 10)
    for _ in range(draw_count):
        y = random.randint(0, height - 1)
        slice_h = random.randint(4, max(5, height // 12))
        x_off = random.randint(-shift * 2, shift * 2)
        strip = result.crop((0, y, width, min(y + slice_h, height)))
        result.paste(strip, (x_off, y))
    return result

def effect_matrix(img: Image.Image) -> Image.Image:
    """Green terminal rain rendered over a darkened copy of the image."""
    img = img.convert("L").point(lambda p: p // 2 + 24).convert("RGB")
    width, height = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _load_font(12)
    chars = "01ｱｲｳｴｵｶｷｸﾊﾋﾌﾍﾎ$#*+=-"
    for column in range(0, width, 12):
        x = column + random.randint(-2, 2)
        y = random.randint(-40, height)
        run_length = random.randint(6, 28)
        for i in range(run_length):
            char = random.choice(chars)
            alpha = max(0, 220 - i * (220 // run_length))
            color = (0, 255, 70, alpha) if i == 0 else (0, 180 + random.randint(0, 60), 60, alpha // 2)
            draw.text((x, y + i * 14), char, font=font, fill=color)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def effect_terminal(img: Image.Image) -> Image.Image:
    """CRT look: scanlines, green tint, vignette and a blinking cursor bar."""
    img = img.convert("RGB")
    width, height = img.size
    green = Image.new("RGB", img.size, (0, 0, 0))
    img_gray = img.convert("L")
    green_px = green.load()
    gray_px = img_gray.load()
    for y in range(height):
        for x in range(0, width, 1):
            v = gray_px[x, y]
            green_px[x, y] = (v // 6, v, v // 6)
    draw = ImageDraw.Draw(green)
    for y in range(0, height, 4):
        draw.line((0, y, width, y), fill=(0, 12, 0), width=1)
    vignette = Image.new("L", img.size, 0)
    vd = ImageDraw.Draw(vignette)
    vd.ellipse((-width // 3, -height // 3, width + width // 3, height + height // 3), fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(60))
    black = Image.new("RGB", img.size, (0, 0, 0))
    result = Image.composite(green, black, vignette.point(lambda p: max(p, 90)))
    cursor_y = height - 24
    result.paste((0, 255, 80), (width - 40, cursor_y, width - 28, cursor_y + 4))
    return result

def effect_cyber(img: Image.Image) -> Image.Image:
    """High-contrast teal/magenta duotone with a HUD-style grid overlay."""
    img = img.convert("L")
    img = ImageEnhance.Contrast(img).enhance(1.6)
    width, height = img.size
    result = Image.new("RGB", img.size)
    px_in = img.load()
    px_out = result.load()
    for y in range(height):
        for x in range(width):
            v = px_in[x, y] / 255
            px_out[x, y] = (int(255 * v ** 2.2), int(90 * v ** 1.2), int(230 * v ** 0.6))
    draw = ImageDraw.Draw(result)
    for x in range(0, width, 48):
        draw.line((x, 0, x, height), fill=(0, 120, 140), width=1)
    for y in range(0, height, 48):
        draw.line((0, y, width, y), fill=(0, 120, 140), width=1)
    return result

def effect_invert(img: Image.Image) -> Image.Image:
    from PIL import ImageOps
    return ImageOps.invert(img.convert("RGB"))

def effect_deepfry(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    img = ImageEnhance.Color(img).enhance(3.0)
    img = ImageEnhance.Contrast(img).enhance(2.2)
    img = ImageEnhance.Brightness(img).enhance(1.3)
    return img

def effect_vhs(img: Image.Image) -> Image.Image:
    """Retro VHS: blur, chromatic offset, scanlines and a timestamp."""
    img = img.convert("RGB").filter(ImageFilter.GaussianBlur(1.2))
    width, height = img.size
    r, g, b = img.split()
    img = Image.merge("RGB", (
        r.transform(r.size, Image.AFFINE, (1, 0, 6, 0, 1, 0)),
        g,
        b.transform(b.size, Image.AFFINE, (1, 0, -6, 0, 1, 0)),
    ))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(0, height, 3):
        draw.line((0, y, width, y), fill=(255, 255, 255, 18), width=1)
    draw.text((18, height - 40), "REC  00:00:00", font=_load_font(24), fill=(255, 255, 255, 230))
    return img

def effect_encrypt(img: Image.Image) -> Image.Image:
    """Image cut into blocks that are re-ordered with a seed from its own hash."""
    img = img.convert("RGB")
    width, height = img.size
    block = 48
    digest = hashlib.sha256(img.tobytes()).hexdigest()
    random.seed(int(digest[:12], 16))
    blocks = []
    for y in range(0, height, block):
        for x in range(0, width, block):
            box = (x, y, min(x + block, width), min(y + block, height))
            blocks.append(img.crop(box))
    random.shuffle(blocks)
    result = Image.new("RGB", img.size)
    i = 0
    for y in range(0, height, block):
        for x in range(0, width, block):
            result.paste(blocks[i], (x, y))
            i += 1
    random.seed()
    return result

EFFECTS = {
    "glitch": effect_glitch,
    "matrix": effect_matrix,
    "terminal": effect_terminal,
    "cyber": effect_cyber,
    "invert": effect_invert,
    "deepfry": effect_deepfry,
    "vhs": effect_vhs,
    "encrypt": effect_encrypt,
}

def apply_effect(img: Image.Image, name: str) -> Image.Image:
    func = EFFECTS.get(name)
    if func is None:
        raise ValueError(f"Unknown effect: {name}")
    return func(img)
