from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class DocumentType(str, Enum):
    """Document type classification."""
    BRIEF = "brief"
    MOTION = "motion"
    OPINION = "opinion"
    PLEADING = "pleading"
    AMICUS_BRIEF = "amicus_brief"
    OTHER = "other"


class Stance(str, Enum):
    """Argument stance classification."""
    PLAINTIFF = "plaintiff"
    DEFENDANT = "defendant"
    AMICUS = "amicus"
    FOR = "for"
    AGAINST = "against"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


class ArgumentCategory(str, Enum):
    """Legal argument category."""
    STATUTORY = "statutory"
    REGULATORY = "regulatory"
    CONSTITUTIONAL = "constitutional"
    CASE_LAW = "case_law"
    PROCEDURAL = "procedural"
    POLICY = "policy"
    OTHER = "other"


class ExtractedPoint(BaseModel):
    """Single legal argument extracted by LLM."""
    summary: str = Field(..., min_length=5)
    importance: Optional[str] = None
    importance_score: float = Field(..., ge=0.0, le=1.0)
    stance: Stance = Field(default=Stance.NEUTRAL)
    supporting_quote: Optional[str] = None
    legal_concepts: List[str] = Field(default_factory=list)

    page_start: Optional[int] = Field(None, ge=1)
    page_end: Optional[int] = Field(None, ge=1)
    line_start: Optional[int] = None
    line_end: Optional[int] = None

    category: Optional[ArgumentCategory] = None

    retrieval_score: Optional[float] = Field(None, ge=0.0)
    combined_score: Optional[float] = Field(None, ge=0.0)


class FinalKeyPoint(ExtractedPoint):
    """Final ranked key point with ranking."""
    final_rank: int = Field(..., ge=1)


class LLMAnalysisOutput(BaseModel):
    """Output from LLM analysis."""
    extracted_points: List[ExtractedPoint]
    confidence: float = Field(..., ge=0.0, le=1.0)
