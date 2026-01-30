"""
Configuration settings for the AI Presentation Evaluation System.
"""
import torch
from pathlib import Path

class Config:
    """Centralized configuration for the evaluation system."""
    
    # Model Configuration
    SUMMARIZATION_MODEL = "facebook/bart-large-cnn"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
    
    # Fallback model for CPU-only environments
    LLM_MODEL_FALLBACK = "google/flan-t5-base"
    
    # Device Configuration
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    USE_8BIT = True if DEVICE == "cuda" else False  # 8-bit quantization for GPU
    
    # Model Parameters
    SUMMARIZATION_MAX_LENGTH = 130
    SUMMARIZATION_MIN_LENGTH = 30
    LLM_MAX_NEW_TOKENS = 1024
    LLM_TEMPERATURE = 0.3
    LLM_TOP_P = 0.9
    
    # API Configuration
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {".pptx"}
    
    # Evaluation Thresholds
    MIN_SCORE = 0
    MAX_SCORE = 10
    SCORE_CATEGORIES = ["relevance", "clarity", "technical_accuracy", "structure", "completeness"]
    
    # Prompt Templates
    EVALUATION_PROMPT_TEMPLATE = """You are a critical HACKATHON JUDGE at a top-tier tech competition. Analyze the following pitch deck/presentation against the problem statement.
    Be strict, look for innovation, and demand technical proof. Return ONLY valid JSON.
    
    PROBLEM STATEMENT:
    {problem_statement}
    
    PRESENTATION CONTENT:
    {presentation_summary}
    
    EVALUATION CRITERIA (HACKATHON STANDARDS):
    1. Relevance (0-10): Problem/Solution Fit. Does it solve a real, significant pain point?
    2. Clarity (0-10): Pitch Quality. Is the storytelling compelling and the value prop clear?
    3. Technical Accuracy (0-10): Feasibility & Engineering. Is the tech stack appropriate? Is it more than just a wrapper?
    4. Structure (0-10): Narrative Flow. Does it follow: Problem -> Solution -> Tech -> Business -> Ask?
    5. Completeness (0-10): MVP Status. Is there a demo/prototype? Is the roadmap realistic?
    
    Return ONLY this JSON structure with no additional text:
    {{
      "scores": {{
        "relevance": <0-10>,
        "clarity": <0-10>,
        "technical_accuracy": <0-10>,
        "structure": <0-10>,
        "completeness": <0-10>
      }},
      "overall_score": <sum of above>,
      "strengths": [<3 specific, detailed compliments on Innovation/Tech/Impact (at least 20 words each). Cite specific slides/features.>],
      "weaknesses": [<3 specific, critical flaws in Feasibility/Business/MVP (at least 20 words each). Be tough.>],
      "improvement_suggestions": [<3 actionable, expert advice on how to win the hackathon (at least 20 words each). Focus on features, pitch delivery, or biz model.>],
      "missing_elements": [<list of specific missing hackathon essentials (e.g., "Demo Video", "Revenue Model", "competitor differentiator")>],
      "summary_evaluation": "<Comprehensive 3-5 sentence judge's verdict. Would you fund this? Is it hackathon-winning material? be direct.>"
    }}"""

    # Cache Directory
    CACHE_DIR = Path.home() / ".cache" / "ppt_evaluator"
    
    @classmethod
    def get_device_info(cls):
        """Return device information for logging."""
        return {
            "device": cls.DEVICE,
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "use_8bit": cls.USE_8BIT
        }
