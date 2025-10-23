import os
import re
import librosa
import numpy as np
import logging
import tempfile
import soundfile
import io

from pydantic import BaseModel
from typing import Optional, Union
from fastapi import UploadFile
from app.services.audio_service import AudioService


logger = logging.getLogger(__name__)


class TextSimplificationRequest(BaseModel):
    """
    Model for the text simplification endpoint request.
    """
    text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello! 😊 This is a text with emojis and special characters... How are you?"
            }
        }


class TextSimplificationResponse(BaseModel):
    """
    Model for the text simplification endpoint response.
    """
    original_text: str
    validate_text: str
    success: bool
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_text": "Hello! 😊 This is a text with emojis and special characters... How are you?",
                "validate_text": "Hello! This is a text with emojis and special characters... How are you?",
                "success": True,
                "message": "Text simplified successfully"
            }
        }


class AudioProcessingRequest(BaseModel):
    """
    Model for the audio processing endpoint request.
    """
    audio_file: UploadFile
    
    class Config:
        json_schema_extra = {
            "example": {
                "audio_file": "Audio file (.wav, .mp3, .flac, .m4a, .ogg)"
            }
        }


class AudioProcessingResponse(BaseModel):
    """
    Model for the audio processing endpoint response.
    """
    filename: str
    transcribed_text: str
    simplified_text: str
    success: bool
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "audio_file.wav",
                "transcribed_text": "Hello! 😊 This is transcribed text from audio... How are you?",
                "simplified_text": "Hello This is transcribed text from audio How are you",
                "success": True,
                "message": "Audio processed successfully"
            }
        }


class TextGenerationRequest(BaseModel):
    """
    Model for the text generation endpoint request.
    """
    prompt: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "The patient presents fever"
            }
        }


class TextGenerationResponse(BaseModel):
    """
    Model for the text generation endpoint response.
    """
    prompt: str
    generated_text: str
    success: bool
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "The future of artificial intelligence is",
                "generated_text": "The future of artificial intelligence is promising and full of possibilities...",
                "success": True,
                "message": "Text generated successfully"
            }
        }


class MessageProcessor(BaseModel):
    """
    Builder pattern class for processing and validating text and audio messages.
    """
    
    # Main attributes
    audio: Optional[Union[str, bytes, np.ndarray]] = None
    text: Optional[str] = None
    processed_text: Optional[str] = None
    audio_to_text_transformed: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def validate_audio_format(self, audio_file: Optional[UploadFile] = None) -> bool:
        """
        Validates that the audio has the correct format.
        
        Args:
            audio_file: UploadFile object containing the audio file
            
        Returns:
            bool: True if the format is valid, False otherwise
        """
        try:
            if audio_file:
                # Check file extension
                valid_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
                filename = audio_file.filename.lower()
                if not filename:
                    logger.error("Audio file has no filename")
                    return False
                
                _, ext = os.path.splitext(filename)
                if ext not in valid_extensions:
                    logger.error(f"Unsupported audio format: {ext}")
                    return False
                
                # Check file size (basic validation)
                if audio_file.size == 0:
                    logger.error("Audio file is empty")
                    return False
                
                # Create temporary file to validate audio content
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                    # Read file content
                    content = audio_file.file.read()
                    temp_file.write(content)
                    temp_file.flush()
                    
                    # Reset file pointer for potential future use
                    audio_file.file.seek(0)
                    
                    # Load and validate audio with librosa
                    audio_data, sample_rate = librosa.load(temp_file.name, sr=None)
                    
                    # Clean up temporary file
                    os.unlink(temp_file.name)
                
                # Validate that audio is not empty
                if len(audio_data) == 0:
                    logger.error("Audio file is empty")
                    return False
                
                # Validate minimum duration (at least 0.1 seconds)
                duration = len(audio_data) / sample_rate
                if duration < 0.1:
                    logger.error("Audio is too short (less than 0.1 seconds)")
                    return False
                
                # Validate that it's not just silence
                if np.max(np.abs(audio_data)) < 0.001:
                    logger.error("Audio appears to be only silence")
                    return False
                
                logger.info(f"Valid audio: {duration:.2f}s, {sample_rate}Hz")
                return True
                
            elif self.audio is not None:
                # Validate already loaded audio
                if isinstance(self.audio, np.ndarray):
                    if len(self.audio) == 0:
                        logger.error("Audio array is empty")
                        return False
                    if np.max(np.abs(self.audio)) < 0.001:
                        logger.error("Audio array appears to be only silence")
                        return False
                    return True
                elif isinstance(self.audio, (str, bytes)):
                    # For audio data in string or bytes, basic validation
                    return len(self.audio) > 0
                
            else:
                logger.error("No audio provided for validation")
                return False
                
        except Exception as e:
            logger.error(f"Error validating audio format: {str(e)}")
            return False
    
    def validate_text(self, text: Optional[str] = None) -> bool:
        """
        Validates that the input text is correct.
        
        Args:
            text: Text to validate (optional if text is already loaded)
            
        Returns:
            bool: True if the text is valid, False otherwise
        """
        try:
            text_to_validate = text if text is not None else self.text
            
            if not text_to_validate:
                logger.error("No text provided for validation")
                return False
            
            # Convert to string if it's not
            text_str = str(text_to_validate).strip()
            
            # Validate that it's not empty
            if not text_str:
                logger.error("Text is empty")
                return False
            
            # Validate minimum length
            if len(text_str) < 2:
                logger.error("Text is too short (less than 2 characters)")
                return False
            
            # Validate maximum length (avoid excessively long texts)
            if len(text_str) > 10000:
                logger.error("Text is too long (more than 10,000 characters)")
                return False
            
            # Validate that it contains at least some alphabetic characters
            alphabetic_chars = re.findall(r'[a-zA-ZáéíóúÁÉÍÓÚñÑ]', text_str)
            if len(alphabetic_chars) < 1:
                logger.error("Text must contain at least one alphabetic character")
                return False
            
            # Validate that it's not just numbers
            only_numbers = re.match(r'^[\d\s\.\,\-\+\(\)]+$', text_str)
            if only_numbers:
                logger.error("Text cannot be only numbers")
                return False
            
            logger.info(f"Valid text: {len(text_str)} characters")
            return True
            
        except Exception as e:
            logger.error(f"Error validating text: {str(e)}")
            return False
    
    def transform_audio_to_text(self, audio_bytes: bytes) -> Optional[str]:
        """
        Transforms audio to text using Lanching and the facebook/wav2vec2-large-xlsr-53-spanish model.
        
        Args:
            audio_bytes: Audio bytes to transcribe
            
        Returns:
            str: Transcribed text from audio, None if there's an error
        """
        try:
            if not audio_bytes:
                logger.error("No audio bytes provided for transcription")
                return None
            
            logger.info("Getting ASR pipeline...")
            pipe = AudioService().get_audio_pipeline()
            
            if pipe is None:
                logger.error("ASR pipeline not available")
                return None
            
            logger.info("Starting audio to text transcription...")
            logger.info("Using model: facebook/wav2vec2-large-xlsr-53-spanish")

            transcribed_text = pipe(audio_bytes)["text"]
            # Save result
            self.audio_to_text_transformed = transcribed_text
            
            logger.info("Transcription completed successfully")
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Error transforming audio to text: {str(e)}")
            return None
    
    def simplify_text(self, text: Optional[str] = None) -> Optional[str]:
        """
        Simplifies text by removing emoticons, unnecessary characters and line breaks.
        
        Args:
            text: Text to simplify (optional if text is already loaded)
            
        Returns:
            str: Simplified text, None if there's an error
        """
        try:
            text_to_simplify = text if text is not None else self.text
            
            if not text_to_simplify:
                logger.error("No text provided for simplification")
                return None
            
            # Convert to string
            text_str = str(text_to_simplify)
            
            # Remove emoticons and emojis
            # Pattern to detect emojis and emoticons
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F300-\U0001F5FF"  # symbols and pictograms
                "\U0001F680-\U0001F6FF"  # transport
                "\U0001F1E0-\U0001F1FF"  # flags
                "\U00002702-\U000027B0"  # miscellaneous symbols
                "\U000024C2-\U0001F251"  # additional symbols
                "]+", flags=re.UNICODE
            )
            text_without_emojis = emoji_pattern.sub('', text_str)
            
            # Remove unnecessary special characters
            # Keep only letters, numbers, spaces, periods, commas, question and exclamation marks
            clean_text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', text_without_emojis)
            
            # Remove line breaks and replace with spaces
            text_without_breaks = re.sub(r'\n+', ' ', clean_text)
            text_without_breaks = re.sub(r'\r+', ' ', text_without_breaks)
            
            # Remove multiple spaces and replace with single space
            text_without_multiple_spaces = re.sub(r'\s+', ' ', text_without_breaks)
            
            # Remove leading and trailing spaces
            final_text = text_without_multiple_spaces.strip()
            
            # Validate that simplified text is not empty
            if not final_text:
                logger.warning("Simplified text is empty")
                return None
            
            # Save result
            self.processed_text = final_text
            
            logger.info(f"Simplified text: {len(final_text)} characters")
            return final_text
            
        except Exception as e:
            logger.error(f"Error simplifying text: {str(e)}")
            return None
