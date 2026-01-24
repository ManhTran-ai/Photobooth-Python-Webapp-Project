import os
from PIL import Image
from models.template_engine import TemplateEngine

def test_get_available_templates():
    te = TemplateEngine(output_dir="static/uploads/collages_test")
    templates = te.get_available_templates()
    assert isinstance(templates, dict)
    assert len(templates) > 0
    # ensure keys look like names
    for name, meta in templates.items():
        assert 'layout' in meta
        assert 'size' in meta


def test_get_anchor_points():
    """Test that anchor points are correctly returned for each template"""
    te = TemplateEngine(output_dir="static/uploads/collages_test")

    # Test 2x2 template
    anchors_2x2 = te.get_anchor_points('2x2')
    assert isinstance(anchors_2x2, list)
    assert len(anchors_2x2) >= 10  # At least 10 anchor points
    for point in anchors_2x2:
        assert isinstance(point, tuple)
        assert len(point) == 2
        # Check that coordinates are within canvas bounds (900x940 for 2x2)
        assert 0 <= point[0] <= 900
        assert 0 <= point[1] <= 940

    # Test classic_strip template (4x1)
    anchors_classic = te.get_anchor_points('classic_strip')
    assert isinstance(anchors_classic, list)
    assert len(anchors_classic) >= 10
    for point in anchors_classic:
        assert isinstance(point, tuple)
        assert len(point) == 2
        # Check coordinates within canvas bounds (640x1850 for classic_strip)
        assert 0 <= point[0] <= 640
        assert 0 <= point[1] <= 1850

    # Test 1x4 template
    anchors_1x4 = te.get_anchor_points('1x4')
    assert isinstance(anchors_1x4, list)
    assert len(anchors_1x4) >= 10
    for point in anchors_1x4:
        assert isinstance(point, tuple)
        assert len(point) == 2

    # Test invalid template raises error
    try:
        te.get_anchor_points('nonexistent_template')
        assert False, "Should raise ValueError for invalid template"
    except ValueError as e:
        assert "not found" in str(e)


def test_remove_sticker_background():
    """Test background removal from stickers"""
    te = TemplateEngine(output_dir="static/uploads/collages_test")

    # Create a test image with a colored background (simulating a sticker with background)
    test_image = Image.new('RGB', (100, 100), (255, 255, 255))

    # Test the background removal function
    result = te._remove_sticker_background(test_image)

    # Result should be RGBA for transparency
    assert result is not None
    assert result.mode == 'RGBA'


def test_place_stickers_with_anchors():
    """Test sticker placement using anchor points"""
    te = TemplateEngine(output_dir="static/uploads/collages_test")

    # Create a test canvas for 2x2 template
    canvas = Image.new('RGBA', (900, 940), (255, 255, 255, 255))

    # Find an existing sticker file
    stickers_dir = os.path.join("static", "templates", "stickers")
    sticker_files = []
    if os.path.exists(stickers_dir):
        for f in os.listdir(stickers_dir):
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                sticker_files.append(os.path.join(stickers_dir, f))

    if not sticker_files:
        # Skip test if no stickers found
        return

    # Test placing stickers with anchor points (with background removal)
    result = te.place_stickers_with_anchors(
        canvas.copy(),
        sticker_files,
        '2x2',
        num_stickers=5,
        rotation_range=(0, 360),
        scale_range=(0.8, 1.2),
        remove_background=True
    )

    assert result is not None
    assert result.size == canvas.size
    assert result.mode == canvas.mode


def test_place_stickers_without_background_removal():
    """Test sticker placement without background removal"""
    te = TemplateEngine(output_dir="static/uploads/collages_test")

    # Create a test canvas for 2x2 template
    canvas = Image.new('RGBA', (900, 940), (255, 255, 255, 255))

    # Find an existing sticker file
    stickers_dir = os.path.join("static", "templates", "stickers")
    sticker_files = []
    if os.path.exists(stickers_dir):
        for f in os.listdir(stickers_dir):
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                sticker_files.append(os.path.join(stickers_dir, f))

    if not sticker_files:
        # Skip test if no stickers found
        return

    # Test placing stickers without background removal
    result = te.place_stickers_with_anchors(
        canvas.copy(),
        sticker_files,
        '2x2',
        num_stickers=5,
        rotation_range=(0, 360),
        scale_range=(0.8, 1.2),
        remove_background=False
    )

    assert result is not None
    assert result.size == canvas.size
    assert result.mode == canvas.mode


def test_place_stickers_with_anchors_empty_stickers():
    """Test that empty sticker paths returns original canvas unchanged"""
    te = TemplateEngine(output_dir="static/uploads/collages_test")
    canvas = Image.new('RGBA', (900, 940), (255, 255, 255, 255))

    # Test with empty sticker list
    result = te.place_stickers_with_anchors(
        canvas.copy(),
        [],
        '2x2',
        num_stickers=5
    )
    assert result is not None
    assert result.size == canvas.size


def test_place_stickers_with_anchors_template_without_anchors():
    """Test template without anchor_points returns canvas unchanged"""
    te = TemplateEngine(output_dir="static/uploads/collages_test")
    canvas = Image.new('RGBA', (900, 940), (255, 255, 255, 255))

    # grid_modern doesn't have anchor_points defined
    result = te.place_stickers_with_anchors(
        canvas.copy(),
        ["static/templates/stickers/1.png"],
        'grid_modern',
        num_stickers=5
    )
    # Should return original canvas unchanged
    assert result is not None
    assert result.size == canvas.size


def test_create_collage_with_anchor_mode():
    """Test create_collage with anchor_mode enabled"""
    te = TemplateEngine(output_dir="static/uploads/collages_test")

    # Find existing sticker files
    stickers_dir = os.path.join("static", "templates", "stickers")
    sticker_files = []
    if os.path.exists(stickers_dir):
        for f in os.listdir(stickers_dir):
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                sticker_files.append(os.path.join(stickers_dir, f))

    # Create dummy images for collage
    dummy_image = Image.new('RGB', (540, 400), (200, 200, 200))
    dummy_path = "static/uploads/collages_test/dummy_test.jpg"
    os.makedirs(os.path.dirname(dummy_path), exist_ok=True)
    dummy_image.save(dummy_path, 'JPEG')

    try:
        # Test create_collage with anchor_mode
        output = te.create_collage(
            [dummy_path] * 4,  # 4 images for 4x1 template
            'classic_strip',
            sticker_paths=sticker_files if sticker_files else None,
            anchor_mode=True
        )

        assert output is not None
        assert os.path.exists(output)

        # Verify output is a valid image
        with Image.open(output) as result_img:
            assert result_img.size[0] == 640  # classic_strip width
            assert result_img.size[1] == 1850  # classic_strip height
    finally:
        # Cleanup
        if os.path.exists(dummy_path):
            os.remove(dummy_path)


def test_anchor_points_distribution():
    """Test that anchor points are distributed on borders and around photo corners"""
    te = TemplateEngine(output_dir="static/uploads/collages_test")

    # For 2x2 template (900x940)
    anchors = te.get_anchor_points('2x2')

    # Check that some points are on the edges (x near 0 or max, y near 0 or max)
    edge_points = [p for p in anchors if p[0] <= 60 or p[0] >= 840 or p[1] <= 60 or p[1] >= 880]
    corner_points = [p for p in anchors if (p[0] <= 60 and p[1] <= 60) or
                                          (p[0] >= 840 and p[1] <= 60) or
                                          (p[0] <= 60 and p[1] >= 880) or
                                          (p[0] >= 840 and p[1] >= 880)]

    # At least 30% of points should be on edges
    assert len(edge_points) >= len(anchors) * 0.3, "Not enough anchor points on edges"

    # At least some points should be at corners
    assert len(corner_points) >= 4, "Not enough anchor points at corners"
