import hashlib
import os
from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
from supabase_connection import SupabaseConnection

load_dotenv()

app = FastAPI()

# Config
MERCHANT_CODE = os.getenv("DUITKU_MERCHANT_CODE")
API_KEY = os.getenv("DUITKU_API_KEY")
DUITKU_URL = os.getenv("DUITKU_BASE_URL")

class DuitkuCallback(BaseModel):
    merchantCode: str
    amount: int
    merchantOrderId: str
    productDetail: str
    additionalParam: str = None
    resultCode: str
    merchantUserId: str
    reference: str
    signature: str
    publisherOrderId: str
    spUserHash: str
    settlementDate: datetime
    issuerCode: str

@app.get("/")
async def root():
    # supabase_product = SupabaseConnection(table_name="master_products")
    # response = supabase_product.select_all()
    return {"message": "Welcome to Duitku Returns API"}

@app.post("/callback")
async def duitku_callback(
    merchantOrderId: str = Form(...),
    amount: int = Form(...),
    merchantCode: str = Form(...),
    productDetails: str = Form(...),
    additionalParam: str = Form(...),
    paymentCode: str = Form(...),
    resultCode: str = Form(...),
    merchantUserId: str = Form(...),
    reference: str = Form(...),
    signature: str = Form(...),
    publisherOrderId: str = Form(...),
    spUserHash: str = Form(...),
    settlementDate: datetime = Form(...),
    issuerCode: str = Form(...)
):
    try:
        # Verify Signature
        raw = f"{merchantCode}{amount}{merchantOrderId}{API_KEY}"
        expected_signature = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        # print(f"expected_signature: {expected_signature}")
        # print(f"received_signature: {signature}")
        if signature != expected_signature:
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Map resultCode
        payment_status = {
            "00": "success",
            "01": "pending",
            "02": "failed"
        }.get(resultCode, "Unknown")
        
        order_status = {
            "00": "processing",
            "01": "unpaid",
            "02": "cancelled"
        }.get(resultCode, "Unknown")
        
        # Supabase update payment status
        supabase_payments = SupabaseConnection(table_name="payments")
        update_payments = supabase_payments.update_where(
            conditions={
                "payment_id": merchantOrderId,
                "reference": reference
            }, 
            new_values={
                "payment_method": paymentCode,
                "payment_status": payment_status,
                "publisher_order_id": publisherOrderId,
                "merchant_user_id": merchantUserId,
                "sp_user_hash": spUserHash,
                "settlement_date": settlementDate.isoformat(),
                "paid_at": datetime.now().isoformat(),
                "issuer_code": issuerCode,
                
            }
        )
        
        update_order = SupabaseConnection(table_name="orders")
        update_order.update_where(
            conditions={
                'order_id': update_payments.data[0].get("order_id"),
            },
            new_values={
                "status": order_status,
            }
        )
        
        # print(update_payments.data[0].get("order_id"))
        print(f"Update payment status: {update_payments}")
        print(f"Update order status: {update_order}")

        return {
            "message": "Callback received successfully",
            "data": {
                "merchantOrderId": merchantOrderId,
                "amount": amount,
                "merchantCode": merchantCode,
                "productDetails": productDetails,
                "additionalParam": additionalParam,
                "paymentCode": paymentCode,
                "resultCode": resultCode,
                "merchantUserId": merchantUserId,
                "reference": reference,
                "signature": signature,
                "publisherOrderId": publisherOrderId,
                "spUserHash": spUserHash,
                "settlementDate": settlementDate,
                "issuerCode": issuerCode,
                "status": payment_status,
                "status_code": resultCode,
            }
        }
    except Exception as e:
        print(f"Error processing callback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing callback: {str(e)}")