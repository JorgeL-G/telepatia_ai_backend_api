import pytest
from unittest.mock import patch, Mock
from app.services.audio_service import AudioService
from app.services.google_genai_service import GoogleGenAIService
from app.schemas.message import MessageProcessor

@pytest.mark.unit
class TestServices:
    """Test core services functionality."""
    
    @patch('app.services.audio_service.pipeline')
    def test_audio_service_initialization(self, mock_pipeline):
        """Test AudioService initialization."""
        # Mock the pipeline loading
        mock_pipeline.return_value = Mock()
        
        service = AudioService()
        result = service.load_audio_pipeline()
        
        assert result is True
        assert service._audio_pipeline is not None
    
    @patch('app.services.google_genai_service.genai')
    def test_google_genai_service_initialization(self, mock_genai):
        """Test GoogleGenAIService initialization."""
        # Mock the client creation
        mock_client = Mock()
        mock_genai.Client.return_value = mock_client
        
        service = GoogleGenAIService()
        result = service.initialize_client()
        
        assert result is True
        assert service._client is not None
    
    def test_message_processor_basic_validation(self):
        """Test MessageProcessor basic text validation."""
        processor = MessageProcessor(text="Hello world")
        
        # Test text validation
        assert processor.validate_text() is True
        
        # Test text simplification
        simplified = processor.simplify_text()
        assert simplified is not None
        assert simplified == "Hello world"
