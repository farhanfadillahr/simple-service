from typing import List, Union, Dict
from fastapi import APIRouter, status, Depends, Request
from fastapi.exceptions import HTTPException
from src.services.callback import CallbackService
from src.schemas.callback import Callback, CallbackSchema, CallbackResponse

callback_router = APIRouter()
callback_service = CallbackService()

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
