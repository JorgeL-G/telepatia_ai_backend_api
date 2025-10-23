import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, WriteError
from bson import ObjectId
from app.config import settings

logger = logging.getLogger(__name__)

class MongoDBConnection:
    """Class to manage MongoDB connection and document operations."""
    
    def __init__(self):
        self.uri = settings.mongodb_url
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        self.database: Optional[Database] = None

    def connect_to_mongo(self, database_name: str = "test") -> None:
        """Connect to MongoDB and set database."""
        try:
            self.client.admin.command("ping")
            self.database = self.client[database_name]
            logger.info(f"Successfully connected to MongoDB: {settings.mongodb_url}")
            logger.info(f"Using database: {database_name}")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise

    def close_mongo_connection(self) -> None:
        """Close MongoDB connection."""
        
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    def get_collection(self, collection_name: str) -> Collection:
        """
        Get a collection from the database.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection: MongoDB collection object
            
        Raises:
            Exception: If database is not connected
        """
        if self.database is None:
            raise Exception("Database not connected. Call connect_to_mongo() first.")
        
        return self.database[collection_name]

    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> Optional[str]:
        """
        Insert a single document into a collection.
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
            
        Returns:
            str: Inserted document ID, None if failed
            
        Raises:
            Exception: If database is not connected or insertion fails
        """
        try:
            if self.database is None:
                raise Exception("Database not connected. Call connect_to_mongo() first.")
            
            collection = self.get_collection(collection_name)

            # Add timestamp if not present
            if 'created_at' not in document:
                document['created_at'] = datetime.utcnow()
            
            if 'updated_at' not in document:
                document['updated_at'] = datetime.utcnow()
            
            result = collection.insert_one(document)
            document_id = str(result.inserted_id)
            
            logger.info(f"Document inserted successfully in collection '{collection_name}' with ID: {document_id}")
            return document_id
            
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error inserting document: {e}")
            raise Exception(f"Document with this key already exists: {e}")
        except WriteError as e:
            logger.error(f"Write error inserting document: {e}")
            raise Exception(f"Failed to insert document: {e}")
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            raise Exception(f"Failed to insert document: {e}")

    def insert_multiple_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple documents into a collection.
        
        Args:
            collection_name: Name of the collection
            documents: List of documents to insert
            
        Returns:
            List[str]: List of inserted document IDs
            
        Raises:
            Exception: If database is not connected or insertion fails
        """
        try:
            if self.database is None:
                raise Exception("Database not connected. Call connect_to_mongo() first.")
            
            collection = self.get_collection(collection_name)
            
            # Add timestamps to all documents
            current_time = datetime.utcnow()
            for doc in documents:
                if 'created_at' not in doc:
                    doc['created_at'] = current_time
                if 'updated_at' not in doc:
                    doc['updated_at'] = current_time
            
            result = collection.insert_many(documents)
            document_ids = [str(doc_id) for doc_id in result.inserted_ids]
            
            logger.info(f"{len(document_ids)} documents inserted successfully in collection '{collection_name}'")
            return document_ids
            
        except Exception as e:
            logger.error(f"Error inserting multiple documents: {e}")
            raise Exception(f"Failed to insert documents: {e}")

    def get_document_by_id(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by its ID.
        
        Args:
            collection_name: Name of the collection
            document_id: ID of the document
            
        Returns:
            Dict[str, Any]: Document if found, None otherwise
            
        Raises:
            Exception: If database is not connected
        """
        try:
            if self.database is None:
                raise Exception("Database not connected. Call connect_to_mongo() first.")
            
            collection = self.get_collection(collection_name)
            
            # Convert string ID to ObjectId
            try:
                object_id = ObjectId(document_id)
            except Exception:
                logger.error(f"Invalid document ID format: {document_id}")
                return None
            
            document = collection.find_one({"_id": object_id})
            
            if document:
                # Convert ObjectId to string for JSON serialization
                document["_id"] = str(document["_id"])
                logger.info(f"Document found with ID: {document_id}")
            else:
                logger.info(f"Document not found with ID: {document_id}")
            
            return document
            
        except Exception as e:
            logger.error(f"Error getting document by ID: {e}")
            raise Exception(f"Failed to get document: {e}")

    def get_documents(self, collection_name: str, filter_query: Optional[Dict[str, Any]] = None, 
                     limit: Optional[int] = None, skip: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get multiple documents from a collection.
        
        Args:
            collection_name: Name of the collection
            filter_query: MongoDB query filter (optional)
            limit: Maximum number of documents to return (optional)
            skip: Number of documents to skip (optional)
            
        Returns:
            List[Dict[str, Any]]: List of documents
            
        Raises:
            Exception: If database is not connected
        """
        try:
            if self.database is None:
                raise Exception("Database not connected. Call connect_to_mongo() first.")
            
            collection = self.get_collection(collection_name)
            
            # Build query
            query = filter_query or {}
            cursor = collection.find(query)
            
            # Apply skip and limit
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            documents = []
            for doc in cursor:
                # Convert ObjectId to string for JSON serialization
                doc["_id"] = str(doc["_id"])
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} documents from collection '{collection_name}'")
            return documents
            
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            raise Exception(f"Failed to get documents: {e}")

    def update_document(self, collection_name: str, document_id: str, 
                       update_data: Dict[str, Any]) -> bool:
        """
        Update a document by its ID.
        
        Args:
            collection_name: Name of the collection
            document_id: ID of the document to update
            update_data: Data to update
            
        Returns:
            bool: True if document was updated, False otherwise
            
        Raises:
            Exception: If database is not connected or update fails
        """
        try:
            if self.database is None:
                raise Exception("Database not connected. Call connect_to_mongo() first.")
            
            collection = self.get_collection(collection_name)
            
            # Convert string ID to ObjectId
            try:
                object_id = ObjectId(document_id)
            except Exception:
                logger.error(f"Invalid document ID format: {document_id}")
                return False
            
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            result = collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Document updated successfully with ID: {document_id}")
                return True
            else:
                logger.info(f"No document found or updated with ID: {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise Exception(f"Failed to update document: {e}")

    def delete_document(self, collection_name: str, document_id: str) -> bool:
        """
        Delete a document by its ID.
        
        Args:
            collection_name: Name of the collection
            document_id: ID of the document to delete
            
        Returns:
            bool: True if document was deleted, False otherwise
            
        Raises:
            Exception: If database is not connected or deletion fails
        """
        try:
            if self.database is None:
                raise Exception("Database not connected. Call connect_to_mongo() first.")
            
            collection = self.get_collection(collection_name)
            
            # Convert string ID to ObjectId
            try:
                object_id = ObjectId(document_id)
            except Exception:
                logger.error(f"Invalid document ID format: {document_id}")
                return False
            
            result = collection.delete_one({"_id": object_id})
            
            if result.deleted_count > 0:
                logger.info(f"Document deleted successfully with ID: {document_id}")
                return True
            else:
                logger.info(f"No document found or deleted with ID: {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise Exception(f"Failed to delete document: {e}")

    def count_documents(self, collection_name: str, filter_query: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents in a collection.
        
        Args:
            collection_name: Name of the collection
            filter_query: MongoDB query filter (optional)
            
        Returns:
            int: Number of documents
            
        Raises:
            Exception: If database is not connected
        """
        try:
            if self.database is None:
                raise Exception("Database not connected. Call connect_to_mongo() first.")
            
            collection = self.get_collection(collection_name)
            query = filter_query or {}
            count = collection.count_documents(query)
            
            logger.info(f"Collection '{collection_name}' has {count} documents")
            return count
            
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            raise Exception(f"Failed to count documents: {e}")
