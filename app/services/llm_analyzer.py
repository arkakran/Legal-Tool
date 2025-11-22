from typing import List, Dict, Any, Tuple
from loguru import logger

from app.models.schemas import ExtractedPoint, LLMAnalysisOutput, Stance, ArgumentCategory
from app.utils.helpers import parse_json_response

try:
    from langchain_groq import ChatGroq
    _HAS_CHATGROQ = True
except Exception:
    _HAS_CHATGROQ = False
    ChatGroq = None


class LLMAnalyzer:
    """Extracts legal arguments from retrieved chunks using LLM."""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile", temperature: float = 0.0):
        self.model = model
        self.temperature = temperature

        if not _HAS_CHATGROQ:
            logger.warning(
                "langchain_groq not available. Running in NO-LLM mode. "
                "Install with: pip install langchain-groq"
            )
            self.llm = None
            return

        try:
            self.llm = ChatGroq(
                model=model,
                groq_api_key=api_key,
                temperature=temperature
            )
            logger.info(f"LLM Analyzer initialized with model: {model}")
        except Exception as e:
            logger.error(f"Failed to initialize ChatGroq: {e}")
            self.llm = None

    def analyze_chunks(self, chunks_with_scores: List[Tuple[Dict[str, Any], float]], max_chunks: int = 30) -> LLMAnalysisOutput:
        """Return extracted points or fallback gracefully if LLM unavailable."""

        # Fallback when LLM is missing
        if self.llm is None:
            logger.warning("LLM unavailable — returning fallback empty analysis result")
            return LLMAnalysisOutput(extracted_points=[], confidence=0.0)

        chunks_to_analyze = chunks_with_scores[:max_chunks]
        context = self._prepare_context(chunks_to_analyze)
        prompt = self._create_extraction_prompt(context)

        try:
            response = self.llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            parsed_data = parse_json_response(response_text)

            if not parsed_data:
                logger.error("Failed to parse LLM response as JSON")
                return LLMAnalysisOutput(extracted_points=[], confidence=0.0)

            extracted_points = []
            points_data = parsed_data.get('arguments', []) or parsed_data.get('extracted_points', [])

            for i, point_data in enumerate(points_data):
                try:
                    retrieval_score = chunks_to_analyze[i][1] if i < len(chunks_to_analyze) else 0.5
                    point_data['retrieval_score'] = retrieval_score

                    stance_str = point_data.get('stance', 'unknown')
                    try:
                        stance = Stance(stance_str.lower())
                    except ValueError:
                        stance = Stance.UNKNOWN

                    category_str = point_data.get('category', 'other')
                    try:
                        category = ArgumentCategory(category_str.lower())
                    except ValueError:
                        category = ArgumentCategory.OTHER

                    point = ExtractedPoint(
                        summary=point_data.get('summary', point_data.get('argument', '')),
                        importance=point_data.get('importance'),
                        importance_score=float(point_data.get('importance_score', 0.5)),
                        stance=stance,
                        supporting_quote=point_data.get('supporting_quote'),
                        legal_concepts=point_data.get('legal_concepts', []),
                        page_start=point_data.get('page_start') or point_data.get('page_number'),
                        page_end=point_data.get('page_end'),
                        category=category,
                        retrieval_score=retrieval_score
                    )
                    extracted_points.append(point)

                except Exception as e:
                    logger.warning(f"Failed to parse point {i}: {e}")
                    continue

            confidence = float(parsed_data.get('confidence', 0.8))

            logger.info(f"Extracted {len(extracted_points)} legal arguments")
            return LLMAnalysisOutput(extracted_points=extracted_points, confidence=confidence)

        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return LLMAnalysisOutput(extracted_points=[], confidence=0.0)

    @staticmethod
    def _prepare_context(chunks_with_scores: List[Tuple[Dict[str, Any], float]]) -> str:
        context_parts = []
        for i, (chunk, _) in enumerate(chunks_with_scores, 1):
            text = chunk['text']
            page = chunk['metadata'].get('page_number', '?')
            context_parts.append(f"[Chunk {i}, Page {page}]:\n{text}\n")
        return "\n".join(context_parts)

    @staticmethod
    def _create_extraction_prompt(context: str) -> str:
        return f"""You are a Supreme Court-level legal analyst. Analyze the legal document excerpts and extract key legal arguments.
                For each argument, provide:
                1. summary: Clear, concise summary of the legal argument (1-2 sentences)
                2. importance: Brief explanation of why this argument matters
                3. importance_score: Float between 0.0-1.0 indicating importance
                4. stance: Identify the document's position/filer:
                   - "amicus" = Amicus curiae brief (friend of court supporting a party)
                   - "plaintiff" = Document filed BY the plaintiff themselves
                   - "defendant" = Document filed BY the defendant themselves
                   - "for" = Document argues FOR/supports a specific position or action
                   - "against" = Document argues AGAINST/opposes a specific position or action
                   - "neutral" = Objective analysis (court opinion, academic paper, neutral brief)

                   CRITICAL: Look at document title/header first to identify the actual filer!
                   Example: "Amicus Brief on Behalf of..." = stance is "amicus"

                5. supporting_quote: Exact quote from text that supports this argument
                6. legal_concepts: List of legal concepts/doctrines mentioned (e.g., ["federalism", "due process", "precedent"])
                7. page_start: Page number where this argument appears
                8. category: Type of argument (statutory/constitutional/case_law/procedural/policy/other)

                DOCUMENT EXCERPTS:
                {context}

                Respond with ONLY valid JSON in this exact format:
                {{
                  "arguments": [
                    {{
                      "summary": "Clear summary of the legal argument",
                      "importance": "Why this argument is significant",
                      "importance_score": 0.85,
                      "stance": "amicus",
                      "supporting_quote": "Exact quote from the document text",
                      "legal_concepts": ["federalism", "state sovereignty"],
                      "page_start": 7,
                      "category": "constitutional"
                    }}
                  ],
                  "confidence": 0.9
                }}

                Extract 5-10 most important legal arguments. Return ONLY valid JSON, no other text."""
