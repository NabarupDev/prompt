"""
Prompt injection detection classifier using transformers.
"""

import os
import logging
from typing import Dict, Any, Optional
from transformers import pipeline

logger = logging.getLogger(__name__)


class PromptInjectionClassifier:
    """
    Machine learning classifier for detecting prompt injection attacks.
    
    This class wraps a pre-trained transformer model to classify text as either
    benign or malicious (prompt injection attempt).
    """
    
    def __init__(self, model_path: str = "./models/prompt_injection_model"):
        """
        Initialize the classifier.
        
        Args:
            model_path: Path to the trained model directory
        """
        self.model_path = model_path
        self.classifier = None
        self.label_mapping = {
            "LABEL_0": "BENIGN",
            "LABEL_1": "PROMPT_INJECTION"
        }
        self._is_loaded = False
    
    @property
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._is_loaded
    
    def load_model(self) -> bool:
        """
        Load the trained prompt injection detection model.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
            
        Raises:
            RuntimeError: If model files are not found or loading fails
        """
        if not os.path.exists(self.model_path):
            logger.error(f"❌ Model not found at: {self.model_path}")
            raise RuntimeError(
                f"Model not found at {self.model_path}. "
                "Please run the training script first to train the model."
            )
        
        try:
            logger.info("🔍 Loading Prompt Injection Detection Model...")
            self.classifier = pipeline(
                "text-classification", 
                model=self.model_path,
                return_all_scores=False
            )
            self._is_loaded = True
            logger.info("✅ Model loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {str(e)}")
            raise RuntimeError(f"Failed to load model: {str(e)}")
    
    def get_risk_level(self, score: float, is_injection: bool) -> str:
        """
        Determine risk level based on confidence score.
        
        Args:
            score: Model confidence score (0-1)
            is_injection: Whether the prediction indicates injection
            
        Returns:
            str: Risk level classification
        """
        if is_injection:
            if score > 0.8:
                return "HIGH"
            elif score > 0.6:
                return "MEDIUM"
            else:
                return "LOW"
        else:
            if score > 0.8:
                return "SAFE_HIGH"
            elif score > 0.6:
                return "SAFE_MEDIUM"
            else:
                return "SAFE_LOW"
    
    def get_risk_message(self, risk_level: str, is_injection: bool) -> str:
        """
        Get descriptive message for risk level.
        
        Args:
            risk_level: Risk level classification
            is_injection: Whether injection was detected
            
        Returns:
            str: Descriptive message
        """
        if is_injection:
            messages = {
                "HIGH": "This input appears to be a clear prompt injection attempt.",
                "MEDIUM": "This input shows some characteristics of prompt injection.",
                "LOW": "This input has some suspicious patterns but may be legitimate."
            }
        else:
            messages = {
                "SAFE_HIGH": "This input appears to be completely safe.",
                "SAFE_MEDIUM": "This input is likely safe but has some ambiguous patterns.",
                "SAFE_LOW": "This input is classified as safe but with low confidence."
            }
        
        return messages.get(risk_level, "Unable to determine risk level.")
    
    def predict(self, text: str, max_length: int = 256) -> Dict[str, Any]:
        """
        Classify text for prompt injection.
        
        Args:
            text: Input text to classify
            max_length: Maximum text length for truncation
            
        Returns:
            Dict containing prediction results
            
        Raises:
            RuntimeError: If model is not loaded
            ValueError: If text is empty
        """
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        if not text.strip():
            raise ValueError("Text input cannot be empty")
        
        # Get prediction from model
        result = self.classifier(text, truncation=True, max_length=max_length)[0]
        
        label = result['label']
        score = result['score']
        prediction = self.label_mapping.get(label, label)
        is_injection = label == "LABEL_1"
        risk_level = self.get_risk_level(score, is_injection)
        
        # Prepare detailed response
        details = {
            "confidence_percentage": round(score * 100, 1),
            "text_length": len(text),
            "truncated": len(text) > max_length,
            "message": self.get_risk_message(risk_level, is_injection)
        }
        
        return {
            "text": text,
            "prediction": prediction,
            "confidence": round(score, 4),
            "risk_level": risk_level,
            "is_injection": is_injection,
            "details": details
        }
