"""
Model utilities for training and evaluation.
"""

import os
import numpy as np
from typing import Dict, Any, Optional
from transformers import (
    DistilBertTokenizerFast, 
    DistilBertForSequenceClassification,
    Trainer, 
    TrainingArguments
)
from datasets import Dataset
import logging

logger = logging.getLogger(__name__)


class ModelUtils:
    """Utility class for model training and evaluation."""
    
    def __init__(self, model_name: str = "distilbert-base-uncased"):
        """
        Initialize model utilities.
        
        Args:
            model_name: Pre-trained model name from HuggingFace
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
    
    def initialize_model_and_tokenizer(self, num_labels: int = 2) -> tuple:
        """
        Initialize tokenizer and model.
        
        Args:
            num_labels: Number of classification labels
            
        Returns:
            Tuple of (tokenizer, model)
        """
        logger.info(f"🔤 Initializing tokenizer and model: {self.model_name}")
        
        self.tokenizer = DistilBertTokenizerFast.from_pretrained(self.model_name)
        self.model = DistilBertForSequenceClassification.from_pretrained(
            self.model_name, 
            num_labels=num_labels
        )
        
        logger.info("✅ Model and tokenizer initialized successfully")
        return self.tokenizer, self.model
    
    def tokenize_dataset(self, dataset: Dataset, text_column: str = "text", 
                        max_length: int = 256) -> Dataset:
        """
        Tokenize dataset for training.
        
        Args:
            dataset: Input dataset
            text_column: Name of the text column
            max_length: Maximum sequence length
            
        Returns:
            Tokenized dataset
        """
        if self.tokenizer is None:
            raise ValueError("Tokenizer not initialized. Call initialize_model_and_tokenizer() first.")
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples[text_column], 
                padding="max_length", 
                truncation=True, 
                max_length=max_length
            )
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        logger.info(f"✅ Tokenized dataset: {len(tokenized_dataset)} samples")
        
        return tokenized_dataset
    
    def create_training_arguments(self, output_dir: str = "./results", 
                                 **kwargs) -> TrainingArguments:
        """
        Create training arguments with sensible defaults.
        
        Args:
            output_dir: Directory to save training outputs
            **kwargs: Additional training arguments
            
        Returns:
            TrainingArguments object
        """
        default_args = {
            "output_dir": output_dir,
            "eval_strategy": "steps",
            "eval_steps": 50,
            "save_strategy": "steps",
            "save_steps": 50,
            "learning_rate": 3e-5,
            "per_device_train_batch_size": 16,
            "per_device_eval_batch_size": 16,
            "num_train_epochs": 4,
            "weight_decay": 0.01,
            "logging_dir": "./logs",
            "logging_steps": 10,
            "save_total_limit": 3,
            "load_best_model_at_end": True,
            "metric_for_best_model": "eval_loss",
            "greater_is_better": False,
            "warmup_steps": 100,
            "seed": 42
        }
        
        # Override defaults with provided kwargs
        default_args.update(kwargs)
        
        return TrainingArguments(**default_args)
    
    def compute_metrics(self, eval_pred) -> Dict[str, float]:
        """
        Compute evaluation metrics.
        
        Args:
            eval_pred: Evaluation predictions from trainer
            
        Returns:
            Dictionary of computed metrics
        """
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        # Calculate accuracy
        accuracy = (predictions == labels).mean()
        
        # Calculate per-class metrics
        unique_labels = np.unique(labels)
        class_metrics = {}
        
        for label in unique_labels:
            label_mask = labels == label
            if label_mask.sum() > 0:
                class_accuracy = (predictions[label_mask] == label).mean()
                class_metrics[f"class_{label}_accuracy"] = class_accuracy
        
        metrics = {
            "accuracy": accuracy,
            **class_metrics
        }
        
        return metrics
    
    def train_model(self, train_dataset: Dataset, eval_dataset: Dataset,
                   training_args: Optional[TrainingArguments] = None) -> Trainer:
        """
        Train the model.
        
        Args:
            train_dataset: Training dataset
            eval_dataset: Evaluation dataset
            training_args: Training arguments (optional)
            
        Returns:
            Trained Trainer object
        """
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model and tokenizer not initialized")
        
        if training_args is None:
            training_args = self.create_training_arguments()
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=self.tokenizer,
            compute_metrics=self.compute_metrics,
        )
        
        logger.info("🏋️ Starting model training...")
        trainer.train()
        
        # Evaluate final model
        logger.info("📈 Evaluating final model...")
        eval_results = trainer.evaluate()
        
        for key, value in eval_results.items():
            if isinstance(value, float):
                logger.info(f"  {key}: {value:.4f}")
            else:
                logger.info(f"  {key}: {value}")
        
        return trainer
    
    def save_model(self, trainer: Trainer, output_dir: str) -> None:
        """
        Save trained model and tokenizer.
        
        Args:
            trainer: Trained Trainer object
            output_dir: Directory to save the model
        """
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"💾 Saving model to {output_dir}...")
        trainer.save_model(output_dir)
        
        if self.tokenizer:
            self.tokenizer.save_pretrained(output_dir)
        
        logger.info("✅ Model saved successfully!")
    
    def evaluate_model(self, trainer: Trainer, dataset: Dataset) -> Dict[str, Any]:
        """
        Evaluate model on a dataset.
        
        Args:
            trainer: Trained Trainer object
            dataset: Dataset to evaluate on
            
        Returns:
            Dictionary of evaluation metrics
        """
        logger.info("📊 Evaluating model...")
        results = trainer.evaluate(eval_dataset=dataset)
        
        logger.info("Evaluation results:")
        for key, value in results.items():
            if isinstance(value, float):
                logger.info(f"  {key}: {value:.4f}")
            else:
                logger.info(f"  {key}: {value}")
        
        return results
