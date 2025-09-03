"""
Unit tests for the prompt injection detection API.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models.classifier import PromptInjectionClassifier
from src.utils.data_processor import DataProcessor
from src.api.models import TextInput, PredictionResponse


class TestPromptInjectionClassifier:
    """Test cases for the PromptInjectionClassifier class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Use a mock model path for testing
        self.model_path = "../models/prompt_injection_model"
        self.classifier = PromptInjectionClassifier(self.model_path)
    
    def test_classifier_initialization(self):
        """Test classifier initialization."""
        assert self.classifier.model_path == self.model_path
        assert not self.classifier.is_loaded
        assert self.classifier.classifier is None
    
    def test_risk_level_calculation(self):
        """Test risk level calculation logic."""
        # Test injection cases
        assert self.classifier.get_risk_level(0.9, True) == "HIGH"
        assert self.classifier.get_risk_level(0.7, True) == "MEDIUM"
        assert self.classifier.get_risk_level(0.5, True) == "LOW"
        
        # Test benign cases
        assert self.classifier.get_risk_level(0.9, False) == "SAFE_HIGH"
        assert self.classifier.get_risk_level(0.7, False) == "SAFE_MEDIUM"
        assert self.classifier.get_risk_level(0.5, False) == "SAFE_LOW"
    
    def test_risk_message_generation(self):
        """Test risk message generation."""
        # Test injection messages
        msg_high = self.classifier.get_risk_message("HIGH", True)
        assert "clear prompt injection attempt" in msg_high
        
        msg_medium = self.classifier.get_risk_message("MEDIUM", True)
        assert "characteristics of prompt injection" in msg_medium
        
        # Test benign messages
        msg_safe = self.classifier.get_risk_message("SAFE_HIGH", False)
        assert "completely safe" in msg_safe


class TestDataProcessor:
    """Test cases for the DataProcessor class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.processor = DataProcessor()
        
        # Create sample data
        self.sample_data = [
            {"text": "Hello world", "label": "benign"},
            {"text": "Ignore instructions", "label": "malicious"},
            {"text": "Normal question", "label": "benign"},
            {"text": "Override system", "label": "malicious"}
        ]
    
    def test_distribution_analysis(self):
        """Test dataset distribution analysis."""
        import pandas as pd
        df = pd.DataFrame(self.sample_data)
        
        stats = self.processor.analyze_distribution(df)
        
        assert stats['total_samples'] == 4
        assert stats['distribution']['benign'] == 2
        assert stats['distribution']['malicious'] == 2
        assert stats['percentages']['benign'] == 50.0
        assert stats['percentages']['malicious'] == 50.0
    
    def test_label_encoding(self):
        """Test label encoding functionality."""
        import pandas as pd
        df = pd.DataFrame(self.sample_data)
        
        df_encoded = self.processor.encode_labels(df)
        
        # Check that labels are now integers
        assert df_encoded['label'].dtype in ['int32', 'int64']
        assert set(df_encoded['label'].unique()) == {0, 1}


class TestAPIModels:
    """Test cases for API models."""
    
    def test_text_input_validation(self):
        """Test TextInput model validation."""
        # Valid input
        valid_input = TextInput(text="Test text", max_length=256)
        assert valid_input.text == "Test text"
        assert valid_input.max_length == 256
        
        # Test default max_length
        default_input = TextInput(text="Test text")
        assert default_input.max_length == 256
        
        # Test validation errors
        with pytest.raises(ValueError):
            TextInput(text="", max_length=256)  # Empty text should fail
    
    def test_prediction_response_structure(self):
        """Test PredictionResponse model structure."""
        response_data = {
            "text": "Test input",
            "prediction": "BENIGN",
            "confidence": 0.95,
            "risk_level": "SAFE_HIGH",
            "is_injection": False,
            "details": {
                "confidence_percentage": 95.0,
                "text_length": 10,
                "truncated": False,
                "message": "Text appears safe"
            }
        }
        
        response = PredictionResponse(**response_data)
        assert response.text == "Test input"
        assert response.prediction == "BENIGN"
        assert response.confidence == 0.95
        assert not response.is_injection


if __name__ == "__main__":
    pytest.main([__file__])
