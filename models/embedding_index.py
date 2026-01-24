"""
EmbeddingIndex: Annoy-based approximate nearest neighbor search for face embeddings
"""

import os
import numpy as np
from typing import List, Tuple, Dict, Optional

try:
    from annoy import AnnoyIndex
    _HAS_ANNOY = True
except ImportError:
    _HAS_ANNOY = False


class EmbeddingIndex:
    """Annoy-based index for fast face embedding search"""

    def __init__(self, embedding_dim: int = 128, index_path: str = None):
        if not _HAS_ANNOY:
            raise ImportError("Annoy not available. Install with: pip install annoy")

        self.embedding_dim = embedding_dim
        self.index_path = index_path or os.path.join(os.path.dirname(__file__), 'embeddings.ann')

        # Index will be loaded/created lazily
        self.index = None
        self.id_to_user_id = {}  # Maps annoy_id to user_id
        self.user_id_to_ids = {}  # Maps user_id to list of annoy_ids

    def load_or_create_index(self, embeddings_data: List[Dict] = None):
        """
        Load existing index or create new one from embeddings data

        Args:
            embeddings_data: List of dicts with 'user_id' and 'embedding_vector'
        """
        if os.path.exists(self.index_path):
            self._load_index()
        elif embeddings_data:
            self._build_index(embeddings_data)
        else:
            # Create empty index
            self.index = AnnoyIndex(self.embedding_dim, 'angular')
            self.id_to_user_id = {}
            self.user_id_to_ids = {}

    def _load_index(self):
        """Load existing Annoy index and mappings"""
        self.index = AnnoyIndex(self.embedding_dim, 'angular')
        self.index.load(self.index_path)

        # Load mappings (you might want to store these separately in a JSON file)
        mapping_path = self.index_path + '.mapping'
        if os.path.exists(mapping_path):
            import json
            with open(mapping_path, 'r') as f:
                mapping = json.load(f)
                self.id_to_user_id = mapping.get('id_to_user_id', {})
                self.user_id_to_ids = mapping.get('user_id_to_ids', {})

    def _build_index(self, embeddings_data: List[Dict]):
        """Build new index from embeddings data"""
        self.index = AnnoyIndex(self.embedding_dim, 'angular')
        self.id_to_user_id = {}
        self.user_id_to_ids = {}

        for i, data in enumerate(embeddings_data):
            user_id = data['user_id']
            embedding = data['embedding_vector']

            # Add to index
            self.index.add_item(i, embedding)
            self.id_to_user_id[i] = user_id

            # Update reverse mapping
            if user_id not in self.user_id_to_ids:
                self.user_id_to_ids[user_id] = []
            self.user_id_to_ids[user_id].append(i)

        # Build index with 10 trees (balance between speed and accuracy)
        self.index.build(10)
        self._save_index()

    def _save_index(self):
        """Save index and mappings"""
        if self.index:
            self.index.save(self.index_path)

            # Save mappings
            mapping_path = self.index_path + '.mapping'
            import json
            mapping = {
                'id_to_user_id': self.id_to_user_id,
                'user_id_to_ids': self.user_id_to_ids
            }
            with open(mapping_path, 'w') as f:
                json.dump(mapping, f)

    def add_embedding(self, user_id: int, embedding: np.ndarray):
        """Add new embedding to index"""
        if self.index is None:
            self.index = AnnoyIndex(self.embedding_dim, 'angular')

        # Find next available ID
        next_id = len(self.id_to_user_id)

        self.index.add_item(next_id, embedding)
        self.id_to_user_id[next_id] = user_id

        if user_id not in self.user_id_to_ids:
            self.user_id_to_ids[user_id] = []
        self.user_id_to_ids[user_id].append(next_id)

        # Rebuild index incrementally (in production, you might want to rebuild periodically)
        self.index.build(10)
        self._save_index()

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Search for similar embeddings

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of (user_id, distance) tuples
        """
        if self.index is None:
            return []

        # Get nearest neighbors
        annoy_ids, distances = self.index.get_nns_by_vector(query_embedding, top_k, include_distances=True)

        results = []
        for annoy_id, distance in zip(annoy_ids, distances):
            user_id = self.id_to_user_id.get(annoy_id)
            if user_id is not None:
                results.append((user_id, distance))

        return results

    def remove_user(self, user_id: int):
        """Remove all embeddings for a user (requires full rebuild)"""
        if user_id in self.user_id_to_ids:
            # Remove from mappings
            annoy_ids = self.user_id_to_ids[user_id]
            for annoy_id in annoy_ids:
                if annoy_id in self.id_to_user_id:
                    del self.id_to_user_id[annoy_id]
            del self.user_id_to_ids[user_id]

            # Note: Annoy doesn't support item removal, so we'd need to rebuild
            # For now, just update mappings and rebuild when needed
            self._save_index()

    def get_user_count(self) -> int:
        """Get number of unique users in index"""
        return len(self.user_id_to_ids)

    def get_embedding_count(self) -> int:
        """Get total number of embeddings in index"""
        return len(self.id_to_user_id)


# Singleton instance
_embedding_index = None

def get_embedding_index() -> EmbeddingIndex:
    """Get singleton EmbeddingIndex instance"""
    global _embedding_index
    if _embedding_index is None:
        _embedding_index = EmbeddingIndex()
    return _embedding_index