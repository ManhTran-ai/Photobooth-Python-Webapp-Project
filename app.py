from flask import Flask, render_template, request, jsonify
from config import config
import os


def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure upload folders exist
    for folder in [app.config['ORIGINALS_FOLDER'],
                   app.config['PROCESSED_FOLDER'],
                   app.config['THUMBNAILS_FOLDER']]:
        os.makedirs(folder, exist_ok=True)

    # Basic routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/gallery')
    def gallery():
        return render_template('gallery.html')

    # API routes
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'ok', 'message': 'Photobooth API is running'})

    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)
