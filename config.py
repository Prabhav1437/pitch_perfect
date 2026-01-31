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
    EVALUATION_PROMPT_TEMPLATE = """You are a highly critical and experienced JUDGE at the SMART INDIA HACKATHON (SIH).
    Your job is to evaluate the following project presentation against the problem statement.
    You must NOT be generic. You must look for Innovation, Technical Feasibility, and Real-world Impact.
    
    PROBLEM STATEMENT:
    {problem_statement}
    
    PRESENTATION CONTENT (Extracted Text):
    {presentation_summary}
    
    EVALUATION GUIDELINES (SIH STANDARDS):
    1. Relevance (0-10): Does this explicitly solve the PS? Is it a "force fit" or a genuine solution?
    2. Clarity (0-10): Is the pitch easy to understand? Did they explain "HOW" it works, not just "WHAT" it is?
    3. Technical Technical Accuracy (0-10): Is the tech stack strictly defined? Is the architecture sound? Penalize for buzzwords without substance.
    4. Structure (0-10): Flow: Problem -> Solution -> Architecture -> USP -> Business -> Team.
    5. Completeness (0-10): Is there evidence of a working prototype? Diagrams? Wireframes? Pure theory gets low scores.
    
    RETURN ONLY THIS JSON (No markdown, no text outside JSON):
    {{
      "scores": {{
        "relevance": <int>,
        "clarity": <int>,
        "technical_accuracy": <int>,
        "structure": <int>,
        "completeness": <int>
      }},
      "overall_score": <sum of scores>,
      "strengths": [
        "<Strict compliment 1: Cite specific tech features/innovation from the inputs>",
        "<Strict compliment 2: Cite specific business/impact potential>"
      ],
      "weaknesses": [
        "<Critical flaw 1: E.g., 'Stack undefined', 'Revenue model missing'>",
        "<Critical flaw 2: E.g., 'No complexity', 'Just a wrapper'>"
      ],
      "detailed_analysis": {{
        "technical_depth": "<Analyze the stack. If they mentioned React/Python/AI, evaluate how they are used. If vague, say 'Vague Tech Stack'. Length: 50 words.>",
        "business_viability": "<Is this market-ready? Who pays? Is it sustainable? Length: 50 words.>",
        "presentation_flow": "<Did they tell a story? Was the flow logical? Length: 50 words.>"
      }},
      "missing_elements": ["<Missing Item 1>", "<Missing Item 2>"],
      "summary_evaluation": "<Final Verdict: FUNDABLE / PROMISING / REJECT. Explain why in 2 sentences.>"
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
