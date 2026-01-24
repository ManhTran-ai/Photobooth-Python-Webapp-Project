"""
Script xóa background checkered (ô vuông đen xám xen kẽ) khỏi sticker PNG.
Background checkered thường có pattern đặc trưng với 2 màu xám xen kẽ.
"""
from PIL import Image
import numpy as np
from pathlib import Path
import os

# Đường dẫn thư mục stickers
TEMPLATES_DIR = Path("static/templates")
STICKERS_DIR = Path("static/templates/stickers")

# Màu checkered pattern phổ biến (RGB)
# Thường là 2 màu xám: sáng (~204, 204, 204) và tối (~153, 153, 153)
CHECKERED_COLORS = [
    # Light gray checkered
    ((200, 200, 200), (210, 210, 210)),  # Range for light squares
    ((145, 145, 145), (165, 165, 165)),  # Range for dark squares
    # Alternative checkered patterns
    ((240, 240, 240), (255, 255, 255)),  # Very light
    ((100, 100, 100), (130, 130, 130)),  # Darker
    # Common Photoshop checkered pattern
    ((192, 192, 192), (210, 210, 210)),  # PS light gray
    ((128, 128, 128), (145, 145, 145)),  # PS dark gray
]


def is_checkered_pixel(r, g, b, tolerance=15):
    """
    Kiểm tra xem một pixel có phải là checkered background hay không.

    Checkered background có đặc điểm:
    1. Màu xám (R ≈ G ≈ B)
    2. Nằm trong một trong các dải màu checkered phổ biến
    """
    # Convert to int to avoid overflow
    r, g, b = int(r), int(g), int(b)

    # Kiểm tra xem có phải màu xám không (R ≈ G ≈ B)
    max_diff = max(abs(r - g), abs(g - b), abs(r - b))
    if max_diff > tolerance:
        return False  # Không phải màu xám

    # Kiểm tra có nằm trong dải màu checkered không
    avg = (r + g + b) // 3

    # Checkered thường có 2 mức xám: ~128-145 (tối) và ~192-210 (sáng)
    checkered_ranges = [
        (125, 165),  # Dark gray range
        (185, 215),  # Light gray range
        (95, 135),   # Very dark gray
        (215, 255),  # Very light gray (near white)
    ]

    for low, high in checkered_ranges:
        if low <= avg <= high:
            return True

    return False


def detect_checkered_pattern(image, sample_size=20):
    """
    Phát hiện xem ảnh có checkered background không bằng cách phân tích các góc.
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    arr = np.array(image)
    height, width = arr.shape[:2]

    # Lấy mẫu từ 4 góc
    corners = [
        arr[0:sample_size, 0:sample_size],  # Top-left
        arr[0:sample_size, width-sample_size:width],  # Top-right
        arr[height-sample_size:height, 0:sample_size],  # Bottom-left
        arr[height-sample_size:height, width-sample_size:width],  # Bottom-right
    ]

    checkered_count = 0
    total_samples = 0

    for corner in corners:
        for row in corner:
            for pixel in row:
                r, g, b, a = pixel
                if a > 200:  # Pixel không trong suốt
                    total_samples += 1
                    if is_checkered_pixel(r, g, b):
                        checkered_count += 1

    if total_samples == 0:
        return False

    # Nếu > 60% pixel ở góc là checkered, coi như có checkered background
    ratio = checkered_count / total_samples
    return ratio > 0.6


def remove_checkered_background(image, tolerance=20):
    """
    Xóa checkered background khỏi ảnh.

    Args:
        image: PIL Image object
        tolerance: Độ chênh lệch cho phép khi so sánh màu

    Returns:
        PIL Image: Ảnh với background trong suốt
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    arr = np.array(image)
    height, width = arr.shape[:2]

    # Tạo mask cho các pixel checkered
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    a = arr[:, :, 3]

    # Tính độ chênh lệch giữa R, G, B (để xác định màu xám)
    diff_rg = np.abs(r - g)
    diff_gb = np.abs(g - b)
    diff_rb = np.abs(r - b)
    max_diff = np.maximum(np.maximum(diff_rg, diff_gb), diff_rb)

    # Mask cho màu xám (R ≈ G ≈ B)
    is_gray = max_diff < tolerance

    # Tính giá trị trung bình
    avg = (r + g + b) // 3

    # Mask cho các dải màu checkered
    checkered_mask = np.zeros((height, width), dtype=bool)

    # Dải màu checkered phổ biến
    checkered_ranges = [
        (120, 170),  # Dark gray (typical checkered dark)
        (180, 220),  # Light gray (typical checkered light)
        (100, 140),  # Very dark gray
        (210, 255),  # Very light (near white)
    ]

    for low, high in checkered_ranges:
        range_mask = (avg >= low) & (avg <= high)
        checkered_mask = checkered_mask | range_mask

    # Kết hợp: pixel phải là màu xám VÀ nằm trong dải checkered
    final_mask = is_gray & checkered_mask

    # Set alpha = 0 cho các pixel checkered
    arr[:, :, 3] = np.where(final_mask, 0, a)

    return Image.fromarray(arr, mode='RGBA')


def remove_checkered_with_edge_detection(image, tolerance=15):
    """
    Xóa checkered background với edge detection để bảo vệ viền của object.
    Phương pháp này giữ lại các pixel ở gần cạnh của object.
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    arr = np.array(image)
    height, width = arr.shape[:2]

    # Tạo bản sao để xử lý
    result = arr.copy()

    r = arr[:, :, 0].astype(np.float32)
    g = arr[:, :, 1].astype(np.float32)
    b = arr[:, :, 2].astype(np.float32)

    # Phát hiện edge bằng gradient
    from scipy import ndimage
    gray = (r + g + b) / 3

    # Tính gradient
    sobel_x = ndimage.sobel(gray, axis=1)
    sobel_y = ndimage.sobel(gray, axis=0)
    gradient = np.sqrt(sobel_x**2 + sobel_y**2)

    # Normalize gradient
    gradient = gradient / (gradient.max() + 1e-6)

    # Mask cho các pixel không phải edge (gradient thấp)
    non_edge_mask = gradient < 0.1

    # Xác định checkered pixels
    diff_max = np.maximum(np.maximum(np.abs(r - g), np.abs(g - b)), np.abs(r - b))
    is_gray = diff_max < tolerance

    avg = (r + g + b) / 3
    is_checkered_color = ((avg >= 120) & (avg <= 170)) | ((avg >= 180) & (avg <= 220))

    # Chỉ xóa pixel nếu: là màu xám checkered VÀ không phải edge
    remove_mask = is_gray & is_checkered_color & non_edge_mask

    result[:, :, 3] = np.where(remove_mask, 0, result[:, :, 3])

    return Image.fromarray(result, mode='RGBA')


def flood_fill_background(image, tolerance=30):
    """
    Sử dụng flood fill từ các góc để xóa background.
    Phương pháp này giả định background checkered nằm ở các góc ảnh.
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    arr = np.array(image)
    height, width = arr.shape[:2]

    # Tạo mask để đánh dấu pixel đã xử lý
    visited = np.zeros((height, width), dtype=bool)
    result = arr.copy()

    def get_pixel_value(x, y):
        return tuple(arr[y, x, :3])

    def is_similar_color(c1, c2, tol=tolerance):
        return all(abs(a - b) <= tol for a, b in zip(c1, c2))

    def is_checkered_color_simple(r, g, b):
        """Kiểm tra nhanh xem có phải màu checkered không"""
        r, g, b = int(r), int(g), int(b)
        max_diff = max(abs(r - g), abs(g - b), abs(r - b))
        if max_diff > 20:
            return False
        avg = (r + g + b) // 3
        return (120 <= avg <= 170) or (180 <= avg <= 220)

    # Flood fill từ các góc
    from collections import deque

    corners = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]

    for start_x, start_y in corners:
        if visited[start_y, start_x]:
            continue

        start_color = get_pixel_value(start_x, start_y)
        if not is_checkered_color_simple(*start_color):
            continue

        queue = deque([(start_x, start_y)])

        while queue:
            x, y = queue.popleft()

            if x < 0 or x >= width or y < 0 or y >= height:
                continue
            if visited[y, x]:
                continue

            current_color = get_pixel_value(x, y)

            # Kiểm tra xem có phải checkered không
            if is_checkered_color_simple(*current_color):
                visited[y, x] = True
                result[y, x, 3] = 0  # Set transparent

                # Thêm các pixel lân cận
                queue.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])

    return Image.fromarray(result, mode='RGBA')


def process_accessory_sticker(filepath, output_path=None, method='combined'):
    """
    Xử lý một sticker phụ kiện để xóa checkered background.

    Args:
        filepath: Đường dẫn file sticker
        output_path: Đường dẫn lưu kết quả (None = ghi đè file gốc)
        method: Phương pháp xử lý ('simple', 'edge', 'flood', 'combined')

    Returns:
        bool: True nếu thành công
    """
    try:
        original = Image.open(filepath).convert('RGBA')

        # Kiểm tra xem có checkered background không
        has_checkered = detect_checkered_pattern(original)

        if not has_checkered:
            print(f"  -> Không phát hiện checkered background")
            # Vẫn thử xử lý trong trường hợp detection sai

        if method == 'simple':
            result = remove_checkered_background(original)
        elif method == 'edge':
            try:
                result = remove_checkered_with_edge_detection(original)
            except ImportError:
                print("  -> scipy không khả dụng, dùng phương pháp simple")
                result = remove_checkered_background(original)
        elif method == 'flood':
            result = flood_fill_background(original)
        elif method == 'combined':
            # Kết hợp nhiều phương pháp
            result = remove_checkered_background(original, tolerance=20)
            # Thêm flood fill để xử lý các vùng còn sót
            result = flood_fill_background(result, tolerance=25)
        else:
            result = remove_checkered_background(original)

        # Lưu kết quả
        save_path = output_path or filepath
        result.save(save_path, 'PNG')
        return True

    except Exception as e:
        print(f"  -> Lỗi: {str(e)}")
        return False


def process_main_accessories():
    """Xử lý các file phụ kiện chính trong static/templates/"""
    accessories = ['hat.png', 'glasses.png', 'rabbit_ears.png', 'mustache.png']

    print("=" * 60)
    print("XÓA CHECKERED BACKGROUND TỪ PHỤ KIỆN CHÍNH")
    print("=" * 60)

    # Tạo thư mục processed nếu chưa có
    processed_dir = TEMPLATES_DIR / 'processed'
    processed_dir.mkdir(exist_ok=True)

    for filename in accessories:
        filepath = TEMPLATES_DIR / filename

        if not filepath.exists():
            print(f"❌ Bỏ qua: {filename} (không tồn tại)")
            continue

        print(f"\n📷 Đang xử lý: {filename}")

        # Lưu vào thư mục processed
        output_path = processed_dir / filename

        if process_accessory_sticker(filepath, output_path, method='combined'):
            print(f"  ✅ Đã lưu: {output_path}")
        else:
            print(f"  ❌ Thất bại: {filename}")

    print("\n" + "=" * 60)
    print("HOÀN TẤT!")
    print("=" * 60)


def process_numbered_stickers():
    """Xử lý các sticker đánh số (1.png - 31.png) trong static/templates/stickers/"""
    print("\n" + "=" * 60)
    print("XÓA CHECKERED BACKGROUND TỪ STICKERS 1-31")
    print("=" * 60)

    if not STICKERS_DIR.exists():
        print(f"❌ Thư mục không tồn tại: {STICKERS_DIR}")
        return

    success_count = 0
    fail_count = 0

    for i in range(1, 32):
        filename = f"{i}.png"
        filepath = STICKERS_DIR / filename

        if not filepath.exists():
            print(f"❌ Bỏ qua: {filename} (không tồn tại)")
            continue

        print(f"📷 Đang xử lý: {filename}", end=" ... ")

        if process_accessory_sticker(filepath, method='combined'):
            print("✅ OK")
            success_count += 1
        else:
            print("❌ FAIL")
            fail_count += 1

    print("\n" + "=" * 60)
    print(f"KẾT QUẢ: {success_count} thành công, {fail_count} thất bại")
    print("=" * 60)


def main():
    """Main function"""
    import sys

    print("\n" + "=" * 60)
    print("CÔNG CỤ XÓA CHECKERED BACKGROUND")
    print("=" * 60)

    # Xử lý phụ kiện chính
    process_main_accessories()

    # Hỏi có muốn xử lý stickers 1-31 không
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        process_numbered_stickers()
    else:
        print("\n💡 Tip: Chạy với --all để xử lý cả stickers 1-31")
        print("   python scripts/remove_checkered_background.py --all")


if __name__ == "__main__":
    main()

