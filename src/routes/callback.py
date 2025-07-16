from typing import List, Union, Dict
from fastapi import APIRouter, status, Depends, Request
from fastapi.exceptions import HTTPException
from src.services.callback import CallbackService
from src.services.redis import RedisService
from src.schemas.callback import Callback, CallbackSchema, CallbackResponse

callback_router = APIRouter()
callback_service = CallbackService()
redis_service = RedisService()
# POST /callback
@callback_router.post("", 
                      status_code=status.HTTP_200_OK)
async def create_callback(request: Request):
    callback_data = await request.form()
    callback = Callback(
        merchant_order_id=callback_data.get("merchantOrderId"),
        amount=int(callback_data.get("amount", 0)),
        merchant_code=callback_data.get("merchantCode"),
        product_details=callback_data.get("productDetails"),
        additional_param=callback_data.get("additionalParam"),
        payment_code=callback_data.get("paymentCode"),
        result_code=callback_data.get("resultCode"),
        merchant_user_id=callback_data.get("merchantUserId"),
        reference=callback_data.get("reference"),
        signature=callback_data.get("signature"),
        publisher_order_id=callback_data.get("publisherOrderId"),
        sp_user_hash=callback_data.get("spUserHash"),
        settlement_date=callback_data.get("settlementDate"),
        issuer_code=callback_data.get("issuerCode")
    )
    
    result = await callback_service.process_callback(callback)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create callback")
    return result

@callback_router.post("/{order_id}")
async def polling_order_status(payment_id: str, order_id: int, status: str = "pending"):
    """
    Polling endpoint to check the status of an order.
    """
    process = await redis_service.notify_payment_status(payment_id, order_id, status)
    print(f"Order status updated: {process}")
    print(process.get("status", "No message provided"))
    return {"message": "Order status updated"}

# @callback_router.get("/{order_id}")
# async def get_order_status(order_id: int, payment_id: str):
#     """
#     Polling endpoint to check the status of an order.
#     """
#     order_data = await redis_service.get_payment_status(order_id, payment_id)
#     if not order_data:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
#     return order_data

@callback_router.post("/publish/{channel}")
async def publish_message(channel: str, message: str):
    """
    Publish a message to a Redis channel.
    """
    print(f"Publishing message to channel {channel}: {message}")
    from src.core.redis_client import RedisClient
    import json
    redis_service = RedisClient()
    try:
        data = {"order_id": message, "status": "success"}
        # result = redis_service.publish("payment_updates", json.dumps(data))
        result = redis_service.publish(channel, json.dumps(data))
        print(f"Message published to channel {channel}: {data}")
    except Exception as e:
        print(f"Error publishing message to Redis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to publish message: {str(e)}")
    print(f"Message published successfully: {result}")
    return {"message": "Message published successfully", "channel": channel, "result": result}
    # result = await redis_service.publish_message(channel, message)
    # if not result:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to publish message")
    # return {"message": "Message published successfully", "channel": channel, "result": result}

