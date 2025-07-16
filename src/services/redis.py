from datetime import datetime
from fastapi import HTTPException
from src.core.config import configs
from src.core.redis_client import RedisClient

class RedisService:
    def __init__(self):
        self.redis_client = RedisClient()

    async def notify_payment_status(self, payment_id: str, order_id: int, status: str):
        """
        Notify payment status by caching the order data in Redis.
        
        Args:
            payment_id (str): The ID of the payment.
            order_id (int): The ID of the order.
            status (str): The payment status to cache.
        """
        key = f"payment_id:{payment_id}"
        order_data = {
            "order_id": order_id,
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        self.redis_client.set(key, str(order_data), ex=3600)

        return order_data

    # async def get_payment_status(self, order_id: int, payment_id: str) -> dict:
    #     """
    #     Retrieve cached payment status from Redis.

    #     Args:
    #         order_id (int): The ID of the order to retrieve.
    #         payment_id (str): The ID of the payment to retrieve.
        
    #     Returns:
    #         dict: The cached order data or None if not found.
    #     """
    #     key = f"payment_id:{payment_id}"
    #     cached_data = self.redis_client.get(key)
    #     return eval(cached_data) if cached_data else None
    
    async def publish_message(self, channel: str, message: str) -> bool:
        """
        Publish a message to a Redis channel.

        Args:
            channel (str): The channel to publish to.
            message (str): The message to publish.
        
        Returns:
            bool: True if the message was published successfully, False otherwise.
        """
        
        try:
            x = self.redis_client.publish(channel, message)
            print(f"Publishing 2 message to channel {channel}: {message}")
        except Exception as e:
            print(f"Error publishing message to Redis: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to publish message: {str(e)}")
        print(f"Publishing 3 message to channel {channel}: {message}")
        print(x)
        return x
