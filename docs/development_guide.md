# Development Guide

## Project Structure

```
prompt-injection-detection/
├── src/                          # Source code
│   ├── __init__.py
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── routes.py            # Route handlers
│   │   └── models.py            # Pydantic models
│   ├── models/                   # ML models
│   │   ├── __init__.py
│   │   └── classifier.py        # Classifier implementation
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       ├── data_processor.py    # Data processing utilities
│       └── model_utils.py       # Model training utilities
├── scripts/                      # Executable scripts
│   ├── prepare_data.py          # Data preparation
│   ├── train_model.py           # Model training
│   ├── test_model.py            # Model testing
│   └── start_server.py          # Server startup
├── data/                         # Dataset files
│   ├── original_dataset.json
│   └── balanced_dataset.json
├── models/                       # Trained models
│   └── prompt_injection_model/
├── examples/                     # Usage examples
│   └── api_client_example.py
├── tests/                        # Test files
│   ├── conftest.py
│   ├── test_api.py
│   └── test_integration.py
├── docs/                         # Documentation
│   ├── api_documentation.md
│   └── development_guide.md
├── requirements.txt              # Python dependencies
├── README.md                     # Project overview
└── .env.example                  # Environment variables template
```

## Setup Development Environment

### 1. Clone Repository
```bash
git clone <repository-url>
cd prompt-injection-detection
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Development Workflow

### 1. Data Preparation
```bash
# Create sample dataset for development
python scripts/prepare_data.py --create-sample --output-file data/dev_dataset.json

# Or process existing dataset
python scripts/prepare_data.py --input-file data/raw_data.json --balance-method undersample
```

### 2. Model Training
```bash
# Train with default parameters
python scripts/train_model.py

# Train with custom parameters
python scripts/train_model.py --epochs 6 --batch-size 32 --learning-rate 2e-5
```

### 3. Model Testing
```bash
# Interactive testing
python scripts/test_model.py

# Test specific text
python scripts/test_model.py --text "Your test text here"

# Run predefined test samples
python scripts/test_model.py --test-samples
```

### 4. Start API Server
```bash
# Development server with auto-reload
python scripts/start_server.py --reload

# Production server
python scripts/start_server.py --host 0.0.0.0 --port 8000
```

## Code Organization

### API Layer (`src/api/`)
- **main.py**: FastAPI application setup, lifespan management
- **routes.py**: Request handlers and business logic
- **models.py**: Pydantic models for request/response validation

### Models Layer (`src/models/`)
- **classifier.py**: ML model wrapper with prediction logic

### Utils Layer (`src/utils/`)
- **data_processor.py**: Dataset loading, processing, and balancing
- **model_utils.py**: Model training, evaluation, and saving utilities

### Scripts (`scripts/`)
- Executable scripts for common tasks
- Each script is self-contained and can be run independently

## Testing

### Unit Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_api.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Integration Tests
```bash
# Start API server first
python scripts/start_server.py &

# Run integration tests
python -m pytest tests/test_integration.py -v
```

### Manual Testing
```bash
# Test API endpoints
python examples/api_client_example.py

# Interactive model testing
python scripts/test_model.py
```

## Adding New Features

### 1. New API Endpoint
1. Add route handler in `src/api/routes.py`
2. Add request/response models in `src/api/models.py`
3. Register route in `src/api/main.py`
4. Add tests in `tests/test_api.py`

### 2. New Model Feature
1. Extend `PromptInjectionClassifier` in `src/models/classifier.py`
2. Update training logic in `src/utils/model_utils.py` if needed
3. Add tests for new functionality

### 3. New Data Processing Feature
1. Add methods to `DataProcessor` in `src/utils/data_processor.py`
2. Update preparation script if needed
3. Add unit tests

## Code Quality

### Linting
```bash
# Install development dependencies
pip install flake8 black isort mypy

# Format code
black src/ scripts/ tests/
isort src/ scripts/ tests/

# Lint code
flake8 src/ scripts/ tests/

# Type checking
mypy src/
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Deployment

### Docker Deployment
```dockerfile
# Example Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY scripts/ ./scripts/
COPY models/ ./models/

EXPOSE 3000
CMD ["python", "scripts/start_server.py", "--host", "0.0.0.0", "--port", "3000"]
```

### Environment Variables
```bash
# Required for production
MODEL_PATH=/app/models/prompt_injection_model
HOST=0.0.0.0
PORT=3000
LOG_LEVEL=info

# Optional
MAX_TEXT_LENGTH=256
BATCH_SIZE_LIMIT=100
```

## Monitoring and Logging

### Application Logging
- Logs are configured in each script and module
- Use structured logging for production
- Log levels: DEBUG, INFO, WARNING, ERROR

### Health Checks
- `/health` endpoint provides service status
- Monitor model loading status
- Check disk space for model files

### Metrics
Consider adding metrics for:
- Request count and latency
- Prediction confidence distribution
- Error rates
- Model performance metrics

## Troubleshooting

### Common Issues

1. **Model not found**
   - Ensure model is trained: `python scripts/train_model.py`
   - Check model path in environment variables

2. **Import errors**
   - Verify Python path includes `src/` directory
   - Check all dependencies are installed

3. **CUDA/GPU issues**
   - Install appropriate PyTorch version for your system
   - Set CUDA_VISIBLE_DEVICES if needed

4. **Memory issues**
   - Reduce batch size in training
   - Use smaller model or optimize for inference

### Debug Mode
```bash
# Start server in debug mode
python scripts/start_server.py --log-level debug --reload

# Test with verbose output
python scripts/test_model.py --verbose
```
