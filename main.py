import json
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis

from models import ScrapingSettings
from scrap import Scraper

app = FastAPI()

# Simple token-based authentication
token_auth_scheme = HTTPBearer()


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
):
    token = credentials.credentials
    if token != "mysecrettoken":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )


# Caching with Redis
cache = redis.Redis(host="localhost", port=6379, db=0)


@app.post("/scrape", dependencies=[Depends(verify_token)])
async def scrape(settings: Optional[ScrapingSettings] = None):
    scraper = Scraper(settings)
    scraper.scrape()

    # Check for price changes
    updated_products = []
    for product in scraper.products:
        cached_price = cache.get(product["product_title"])
        if cached_price is None or cached_price != product["product_price"]:
            updated_products.append(product)
            cache.set(product["product_title"], product["product_price"])

    # Save updated products to JSON
    with open("products.json", "w") as f:
        json.dump(updated_products, f, indent=4)

    # Notify the result
    scraper.notify()

    return {"message": f"{len(updated_products)} products were scraped and updated."}
