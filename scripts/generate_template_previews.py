#!/usr/bin/env python3
"""
Generate preview thumbnails for templates located in static/templates/assets/

Usage: python scripts/generate_template_previews.py
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(ROOT, 'static', 'templates', 'assets')
PREVIEWS_DIR = os.path.join(ROOT, 'static', 'templates', 'previews')

os.makedirs(PREVIEWS_DIR, exist_ok=True)

def make_preview(src_path, dest_path, width=320):
    with Image.open(src_path) as im:
        w, h = im.size
        ratio = width / float(w)
        new_h = int(h * ratio)
        im = im.resize((width, new_h), Image.LANCZOS)
        im.save(dest_path, 'PNG')

def main():
    for fname in os.listdir(ASSETS_DIR):
        if not fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
        src = os.path.join(ASSETS_DIR, fname)
        name, _ = os.path.splitext(fname)
        dest = os.path.join(PREVIEWS_DIR, f"{name.replace(' ', '_').lower()}_preview.png")
        try:
            make_preview(src, dest)
            print('Generated', dest)
        except Exception as e:
            print('Failed for', src, e)

if __name__ == '__main__':
    main()


