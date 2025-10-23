# Telepatía AI Backend API

Telepatía backend API - API for capture, validation, storage, transcription and structuring of clinical information from audio or text. Designed for fast MVPs with FastAPI (Python).

## 🚀 Features

- **Audio Processing**: Transcribe audio files to text using ASR (Automatic Speech Recognition)
- **Text Processing**: Validate and simplify text input
- **Medical Information Extraction**: Extract structured medical data from text using AI
- **Database Storage**: Store processed messages in MongoDB
- **Health Monitoring**: Database connection status and API health checks
- **CORS Support**: Cross-origin resource sharing enabled

## 📋 Prerequisites

- **Python 3.11+**
- **MongoDB** (local or cloud instance)
- **Google GenAI API Key** (for medical information extraction)
- **Conda** (recommended) or pip

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd telepatia_ai_backend_api
```

### 2. Create Virtual Environment
```bash
# Using conda (recommended)
conda create -n telepatia_ai python=3.11
conda activate telepatia_ai

# Or using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```bash
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017

# Google GenAI Configuration
GOOGLE_API_KEY=your_google_genai_api_key_here

# Application Configuration (optional)
APP_NAME=Telepatía AI Backend API
APP_VERSION=1.0.0
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

### 5. Start MongoDB
Make sure MongoDB is running:
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or start your local MongoDB service
mongod
```

## 🚀 Running the Application

### Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔗 API Endpoints

### Health Endpoints
- `GET /health/ping` - Simple ping endpoint
- `GET /health/db_connection` - MongoDB connection status

### Message Processing Endpoints
- `POST /message/validate-process-text` - Validate and simplify text
- `POST /message/validate-process-audio` - Process audio file and return transcribed text
- `POST /message/generate-text` - Extract structured medical information from text

## 📝 API Usage Examples

### 1. Text Validation and Simplification
```bash
curl -X POST "http://localhost:8000/message/validate-process-text" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello! 😊 This is a text with emojis and special characters... How are you?"}'
```

### 2. Audio Processing
```bash
curl -X POST "http://localhost:8000/message/validate-process-audio" \
     -F "audio_file=@your_audio_file.wav"
```

### 3. Medical Information Extraction
```bash
curl -X POST "http://localhost:8000/message/generate-text" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "The patient presents fever and headache"}'
```

## 🏗️ Project Structure

```
telepatia_ai_backend_api/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration and environment variables
│   ├── database.py                # MongoDB connection and operations
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── medical_extraction_prompt.py  # Medical AI prompt templates
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py              # Health check endpoints
│   │   └── message.py             # Message processing endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── health.py              # Health response schemas
│   │   └── message.py             # Message processing schemas
│   └── services/
│       ├── __init__.py
│       ├── audio_service.py       # Audio processing service
│       └── google_genai_service.py # Google GenAI integration
├── requirements.txt               # Python dependencies
├── README.md                     # This file
└── .env                          # Environment variables (create this)
```

## 🔧 Configuration

### Environment Variables
- `MONGODB_URL`: MongoDB connection string (default: mongodb://localhost:27017)
- `GOOGLE_API_KEY`: Google GenAI API key (required for medical extraction)
- `APP_NAME`: Application name (default: Telepatía AI Backend API)
- `APP_VERSION`: Application version (default: 1.0.0)
- `DEBUG`: Debug mode (default: true)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

### Supported Audio Formats
- WAV (.wav)
- MP3 (.mp3)
- FLAC (.flac)
- M4A (.m4a)
- OGG (.ogg)

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_health.py -v

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Structure
```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_health.py           # Health endpoint tests (2 tests)
├── test_text_processing.py  # Text processing tests (4 tests)
└── test_services.py         # Service tests (3 tests)
```

### Pre-commit Hooks
Tests run automatically before each commit:
```bash
# Install pre-commit hooks
pre-commit install

# Test pre-commit manually
pre-commit run --all-files
```

### Manual Testing

#### Health Check
```bash
curl http://localhost:8000/health/ping
```

#### Database Connection
```bash
curl http://localhost:8000/health/db_connection
```

## 🐛 Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Check the `MONGODB_URL` in your `.env` file

2. **Google GenAI Service Error**
   - Verify your `GOOGLE_API_KEY` is valid
   - Check API quota and billing

3. **Audio Processing Error**
   - Ensure audio file format is supported
   - Check file size (not too large)
   - Verify audio is not corrupted

4. **Dependencies Installation Error**
   - Use Python 3.11+
   - Try upgrading pip: `pip install --upgrade pip`
   - Install system dependencies for audio processing libraries

## 📦 Dependencies

Key dependencies include:
- **FastAPI**: Web framework
- **MongoDB**: Database (PyMongo, Motor)
- **Transformers**: ASR model (facebook/wav2vec2-large-xlsr-53-spanish)
- **Google GenAI**: AI text generation
- **Librosa**: Audio processing
- **Pydantic**: Data validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions, please open an issue in the repository.