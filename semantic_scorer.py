"""
Semantic similarity scoring using sentence embeddings.
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticScorer:
    """Calculate semantic relevance using embeddings."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize the semantic scorer.
        
        Args:
            model_name: Hugging Face model ID (default from config)
        """
        self.model_name = model_name or Config.EMBEDDING_MODEL
        self.model = None
        
        logger.info(f"Initializing semantic scorer with model: {self.model_name}")
    
    def load_model(self):
        """Lazy load the embedding model."""
        if self.model is None:
            try:
                logger.info("Loading embedding model...")
                self.model = SentenceTransformer(self.model_name)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading embedding model: {str(e)}")
                raise
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts into embeddings.
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            Numpy array of embeddings
        """
        self.load_model()
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            logger.error(f"Error encoding texts: {str(e)}")
            raise
    
    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between -1 and 1
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)
    
    def calculate_relevance_score(
        self, 
        problem_statement: str, 
        presentation_content: str
    ) -> float:
        """
        Calculate relevance score between problem statement and presentation.
        
        Args:
            problem_statement: The problem/rubric to evaluate against
            presentation_content: The presentation content (summarized)
            
        Returns:
            Relevance score from 0 to 10
        """
        self.load_model()
        
        try:
            # Encode both texts
            embeddings = self.encode([problem_statement, presentation_content])
            
            # Calculate similarity
            similarity = self.cosine_similarity(embeddings[0], embeddings[1])
            
            # Convert from [-1, 1] to [0, 10]
            # Cosine similarity is typically in [0, 1] for similar texts
            # We map [0, 1] -> [0, 10]
            score = max(0, min(10, similarity * 10))
            
            logger.info(f"Semantic relevance score: {score:.2f}/10")
            return round(score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating relevance: {str(e)}")
            # Return neutral score on error
            return 5.0
    
    def calculate_slide_relevance(
        self,
        problem_statement: str,
        slide_summaries: List[str]
    ) -> List[float]:
        """
        Calculate relevance score for each slide.
        
        Args:
            problem_statement: The problem/rubric to evaluate against
            slide_summaries: List of slide summaries
            
        Returns:
            List of relevance scores (0-10) for each slide
        """
        self.load_model()
        
        try:
            # Encode problem statement once
            problem_embedding = self.encode([problem_statement])[0]
            
            # Encode all slides
            slide_embeddings = self.encode(slide_summaries)
            
            # Calculate similarity for each slide
            scores = []
            for slide_embedding in slide_embeddings:
                similarity = self.cosine_similarity(problem_embedding, slide_embedding)
                score = max(0, min(10, similarity * 10))
                scores.append(round(score, 2))
            
            logger.info(f"Calculated relevance for {len(scores)} slides")
            return scores
            
        except Exception as e:
            logger.error(f"Error calculating slide relevance: {str(e)}")
            # Return neutral scores on error
            return [5.0] * len(slide_summaries)


if __name__ == "__main__":
    # Example usage
    scorer = SemanticScorer()
    problem = "Build a web scraper for e-commerce websites"
    presentation = "This presentation covers web scraping techniques using Python and BeautifulSoup"
    score = scorer.calculate_relevance_score(problem, presentation)
    print(f"Relevance score: {score}/10")
