from typing import Dict, Any, List
from loguru import logger

class MetadataExtractor:
    # Extract metadata from document.

    @staticmethod
    def extract_metadata(chunks: List[Dict[str, Any]], doc_name: str) -> Dict[str, Any]:
        # Extract basic metadata from chunks.
        if not chunks:
            return {}

        first_chunk_meta = chunks[0].get('metadata', {})

        metadata = {
            'document_name': doc_name,
            'total_pages': first_chunk_meta.get('total_pages', 0),
            'total_chunks': len(chunks),
            'document_id': first_chunk_meta.get('document_id', ''),
        }

        logger.info(f"Extracted metadata: {metadata['total_chunks']} chunks, {metadata['total_pages']} pages")
        return metadata
