import logging
from typing import Optional
import google.genai as genai
from app.config import settings

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-2.0-flash-exp"


class GoogleGenAIService:
    """
    Singleton class for managing Google GenAI text generation.
    """
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GoogleGenAIService, cls).__new__(cls)
        return cls._instance
    
    def initialize_client(self) -> bool:
        """
        Initialize the Google GenAI client. Returns True if successful.
        
        Returns:
            bool: True if the client initialized successfully, False otherwise
        """
        try:
            if not settings.google_api_key:
                logger.error("Google API key is not configured")
                return False
                
            logger.info(f"Initializing Google GenAI client with model: {MODEL_NAME}")
            self._client = genai.Client(api_key=settings.google_api_key)
            logger.info("Google GenAI client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Google GenAI client: {str(e)}")
            return False
    
    def get_client(self):
        """
        Get the client, initializing it lazily if necessary.
        
        Returns:
            Optional[genai.Client]: The Google GenAI client or None if it cannot be initialized
        """
        if self._client is None:
            logger.info("Google GenAI client not preloaded, attempting lazy initialization...")
            self.initialize_client()
        return self._client
    
    def generate_content(self, prompt: str) -> Optional[str]:
        """
        Generate content using Google GenAI.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Optional[str]: Generated content or None if there's an error
        """
        try:
            client = self.get_client()
            if client is None:
                logger.error("Google GenAI client is not available")
                return None
            
            logger.info("Starting content generation with Google GenAI...")
            
            # Generate content using the model
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            
            # Extract the generated text
            generated_text = response.text.strip()
            
            logger.info(f"Content generation completed: {len(generated_text)} characters generated")
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return None
