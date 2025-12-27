from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import asyncio
import os
import json
import re

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:tquVYZmtvegaklgyFRMRzqCGrJthRFHl@mysql.railway.internal:3306/railway")
engine = create_engine(DATABASE_URL.replace("mysql://", "mysql+pymysql://"))
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True)
    brand = Column(String(255))
    name = Column(String(255))
    size = Column(String(50))
    price = Column(Float)
    original_price = Column(Float)
    store = Column(String(100))
    url = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Niche Perfume Price Tracker")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

STORES = {
    "fragrancex": {"name": "FragranceX", "base": "https://www.fragrancex.com", "search": "/search?q={}"},
    "fragrancenet": {"name": "FragranceNet", "base": "https://www.fragrancenet.com", "search": "/search?q={}"},
    "maxaroma": {"name": "MaxAroma", "base": "https://www.maxaroma.com", "search": "/catalogsearch/result/?q={}"},
    "jomashop": {"name": "Jomashop", "base": "https://www.jomashop.com", "search": "/search?q={}"},
    "fragrancebuy": {"name": "FragranceBuy CA", "base": "https://fragrancebuy.ca", "search": "/search?q={}"},
}

async def scrape_store(client, store_key, query):
    store = STORES[store_key]
    results = []
    try:
        url = store["base"] + store["search"].format(query.replace(" ", "+"))
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = await client.get(url, headers=headers, timeout=15, follow_redirects=True)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Generic parsing - each store has different structure
        products = soup.select(".product-item, .product-card, .product, [data-product]")[:5]
        for p in products:
            name_el = p.select_one(".product-name, .product-title, h2, h3, a[title]")
            price_el = p.select_one(".price, .special-price, [data-price]")
            link_el = p.select_one("a[href*='/']")
            
            if name_el and price_el:
                price_text = re.sub(r'[^\d.]', '', price_el.get_text())
                if price_text:
                    results.append({
                        "brand": query.split()[0] if query else "",
                        "name": name_el.get_text(strip=True)[:100],
                        "price": float(price_text) if price_text else 0,
                        "store": store["name"],
                        "url": store["base"] + link_el.get("href", "") if link_el else url
                    })
    except Exception as e:
        print(f"Error scraping {store_key}: {e}")
    return results

async def search_all_stores(query):
    async with httpx.AsyncClient() as client:
        tasks = [scrape_store(client, key, query) for key in STORES.keys()]
        all_results = await asyncio.gather(*tasks)
        return [item for sublist in all_results for item in sublist]

# Save to database
def save_prices(prices):
    db = SessionLocal()
    for p in prices:
        db_price = Price(brand=p.get("brand",""), name=p.get("name",""), price=p.get("price",0), store=p.get("store",""), url=p.get("url",""), updated_at=datetime.utcnow())
        db.add(db_price)
    db.commit()
    db.close()

def search_db(query):
    db = SessionLocal()
    results = db.query(Price).filter(Price.name.ilike(f"%{query}%")).order_by(Price.price).limit(50).all()
    db.close()
    return [{"brand": r.brand, "name": r.name, "size": r.size or "", "price": r.price, "store": r.store, "url": r.url} for r in results]

HTML_PAGE = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Niche Perfume Tracker - Compare Prices</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui,sans-serif;background:#0a0a0f;color:#e0e0e0;min-height:100vh}
.header{background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:50px 20px;text-align:center}
.header h1{font-size:2.5rem;margin-bottom:10px}.header p{opacity:.8}
.container{max-width:1000px;margin:0 auto;padding:20px}
.search-box{background:#1a1a2e;padding:30px;border-radius:16px;margin:-40px auto 30px;max-width:700px;box-shadow:0 20px 60px rgba(0,0,0,.5)}
.search-form{display:flex;gap:10px}
.search-form input{flex:1;padding:16px 20px;font-size:1.1rem;border:2px solid #333;border-radius:12px;background:#0d0d14;color:#fff}
.search-form input:focus{outline:none;border-color:#6366f1}
.search-form button{padding:16px 32px;background:#6366f1;color:#fff;border:none;border-radius:12px;font-size:1rem;cursor:pointer;font-weight:600}
.search-form button:hover{background:#4f46e5}
.search-form button:disabled{background:#333;cursor:wait}
.progress{margin-top:20px;display:none}.progress.show{display:block}
.progress-bar{height:6px;background:#1e1e2e;border-radius:3px;overflow:hidden}
.progress-fill{height:100%;background:linear-gradient(90deg,#6366f1,#8b5cf6);width:0%;transition:width .3s}
.progress-text{text-align:center;margin-top:10px;color:#888;font-size:.9rem}
.results{margin-top:30px}
.result-card{background:#12121a;border:1px solid #222;border-radius:12px;padding:20px;margin-bottom:15px;display:flex;justify-content:space-between;align-items:center}
.result-info h3{font-size:1.1rem;margin-bottom:5px}.result-info p{color:#888;font-size:.9rem}
.result-price{text-align:right}
.result-price .price{font-size:1.5rem;font-weight:700;color:#22c55e}
.result-price .store{color:#888;font-size:.85rem;margin-top:5px}
.result-price a{display:inline-block;margin-top:10px;padding:8px 16px;background:#6366f1;color:#fff;text-decoration:none;border-radius:8px;font-size:.85rem}
.no-results{text-align:center;padding:60px;color:#666}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-bottom:30px}
.stat{background:#12121a;padding:20px;border-radius:12px;text-align:center}
.stat-value{font-size:1.8rem;font-weight:700;color:#6366f1}.stat-label{color:#888;font-size:.85rem}
</style></head>
<body>
<div class="header"><h1>🔍 Niche Perfume Price Tracker</h1><p>Compare prices from 5+ gray market stores instantly</p></div>
<div class="container">
<div class="search-box">
<form class="search-form" onsubmit="searchPerfume(event)">
<input type="text" id="query" placeholder="Search any perfume... e.g. Aventus, Baccarat Rouge, Layton" required>
<button type="submit" id="searchBtn">Search</button>
</form>
<div class="progress" id="progress"><div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div><p class="progress-text" id="progressText">Searching stores...</p></div>
</div>
<div id="stats" class="stats" style="display:none">
<div class="stat"><div class="stat-value" id="lowestPrice">-</div><div class="stat-label">Lowest Price</div></div>
<div class="stat"><div class="stat-value" id="numResults">-</div><div class="stat-label">Results Found</div></div>
<div class="stat"><div class="stat-value" id="numStores">-</div><div class="stat-label">Stores Searched</div></div>
</div>
<div id="results" class="results"></div>
</div>
<script>
async function searchPerfume(e){
e.preventDefault();
const query=document.getElementById("query").value;
const btn=document.getElementById("searchBtn");
const progress=document.getElementById("progress");
const fill=document.getElementById("progressFill");
const text=document.getElementById("progressText");
const results=document.getElementById("results");
const stats=document.getElementById("stats");
btn.disabled=true;btn.textContent="Searching...";
progress.classList.add("show");results.innerHTML="";stats.style.display="none";
let pct=0;const stores=["FragranceX","FragranceNet","MaxAroma","Jomashop","FragranceBuy"];
const interval=setInterval(()=>{if(pct<90){pct+=Math.random()*15;fill.style.width=pct+"%";text.textContent="Searching "+stores[Math.floor(pct/20)]+"...";}},500);
try{
const res=await fetch("/api/search?q="+encodeURIComponent(query));
const data=await res.json();
clearInterval(interval);fill.style.width="100%";text.textContent="Done!";
setTimeout(()=>{progress.classList.remove("show");},1000);
if(data.results&&data.results.length>0){
stats.style.display="grid";
const prices=data.results.map(r=>r.price).filter(p=>p>0);
document.getElementById("lowestPrice").textContent="$"+Math.min(...prices).toFixed(2);
document.getElementById("numResults").textContent=data.results.length;
document.getElementById("numStores").textContent=new Set(data.results.map(r=>r.store)).size;
results.innerHTML=data.results.sort((a,b)=>a.price-b.price).map(r=>`
<div class="result-card">
<div class="result-info"><h3>${r.name}</h3><p>${r.brand} ${r.size}</p></div>
<div class="result-price"><div class="price">$${r.price.toFixed(2)}</div><div class="store">${r.store}</div>
${r.url?`<a href="${r.url}" target="_blank">View Deal →</a>`:""}</div>
</div>`).join("");
}else{results.innerHTML='<div class="no-results"><h3>No results found</h3><p>Try a different search term</p></div>';}
}catch(err){clearInterval(interval);results.innerHTML='<div class="no-results"><h3>Error</h3><p>'+err.message+'</p></div>';}
btn.disabled=false;btn.textContent="Search";}
</script>
</body></html>'''

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE

@app.get("/api/search")
async def api_search(q: str = Query(..., min_length=2)):
    # First check database
    db_results = search_db(q)
    if len(db_results) >= 3:
        return {"results": db_results, "source": "database"}
    # If not enough in DB, scrape live
    live_results = await search_all_stores(q)
    if live_results:
        save_prices(live_results)
    all_results = db_results + live_results
    # Remove duplicates
    seen = set()
    unique = []
    for r in all_results:
        key = (r["name"][:30], r["store"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return {"results": unique[:20], "source": "live" if live_results else "database"}

@app.get("/api/stores")
def get_stores():
    return {"stores": [{"name": s["name"], "url": s["base"]} for s in STORES.values()]}
