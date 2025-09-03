"""
Main FastAPI application for prompt injection detection service.
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from ..models.classifier import PromptInjectionClassifier
from .routes import PromptInjectionRoutes
from .models import TextInput, PredictionResponse, HealthResponse, BatchPredictionResponse

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global classifier instance
classifier = None
routes_handler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    global classifier, routes_handler
    
    # Startup
    logger.info("🚀 Starting Prompt Injection Detection API...")
    
    # Initialize classifier
    model_path = os.getenv("MODEL_PATH", "./models/prompt_injection_model")
    classifier = PromptInjectionClassifier(model_path)
    
    try:
        classifier.load_model()
        routes_handler = PromptInjectionRoutes(classifier)
        logger.info("✅ Service initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down service...")


# Initialize FastAPI app
app = FastAPI(
    title="Prompt Injection Detection API",
    description="API service for detecting prompt injection attacks using machine learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check service health and model status."""
    if routes_handler is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return await routes_handler.health_check()


# Prediction endpoints
@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_injection(input_data: TextInput):
    """
    Analyze text for prompt injection attempts.
    
    Returns detailed classification results including confidence scores
    and risk assessment.
    """
    if routes_handler is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return await routes_handler.predict_injection(input_data)


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_batch(texts: list[TextInput]):
    """
    Analyze multiple texts for prompt injection attempts.
    
    Supports batch processing up to 100 texts at once.
    """
    if routes_handler is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return await routes_handler.predict_batch(texts)


# Test samples endpoint
@app.get("/test-samples", tags=["Testing"])
async def get_test_samples():
    """
    Get predefined test cases for quick API verification.
    
    Returns sample predictions for both benign and malicious inputs.
    """
    if routes_handler is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return await routes_handler.get_test_samples()


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint with basic information."""
    return {
        "message": "Prompt Injection Detection API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }
