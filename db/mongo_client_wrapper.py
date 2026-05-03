
import os
import logging
from typing import Optional
from pymongo import MongoClient
import motor.motor_asyncio
import asyncio

logger = logging.getLogger(__name__)

# Global client instances for reuse
_async_client = None
_sync_client = None

def get_mongo_uri() -> str:
    """Get MongoDB URI from environment variables."""
    return os.environ.get('MONGO_URI', 'mongodb://localhost:27017')

async def get_mongo_client(uri: Optional[str] = None, **kwargs) -> motor.motor_asyncio.AsyncIOMotorClient:
    """Get or create an asynchronous MongoDB client."""
    global _async_client
    if _async_client is None:
        if uri is None:
            uri = get_mongo_uri()
        _async_client = motor.motor_asyncio.AsyncIOMotorClient(uri, **kwargs)
        logger.info("✅ Created asynchronous MongoDB client")
    return _async_client

def get_mongo_client_sync(uri: Optional[str] = None, **kwargs) -> MongoClient:
    """Get or create a synchronous MongoDB client."""
    global _sync_client
    if _sync_client is None:
        if uri is None:
            uri = get_mongo_uri()
        _sync_client = MongoClient(uri, **kwargs)
        logger.info("✅ Created synchronous MongoDB client")
    return _sync_client

def mongo_enabled() -> bool:
    """Check if MongoDB is configured and available."""
    return bool(os.environ.get('MONGO_URI'))

def close_mongo_client():
    """Close MongoDB client connections."""
    global _async_client, _sync_client
    if _async_client:
        try:
            _async_client.close()
        except Exception:
            pass
        _async_client = None
    if _sync_client:
        try:
            _sync_client.close()
        except Exception:
            pass
        _sync_client = None
    logger.info("🛑 MongoDB connections closed")
