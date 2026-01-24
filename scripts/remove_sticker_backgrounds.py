"""
Script xoa nen translucence khoi tat ca sticker PNG.
Su dung rembg va Pillow de xu ly.
"""
from PIL import Image
import rembg
import io
from pathlib import Path

# Duong dan thu muc stickers
STICKERS_DIR = Path("static/templates/stickers")

def remove_background(image):
    """Xoa nen su dung rembg voi post-processing."""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    input_bytes = buffer.getvalue()
    
    # Su dung rembg
    output_bytes = rembg.remove(input_bytes)
    result = Image.open(io.BytesIO(output_bytes))
    
    # Dam bao RGBA
    if result.mode != 'RGBA':
        result = result.convert('RGBA')
    
    # Post-processing: loai bo nen mo con sot lai
    result = clean_alpha_channel(result, alpha_threshold=10)
    
    return result

def clean_alpha_channel(image, alpha_threshold=10):
    """Loai bo pixel co alpha thap."""
    import numpy as np
    if image.mode != 'RGBA':
        return image
    
    arr = np.array(image)
    alpha = arr[:, :, 3]
    mask = alpha < alpha_threshold
    arr[:, :, 3] = np.where(mask, 0, alpha)
    return Image.fromarray(arr, mode='RGBA')

def process_all_stickers():
    """Xu ly tat ca 31 stickers."""
    print(f"Thu muc stickers: {STICKERS_DIR}")
    print(f"Tong so stickers: 31")
    print("-" * 50)
    
    for i in range(1, 32):
        filename = f"{i}.png"
        filepath = STICKERS_DIR / filename
        
        if not filepath.exists():
            print(f"Bo qua: {filename} (khong ton tai)")
            continue
            
        try:
            # Mo anh goc
            original = Image.open(filepath).convert("RGBA")
            
            # Xoa nen
            cleaned = remove_background(original)
            
            # Ghi de file goc
            cleaned.save(filepath, "PNG", quality=100)
            print(f"OK: {filename} - Da xoa nen translucent")
            
        except Exception as e:
            print(f"LOI: {filename} - {str(e)}")
    
    print("-" * 50)
    print("Hoan tat!")

if __name__ == "__main__":
    process_all_stickers()
