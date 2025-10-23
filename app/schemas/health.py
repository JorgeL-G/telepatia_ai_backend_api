from pydantic import BaseModel
from datetime import datetime


class DbConnectionResponse(BaseModel):
    """Response model for MongoDB database connection endpoint."""
    timestamp: datetime
    database_status: str
    version: str
