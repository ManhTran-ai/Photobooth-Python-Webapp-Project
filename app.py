from flask import Flask, render_template, request, jsonify
from config import config
from routes.api import api_bp
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

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    # Basic routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/gallery')
    def gallery():
        return render_template('gallery.html')

    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)
