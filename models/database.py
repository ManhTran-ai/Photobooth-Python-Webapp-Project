"""
Database models and initialization for photobooth application
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()


class Session(db.Model):
    """Session model - represents a 4-photo capture session"""
    __tablename__ = 'sessions'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='capturing')  # capturing, filtering, completed
    
    # Relationships
    photos = db.relationship('Photo', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'photo_count': len(self.photos)
        }


class Photo(db.Model):
    """Photo model - represents a single captured photo"""
    __tablename__ = 'photos'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('sessions.id'), nullable=False)
    photo_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3, or 4
    original_filename = db.Column(db.String(255), nullable=False)
    processed_filename = db.Column(db.String(255), nullable=True)
    thumbnail_filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Filter information
    applied_filter = db.Column(db.String(50), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'photo_number': self.photo_number,
            'original_filename': self.original_filename,
            'processed_filename': self.processed_filename,
            'thumbnail_filename': self.thumbnail_filename,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'applied_filter': self.applied_filter
        }


class FilterApplied(db.Model):
    """Track filter applications to sessions"""
    __tablename__ = 'filters_applied'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('sessions.id'), nullable=False)
    filter_name = db.Column(db.String(50), nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    session = db.relationship('Session', backref='filter_history')

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'filter_name': self.filter_name,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None
        }


class User(db.Model):
    """User model for face recognition - stores user profile information"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False, unique=True)  # e.g., "user_123" or "john_doe"
    display_name = db.Column(db.String(255), nullable=True)  # Optional human-readable name
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = db.Column(db.DateTime, nullable=True)

    # Metadata
    age_range = db.Column(db.String(20), nullable=True)  # e.g., "25-34"
    gender = db.Column(db.String(10), nullable=True)     # male/female/other

    # Relationships
    embeddings = db.relationship('FaceEmbedding', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'label': self.label,
            'display_name': self.display_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'age_range': self.age_range,
            'gender': self.gender,
            'embedding_count': len(self.embeddings)
        }


class FaceEmbedding(db.Model):
    """Face embedding vectors for recognition"""
    __tablename__ = 'face_embeddings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    embedding_vector = db.Column(db.LargeBinary, nullable=False)  # Serialized numpy array
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Quality metrics
    confidence = db.Column(db.Float, nullable=True)  # Face detection confidence
    image_hash = db.Column(db.String(64), nullable=True)  # To avoid duplicate embeddings

    # Relationships are defined in User model with backref

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'confidence': self.confidence,
            'image_hash': self.image_hash
        }


def init_db(app):
    """
    Initialize database with tables
    """
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

