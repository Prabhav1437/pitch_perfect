"""
LLM-based evaluation engine using instruction-tuned models.
"""
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import json
import re
import logging
from typing import Dict, Optional
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMEvaluator:
    """Evaluate presentations using instruction-tuned LLMs."""
    
    def __init__(self, model_name: str = None, device: str = None, use_8bit: bool = None):
        """
        Initialize the LLM evaluator.
        
        Args:
            model_name: Hugging Face model ID (default from config)
            device: Device to run on ('cuda' or 'cpu', auto-detected if None)
            use_8bit: Use 8-bit quantization (default from config)
        """
        self.model_name = model_name or Config.LLM_MODEL
        self.device = device or Config.DEVICE
        self.use_8bit = use_8bit if use_8bit is not None else Config.USE_8BIT
        self.model = None
        self.tokenizer = None
        
        # Use fallback model if on CPU and primary model is too large
        if self.device == "cpu" and "7B" in self.model_name:
            logger.warning(f"Switching to fallback model for CPU: {Config.LLM_MODEL_FALLBACK}")
            self.model_name = Config.LLM_MODEL_FALLBACK
            self.use_8bit = False
        
        logger.info(f"Initializing LLM evaluator with model: {self.model_name}")
        logger.info(f"Device: {self.device}, 8-bit: {self.use_8bit}")
    
    def load_model(self):
        """Lazy load the LLM model."""
        if self.model is None:
            try:
                logger.info("Loading LLM model... This may take a few minutes.")
                
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                
                # Determine model class based on architecture
                if "t5" in self.model_name.lower():
                    # T5 is seq2seq
                    model_class = AutoModelForSeq2SeqLM
                else:
                    # Mistral, Llama, etc. are causal LM
                    model_class = AutoModelForCausalLM
                
                # Load with quantization if enabled
                if self.use_8bit and self.device == "cuda":
                    self.model = model_class.from_pretrained(
                        self.model_name,
                        load_in_8bit=True,
                        device_map="auto",
                        torch_dtype=torch.float16
                    )
                else:
                    self.model = model_class.from_pretrained(
                        self.model_name,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                    )
                    self.model.to(self.device)
                
                logger.info("LLM model loaded successfully")
                
            except Exception as e:
                logger.error(f"Error loading LLM model: {str(e)}")
                raise
    
    def extract_json_from_text(self, text: str) -> Optional[Dict]:
        """
        Extract JSON from LLM output, handling various formats.
        
        Args:
            text: LLM output text
            
        Returns:
            Parsed JSON dictionary or None if parsing fails
        """
        # Try to find JSON in the text
        # Look for content between curly braces
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("Found JSON-like structure but failed to parse")
        
        # Try parsing the entire text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to extract valid JSON from LLM output")
            return None
    
    def validate_and_fix_response(self, response: Dict) -> Dict:
        """
        Validate and fix the LLM response to match required schema.
        
        Args:
            response: Parsed JSON response
            
        Returns:
            Validated and fixed response
        """
        # Ensure all required fields exist
        if "scores" not in response:
            response["scores"] = {}
        
        # Ensure all score categories exist and are in range
        for category in Config.SCORE_CATEGORIES:
            if category not in response["scores"]:
                response["scores"][category] = 5  # Default neutral score
            else:
                # Clamp to valid range
                response["scores"][category] = max(
                    Config.MIN_SCORE,
                    min(Config.MAX_SCORE, response["scores"][category])
                )
        
        # Calculate overall score
        response["overall_score"] = sum(response["scores"].values())
        
        # Ensure detailed_analysis exists
        if "detailed_analysis" not in response or not isinstance(response["detailed_analysis"], dict):
             # Try to migrate from suggestions if old model used
             suggestions = response.get("improvement_suggestions", ["Analysis is brief."])
             combined_suggestions = " ".join(suggestions) if isinstance(suggestions, list) else str(suggestions)
             
             response["detailed_analysis"] = {
                 "technical_depth": f"Technical review pending. {combined_suggestions}",
                 "business_viability": "Market impact analysis required.",
                 "presentation_flow": "Structure needs further evaluation."
             }
        
        # Ensure summary exists
        if "summary_evaluation" not in response or not response["summary_evaluation"]:
            response["summary_evaluation"] = "Evaluation completed."
        
        return response
    
    def evaluate(
        self,
        problem_statement: str,
        presentation_summary: str,
        max_retries: int = 3
    ) -> Dict:
        """
        Evaluate presentation using LLM.
        
        Args:
            problem_statement: The problem/rubric to evaluate against
            presentation_summary: Summarized presentation content
            max_retries: Number of retries if JSON parsing fails
            
        Returns:
            Evaluation results as dictionary
        """
        self.load_model()
        
        # Create prompt
        prompt = Config.EVALUATION_PROMPT_TEMPLATE.format(
            problem_statement=problem_statement,
            presentation_summary=presentation_summary
        )
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Generating evaluation (attempt {attempt + 1}/{max_retries})...")
                
                # Tokenize input
                inputs = self.tokenizer(
                    prompt,
                    return_tensors="pt",
                    truncation=True,
                    max_length=4096
                ).to(self.device)
                
                # Generate response
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=Config.LLM_MAX_NEW_TOKENS,
                        temperature=Config.LLM_TEMPERATURE,
                        top_p=Config.LLM_TOP_P,
                        do_sample=True if Config.LLM_TEMPERATURE > 0 else False,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                # Decode response
                response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # For instruction models, extract only the response part
                if "[/INST]" in response_text:
                    response_text = response_text.split("[/INST]")[-1].strip()
                elif "Response:" in response_text:
                    response_text = response_text.split("Response:")[-1].strip()
                
                logger.debug(f"LLM output: {response_text[:200]}...")
                
                # Parse JSON
                evaluation = self.extract_json_from_text(response_text)
                
                if evaluation:
                    # Validate and fix
                    evaluation = self.validate_and_fix_response(evaluation)
                    logger.info("Evaluation completed successfully")
                    return evaluation
                else:
                    logger.warning(f"Failed to parse JSON on attempt {attempt + 1}")
                    
            except Exception as e:
                logger.error(f"Error during evaluation (attempt {attempt + 1}): {str(e)}")
        
        # If all retries failed, return default evaluation
        logger.warning("All evaluation attempts failed. Returning default evaluation.")
        return self.get_default_evaluation(problem_statement, presentation_summary)
    
    def generate_heuristic_evaluation(self, problem_statement: str, presentation_summary: str) -> Dict:
        """
        Generate a HACKATHON-GRADE heuristic evaluation when LLM fails.
        Acts as a critical judge looking for Tech Stack, Business, and MVP.
        """
        logger.info("Running Hackathon Mode heuristic evaluation...")
        
        summary_lower = presentation_summary.lower()
        
        # --- 1. SPECIALIZED HACKATHON CHECKS ---
        
        # A. Tech Stack Detection
        tech_keywords = [
            'python', 'javascript', 'react', 'node', 'aws', 'firebase', 'docker', 'kubernetes', 
            'api', 'database', 'sql', 'nosql', 'mongodb', 'ai', 'ml', 'llm', 'blockchain', 
            'smart contract', 'flutter', 'swift', 'tensorflow', 'pytorch', 'backend', 'frontend'
        ]
        detected_tech = [t for t in tech_keywords if t in summary_lower]
        has_tech_depth = len(detected_tech) >= 3
        
        # B. Business/Viability Detection
        biz_keywords = [
            'market', 'revenue', 'business model', 'subscription', 'b2b', 'b2c', 'saas', 
            'competitor', 'user acquisition', 'growth', 'scale', 'monetization', 'cost'
        ]
        has_biz_plan = any(k in summary_lower for k in biz_keywords)
        
        # C. MVP/Protoype Detection
        mvp_keywords = [
            'demo', 'prototype', 'mvp', 'live', 'screenshot', 'walkthrough', 'architecture', 
            'flowchart', 'github', 'repo', 'implementation'
        ]
        has_mvp = any(k in summary_lower for k in mvp_keywords)
        
        # --- 2. CALCULATE HACKATHON SCORES ---
        
        # Relevance (Problem/Solution Fit)
        # Did they actually solve the problem? usage keyword overlap
        problem_words = set(re.findall(r'\w+', problem_statement.lower())) - {'the', 'a', 'an', 'to', 'of'}
        summary_words = set(re.findall(r'\w+', summary_lower))
        overlap = len(set(problem_words).intersection(summary_words))
        relevance_score = min(9.5, max(4.0, (overlap / len(problem_words) * 10 * 1.5)))
        
        # Technical Accuracy (Feasibility)
        # Heavily weighted by tech stack detection
        tech_score = 8.5 if has_tech_depth else 5.0
        if 'wrapper' in summary_lower or 'simple' in summary_lower:
            tech_score -= 1.0
            
        # Completeness (MVP Status)
        # No demo/mvp mention = instant penalty
        completeness_score = 8.0 if has_mvp else 4.0
        
        # Structure (Pitch Flow)
        structural_markers = ['problem', 'solution', 'tech', 'demo', 'business', 'team', 'ask']
        structure_count = sum(1 for w in structural_markers if w in summary_lower)
        structure_score = min(9.0, 4.0 + structure_count)
        
        # Clarity (Pitch Quality)
        clarity_score = 7.5  # Baseline
        
        scores = {
            "relevance": round(relevance_score, 1),
            "clarity": round(clarity_score, 1),
            "technical_accuracy": round(tech_score, 1),
            "structure": round(structure_score, 1),
            "completeness": round(completeness_score, 1)
        }
        overall_score = sum(scores.values())

        # --- 3. GENERATE JUDGE'S FEEDBACK ---
        
        # Strengths (Compliments)
        strengths = []
        if has_tech_depth:
            strengths.append(f"Impressive technical depth detected ({', '.join(detected_tech[:3])}). The engineering effort appears strictly robust and goes beyond a simple UI wrapper.")
        else:
            strengths.append("The project targets a clear problem space, and the initial concept shows potential for a viable hackathon entry if technical details are fleshed out.")
            
        if has_biz_plan:
            strengths.append("Strong business viability signals. You've clearly thought about market fit and monetization, which sets you apart from pure engineering projects.")
        else:
            strengths.append("The narrative follows a logical problem-solution cadence, making the core value proposition easy for judges to understand quickly.")
            
        if relevance_score > 7:
            strengths.append("Direct hit on the problem statement. The solution aligns perfectly with the competition track and addresses a significant pain point.")
        else:
            strengths.append("The slide deck is visually structured to guide the audience, ensuring that the key 'Ask' or conclusion is not lost in the details.")

        # Weaknesses (Critical Flaws)
        weaknesses = []
        if not has_tech_depth:
            weaknesses.append("CRITICAL: Lack of deep technical details. Judges need to see architecture diagrams, API specs, or code snippets, not just high-level concepts. What is the stack?")
        else:
            weaknesses.append("The connection between the complex tech stack and the user value proposition could be sharper. Don't just list tools; explain *why* they were chosen.")
            
        if not has_mvp:
            weaknesses.append("MAJOR RED FLAG: No clear evidence of a functional MVP or Demo. Hackathons are about *building*, not just pitching ideas. Where is the prototype?")
        else:
            weaknesses.append("The current MVP feature set seems ambitious. Ensure you can actually demo the core 'Happy Path' live without smoking mirrors.")
            
        if not has_biz_plan:
            weaknesses.append("Missing commercial viability. Even for non-profits, you need a sustainability model. Who pays? How do you scale? The 'Business' slide seems missing.")
        else:
            weaknesses.append("The competitive analysis feels light. You need to explicitly state why you are 10x better than existing solution X or Y.")

        # Detailed Analysis (Replacements for Suggestions)
        detailed_analysis = {
            "technical_depth": f"The proposed solution {'demonstrates a strong engineering foundation' if has_tech_depth else 'lacks sufficient technical specificity'}. {'The stack includes ' + ', '.join(detected_tech) + '.' if detected_tech else 'No clear tech stack was identified.'} Architecture validation required.",
            "business_viability": f"{'A clear business model was detected' if has_biz_plan else 'Commercial viability is unclear'}. The presentation {'addresses' if has_biz_plan else 'fails to address'} market fit and revenue streams adequately for a venture-backed track.",
            "presentation_flow": f"The narrative structure scores {structure_score}/10. It {'successfully' if structure_score > 7 else 'partially'} follows standard pitch deck conventions (Problem->Solution->Tech->Biz). Visual clarity baseline estimated at {clarity_score}/10."
        }

        # Summary Generation
        verdict = "FUNDABLE" if overall_score > 40 else "PROMISING" if overall_score > 30 else "NEEDS WORK"
        summary_eval = (
            f"JUDGE'S VERDICT: {verdict} (Score: {overall_score}/50). "
            f"This entry {'has strong winning potential' if has_tech_depth and has_mvp else 'has a good concept but lacks execution proof'}. "
            f"{'The technical implementation is the standout feature.' if has_tech_depth else 'You need to prove this is more than just a slide deck.'} "
            f"Focus entirely on polishing the {('Demo' if not has_mvp else 'Business Case')} for the final pitch."
        )

        return {
            "scores": scores,
            "overall_score": overall_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "detailed_analysis": detailed_analysis,
            "missing_elements": ["Live Demo Link", "System Architecture Diagram", "Go-to-Market Strategy"],
            "summary_evaluation": summary_eval
        }

    def get_default_evaluation(self, problem_statement: str = "", presentation_summary: str = "") -> Dict:
        """
        Wrapper to call heuristic evaluation.
        """
        return self.generate_heuristic_evaluation(problem_statement, presentation_summary)


if __name__ == "__main__":
    # Example usage
    evaluator = LLMEvaluator()
    result = evaluator.evaluate(
        "Build a web scraper",
        "Presentation covers Python, BeautifulSoup, and scraping techniques"
    )
    print(json.dumps(result, indent=2))
