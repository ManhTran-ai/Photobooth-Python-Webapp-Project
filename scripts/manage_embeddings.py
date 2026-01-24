#!/usr/bin/env python3
"""
CLI tool for managing face embeddings and models.

Usage:
    python manage_embeddings.py rebuild-index
    python manage_embeddings.py export-onnx
    python manage_embeddings.py stats
    python manage_embeddings.py cleanup
"""

import sys
import os
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.model_manager import get_model_manager
from models.embedding_index import get_embedding_index
from models.database import db, User, FaceEmbedding
from app import create_app


def rebuild_index():
    """Rebuild the Annoy index from database embeddings"""
    print("Rebuilding embedding index...")

    app = create_app()
    with app.app_context():
        # Get all embeddings from database
        embeddings_data = []
        embedding_records = FaceEmbedding.query.all()

        print(f"Found {len(embedding_records)} embeddings in database")

        for record in embedding_records:
            embeddings_data.append({
                'user_id': record.user_id,
                'embedding_vector': record.embedding_vector
            })

        # Rebuild index
        index = get_embedding_index()
        index.load_or_create_index(embeddings_data)

        print(f"Index rebuilt with {len(embeddings_data)} embeddings")


def export_onnx():
    """Export FaceNet model to ONNX format"""
    print("Exporting FaceNet model to ONNX...")

    try:
        model_manager = get_model_manager()
        onnx_path = model_manager.embedding_model.export_to_onnx()
        print(f"Model exported to: {onnx_path}")

        # Test ONNX model
        print("Testing ONNX model...")
        model_manager.embedding_model.load_onnx_model(onnx_path)
        print("ONNX model loaded successfully")

    except Exception as e:
        print(f"Failed to export ONNX model: {e}")
        sys.exit(1)


def show_stats():
    """Show statistics about embeddings and users"""
    app = create_app()
    with app.app_context():
        user_count = User.query.count()
        embedding_count = FaceEmbedding.query.count()
        index = get_embedding_index()

        # Load index to get stats
        try:
            if index.index is None:
                print("Index not loaded - run rebuild-index first")
                return

            index_user_count = index.get_user_count()
            index_embedding_count = index.get_embedding_count()

            print("=== Embedding Statistics ===")
            print(f"Database Users: {user_count}")
            print(f"Database Embeddings: {embedding_count}")
            print(f"Index Users: {index_user_count}")
            print(f"Index Embeddings: {index_embedding_count}")

        except Exception as e:
            print(f"Error loading index: {e}")


def cleanup():
    """Clean up orphaned embeddings and optimize database"""
    app = create_app()
    with app.app_context():
        print("Cleaning up orphaned embeddings...")

        # Find embeddings without users
        orphaned = FaceEmbedding.query.filter(
            ~FaceEmbedding.user_id.in_(
                db.session.query(User.id).subquery()
            )
        ).all()

        if orphaned:
            print(f"Found {len(orphaned)} orphaned embeddings")
            for emb in orphaned:
                db.session.delete(emb)
            db.session.commit()
            print("Orphaned embeddings removed")
        else:
            print("No orphaned embeddings found")

        # Rebuild index after cleanup
        rebuild_index()


def main():
    parser = argparse.ArgumentParser(description='Manage face embeddings and models')
    parser.add_argument('command', choices=['rebuild-index', 'export-onnx', 'stats', 'cleanup'],
                       help='Command to execute')

    args = parser.parse_args()

    if args.command == 'rebuild-index':
        rebuild_index()
    elif args.command == 'export-onnx':
        export_onnx()
    elif args.command == 'stats':
        show_stats()
    elif args.command == 'cleanup':
        cleanup()


if __name__ == '__main__':
    main()