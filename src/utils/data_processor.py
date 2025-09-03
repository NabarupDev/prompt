"""
Data processing utilities for dataset preparation and management.
"""

import json
import pandas as pd
from typing import List, Dict, Tuple, Any
from sklearn.preprocessing import LabelEncoder
from datasets import Dataset, ClassLabel
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Utility class for processing training data."""
    
    def __init__(self):
        self.label_encoder = LabelEncoder()
    
    def load_dataset(self, file_path: str) -> pd.DataFrame:
        """
        Load dataset from JSON file.
        
        Args:
            file_path: Path to the JSON dataset file
            
        Returns:
            pandas.DataFrame: Loaded dataset
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            logger.info(f"✅ Loaded dataset from {file_path}: {len(df)} samples")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to load dataset from {file_path}: {e}")
            raise
    
    def save_dataset(self, df: pd.DataFrame, file_path: str) -> None:
        """
        Save dataset to JSON file.
        
        Args:
            df: DataFrame to save
            file_path: Output file path
        """
        try:
            data = df.to_dict('records')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved dataset to {file_path}: {len(df)} samples")
            
        except Exception as e:
            logger.error(f"❌ Failed to save dataset to {file_path}: {e}")
            raise
    
    def analyze_distribution(self, df: pd.DataFrame, label_column: str = 'label') -> Dict[str, Any]:
        """
        Analyze label distribution in dataset.
        
        Args:
            df: Input DataFrame
            label_column: Name of the label column
            
        Returns:
            Dict containing distribution statistics
        """
        if label_column not in df.columns:
            raise ValueError(f"Column '{label_column}' not found in dataset")
        
        distribution = df[label_column].value_counts()
        total = len(df)
        
        stats = {
            'total_samples': total,
            'distribution': distribution.to_dict(),
            'percentages': {
                label: count / total * 100 
                for label, count in distribution.items()
            }
        }
        
        logger.info(f"Dataset distribution: {stats}")
        return stats
    
    def encode_labels(self, df: pd.DataFrame, label_column: str = 'label') -> pd.DataFrame:
        """
        Encode string labels to integers.
        
        Args:
            df: Input DataFrame
            label_column: Name of the label column to encode
            
        Returns:
            DataFrame with encoded labels
        """
        df_encoded = df.copy()
        df_encoded[label_column] = self.label_encoder.fit_transform(df[label_column])
        
        # Log the mapping
        label_mapping = dict(zip(
            self.label_encoder.classes_, 
            self.label_encoder.transform(self.label_encoder.classes_)
        ))
        logger.info(f"Label encoding: {label_mapping}")
        
        return df_encoded
    
    def balance_dataset(self, df: pd.DataFrame, label_column: str = 'label', 
                       method: str = 'undersample') -> pd.DataFrame:
        """
        Balance dataset by equalizing class distributions.
        
        Args:
            df: Input DataFrame
            label_column: Name of the label column
            method: Balancing method ('undersample' or 'oversample')
            
        Returns:
            Balanced DataFrame
        """
        distribution = df[label_column].value_counts()
        min_count = distribution.min()
        max_count = distribution.max()
        
        if method == 'undersample':
            # Sample min_count from each class
            balanced_dfs = []
            for label in distribution.index:
                class_df = df[df[label_column] == label].sample(n=min_count, random_state=42)
                balanced_dfs.append(class_df)
            
            balanced_df = pd.concat(balanced_dfs, ignore_index=True).sample(frac=1, random_state=42)
            logger.info(f"✅ Undersampled dataset to {len(balanced_df)} samples ({min_count} per class)")
            
        elif method == 'oversample':
            # Duplicate minority classes to match majority
            balanced_dfs = []
            for label in distribution.index:
                class_df = df[df[label_column] == label]
                if len(class_df) < max_count:
                    # Oversample with replacement
                    oversampled = class_df.sample(n=max_count, replace=True, random_state=42)
                    balanced_dfs.append(oversampled)
                else:
                    balanced_dfs.append(class_df)
            
            balanced_df = pd.concat(balanced_dfs, ignore_index=True).sample(frac=1, random_state=42)
            logger.info(f"✅ Oversampled dataset to {len(balanced_df)} samples ({max_count} per class)")
            
        else:
            raise ValueError(f"Unknown balancing method: {method}")
        
        return balanced_df
    
    def prepare_for_training(self, df: pd.DataFrame, text_column: str = 'text', 
                           label_column: str = 'label', test_size: float = 0.2) -> Tuple[Dataset, Dataset]:
        """
        Prepare dataset for model training.
        
        Args:
            df: Input DataFrame
            text_column: Name of the text column
            label_column: Name of the label column
            test_size: Proportion of data for validation
            
        Returns:
            Tuple of (train_dataset, val_dataset)
        """
        if text_column not in df.columns or label_column not in df.columns:
            raise ValueError(f"Required columns '{text_column}' or '{label_column}' not found")
        
        # Convert to HuggingFace dataset
        dataset = Dataset.from_pandas(df[[text_column, label_column]])
        
        # Cast label column to ClassLabel for stratification
        unique_labels = sorted(df[label_column].unique())
        dataset = dataset.cast_column(label_column, ClassLabel(names=[str(label) for label in unique_labels]))
        
        # Split with stratification
        split_dataset = dataset.train_test_split(
            test_size=test_size, 
            stratify_by_column=label_column, 
            seed=42
        )
        
        train_dataset = split_dataset["train"]
        val_dataset = split_dataset["test"]
        
        logger.info(f"✅ Prepared datasets - Train: {len(train_dataset)}, Val: {len(val_dataset)}")
        
        return train_dataset, val_dataset
