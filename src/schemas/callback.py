from zoneinfo import ZoneInfo
from pydantic import BaseModel, field_serializer
from datetime import datetime
from typing import List, Optional


# # Mapping status codes to human-readable strings
def get_payment_status(result_code: str) -> str:
    return {
        "00": "success",
        "01": "pending",
        "02": "failed"
    }.get(result_code, "Unknown")
    
def get_order_status(result_code: str) -> str:
    return {
        "00": "processing",
        "01": "unpaid",
        "02": "cancelled"
    }.get(result_code, "Unknown")
    
    
class Callback(BaseModel):
    merchant_order_id: str
    amount: int
    merchant_code: str
    product_details: Optional[str] = None
    additional_param: Optional[str] = None
    payment_code: str
    result_code: str
    merchant_user_id: str
    reference: Optional[str] = None
    signature: str
    publisher_order_id: str
    sp_user_hash: Optional[str] = None
    settlement_date: Optional[str] = None
    issuer_code: Optional[str] = None

class CallbackSchema(Callback):
    """Response model for callback processing."""
    status: str
    order_status: str

    @field_serializer("status")
    def serialize_status(self, status: str, _info):
        return {"00": "success", "01": "pending", "02": "failed"}.get(status, "Unknown")

    @field_serializer("order_status")
    def serialize_order_status(self, order_status: str, _info):
        return {"00": "processing", "01": "unpaid", "02": "cancelled"}.get(order_status, "Unknown")


class CallbackResponse(BaseModel):
    message: str
    data: CallbackSchema

    # @field_serializer("data")
    # def serialize_data(self, data: CallbackSchema, _info):
    #     return data.model_dump(exclude_none=True)

    
    


    

class PaymentInfo(BaseModel):
    payment_method: str
    payment_status: str
    publisher_order_id: str
    merchant_user_id: str
    sp_user_hash: Optional[str] = None
    settlement_date: Optional[str] = None
    paid_at: Optional[datetime] = datetime.now(ZoneInfo("Asia/Jakarta")).isoformat()
    issuer_code: Optional[str] = None

    # @field_serializer("paid_at")
    # def serialize_paid_at(self, dt: Optional[datetime], _info):
    #     if dt is None:
    #         return None  # Return None if no value
    #     return dt.strftime("%Y-%m-%d %H:%M:%S") 
    