"""
View routes for photobooth application
"""
from flask import Blueprint, render_template, request, current_app, url_for
import os

views_bp = Blueprint('views', __name__)


@views_bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@views_bp.route('/capture')
def capture():
    """Camera capture interface"""
    return render_template('capture.html')


@views_bp.route('/gallery')
def gallery():
    """Photo gallery"""
    return render_template('gallery.html')


@views_bp.route('/session/<session_id>')
def session_view(session_id):
    """Individual session view for filter selection"""
    # collect sticker filenames from static/templates/stickers
    stickers_dir = os.path.join(current_app.static_folder, 'templates', 'stickers')
    stickers = []
    try:
        if os.path.exists(stickers_dir):
            for fname in sorted(os.listdir(stickers_dir)):
                if fname.lower().endswith(('.png', '.svg', '.webp', '.jpg', '.jpeg')):
                    # exclude some stickers that should not appear as buttons (e.g. heart/start)
                    excluded_names = {'heart.svg', 'start.svg', 'star.svg'}
                    if fname.lower() in excluded_names:
                        continue
                    # use forward-slash path for URL building so url_for generates valid static URLs
                    file_path = f"templates/stickers/{fname}"
                    stickers.append(url_for('static', filename=file_path))
    except Exception:
        stickers = []

    return render_template('session.html', session_id=session_id, stickers=stickers)

