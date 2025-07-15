from datetime import datetime
from inspect import signature
from fastapi import HTTPException
from src.schemas.callback import Callback, CallbackResponse, CallbackSchema, get_payment_status, get_order_status
from src.core.config import configs
import hashlib
from src.core.supabase_connection import supabase_orders, supabase_payments
from zoneinfo import ZoneInfo

class CallbackService:
    async def get_callbacks(self):
        result = [{"id": 1, "name": "Callback Example", "status": "active"},
                  {"id": 2, "name": "Another Callback", "status": "inactive"}]
        return result

    async def process_callback(self, callback: Callback):
        # Simulate processing the callback
        try:
            raw = f"{callback.merchant_code}{callback.amount}{callback.merchant_order_id}{configs.duitku_api_key}"
            
            expected_signature = hashlib.md5(raw.encode("utf-8")).hexdigest()
            
            if callback.signature != expected_signature:
                raise HTTPException(status_code=400, detail="Invalid signature")
            
            update_payments = supabase_payments.update_where(
                conditions={
                    "payment_id": callback.merchant_order_id,
                    "reference": callback.reference
                }, 
                new_values={
                    "payment_method": callback.payment_code,
                    "payment_status": get_payment_status(callback.result_code),
                    "publisher_order_id": callback.publisher_order_id,
                    "merchant_user_id": callback.merchant_user_id,
                    "sp_user_hash": callback.sp_user_hash,
                    "settlement_date": callback.settlement_date,
                    "paid_at": datetime.now(ZoneInfo("Asia/Jakarta")).isoformat(),
                    "issuer_code": callback.issuer_code,
                }
            )
            
            update_order = supabase_orders.update_where(
                conditions={
                    'order_id': update_payments.data[0].get("order_id"),
                },
                new_values={
                    "status": get_order_status(callback.result_code),
                }
            )
            
            return CallbackResponse(
                message="Callback received successfully",
                data=CallbackSchema(**callback.model_dump(exclude_none=True), 
                                     status=callback.result_code,
                                     order_status=callback.result_code
                )
            )
                
        
        except Exception as e:
            print(f"Error processing callback: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing callback: {str(e)}") 