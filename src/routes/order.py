from typing import List, Union, Dict
from fastapi import APIRouter, status, Depends, Request
from fastapi.exceptions import HTTPException
from src.services.callback import CallbackService
from src.services.order import OrderService
from src.schemas.order import OrderResponse, OrderUpdateStatus, OrderUpdateResponse

order_router = APIRouter()
order_service = OrderService()

# GET /orders
@order_router.get("",
                status_code=status.HTTP_200_OK,
                response_model=OrderResponse,)
async def get_orders(order_id: Union[int, None] = None):
    orders = await order_service.get_orders(order_id=order_id)
    
    if not orders:
        raise HTTPException(status_code=404, detail="Orders not found")

    return OrderResponse(message="Orders retrieved successfully", data=orders)

# update order status
@order_router.put("/update-status",
                status_code=status.HTTP_200_OK,
                response_model=OrderUpdateResponse)
async def update_order_status(order_update: OrderUpdateStatus):
    try:
        updated_order = await order_service.update_order_status(order_update)
        print(f"Updated order: {updated_order}")
        print(f"Updated order status: {updated_order.get('status')}")
        print(f"Updated order ID: {updated_order.get('order_id')}")
        return OrderUpdateResponse(message="Order status updated successfully", data=OrderUpdateStatus(
            order_id=updated_order.get("order_id"),
            status=updated_order.get("status")
        ))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

