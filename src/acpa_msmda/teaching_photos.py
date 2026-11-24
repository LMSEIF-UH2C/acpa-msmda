"""Session-only teaching photos. Decode and re-encode to strip metadata."""
from io import BytesIO
from PIL import Image, ImageOps

MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 20_000_000

def clean_photo(raw: bytes) -> bytes:
    if not raw or len(raw) > MAX_BYTES:
        raise ValueError("Invalid image size")
    try:
        with Image.open(BytesIO(raw)) as source:
            if source.format not in ("JPEG", "PNG") or source.width * source.height > MAX_PIXELS:
                raise ValueError("Unsupported image")
            image = ImageOps.exif_transpose(source).convert("RGB")
            image.thumbnail((1600, 1600))
            # A fresh image prevents metadata from being copied into the export.
            clean = Image.new("RGB", image.size)
            clean.paste(image)
            output = BytesIO()
            clean.save(output, format="JPEG", quality=85)
            return output.getvalue()
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        raise ValueError("Invalid image") from exc
