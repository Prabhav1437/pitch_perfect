"""
Evaluation orchestrator - coordinates all components.
"""
from ppt_extractor import PPTExtractor
from summarizer import Summarizer
from semantic_scorer import SemanticScorer
from llm_evaluator import LLMEvaluator
from typing import Dict
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EvaluationOrchestrator:
    """Orchestrate the complete evaluation pipeline."""
    
    def __init__(self):
        """Initialize all components."""
        logger.info("Initializing Evaluation Orchestrator")
        
        # Initialize components (lazy loading)
        self.ppt_extractor = PPTExtractor()
        self.summarizer = Summarizer()
        self.semantic_scorer = SemanticScorer()
        self.llm_evaluator = LLMEvaluator()
        
        logger.info("Orchestrator initialized")
    
    def evaluate_presentation(
        self,
        ppt_file_path: str,
        problem_statement: str
    ) -> Dict:
        """
        Complete evaluation pipeline.
        
        Args:
            ppt_file_path: Path to the PowerPoint file
            problem_statement: Problem statement or evaluation rubric
            
        Returns:
            Complete evaluation results as dictionary
        """
        try:
            logger.info("=" * 60)
            logger.info("Starting presentation evaluation")
            logger.info("=" * 60)
            
            # Step 1: Extract PPT content
            logger.info("Step 1/4: Extracting PowerPoint content...")
            presentation_data = self.ppt_extractor.extract_from_file(ppt_file_path)
            logger.info(f"✓ Extracted {presentation_data['slide_count']} slides")
            
            # Step 2: Summarize content
            logger.info("Step 2/4: Summarizing presentation content...")
            presentation_summary = self.summarizer.get_presentation_summary(presentation_data)
            logger.info(f"✓ Generated summary ({len(presentation_summary)} characters)")
            
            # Step 3: Calculate semantic relevance
            logger.info("Step 3/4: Calculating semantic relevance...")
            semantic_score = self.semantic_scorer.calculate_relevance_score(
                problem_statement,
                presentation_summary
            )
            logger.info(f"✓ Semantic relevance: {semantic_score}/10")
            
            # Step 4: LLM evaluation
            logger.info("Step 4/4: Running LLM evaluation...")
            llm_evaluation = self.llm_evaluator.evaluate(
                problem_statement,
                presentation_summary
            )
            logger.info("✓ LLM evaluation completed")
            
            # Combine results
            # Use semantic score to adjust relevance if significantly different
            original_relevance = llm_evaluation["scores"]["relevance"]
            
            # Weighted average: 70% LLM, 30% semantic
            adjusted_relevance = round(
                0.7 * original_relevance + 0.3 * semantic_score,
                1
            )
            
            llm_evaluation["scores"]["relevance"] = adjusted_relevance
            llm_evaluation["overall_score"] = sum(llm_evaluation["scores"].values())
            
            # Add metadata
            llm_evaluation["metadata"] = {
                "slide_count": presentation_data["slide_count"],
                "semantic_relevance_score": semantic_score,
                "llm_relevance_score": original_relevance,
                "adjusted_relevance_score": adjusted_relevance
            }
            llm_evaluation["presentation_summary"] = presentation_summary
            
            logger.info("=" * 60)
            logger.info(f"Evaluation complete! Overall score: {llm_evaluation['overall_score']}/50")
            logger.info("=" * 60)
            
            return llm_evaluation
            
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            raise Exception(f"Evaluation pipeline failed: {str(e)}")
    
    def evaluate_from_bytes(
        self,
        ppt_bytes: bytes,
        filename: str,
        problem_statement: str,
        temp_dir: str = "/tmp"
    ) -> Dict:
        """
        Evaluate presentation from bytes (for API uploads).
        
        Args:
            ppt_bytes: PowerPoint file as bytes
            filename: Original filename
            problem_statement: Problem statement or evaluation rubric
            temp_dir: Temporary directory for file storage
            
        Returns:
            Complete evaluation results as dictionary
        """
        import tempfile
        import os
        
        # Save bytes to temporary file
        temp_path = Path(temp_dir) / filename
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(temp_path, 'wb') as f:
                f.write(ppt_bytes)
            
            # Evaluate
            result = self.evaluate_presentation(str(temp_path), problem_statement)
            
            return result
            
        finally:
            # Clean up temporary file
            if temp_path.exists():
                os.remove(temp_path)
                logger.debug(f"Cleaned up temporary file: {temp_path}")


if __name__ == "__main__":
    # Example usage
    orchestrator = EvaluationOrchestrator()
    # result = orchestrator.evaluate_presentation(
    #     "sample.pptx",
    #     "Build a web scraper for e-commerce websites"
    # )
    # print(json.dumps(result, indent=2))
