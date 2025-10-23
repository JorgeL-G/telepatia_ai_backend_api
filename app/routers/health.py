import logging

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict
from app.database import MongoDBConnection
from app.schemas.health import DbConnectionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/db_connection", response_model=DbConnectionResponse)
async def db_connection_status() -> DbConnectionResponse:
    """
    Endpoint to verify MongoDB database connection.
    
    Returns:
        HealthResponse: Database connection status
    """
    try:
        # Verify MongoDB connectivity using PyMongo
        client = MongoDBConnection()
        connection = client.connect_to_mongo()
        database_status = "connected"
        
    except Exception as e:
        logger.error(f"Error verifying MongoDB: {e}")
        database_status = "disconnected"
    
    return DbConnectionResponse(
        timestamp=datetime.utcnow(),
        database_status=database_status,
        version="1.0.0"
    )


@router.get("/ping")
async def ping() -> Dict[str, str]:
    """
    Simple ping endpoint to verify that the API is working.
    
    Returns:
        Dict[str, str]: Response message
    """
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}
