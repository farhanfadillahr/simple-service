import json
import redis
from .config import configs

class RedisClient:
    """Redis client for caching and data storage"""
    
    def __init__(self):
        self.client = redis.from_url(configs.redis_url)
    
    def set(self, key: str, value: str, ex: int = None) -> bool:
        """
        Set a key-value pair in Redis
        
        Args:
            key (str): The key to set
            value (str): The value to store
            ex (int, optional): Expiration time in seconds
            
        Returns:
            bool: True if the operation was successful, False otherwise
        """
        return self.client.set(key, value, ex=ex)
    
    def get(self, key: str) -> str:
        """
        Get a value by key from Redis
        
        Args:
            key (str): The key to retrieve
            
        Returns:
            str: The value associated with the key, or None if not found
        """
        return self.client.get(key)
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from Redis
        
        Args:
            key (str): The key to delete
            
        Returns:
            bool: True if the operation was successful, False otherwise
        """
        return self.client.delete(key) > 0
    
    def publish(self, channel: str, message: str) -> bool:
        """
        Publish a message to a Redis channel
        
        Args:
            channel (str): The channel to publish to
            message (str): The message to publish
            
        Returns:
            bool: True if the operation was successful, False otherwise
        """
        return self.client.publish(channel, json.dumps(message)) > 0