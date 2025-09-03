"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any


class TextInput(BaseModel):
    """Input model for text classification requests."""
    text: str = Field(..., description="Text to analyze for prompt injection", min_length=1)
    max_length: int = Field(default=256, description="Maximum text length for truncation", ge=1, le=512)


class PredictionResponse(BaseModel):
    """Response model for prediction results."""
    text: str = Field(..., description="Original input text")
    prediction: str = Field(..., description="Classification result (BENIGN or PROMPT_INJECTION)")
    confidence: float = Field(..., description="Model confidence score", ge=0.0, le=1.0)
    risk_level: str = Field(..., description="Risk assessment level")
    is_injection: bool = Field(..., description="Boolean flag indicating if injection detected")
    details: Dict[str, Any] = Field(..., description="Additional details and metadata")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service health status")
    model_loaded: bool = Field(..., description="Whether ML model is loaded")
    version: str = Field(..., description="API version")


class BatchPredictionResponse(BaseModel):
    """Response model for batch predictions."""
    results: list = Field(..., description="List of prediction results")
    total: int = Field(..., description="Total number of results")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
