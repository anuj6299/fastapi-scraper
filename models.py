from pydantic import BaseModel
from typing import List, Optional

class Product(BaseModel):
    product_title: str
    product_price: float
    path_to_image: str

class ScrapingSettings(BaseModel):
    pages_limit: Optional[int] = None
    proxy: Optional[str] = None
