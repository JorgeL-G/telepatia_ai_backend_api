import logging

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from app.config import settings

logger = logging.getLogger(__name__)

class MongoDBConnection:
    """Class to manage MongoDB connection."""
    
    def __init__(self):
        self.uri = settings.mongodb_url
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))

    def connect_to_mongo(self) -> None:
        """Connect to MongoDB."""
        try:
            self.client.admin.command("ping")
            logger.info(f"Successfully connected to MongoDB: {settings.mongodb_url}")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise

    def close_mongo_connection(self) -> None:
        """Close MongoDB connection."""
        
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


