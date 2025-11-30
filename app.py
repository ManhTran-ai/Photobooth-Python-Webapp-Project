from flask import Flask, render_template, request, jsonify
from config import config
from routes.api import api_bp
from routes.views import views_bp
from models.database import db, init_db
import os


def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Initialize database tables
    init_db(app)

    # Ensure upload folders exist
    for folder in [app.config['ORIGINALS_FOLDER'],
                   app.config['PROCESSED_FOLDER'],
                   app.config['THUMBNAILS_FOLDER'],
                   app.config['COLLAGES_FOLDER']]:
        os.makedirs(folder, exist_ok=True)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(views_bp)

    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)
