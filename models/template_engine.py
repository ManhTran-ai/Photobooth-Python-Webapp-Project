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

    # Anchor points for stickers - Option 1 (stickers 1-15)
    ANCHOR_POINTS_4x1_OPTION1 = [
        (105, 45),    # Vị trí 1
        (269, 340),   # Vị trí 2
        (15, 150),    # Vị trí 3
        (410, 485),   # Vị trí 4
        (305, 640),   # Vị trí 5
        (125, 940),   # Vị trí 6
        (340, 1200),  # Vị trí 7
        (90, 1240),   # Vị trí 8
    ]

    # Anchor points for stickers - Option 2 (stickers 16-31)
    ANCHOR_POINTS_4x1_OPTION2 = [
        (390, 50),    # Vị trí 1
        (20, 210),    # Vị trí 2
        (195, 345),   # Vị trí 3
        (370, 635),   # Vị trí 4
        (15, 780),    # Vị trí 5
        (270, 937),   # Vị trí 6
        (20, 1130),   # Vị trí 7
        (350, 1240),  # Vị trí 8
    ]

    # Anchor points for 2x2 templates - Option 1 (stickers 1-15)
    ANCHOR_POINTS_2x2_OPTION1 = [
        (60, 50),     # Vị trí 1
        (65, 425),    # Vị trí 2
        (700, 470),   # Vị trí 3
        (450, 700),   # Vị trí 4
        (45, 890),    # Vị trí 5
        (875, 900),   # Vị trí 6
    ]

    # Anchor points for 2x2 templates - Option 2 (stickers 16-31)
    ANCHOR_POINTS_2x2_OPTION2 = [
        (860, 30),    # Vị trí 1
        (810, 470),   # Vị trí 2
        (60, 495),    # Vị trí 3
        (45, 900),    # Vị trí 4
        (870, 900),   # Vị trí 5
        (30, 40),     # Vị trí 6
    ]

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
            "style": "strip",
            # Anchor points for sticker placement - sử dụng option mặc định (sẽ được chọn động)
            "anchor_points": []  # Sẽ được populate động dựa trên sticker indices
        },
        # Template 2x2 - Lưới vuông
        "2x2": {
            "layout": "2x2",
            "size": (900, 940),
            "background": "#FFFFFF",
            "photo_size": (360, 360),
            "positions": [(60, 60), (480, 60), (60, 520), (480, 520)],
            "gap": 60,
            "style": "grid",
            # Anchor points for sticker placement - sử dụng option mặc định (sẽ được chọn động)
            "anchor_points": []  # Sẽ được populate động dựa trên sticker indices
        },
        "classic_strip": {
            "layout": "4x1",
            "size": (640, 1850),
            "background": "#FFFFFF",
            "photo_size": (540, 400),
            "positions": [(50, 40), (50, 480), (50, 920), (50, 1360)],
            "border_color": "#000000",
            "border_width": 3,
            "style": "classic",
            # Anchor points for sticker placement - sử dụng option mặc định (sẽ được chọn động)
            "anchor_points": []  # Sẽ được populate động dựa trên sticker indices
        },
        "grid_modern": {
            "layout": "2x2",
            "size": (1200, 1200),
            "background": "#FFFFFF",
            "photo_size": (560, 560),
            "positions": [(20, 20), (620, 20), (20, 620), (620, 620)],
            "gap": 20,
            "style": "modern",
            # Anchor points for sticker placement - sử dụng option mặc định (sẽ được chọn động)
            "anchor_points": []  # Sẽ được populate động dựa trên sticker indices
        },
        "pastel_pink": {
            "layout": "4x1",
            "size": (640, 1850),
            "background": "#FFE4EC",
            "photo_size": (540, 400),
            "positions": [(50, 40), (50, 480), (50, 920), (50, 1360)],
            "rounded_corners": 20,
            "style": "cute",
            # Anchor points for sticker placement - sử dụng option mặc định (sẽ được chọn động)
            "anchor_points": []  # Sẽ được populate động dựa trên sticker indices
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

    def create_collage(self, image_paths: list, template_name: str, colors: dict=None,
                       decorations: list=None, fill_mode: str='duplicate',
                       sticker_paths: list=None, anchor_mode: bool=False,
                       sticker_indices: list=None) -> str:
        """
        Create a collage image from provided image paths according to template.
        Returns absolute path to saved PNG.

        Args:
            image_paths: list of image file paths
            template_name: name of template to use
            colors: dict with color overrides (bg, accent, border)
            decorations: list of decoration dicts with path, x, y, scale, color
            fill_mode: how to handle missing images (duplicate, placeholder, center)
            sticker_paths: list of sticker file paths for anchor-based placement
            anchor_mode: if True, place stickers using anchor points with random transforms
            sticker_indices: list of sticker indices (starting from 1) for anchor point selection
                           - Indices 1-15: use Option 1 anchor points
                           - Indices 16-31: use Option 2 anchor points
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

        # Place stickers using anchor points if anchor_mode is enabled
        if anchor_mode and sticker_paths:
            canvas = self.place_stickers_with_anchors(
                canvas, sticker_paths, template_name,
                sticker_indices=sticker_indices,
                num_stickers=2, rotation_range=(0, 360), scale_range=(3.0, 4.0)
            )

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

    @staticmethod
    def _remove_sticker_background(image):
        """
        Tách nền khỏi sticker - hỗ trợ cả checkered background và nền thông thường.

        Args:
            image: PIL Image object (ảnh sticker có nền)

        Returns:
            PIL Image: Ảnh sticker đã được tách nền, hệ màu RGBA với nền trong suốt hoàn toàn
        """
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Đầu tiên, thử xóa checkered background (ô vuông đen xám xen kẽ)
        result = TemplateEngine._remove_checkered_background(image)

        # Kiểm tra xem đã xóa được nhiều pixel chưa
        import numpy as np
        original_arr = np.array(image)
        result_arr = np.array(result)

        original_opaque = np.sum(original_arr[:, :, 3] > 128)
        result_opaque = np.sum(result_arr[:, :, 3] > 128)

        # Nếu đã xóa được > 10% pixel, coi như thành công
        if original_opaque > 0 and (original_opaque - result_opaque) / original_opaque > 0.1:
            return TemplateEngine._clean_alpha_channel(result)

        # Nếu không, thử dùng rembg
        try:
            import rembg
            from io import BytesIO

            buffer = BytesIO()
            image.save(buffer, format='PNG')
            input_bytes = buffer.getvalue()

            output_bytes = rembg.remove(input_bytes)
            result = Image.open(BytesIO(output_bytes))

            if result.mode != 'RGBA':
                result = result.convert('RGBA')

            result = TemplateEngine._clean_alpha_channel(result)
            return result

        except ImportError:
            return TemplateEngine._remove_background_pillow(image)
        except Exception:
            try:
                return TemplateEngine._remove_background_pillow(image)
            except Exception:
                return image

    @staticmethod
    def _remove_checkered_background(image, tolerance=20):
        """
        Xóa checkered background (ô vuông đen xám xen kẽ) khỏi ảnh.

        Checkered background thường có 2 màu xám xen kẽ:
        - Màu sáng: ~192-210 (RGB)
        - Màu tối: ~128-150 (RGB)

        Args:
            image: PIL Image object (RGBA)
            tolerance: Độ chênh lệch cho phép khi xác định màu xám

        Returns:
            PIL Image: Ảnh với checkered background đã được xóa
        """
        import numpy as np

        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        arr = np.array(image)
        height, width = arr.shape[:2]

        r = arr[:, :, 0].astype(np.int16)
        g = arr[:, :, 1].astype(np.int16)
        b = arr[:, :, 2].astype(np.int16)
        a = arr[:, :, 3]

        # Kiểm tra màu xám (R ≈ G ≈ B)
        diff_rg = np.abs(r - g)
        diff_gb = np.abs(g - b)
        diff_rb = np.abs(r - b)
        max_diff = np.maximum(np.maximum(diff_rg, diff_gb), diff_rb)
        is_gray = max_diff < tolerance

        # Tính giá trị trung bình màu
        avg = (r + g + b) // 3

        # Các dải màu checkered phổ biến
        # Photoshop/GIMP checkered: ~128 (dark) và ~192-204 (light)
        checkered_ranges = [
            (120, 170),  # Dark gray squares
            (185, 215),  # Light gray squares
            (100, 135),  # Very dark gray
            (215, 250),  # Very light gray (near white)
        ]

        checkered_mask = np.zeros((height, width), dtype=bool)
        for low, high in checkered_ranges:
            range_mask = (avg >= low) & (avg <= high)
            checkered_mask = checkered_mask | range_mask

        # Pixel phải là màu xám VÀ nằm trong dải checkered
        remove_mask = is_gray & checkered_mask

        # Set alpha = 0 cho các pixel checkered
        arr[:, :, 3] = np.where(remove_mask, 0, a)

        return Image.fromarray(arr, mode='RGBA')

    @staticmethod
    def _clean_alpha_channel(image, alpha_threshold=10):
        """
        Loại bỏ các pixel có alpha thấp (nền mờ còn sót lại).

        Args:
            image: PIL Image object (RGBA)
            alpha_threshold: Ngưỡng alpha để xóa (0-255). Pixel có alpha < threshold sẽ thành trong suốt

        Returns:
            PIL Image: Ảnh đã được làm sạch
        """
        if image.mode != 'RGBA':
            return image

        # Chuyển đổi sang numpy array để xử lý nhanh hơn
        import numpy as np

        arr = np.array(image)
        alpha = arr[:, :, 3]

        # Tạo mask cho các pixel có alpha thấp (nền mờ)
        # Các pixel này sẽ được set thành hoàn toàn trong suốt
        mask = alpha < alpha_threshold

        # Cập nhật alpha channel: set các pixel nền mờ thành 0
        arr[:, :, 3] = np.where(mask, 0, alpha)

        # Chuyển đổi lại thành PIL Image
        return Image.fromarray(arr, mode='RGBA')

    @staticmethod
    def _remove_background_pillow(image):
        """
        Tách nền bằng Pillow (phương pháp dựa trên màu sắc).
        Phù hợp cho các sticker có nền đồng nhất.

        Args:
            image: PIL Image object

        Returns:
            PIL Image: Ảnh đã được tách nền (RGBA)
        """
        # Chuyển đổi sang RGBA nếu chưa phải
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Lấy dữ liệu pixel
        datas = image.getdata()

        new_data = []
        for item in datas:
            r, g, b, a = item

            # Kiểm tra nếu pixel là nền (màu nâu/đỏ/đen mờ hoặc trắng/xám)
            # Nền pixel art thường có độ bão hòa thấp hoặc độ sáng cao/thấp đặc trưng
            is_background = False

            # Trường hợp 1: Pixel trong suốt hoặc gần trong suốt
            if a < 50:
                is_background = True

            # Trường hợp 2: Pixel màu trắng/xám nhạt (nền sáng)
            elif r > 230 and g > 230 and b > 230:
                is_background = True

            # Trường hợp 3: Pixel màu nâu/đỏ đặc trưng của nền sticker pixel art
            elif (r > 150 and r < 220 and g > 100 and g < 180 and b > 80 and b < 150):
                # Nền màu nâu đỏ đặc trưng
                is_background = True

            # Trường hợp 4: Pixel tối (đen/xám đậm)
            elif r < 30 and g < 30 and b < 30 and a < 200:
                is_background = True

            if is_background:
                new_data.append((0, 0, 0, 0))  # Hoàn toàn trong suốt
            else:
                new_data.append(item)

        # Tạo ảnh mới với dữ liệu đã xử lý
        image.putdata(new_data)
        return image

    def get_anchor_points_for_template(self, template_name, sticker_indices=None):
        """
        Trả về danh sách anchor points cho template dựa trên sticker indices.

        Args:
            template_name: tên template
            sticker_indices: list các chỉ số của sticker (bắt đầu từ 1)
                           - Nếu sticker_indices chứa các giá trị 1-15: dùng Option 1
                           - Nếu sticker_indices chứa các giá trị 16-31: dùng Option 2
                           - Nếu mixed: dùng Option 1 (ưu tiên option 1)

        Returns:
            list: Danh sách các tuple (x, y) anchor points
        """
        if template_name not in self.TEMPLATES:
            raise ValueError(f"Template '{template_name}' not found")

        template = self.TEMPLATES[template_name]
        layout = template.get("layout", "")

        # Xác định option dựa trên sticker_indices
        option = 1  # Mặc định dùng option 1

        if sticker_indices:
            # Lọc các indices hợp lệ (1-31)
            valid_indices = [idx for idx in sticker_indices if isinstance(idx, int) and 1 <= idx <= 31]

            if valid_indices:
                # Kiểm tra xem có sticker nào từ 16-31 không
                has_high_indices = any(idx >= 16 for idx in valid_indices)
                has_low_indices = any(1 <= idx <= 15 for idx in valid_indices)

                # Nếu chỉ có sticker 16-31 -> dùng option 2
                # Nếu chỉ có sticker 1-15 -> dùng option 1
                # Nếu mixed -> ưu tiên option 1 (dùng option 1)
                if has_high_indices and not has_low_indices:
                    option = 2

        # Chọn anchor points dựa trên layout và option
        if layout in ("1x4", "4x1"):
            # Template 4x1 - 8 anchor points
            if option == 1:
                return self.ANCHOR_POINTS_4x1_OPTION1
            else:
                return self.ANCHOR_POINTS_4x1_OPTION2
        elif layout == "2x2":
            # Template 2x2 - 6 anchor points
            if option == 1:
                return self.ANCHOR_POINTS_2x2_OPTION1
            else:
                return self.ANCHOR_POINTS_2x2_OPTION2
        else:
            # Layout khác - trả về empty list
            return []

    def get_anchor_points(self, template_name):
        """
        Trả về danh sách anchor points cho template (legacy method - không khuyến khích sử dụng).

        Args:
            template_name: tên template

        Returns:
            list: Danh sách các tuple (x, y) anchor points
        """
        # Legacy method - trả về empty list vì bây giờ anchor points được chọn động
        if template_name not in self.TEMPLATES:
            raise ValueError(f"Template '{template_name}' not found")
        return self.TEMPLATES[template_name].get("anchor_points", [])

    def place_stickers_with_anchors(self, canvas, sticker_paths, template_name,
                                      sticker_indices=None, num_stickers=2,
                                      rotation_range=(0, 360), scale_range=(3.0, 4.0),
                                      remove_background=True):
        """
        Gắn stickers sử dụng anchor points cố định.

        Phương pháp "Điểm neo cố định với lựa chọn động":
        - Chọn option anchor points dựa trên sticker_indices:
          * Stickers 1-15 -> Option 1
          * Stickers 16-31 -> Option 2
        - Chọn ngẫu nhiên N điểm từ anchor_points (tối đa 2 stickers)
        - Mỗi sticker được xoay ngẫu nhiên 0-360 độ
        - Mỗi sticker được phóng to/thu nhỏ ngẫu nhiên 3-4 lần
        - Nền sticker được loại bỏ bằng rembg (nếu remove_background=True)

        Args:
            canvas: PIL Image object (canvas template)
            sticker_paths: list of sticker file paths
            template_name: tên template
            sticker_indices: list các chỉ số của sticker (bắt đầu từ 1)
            num_stickers: số lượng sticker tối đa (mặc định 2)
            rotation_range: tuple (min, max) độ xoay
            scale_range: tuple (min, max) tỷ lệ phóng to/thu nhỏ (mặc định 3-4 lần)
            remove_background: nếu True, loại bỏ nền sticker bằng rembg

        Returns:
            PIL Image: Canvas với stickers đã được gắn
        """
        import random

        # Lấy anchor points dựa trên template và sticker indices
        anchor_points = self.get_anchor_points_for_template(template_name, sticker_indices)
        if not anchor_points:
            return canvas

        if not sticker_paths:
            return canvas

        # Chọn ngẫu nhiên N điểm từ anchor_points (tối đa 2 stickers)
        num_to_place = min(num_stickers, len(anchor_points))
        selected_points = random.sample(anchor_points, num_to_place)

        # Trộm sticker paths đã chọn để không lặp lại
        available_stickers = list(sticker_paths)
        random.shuffle(available_stickers)

        for i, (x, y) in enumerate(selected_points):
            if i >= len(available_stickers):
                break

            sticker_path = available_stickers[i]

            try:
                # Mở sticker và chuyển sang RGBA
                sticker = Image.open(sticker_path).convert("RGBA")

                # Tách nền bằng rembg (loại bỏ hoàn toàn nền trắng/đen)
                if remove_background:
                    sticker = self._remove_sticker_background(sticker)

            except Exception:
                continue

            # Biến đổi ngẫu nhiên: Xoay 0-360 độ
            angle = random.uniform(rotation_range[0], rotation_range[1])
            sticker = sticker.rotate(angle, Image.BICUBIC, expand=True)

            # Biến đổi ngẫu nhiên: Phóng to/thu nhỏ 3-4 lần
            scale = random.uniform(scale_range[0], scale_range[1])
            new_w = int(sticker.width * scale)
            new_h = int(sticker.height * scale)
            sticker = sticker.resize((new_w, new_h), Image.BICUBIC)

            # Paste sticker lên canvas (anchor point là tâm, dùng sticker làm mask)
            center_x = x - new_w // 2
            center_y = y - new_h // 2
            canvas.paste(sticker, (center_x, center_y), sticker)

        return canvas


