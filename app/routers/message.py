import logging

from fastapi import APIRouter, HTTPException, UploadFile, File
from app.schemas.message import TextSimplificationRequest, TextSimplificationResponse, AudioProcessingResponse, TextGenerationRequest, TextGenerationResponse, MessageProcessor
from app.database import MongoDBConnection
from app.services.google_genai_service import GoogleGenAIService
from app.prompts.medical_extraction_prompt import get_medical_extraction_prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/message", tags=["message"])


def save_message_to_db(message_type: str, message: str, simplified_message: str, audio_bytes: bytes = None) -> bool:
    """
    Helper function to save messages to the database.
    
    Args:
        message_type: Message type ("text" or "audio")
        message: Original or transcribed message
        simplified_message: Simplified message
        audio_bytes: Audio bytes (only for "audio" type)
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        db = MongoDBConnection()
        db.connect_to_mongo()
        
        document = {
            "message_type": message_type,
            "message": message,
            "simplified_message": simplified_message,
            "audio_bytes": audio_bytes
        }
        
        document_id = db.insert_document("messages", document)
        logger.info(f"{message_type} message saved with ID: {document_id}")
        
        # Close connection
        db.close_mongo_connection()
        return True
        
    except Exception as e:
        logger.error(f"Error saving message to database: {e}")
        return False


@router.post("/validate-process-text", response_model=TextSimplificationResponse)
async def validate_process_text(request: TextSimplificationRequest):
    """
    Endpoint to validate and simplify text using the Builder pattern with MessageProcessor.
    
    Args:
        request: Object with the text to validate and simplify
        
    Returns:
        TextSimplificationResponse: Response with original and simplified text
    """
    try:
        logger.info(f"Processing text validation and simplification request: {len(request.text)} characters")
        
        # Use Builder pattern with MessageProcessor
        processor = MessageProcessor(text=request.text)
        
        # Step 1: Validate the text using the validate_text method
        if not processor.validate_text():
            raise HTTPException(
                status_code=400,
                detail="The provided text is not valid. Please verify that it contains at least one alphabetic character and is not only numbers."
            )
        
        # Step 2: Simplify the text using the simplify_text method
        simplified_text = processor.simplify_text()
        
        if simplified_text is None:
            raise HTTPException(
                status_code=500,
                detail="Error simplifying the text. The result is empty."
            )
        
        # Step 3: Save to database before returning
        save_message_to_db("text", request.text, simplified_text)
        
        # Create successful response
        response = TextSimplificationResponse(
            original_text=request.text,
            validate_text=simplified_text,
            success=True,
            message="Text validated and simplified successfully"
        )
        
        logger.info(f"Validation and simplification completed: {len(simplified_text)} characters")
        return response
        
    except HTTPException:
        # Re-raise HTTPException to maintain status code
        raise
    except Exception as e:
        logger.error(f"Unexpected error in validate_text: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/validate-process-audio", response_model=AudioProcessingResponse)
async def validate_process_audio(audio_file: UploadFile = File(...)):
    """
    Endpoint to process user audio and return simplified text using the Builder pattern with MessageProcessor.
    
    Args:
        audio_file: Audio file uploaded by the user
        
    Returns:
        AudioProcessingResponse: Response with transcribed and simplified text
    """
    try:
        logger.info(f"Processing audio request: {audio_file.filename}")
        
        # Use Builder pattern with MessageProcessor
        processor = MessageProcessor()
        
        # Step 1: Validate the audio format
        if not processor.validate_audio_format(audio_file):
            raise HTTPException(
                status_code=400,
                detail="The audio file is not valid. Please verify that it has a supported format (.wav, .mp3, .flac, .m4a, .ogg) and is not empty."
            )
        
        # Step 2: Read audio_bytes BEFORE transcribing (since the file gets consumed)
        audio_bytes = audio_file.file.read()
        
        # Step 3: Transform audio to text
        transcribed_text = processor.transform_audio_to_text(audio_bytes)
        
        if transcribed_text is None:
            raise HTTPException(
                status_code=500,
                detail="Error transcribing the audio. Could not convert audio to text."
            )
        
        # Step 4: Validate the transcribed text
        processor.text = transcribed_text
        if not processor.validate_text():
            raise HTTPException(
                status_code=400,
                detail="The transcribed text is not valid. The audio might contain only noise or be empty."
            )
        
        # Step 5: Simplify the transcribed text
        simplified_text = processor.simplify_text()
        
        if simplified_text is None:
            raise HTTPException(
                status_code=500,
                detail="Error simplifying the transcribed text. The result is empty."
            )
        
        # Step 6: Save to database before returning
        save_message_to_db("audio", transcribed_text, simplified_text, audio_bytes)
        
        # Create successful response
        response = AudioProcessingResponse(
            filename=audio_file.filename,
            transcribed_text=transcribed_text,
            simplified_text=simplified_text,
            success=True,
            message="Audio processed successfully"
        )
        
        logger.info(f"Audio processing completed: {len(transcribed_text)} characters transcribed, {len(simplified_text)} characters simplified")
        return response
        
    except HTTPException:
        # Re-raise HTTPException to maintain status code
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_audio_endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/generate-text", response_model=TextGenerationResponse)
async def generate_text(request: TextGenerationRequest):
    """
    Endpoint to extract structured medical information from text using AI.
    Uses a predefined medical extraction prompt to analyze user input and return JSON.
    
    Args:
        request: Object with the text to analyze and generation parameters
        
    Returns:
        TextGenerationResponse: Response with the structured medical data in JSON format
    """
    try:
        logger.info(f"Processing text generation request: '{request.prompt[:50]}...'")
        
        # Combine medical prompt with user text using the function
        full_prompt = get_medical_extraction_prompt(request.prompt)
        
        # Generate content using Google GenAI
        generated_text = GoogleGenAIService().generate_content(full_prompt)
        
        if generated_text is None:
            raise HTTPException(
                status_code=500,
                detail="Text generation service is not available. Please try again later."
            )
        
        # Validate that we have generated content
        if not generated_text:
            raise HTTPException(
                status_code=500,
                detail="No text was generated. Please try with a different prompt."
            )
        
        # Create successful response
        response = TextGenerationResponse(
            prompt=request.prompt,
            generated_text=generated_text,
            success=True,
            message="Text generated successfully"
        )
        
        logger.info(f"Text generation completed: {len(generated_text)} characters generated")
        return response
        
    except HTTPException:
        # Re-raise HTTPException to maintain status code
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_text: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
