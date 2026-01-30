"""
FastAPI application for presentation evaluation.
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from pathlib import Path
import tempfile
import os

from evaluation_orchestrator import EvaluationOrchestrator
from models import EvaluationResponse, HealthResponse
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Presentation Evaluation System",
    description="Automated evaluation of PowerPoint presentations using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator (lazy loading of models)
orchestrator = None


def get_orchestrator() -> EvaluationOrchestrator:
    """Get or create orchestrator instance."""
    global orchestrator
    if orchestrator is None:
        logger.info("Initializing evaluation orchestrator...")
        orchestrator = EvaluationOrchestrator()
    return orchestrator


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("=" * 60)
    logger.info("AI Presentation Evaluation System Starting")
    logger.info("=" * 60)
    logger.info(f"Device info: {Config.get_device_info()}")
    logger.info("API ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down AI Presentation Evaluation System")


@app.get("/", tags=["General"])
async def root():
    """Root endpoint."""
    return {
        "message": "AI Presentation Evaluation System",
        "version": "1.0.0",
        "endpoints": {
            "evaluate": "/evaluate",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint.
    
    Returns system status and model loading state.
    """
    orch = get_orchestrator()
    
    return HealthResponse(
        status="healthy",
        device_info=Config.get_device_info(),
        models_loaded={
            "ppt_extractor": True,
            "summarizer": orch.summarizer.pipeline is not None,
            "semantic_scorer": orch.semantic_scorer.model is not None,
            "llm_evaluator": orch.llm_evaluator.model is not None
        }
    )


@app.post("/evaluate", response_model=EvaluationResponse, tags=["Evaluation"])
async def evaluate_presentation(
    file: UploadFile = File(..., description="PowerPoint file (.pptx)"),
    problem_statement: str = Form(..., description="Problem statement or evaluation rubric")
):
    """
    Evaluate a PowerPoint presentation.
    
    **Parameters:**
    - **file**: PowerPoint file (.pptx format)
    - **problem_statement**: The problem statement or evaluation rubric to compare against
    
    **Returns:**
    - Structured evaluation with scores, feedback, and suggestions
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/evaluate" \\
      -F "file=@presentation.pptx" \\
      -F "problem_statement=Build a web scraper for e-commerce websites"
    ```
    """
    # Validate file extension
    if not file.filename.endswith('.pptx'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only .pptx files are supported."
        )
    
    # Validate file size
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > Config.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {Config.MAX_UPLOAD_SIZE / (1024*1024):.0f}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Empty file uploaded"
        )
    
    # Validate problem statement
    if not problem_statement or len(problem_statement.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Problem statement must be at least 10 characters long"
        )
    
    # Create temporary file
    temp_file = None
    try:
        # Create temp file with .pptx extension
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        logger.info(f"Processing file: {file.filename} ({file_size / 1024:.1f} KB)")
        logger.info(f"Problem statement: {problem_statement[:100]}...")
        
        # Get orchestrator and evaluate
        orch = get_orchestrator()
        result = orch.evaluate_presentation(temp_file_path, problem_statement)
        
        # Convert to response model
        response = EvaluationResponse(**result)
        
        logger.info(f"Evaluation completed successfully. Score: {response.overall_score}/50")
        
        return response
        
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {e}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server...")
    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=False,  # Set to True for development
        log_level="info"
    )
