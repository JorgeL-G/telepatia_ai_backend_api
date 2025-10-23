import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from app.schemas.message import MessageProcessor

@pytest.mark.unit
class TestTextProcessing:
    """Test text processing functionality."""
    
    def test_validate_text_valid(self, sample_text):
        """Test text validation with valid text."""
        processor = MessageProcessor(text=sample_text)
        result = processor.validate_text()
        
        assert result is True
    
    def test_validate_text_invalid(self, sample_invalid_text):
        """Test text validation with invalid text (only numbers)."""
        processor = MessageProcessor(text=sample_invalid_text)
        result = processor.validate_text()
        
        assert result is False
    
    def test_simplify_text_with_emojis(self, sample_text):
        """Test text simplification removes emojis and special characters."""
        processor = MessageProcessor(text=sample_text)
        simplified = processor.simplify_text()
        
        assert simplified is not None
        assert "😊" not in simplified
        assert len(simplified) < len(sample_text)
        assert simplified.strip() != ""

@pytest.mark.integration
class TestTextProcessingEndpoints:
    """Test text processing API endpoints."""
    
    @patch('app.database.MongoDBConnection')
    def test_validate_process_text_endpoint(self, mock_mongodb, client: TestClient, sample_text):
        """Test POST /message/validate-process-text endpoint."""
        # Mock database operations
        mock_instance = mock_mongodb.return_value
        mock_instance.connect_to_mongo.return_value = None
        mock_instance.insert_document.return_value = "test_id"
        mock_instance.close_mongo_connection.return_value = None
        
        response = client.post(
            "/message/validate-process-text",
            json={"text": sample_text}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["original_text"] == sample_text
        assert "validate_text" in data
        assert data["message"] == "Text validated and simplified successfully"
