from typing import Union, List

from fastapi import FastAPI

from src.core.config import configs
from src.utils import singleton
from src.routes import callback, order
from src.middleware import register_middleware


    
    
@singleton
class AppCreator:
    def __init__(self):
        # set app default
        self.app = FastAPI(
            title=configs.PROJECT_NAME,
            openapi_url=f"{configs.API}/openapi.json",
            version=configs.VERSION,
        )

        
        register_middleware(self.app)
        
        self.app.include_router(
            callback.callback_router, prefix="/callback", tags=["callback"]
        )
        self.app.include_router(
            order.order_router, prefix="/orders", tags=["orders"]
        )

app_creator = AppCreator()
app = app_creator.app