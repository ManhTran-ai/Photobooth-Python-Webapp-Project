import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Upload settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///photobooth.db')

    # Folders
    ORIGINALS_FOLDER = os.path.join(UPLOAD_FOLDER, 'originals')
    PROCESSED_FOLDER = os.path.join(UPLOAD_FOLDER, 'processed')
    THUMBNAILS_FOLDER = os.path.join(UPLOAD_FOLDER, 'thumbnails')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}