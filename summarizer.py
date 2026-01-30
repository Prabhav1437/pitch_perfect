"""
Summarization module using BART for content compression.
"""
from transformers import pipeline, BartForConditionalGeneration, BartTokenizer
import torch
from typing import List, Dict, Any
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Summarizer:
    """Summarize presentation content using BART."""
    
    def __init__(self, model_name: str = None, device: str = None):
        """
        Initialize the summarization pipeline.
        
        Args:
            model_name: Hugging Face model ID (default from config)
            device: Device to run on ('cuda' or 'cpu', auto-detected if None)
        """
        self.model_name = model_name or Config.SUMMARIZATION_MODEL
        self.device = device or Config.DEVICE
        self.pipeline = None
        
        logger.info(f"Initializing summarizer with model: {self.model_name}")
        logger.info(f"Using device: {self.device}")
    
    def load_model(self):
        """Lazy load the summarization model."""
        if self.pipeline is None:
            try:
                logger.info("Loading summarization model...")
                # Use model and tokenizer directly instead of pipeline
                # to avoid deprecated "summarization" task in transformers 5.0+
                self.tokenizer = BartTokenizer.from_pretrained(self.model_name)
                device_id = 0 if self.device == "cuda" else -1
                
                if device_id == 0:
                    self.model = BartForConditionalGeneration.from_pretrained(self.model_name).to("cuda")
                else:
                    self.model = BartForConditionalGeneration.from_pretrained(self.model_name)
                
                # Create a simple wrapper to maintain compatibility
                class ModelWrapper:
                    def __init__(self, model, tokenizer):
                        self.model = model
                        self.tokenizer = tokenizer
                    
                    def __call__(self, text, max_length=130, min_length=30, do_sample=False, truncation=True):
                        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=1024)
                        if self.model.device.type == "cuda":
                            inputs = {k: v.to("cuda") for k, v in inputs.items()}
                        
                        summary_ids = self.model.generate(
                            inputs["input_ids"],
                            max_length=max_length,
                            min_length=min_length,
                            do_sample=do_sample,
                            num_beams=4,
                            early_stopping=True
                        )
                        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                        return [{"summary_text": summary}]
                
                self.pipeline = ModelWrapper(self.model, self.tokenizer)
                logger.info("Summarization model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading summarization model: {str(e)}")
                raise
    
    def summarize_text(self, text: str, max_length: int = None, min_length: int = None) -> str:
        """
        Summarize a single text passage.
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of summary (default from config)
            min_length: Minimum length of summary (default from config)
            
        Returns:
            Summarized text
        """
        if not text or len(text.strip()) < 50:
            return text  # Too short to summarize
        
        self.load_model()
        
        max_length = max_length or Config.SUMMARIZATION_MAX_LENGTH
        min_length = min_length or Config.SUMMARIZATION_MIN_LENGTH
        
        try:
            # Truncate input if too long (BART max is 1024 tokens)
            max_input_length = 1024
            inputs = self.pipeline.tokenizer(text, return_tensors="pt", truncation=True, max_length=max_input_length)
            input_length = inputs['input_ids'].shape[1]
            
            # Adjust summary length based on input
            adjusted_max_length = min(max_length, input_length // 2)
            adjusted_min_length = min(min_length, adjusted_max_length - 10)
            
            summary = self.pipeline(
                text,
                max_length=adjusted_max_length,
                min_length=adjusted_min_length,
                do_sample=False,
                truncation=True
            )
            
            return summary[0]['summary_text']
            
        except Exception as e:
            logger.warning(f"Summarization failed: {str(e)}. Returning truncated text.")
            # Fallback: return first N characters
            return text[:500] + "..." if len(text) > 500 else text
    
    def summarize_slides(self, presentation_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Summarize each slide's content.
        
        Args:
            presentation_data: Dictionary from PPTExtractor
            
        Returns:
            List of dictionaries with slide summaries
        """
        self.load_model()
        
        summarized_slides = []
        
        for slide in presentation_data["slides"]:
            # Combine slide content
            slide_text_parts = []
            
            if slide["title"]:
                slide_text_parts.append(slide["title"])
            
            if slide["content"]:
                slide_text_parts.append(" ".join(slide["content"]))
            
            if slide["notes"]:
                slide_text_parts.append(slide["notes"])
            
            full_slide_text = " ".join(slide_text_parts)
            
            # Summarize if content is substantial
            if len(full_slide_text) > 100:
                summary = self.summarize_text(full_slide_text)
            else:
                summary = full_slide_text
            
            summarized_slides.append({
                "slide_number": slide["slide_number"],
                "title": slide["title"],
                "summary": summary
            })
            
            logger.debug(f"Summarized slide {slide['slide_number']}")
        
        return summarized_slides
    
    def get_presentation_summary(self, presentation_data: Dict[str, Any]) -> str:
        """
        Get a comprehensive summary of the entire presentation.
        
        Args:
            presentation_data: Dictionary from PPTExtractor
            
        Returns:
            Combined summary of all slides
        """
        slide_summaries = self.summarize_slides(presentation_data)
        
        # Combine all summaries
        combined_text = "\n\n".join([
            f"Slide {s['slide_number']} - {s['title']}: {s['summary']}"
            for s in slide_summaries
        ])
        
        # If combined text is very long, summarize again
        if len(combined_text) > 2000:
            logger.info("Creating meta-summary of presentation")
            return self.summarize_text(combined_text, max_length=300, min_length=100)
        
        return combined_text


if __name__ == "__main__":
    # Example usage
    summarizer = Summarizer()
    text = "This is a long presentation about machine learning. " * 50
    summary = summarizer.summarize_text(text)
    print(f"Summary: {summary}")
