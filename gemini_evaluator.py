
import os
import json
import logging
import google.generativeai as genai
from typing import Dict, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiEvaluator:
    """Wrapper for Google's Gemini API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. Gemini features will fail.")
        else:
            genai.configure(api_key=self.api_key)
            # Use a model that supports JSON mode if possible, or just standard
            # Using the user-requested model
            self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_response(self, prompt: str) -> str:
        """Generate text response from Gemini."""
        if not self.api_key:
            return "Error: GEMINI_API_KEY not set."
            
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {str(e)}")
            return f"Error: {str(e)}"

    def extract_json_from_text(self, text: str) -> Optional[Dict]:
        """Extract JSON from Gemini output."""
        # Try to find JSON in the text
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Try cleaning up markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to extract valid JSON from Gemini output")
            return None
