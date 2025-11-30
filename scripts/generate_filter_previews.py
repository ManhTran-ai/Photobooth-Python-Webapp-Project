"""
Utility script to (re)generate filter preview thumbnails used on the session page.
"""
import os
from PIL import Image, ImageDraw
from models.filter_engine import FilterEngine


def build_base_image(width=320, height=240):
    """Create a colorful base image with shapes and gradients."""
    base = Image.new("RGB", (width, height), "#fef4e8")
    draw = ImageDraw.Draw(base)

    palette = ["#ff7f50", "#ffd166", "#06d6a0", "#118ab2", "#5e60ce"]
    stripe_width = width // len(palette)

    for index, color in enumerate(palette):
        draw.rectangle(
            (
                index * stripe_width,
                0,
                (index + 1) * stripe_width,
                height,
            ),
            fill=color,
        )

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.ellipse(
        (width * 0.2, height * 0.15, width * 0.8, height * 0.85),
        fill=(255, 255, 255, 90),
        outline=(0, 0, 0, 40),
        width=4,
    )

    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def main():
    preview_dir = os.path.join("static", "filter_previews")
    os.makedirs(preview_dir, exist_ok=True)

    base_image = build_base_image()
    filters = FilterEngine.get_available_filters()

    for filter_def in filters:
        name = filter_def["name"]
        preview_image = base_image.copy()
        if name != "none":
            preview_image = FilterEngine.apply_filter(preview_image, name)

        output_path = os.path.join(preview_dir, f"{name}.jpg")
        preview_image.save(output_path, "JPEG", quality=85)
        print(f"Generated preview for {name} -> {output_path}")


if __name__ == "__main__":
    main()






