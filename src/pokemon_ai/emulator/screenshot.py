"""Screenshot capture and encoding helpers."""

import base64
from io import BytesIO

from PIL import Image


def png_to_base64(png_bytes: bytes) -> str:
    """Convert PNG bytes to a base64 string for LLM consumption."""
    return base64.b64encode(png_bytes).decode("utf-8")


def resize_screenshot(png_bytes: bytes, max_width: int = 480) -> bytes:
    """Resize a screenshot to reduce token cost while preserving readability."""
    img = Image.open(BytesIO(png_bytes))
    if img.width <= max_width:
        return png_bytes

    ratio = max_width / img.width
    new_size = (max_width, int(img.height * ratio))
    img = img.resize(new_size, Image.NEAREST)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
