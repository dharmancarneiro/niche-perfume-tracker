from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime

app = FastAPI(
    title="Niche Perfume Price Tracker",
    description="Compare precos de perfumes de nicho em 10 lojas",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STORES = [
    {"name": "FragranceX", "url": "https://fragrancex.com", "discount": "30-50%"},
    {"name": "FragranceNet", "url": "https://fragrancenet.com", "discount": "35-60%"},
    {"name": "MaxAroma", "url": "https://maxaroma.com", "discount": "20-40%"},
    {"name": "Jomashop", "url": "https://jomashop.com", "discount": "15-35%"},
    {"name": "FragranceBuy CA", "url": "https://fragrancebuy.ca", "discount": "20-35%"},
]

BRANDS = ["Creed", "Parfums de Marly", "Initio", "MFK", "Xerjoff", "Amouage", "Tom Ford", "Byredo", "Le Labo", "Kilian"]

DEALS = [
    {"id": 1, "brand": "Creed", "name": "Aventus", "size": "100ml", "original": 445, "price": 289, "discount": 35, "store": "FragranceX", "score": 85},
    {"id": 2, "brand": "Parfums de Marly", "name": "Layton", "size": "125ml", "original": 335, "price": 219, "discount": 35, "store": "MaxAroma", "score": 82},
    {"id": 3, "brand": "Initio", "name": "Side Effect", "size": "90ml", "original": 380, "price": 245, "discount": 36, "store": "FragranceNet", "score": 80},
    {"id": 4, "brand": "MFK", "name": "Baccarat Rouge 540", "size": "70ml", "original": 325, "price": 275, "discount": 15, "store": "Jomashop", "score": 75},
    {"id": 5, "brand": "Xerjoff", "name": "Naxos", "size": "100ml", "original": 320, "price": 199, "discount": 38, "store": "FragranceBuy CA", "score": 88},
]

@app.get("/")
def home():
    return {
        "service": "Niche Perfume Price Tracker",
        "status": "online",
        "endpoints": ["/stores", "/brands", "/deals", "/search"],
    }

@app.get("/stores")
def get_stores():
    return {"stores": STORES, "total": len(STORES)}

@app.get("/brands")
def get_brands():
    return {"brands": BRANDS, "total": len(BRANDS)}

@app.get("/deals")
def get_deals(min_discount: int = Query(0, ge=0, le=100)):
    filtered = [d for d in DEALS if d["discount"] >= min_discount]
    return {"deals": filtered, "total": len(filtered)}

@app.get("/search")
def search(q: str = Query(..., min_length=2)):
    results = [d for d in DEALS if q.lower() in d["name"].lower() or q.lower() in d["brand"].lower()]
    return {"results": results, "query": q}
