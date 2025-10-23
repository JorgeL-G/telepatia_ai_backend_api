import pytest
import asyncio
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_mongodb():
    """Mock MongoDB connection."""
    with patch('app.database.MongoDBConnection') as mock:
        mock_instance = Mock()
        mock_instance.connect_to_mongo.return_value = None
        mock_instance.close_mongo_connection.return_value = None
        mock_instance.insert_document.return_value = "test_document_id"
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_google_genai():
    """Mock Google GenAI service."""
    with patch('app.services.google_genai_service.GoogleGenAIService') as mock:
        mock_instance = Mock()
        mock_instance.initialize_client.return_value = True
        mock_instance.generate_content.return_value = '{"test": "response"}'
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_audio_service():
    """Mock Audio service."""
    with patch('app.services.audio_service.AudioService') as mock:
        mock_instance = Mock()
        mock_instance.load_audio_pipeline.return_value = True
        mock_instance.get_audio_pipeline.return_value = Mock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return "Hello! 😊 This is a test text with emojis and special characters... How are you?"

@pytest.fixture
def sample_invalid_text():
    """Sample invalid text for testing."""
    return "123456789"

@pytest.fixture
def sample_medical_text():
    """Sample medical text for testing."""
    return "The patient presents fever and headache"
