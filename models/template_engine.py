"""
TemplateEngine: dynamic template renderer using Pillow.

Provides:
- get_available_templates()
- create_collage(image_paths, template_name, colors=None, decorations=None, fill_mode='duplicate')
"""
from PIL import Image, ImageDraw, ImageFilter
import os
import io
import math
try:
    import cairosvg
    _HAS_CAIROSVG = True
except Exception:
    _HAS_CAIROSVG = False

class TemplateEngine:
    """Engine tạo template photobooth động"""

    # Minimal example templates. Extend as needed or load from metadata file.
    TEMPLATES = {
        # Template 1x4 - Dọc dạng strip (như ảnh photo booth)
        "1x4": {
            "layout": "1x4",
            "size": (420, 1300),
            "background": "#FFFFFF",
            "photo_size": (360, 260),
            "positions": [(30, 60), (30, 360), (30, 660), (30, 960)],
            "border_color": "#000000",
            "border_width": 2,
            "style": "strip"
        },
        # Template 2x2 - Lưới vuông
        "2x2": {
            "layout": "2x2",
            "size": (900, 940),
            "background": "#FFFFFF",
            "photo_size": (360, 360),
            "positions": [(60, 60), (480, 60), (60, 520), (480, 520)],
            "gap": 60,
            "style": "grid"
        },
        "classic_strip": {
            "layout": "4x1",
            "size": (640, 1850),
            "background": "#FFFFFF",
            "photo_size": (540, 400),
            "positions": [(50, 40), (50, 480), (50, 920), (50, 1360)],
            "border_color": "#000000",
            "border_width": 3,
            "style": "classic"
        },
        "grid_modern": {
            "layout": "2x2",
            "size": (1200, 1200),
            "background": "#FFFFFF",
            "photo_size": (560, 560),
            "positions": [(20, 20), (620, 20), (20, 620), (620, 620)],
            "gap": 20,
            "style": "modern"
        },
        "pastel_pink": {
            "layout": "4x1",
            "size": (640, 1850),
            "background": "#FFE4EC",
            "photo_size": (540, 400),
            "positions": [(50, 40), (50, 480), (50, 920), (50, 1360)],
            "rounded_corners": 20,
            "style": "cute"
        }
    }

    def __init__(self, output_dir=None):
        # default to static/uploads/collages if not provided
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join("static", "uploads", "collages")
        os.makedirs(self.output_dir, exist_ok=True)

    def get_available_templates(self):
        """Return basic metadata for available templates"""
        return {
            name: {
                "layout": t["layout"],
                "style": t.get("style"),
                "size": t["size"]
            }
            for name, t in self.TEMPLATES.items()
        }

    def create_collage(self, image_paths: list, template_name: str, colors: dict=None, decorations: list=None, fill_mode: str='duplicate') -> str:
        """
        Create a collage image from provided image paths according to template.
        Returns absolute path to saved PNG.
        """
        if template_name not in self.TEMPLATES:
            raise ValueError(f"Template '{template_name}' not found")

        template = self.TEMPLATES[template_name]
        slots = len(template.get("positions", []))

        # Normalize image_paths to required slots
        images = list(image_paths)
        if len(images) < slots:
            if len(images) == 0:
                raise ValueError("No images provided")
            if fill_mode == 'duplicate':
                i = 0
                while len(images) < slots:
                    images.append(images[i % len(images)])
                    i += 1
            elif fill_mode == 'placeholder':
                placeholder = os.path.join("static", "templates", "placeholders", "placeholder.png")
                while len(images) < slots:
                    images.append(placeholder)
            else:
                # center or other modes: pad with last image
                while len(images) < slots:
                    images.append(images[-1])
        else:
            images = images[:slots]

        # Create canvas
        canvas = self._create_background(template, colors)

        # Place each photo
        for idx, img_path in enumerate(images):
            try:
                photo = Image.open(img_path).convert("RGBA")
            except Exception:
                # if image cannot be opened, create blank
                photo = Image.new("RGBA", template["photo_size"], (230,230,230,255))

            photo = self._resize_and_crop(photo, template["photo_size"])

            if template.get("rounded_corners"):
                photo = self._add_rounded_corners(photo, template["rounded_corners"])

            if template.get("border_color"):
                photo = self._add_border(photo, template["border_color"], template.get("border_width", 2))

            if template.get("shadow"):
                canvas = self._add_shadow(canvas, template["positions"][idx], template["photo_size"])

            canvas.paste(photo, template["positions"][idx], photo)

        # Decorations (simple: paste PNGs; SVG rasterization handled externally)
        if decorations:
            for deco in decorations:
                deco_path = deco.get("path")
                x = int(deco.get("x", 0))
                y = int(deco.get("y", 0))
                scale = float(deco.get("scale", 1.0))
                color = deco.get("color")
                try:
                    if deco_path and deco_path.lower().endswith('.svg') and _HAS_CAIROSVG:
                        # rasterize SVG to PNG bytes
                        png_bytes = cairosvg.svg2png(url=deco_path)
                        dimg = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
                    else:
                        dimg = Image.open(deco_path).convert("RGBA")
                    if scale != 1.0:
                        new_w = int(dimg.width * scale)
                        new_h = int(dimg.height * scale)
                        dimg = dimg.resize((new_w, new_h), Image.LANCZOS)
                    canvas.paste(dimg, (x, y), dimg)
                except Exception:
                    continue

        # final effects (film holes, neon etc) - not exhaustive
        if template.get("film_holes"):
            canvas = self._add_film_holes(canvas)

        # Save
        filename = f"collage_{template_name}_{os.urandom(4).hex()}.png"
        output_path = os.path.join(self.output_dir, filename)
        # Ensure canvas is RGBA -> convert to RGB for smaller files with white background if desired
        canvas.save(output_path, "PNG", quality=95)
        return os.path.abspath(output_path)

    def _create_background(self, template, colors=None):
        size = template["size"]
        bg = template.get("background", "#FFFFFF")
        if isinstance(bg, dict) and bg.get("type") == "gradient":
            return self._create_gradient(size, bg.get("colors", ["#FFFFFF", "#000000"]))
        else:
            # Allow override via colors dict (key 'bg')
            if colors and colors.get("bg"):
                bg_color = colors.get("bg")
            else:
                bg_color = bg
            return Image.new("RGBA", size, bg_color)

    def _create_gradient(self, size, colors):
        from PIL import ImageDraw
        img = Image.new("RGBA", size)
        draw = ImageDraw.Draw(img)
        r1, g1, b1 = self._hex_to_rgb(colors[0])
        r2, g2, b2 = self._hex_to_rgb(colors[1])
        for y in range(size[1]):
            ratio = y / max(1, size[1]-1)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            draw.line([(0, y), (size[0], y)], fill=(r, g, b, 255))
        return img

    def _resize_and_crop(self, image, target_size):
        """Resize và crop ảnh để fit vào khung"""
        img_ratio = image.width / image.height
        target_ratio = target_size[0] / target_size[1]
        if img_ratio > target_ratio:
            # image wider
            new_height = target_size[1]
            new_width = int(new_height * img_ratio)
        else:
            new_width = target_size[0]
            new_height = int(new_width / img_ratio)
        image = image.resize((new_width, new_height), Image.LANCZOS)
        left = (new_width - target_size[0]) // 2
        top = (new_height - target_size[1]) // 2
        right = left + target_size[0]
        bottom = top + target_size[1]
        return image.crop((left, top, right, bottom))

    def _add_rounded_corners(self, image, radius):
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), image.size], radius, fill=255)
        output = Image.new("RGBA", image.size, (0, 0, 0, 0))
        output.paste(image, mask=mask)
        return output

    def _add_border(self, image, color, width):
        bordered = Image.new("RGBA", (image.width + width*2, image.height + width*2), color)
        bordered.paste(image, (width, width))
        return bordered

    def _add_shadow(self, canvas, position, size):
        shadow = Image.new("RGBA", size, (0, 0, 0, 60))
        shadow = shadow.filter(ImageFilter.GaussianBlur(10))
        canvas.paste(shadow, (position[0] + 8, position[1] + 8), shadow)
        return canvas

    def _add_film_holes(self, canvas):
        draw = ImageDraw.Draw(canvas)
        hole_radius = 8
        for y in range(30, canvas.height, 60):
            draw.ellipse([(10, y-hole_radius), (10+hole_radius*2, y+hole_radius)], fill="#333333")
            draw.ellipse([(canvas.width-30, y-hole_radius), (canvas.width-30+hole_radius*2, y+hole_radius)], fill="#333333")
        return canvas

    @staticmethod
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


