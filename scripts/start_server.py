#!/usr/bin/env python3
"""
API server startup script for prompt injection detection service.

This script starts the FastAPI server with proper configuration.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import transformers
        import torch
        logger.info("✅ All dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("Install dependencies with: pip install -r requirements.txt")
        return False


def check_model_exists(model_path: Path) -> bool:
    """Check if the trained model exists."""
    if not model_path.exists():
        logger.error(f"❌ Model not found at: {model_path}")
        logger.error("Train the model first with: python scripts/train_model.py")
        return False
    
    required_files = ["config.json", "model.safetensors", "tokenizer.json"]
    missing_files = []
    
    for file in required_files:
        if not (model_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"❌ Missing model files: {missing_files}")
        return False
    
    logger.info("✅ Model files found")
    return True


def main():
    """Main server startup function."""
    parser = argparse.ArgumentParser(description="Start prompt injection detection API server")
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0",
        help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=3000,
        help="Port to bind the server to"
    )
    parser.add_argument(
        "--model-path", 
        type=str, 
        default="../models/prompt_injection_model",
        help="Path to trained model directory"
    )
    parser.add_argument(
        "--reload", 
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Convert relative path to absolute
    script_dir = Path(__file__).parent
    model_path = script_dir / args.model_path
    
    logger.info("🚀 Starting Prompt Injection Detection API Server")
    logger.info("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check model
    if not check_model_exists(model_path):
        return 1
    
    # Set environment variables for the API
    os.environ["MODEL_PATH"] = str(model_path)
    os.environ["HOST"] = args.host
    os.environ["PORT"] = str(args.port)
    
    # Import and start the server
    try:
        import uvicorn
        from src.api.main import app
        
        logger.info(f"🌐 Server will be available at: http://{args.host}:{args.port}")
        logger.info(f"📖 API documentation: http://{args.host}:{args.port}/docs")
        logger.info(f"🧪 Interactive API: http://{args.host}:{args.port}/redoc")
        logger.info(f"🔍 Health check: http://{args.host}:{args.port}/health")
        logger.info("=" * 60)
        
        # Start server
        uvicorn.run(
            "src.api.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("\n👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
