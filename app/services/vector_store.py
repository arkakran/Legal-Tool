from typing import List, Tuple, Optional, Dict, Any
import faiss
import math
from loguru import logger

from app.utils.embeddings import EmbeddingService

class VectorStore:
    def __init__(self, embedding_service: EmbeddingService, m: int = 32, ef_construction: int = 64):
        self.embedding_service = embedding_service
        self.dimension = embedding_service.dimension
        self.m = m
        self.ef_construction = ef_construction

        self.index: Optional[faiss.IndexHNSWFlat] = None
        self.chunks: List[Dict[str, Any]] = []
        self.doc_id: Optional[str] = None

    def initialize_index(self, doc_id: str, force_new: bool = False):
        if self.index is not None and not force_new:
            logger.warning(f"Index already exists for {doc_id}. Use force_new=True to recreate.")
            return

        try:
            self.index = faiss.IndexHNSWFlat(self.dimension, self.m)
            self.index.hnsw.efConstruction = self.ef_construction
            self.doc_id = doc_id
            self.chunks = []
            logger.info(f"Initialized FAISS index for doc: {doc_id}")

        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
            raise RuntimeError(f"FAISS initialization failed: {e}") from e

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        if not self.index:
            raise RuntimeError("Index not initialized. Call initialize_index() first.")

        texts = [chunk['text'] for chunk in chunks]

        try:
            embeddings = self.embedding_service.encode(texts)
            self.index.add(embeddings)
            self.chunks.extend(chunks)

            logger.info(f"Added {len(chunks)} chunks to vector store")

        except Exception as e:
            logger.error(f"Failed to add chunks: {e}")
            raise

    def search(self, query: str, top_k: int = 60, ef_search: int = 64) -> List[Tuple[Dict[str, Any], float]]:
        if not self.index or not self.chunks:
            logger.warning("No chunks in index")
            return []

        try:
            self.index.hnsw.efSearch = ef_search
            query_embedding = self.embedding_service.encode([query])

            distances, indices = self.index.search(
                query_embedding,
                min(top_k, len(self.chunks))
            )

            results = []

            for dist, idx in zip(distances[0], indices[0]):
                if 0 <= idx < len(self.chunks):
                    chunk = self.chunks[int(idx)].copy()

                    # Sanitize FAISS distance
                    if math.isnan(dist) or math.isinf(dist):
                        dist = 1e6 

                    # Clamp negative distances
                    dist = max(dist, 0.0)

                    # Convert to 0–1 similarity score
                    retrieval_score = 1.0 / (1.0 + dist)

                    # Enforce valid range
                    retrieval_score = max(0.0, min(retrieval_score, 1.0))

                    results.append((chunk, retrieval_score))

            logger.info(f"Retrieved {len(results)} chunks for query")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise RuntimeError(f"Vector search failed: {e}") from e
