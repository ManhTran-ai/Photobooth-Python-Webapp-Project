"""
View routes for photobooth application
"""
from flask import Blueprint, render_template, request

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
    return render_template('session.html', session_id=session_id)

