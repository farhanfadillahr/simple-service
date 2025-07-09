import hashlib
import os
from fastapi import FastAPI, HTTPException, Form, Request
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

@app.get("/")
async def root():
    # supabase_product = SupabaseConnection(table_name="master_products")
    # response = supabase_product.select_all()
    return {"message": "Welcome to Duitku Returns API"}


@app.post("/webhook")
async def receive_form_data(request: Request):
    form_data = await request.form()
    # form_data = {'merchantCode': 'DS23784', 'amount': '575600', 'merchantOrderId': 'INV-160-87724065100-1752016835153', 'productDetail': 'AS GEAR DEPAN GL 100 (SKU: AGDSH05), CDI SUPRA  (SKU: CDIBH08)', 'additionalParam': '', 'resultCode': '00', 'paymentCode': 'BC', 'merchantUserId': '', 'reference': 'DS23784252IH446O5EGONJLM', 'signature': '6db3f7f33ba526d49fe245b447576af4', 'publisherOrderId': 'BC2531WS3CTJEG73KVA', 'settlementDate': '2025-07-11', 'vaNumber': '7007014004420346', 'sourceAccount': ''}
    merchantOrderId = form_data.get("merchantOrderId")
    amount = form_data.get("amount", 0) # Convert amount to integer
    merchantCode = form_data.get("merchantCode")
    productDetails = form_data.get("productDetails")
    additionalParam = form_data.get("additionalParam")
    paymentCode = form_data.get("paymentCode")
    resultCode = form_data.get("resultCode", "01")
    merchantUserId = form_data.get("merchantUserId")
    reference = form_data.get("reference", "")
    signature = form_data.get("signature")
    publisherOrderId = form_data.get("publisherOrderId")
    spUserHash = form_data.get("spUserHash")
    settlementDate = datetime.strptime(form_data.get("settlementDate", datetime.today().strftime("%Y-%m-%d")), "%Y-%m-%d").isoformat()
    issuerCode = form_data.get("issuerCode")
    try:
        raw = f"{merchantCode}{amount}{merchantOrderId}{API_KEY}"
        expected_signature = hashlib.md5(raw.encode("utf-8")).hexdigest()
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
                "settlement_date": settlementDate,
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
        
        # # print(update_payments.data[0].get("order_id"))
        # print(f"Update payment status: {update_payments}")
        # print(f"Update order status: {update_order}")

        return {
            "message": "Callback received successfully",
            "data": {
                "merchantOrderId": merchantOrderId,
                "amount": int(amount),
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

@app.post("/callback")
async def duitku_callback(
    merchantOrderId: str = Form(...),
    amount: str = Form(...),
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
    settlementDate: str = Form(...),
    issuerCode: str = Form(...)
):
    try:
        # Verify Signature
        raw = f"{merchantCode}{amount}{merchantOrderId}{API_KEY}"
        expected_signature = hashlib.md5(raw.encode("utf-8")).hexdigest()
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
                "settlement_date": settlementDate,
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
        
        # # print(update_payments.data[0].get("order_id"))
        # print(f"Update payment status: {update_payments}")
        # print(f"Update order status: {update_order}")

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

