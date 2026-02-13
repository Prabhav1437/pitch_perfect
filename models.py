"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any


class EvaluationScores(BaseModel):
    """Individual evaluation scores."""
    relevance: float = Field(..., ge=0, le=10, description="Relevance to problem statement")
    clarity: float = Field(..., ge=0, le=10, description="Clarity of explanation")
    technical_accuracy: float = Field(..., ge=0, le=10, description="Technical correctness")
    structure: float = Field(..., ge=0, le=10, description="Logical structure and flow")
    completeness: float = Field(..., ge=0, le=10, description="Completeness of solution")


class EvaluationMetadata(BaseModel):
    """Metadata about the evaluation."""
    slide_count: int
    semantic_relevance_score: float
    llm_relevance_score: float
    adjusted_relevance_score: float


class DetailedAnalysis(BaseModel):
    """Deep dive analysis per category."""
    technical_depth: str
    business_viability: str
    presentation_flow: str

class EvaluationResponse(BaseModel):
    """Complete evaluation response matching required schema."""
    scores: EvaluationScores
    overall_score: float = Field(..., ge=0, le=50, description="Sum of all scores")
    strengths: List[str] = Field(..., min_items=1, description="List of strengths")
    weaknesses: List[str] = Field(..., min_items=1, description="List of weaknesses")
    detailed_analysis: DetailedAnalysis = Field(..., description="Deep dive analysis")
    missing_elements: List[str] = Field(..., description="Missing key elements")
    summary_evaluation: str = Field(..., min_length=10, description="Overall assessment")
    metadata: Optional[EvaluationMetadata] = Field(None, description="Additional metadata")
    presentation_summary: Optional[str] = Field(None, description="Raw summary of the presentation content")
    
    @validator('overall_score', always=True)
    def validate_overall_score(cls, v, values):
        """Ensure overall score matches sum of individual scores."""
        if 'scores' in values:
            expected = sum([
                values['scores'].relevance,
                values['scores'].clarity,
                values['scores'].technical_accuracy,
                values['scores'].structure,
                values['scores'].completeness
            ])
            # Allow small floating point differences
            if abs(v - expected) > 0.1:
                return expected
        return v


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    device_info: Dict[str, Any]
    models_loaded: Dict[str, bool]


class ReconstructionRequest(BaseModel):
    """Request for initial PPT reconstruction."""
    presentation_summary: str
    problem_statement: str
    analysis: Dict[str, Any]
    custom_instructions: Optional[str] = None


class ReconstructionChatRequest(BaseModel):
    """Request for refining the PPT based on chat."""
    current_structure: Dict[str, Any]
    user_message: str
    presentation_summary: str


class ReconstructionResponse(BaseModel):
    """Response with new PPT structure and download link."""
    structure: Dict[str, Any]
    file_path: str
    download_url: str
