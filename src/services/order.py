from datetime import datetime
from fastapi import HTTPException
from src.schemas.order import Order, Address, Shipping, Product, OrderUpdateStatus
from src.core.config import configs
import hashlib
from src.core.supabase_connection import supabase_orders, supabase_orders_details, supabase_products
from zoneinfo import ZoneInfo

class OrderService:
    async def get_orders(self, order_id: int = None):
        try:
            if order_id:
                orders = supabase_orders.select_where(
                    conditions={"order_id": order_id}
                )
            else:
                orders = supabase_orders.select_all() # Debugging line to check order IDs

            orders_output = []
            for order in orders:
                order_output = Order(
                    order_id=order.get("order_id"),
                    customer_id=order.get("customer_id"),
                    order_date=order.get("order_date"),
                    status=order.get("status"),
                    address=Address(
                        address=order.get("address"),
                        city=order.get("city"),
                        district=order.get("district"),
                        subdistrict=order.get("subdistrict"),
                        province=order.get("province"),
                        postal_code=order.get("postal_code"),
                    ),
                    shipping_info=Shipping(
                        shipping_name=order.get("shipping_name"),
                        service_type=order.get("service_type"),
                        service_name=order.get("service_name"),
                        shipping_cost=order.get("shipping_cost"),
                        is_cod=order.get("is_cod"),
                        estimated_delivery_date=order.get("estimated_delivery_date")
                    ),
                    items=[],
                )
                order_detail = supabase_orders_details.select_where(
                    conditions={"order_id": order.get("order_id")}
                )
                for item in order_detail:
                    product = supabase_products.select_where(
                        conditions={"sku": item.get("sku")}
                    )
                    
                    
                    order_output.items.append(Product(
                        name=product[0].get("name"),
                        quantity=item.get("quantity"),
                        sku=item.get("sku"),
                        unit_price=item.get("unit_price")
                    ))
                orders_output.append(order_output)

            return orders_output

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving orders: {str(e)}")

    async def update_order_status(self, order_update: OrderUpdateStatus):
        try:
            update_order = supabase_orders.update_where(
                conditions={"order_id": order_update.order_id},
                new_values={"status": order_update.status}
            )
            if not update_order.data[0]:
                raise HTTPException(status_code=404, detail="Order not found")
            
            
            return update_order.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating order status: {str(e)}")
