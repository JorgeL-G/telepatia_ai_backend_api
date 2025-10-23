import logging
from transformers import pipeline
from typing import Optional

logger = logging.getLogger(__name__)

MODEL_NAME = "facebook/wav2vec2-large-xlsr-53-spanish"


class AudioService:
    """
    Singleton class for managing the ASR audio pipeline.
    """
    _instance = None
    _audio_pipeline = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioService, cls).__new__(cls)
        return cls._instance
    
    def load_audio_pipeline(self):
        """
        Load the ASR pipeline. Returns True if successful.
        
        Returns:
            bool: True if the pipeline loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading ASR model: {MODEL_NAME}")
            self._audio_pipeline = pipeline("automatic-speech-recognition", model=MODEL_NAME)
            logger.info("ASR model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading ASR model: {str(e)}")
            return False
    
    def get_audio_pipeline(self):
        """
        Get the pipeline, loading it lazily if necessary.
        
        Returns:
            Optional[pipeline]: The ASR pipeline or None if it cannot be loaded
        """
        if self._audio_pipeline is None:
            logger.info("Pipeline not preloaded, attempting lazy loading...")
            self.load_audio_pipeline()
        return self._audio_pipeline
