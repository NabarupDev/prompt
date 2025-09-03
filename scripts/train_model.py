#!/usr/bin/env python3
"""
Training script for the prompt injection detection model.

This script trains a DistilBERT-based classifier to detect prompt injection attacks.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.data_processor import DataProcessor
from src.utils.model_utils import ModelUtils

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train prompt injection detection model")
    parser.add_argument(
        "--data-file", 
        type=str, 
        default="../data/training_dataset.json",
        help="Path to training dataset JSON file"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="../models/prompt_injection_model",
        help="Directory to save trained model"
    )
    parser.add_argument(
        "--max-length", 
        type=int, 
        default=256,
        help="Maximum sequence length for tokenization"
    )
    parser.add_argument(
        "--epochs", 
        type=int, 
        default=4,
        help="Number of training epochs"
    )
    parser.add_argument(
        "--batch-size", 
        type=int, 
        default=16,
        help="Training batch size"
    )
    parser.add_argument(
        "--learning-rate", 
        type=float, 
        default=3e-5,
        help="Learning rate"
    )
    
    args = parser.parse_args()
    
    # Convert relative paths to absolute
    script_dir = Path(__file__).parent
    data_file = script_dir / args.data_file
    output_dir = script_dir / args.output_dir
    
    logger.info("🚀 Starting Prompt Injection Detection Model Training")
    logger.info("=" * 60)
    
    # Initialize processors
    data_processor = DataProcessor()
    model_utils = ModelUtils()
    
    # Load and process data
    logger.info(f"📁 Loading dataset from: {data_file}")
    df = data_processor.load_dataset(str(data_file))
    
    # Analyze distribution
    stats = data_processor.analyze_distribution(df)
    logger.info(f"Dataset statistics: {stats}")
    
    # Encode labels
    df_encoded = data_processor.encode_labels(df)
    
    # Prepare datasets for training
    train_dataset, val_dataset = data_processor.prepare_for_training(df_encoded)
    
    # Initialize model and tokenizer
    tokenizer, model = model_utils.initialize_model_and_tokenizer(num_labels=2)
    
    # Tokenize datasets
    train_dataset = model_utils.tokenize_dataset(train_dataset, max_length=args.max_length)
    val_dataset = model_utils.tokenize_dataset(val_dataset, max_length=args.max_length)
    
    # Create training arguments
    training_args = model_utils.create_training_arguments(
        output_dir=str(output_dir.parent / "results"),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.learning_rate
    )
    
    # Train model
    trainer = model_utils.train_model(train_dataset, val_dataset, training_args)
    
    # Save model
    model_utils.save_model(trainer, str(output_dir))
    
    logger.info("✅ Training completed successfully!")
    logger.info(f"📁 Model saved to: {output_dir}")
    logger.info("🔍 Test the model with: python scripts/test_model.py")


if __name__ == "__main__":
    main()
