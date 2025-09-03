"""
API module for prompt injection detection service.
"""

from .main import app
from .routes import PromptInjectionRoutes
from .models import TextInput, PredictionResponse, HealthResponse

__all__ = ["app", "PromptInjectionRoutes", "TextInput", "PredictionResponse", "HealthResponse"]
