from typing import List, Optional, Tuple
from rapidfuzz import fuzz
from loguru import logger

from app.models.schemas import ExtractedPoint, FinalKeyPoint

class PostProcessor:
    # Post-process and rank extracted arguments.

    def __init__(self, top_k: int = 10):
        self.top_k = top_k

    def process_and_rank(self, extracted_points: List[ExtractedPoint], chunks: List[dict]) -> List[FinalKeyPoint]:
        # Process extracted points and create final ranked list.

        final_points = []

        for point in extracted_points:
            retrieval_score = point.retrieval_score or 0.5
            importance_score = point.importance_score or 0.5

            # Enhanced quote matching (now used!)
            quote = point.supporting_quote or point.summary
            best_chunk, match_confidence = self._find_best_matching_chunk(
                quote,
                chunks,
                point.page_start
            )

            # If we found a better page location, update metadata
            if best_chunk:
                point.page_start = best_chunk.get("metadata", {}).get("page_number", point.page_start)

            # NEW: incorporate match confidence into scoring
            # match_confidence = 0.0–1.0
            # helps penalize hallucinated arguments
            combined_score = (
                0.5 * importance_score +
                0.3 * retrieval_score +
                0.2 * match_confidence
            )

            final_point = FinalKeyPoint(
                summary=point.summary,
                importance=point.importance,
                importance_score=importance_score,
                stance=point.stance,
                supporting_quote=quote,
                legal_concepts=point.legal_concepts,
                page_start=point.page_start,
                page_end=point.page_end,
                line_start=point.line_start,
                line_end=point.line_end,
                category=point.category,
                retrieval_score=retrieval_score,
                combined_score=combined_score,
                final_rank=1
            )

            final_points.append(final_point)

        # Sort by combined score (descending)
        final_points.sort(key=lambda x: x.combined_score, reverse=True)

        # Limit to top_k
        final_points = final_points[:self.top_k]

        # Assign final ranks
        for i, point in enumerate(final_points, 1):
            point.final_rank = i

        logger.info(f"Processed and ranked {len(final_points)} final key points")
        return final_points

    @staticmethod
    def _find_best_matching_chunk(quote: str, chunks: List[dict], expected_page: Optional[int]) -> Tuple[Optional[dict], float]:
        # Find chunk that best matches the quote.

        if not quote or not chunks:
            return None, 0.0

        best_match = None
        best_score = 0.0

        # Filter chunks by page if available
        candidate_chunks = chunks
        if expected_page:
            candidate_chunks = [
                c for c in chunks
                if c.get('metadata', {}).get('page_number') == expected_page
            ]
            if not candidate_chunks:
                candidate_chunks = chunks

        # Find best matching chunk using fuzzy matching
        for chunk in candidate_chunks:
            chunk_text = chunk.get('text', '')
            score = fuzz.token_set_ratio(quote.lower(), chunk_text.lower()) / 100.0

            if score > best_score:
                best_score = score
                best_match = chunk

        logger.debug(f"Quote match confidence: {best_score:.2f}")

        return best_match, best_score
