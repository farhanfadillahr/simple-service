from zoneinfo import ZoneInfo
from pydantic import BaseModel, field_serializer
from datetime import datetime
from typing import List, Optional, Literal
# from typing_extensions import Literal
    
class Address(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    subdistrict: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    
class Product(BaseModel):
    name: str
    quantity: int
    sku: str
    unit_price: float
    
class Order(BaseModel):
    order_id: int
    customer_id: int
    order_date: datetime
    status: str
    address: Optional[Address] = None
    shipping_info: Optional['Shipping'] = None
    items: List[Product] = []
    
class Shipping(BaseModel):
    shipping_name: Optional[str] = None
    service_type: Optional[str] = None
    service_name: Optional[str] = None
    shipping_cost: Optional[float] = None
    is_cod: Optional[bool] = None
    estimated_delivery_date: Optional[datetime] = None
    
class OrderResponse(BaseModel):
    message: str
    data: List[Order]

    @field_serializer("data")
    def serialize_data(self, data: List[Order], _info):
        return [item.model_dump(exclude_none=True) for item in data]

class OrderUpdateStatus(BaseModel):
    order_id: int
    status: Literal['unpaid', 'processing', 'shipped', 'cancelled', 'completed']

    @field_serializer("status")
    def serialize_status(self, status: Literal['unpaid', 'processing', 'shipped', 'cancelled', 'completed'], _info):
        return status.lower()
    
class OrderUpdateResponse(BaseModel):
    message: str
    data: OrderUpdateStatus
