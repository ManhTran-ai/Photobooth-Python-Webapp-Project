import os
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


