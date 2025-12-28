from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup
import asyncio
import re
from urllib.parse import quote_plus, urljoin
from datetime import datetime

app = FastAPI(title="Niche Perfume Price Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STORES = [
    {"name": "FragranceX", "base_url": "https://www.fragrancex.com", "search_url": "https://www.fragrancex.com/search?q={query}"},
    {"name": "FragranceNet", "base_url": "https://www.fragrancenet.com", "search_url": "https://www.fragrancenet.com/search?searchTerm={query}"},
    {"name": "MaxAroma", "base_url": "https://www.maxaroma.com", "search_url": "https://www.maxaroma.com/search?q={query}"},
    {"name": "Jomashop", "base_url": "https://www.jomashop.com", "search_url": "https://www.jomashop.com/catalogsearch/result/?q={query}"},
    {"name": "FragranceBuy", "base_url": "https://fragrancebuy.ca", "search_url": "https://fragrancebuy.ca/search?type=product&q={query}"},
]

def clean_price(price_text):
    if not price_text:
        return None
    try:
        cleaned = re.sub(r'[^\d.,]', '', price_text.strip())
        if ',' in cleaned and '.' in cleaned:
            cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            parts = cleaned.split(',')
            if len(parts[-1]) == 2:
                cleaned = cleaned.replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')
        return float(cleaned) if cleaned else None
    except:
        return None

async def search_store(client, store, query):
    results = []
    search_url = store["search_url"].format(query=quote_plus(query))
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
        response = await client.get(search_url, headers=headers, timeout=10.0, follow_redirects=True)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for sel in ['div.product-card', 'div.product-item', 'div.product', '[data-product-id]']:
                products = soup.select(sel)[:3]
                if products:
                    break
            for product in products:
                name_elem = product.select_one('h2, h3, h4, .product-name, .product-title, [class*="title"]')
                name = name_elem.get_text(strip=True) if name_elem else None
                if not name or not any(w in name.lower() for w in query.lower().split()):
                    continue
                price_elem = product.select_one('.price, [class*="price"]')
                price = clean_price(price_elem.get_text(strip=True)) if price_elem else None
                if not price:
                    continue
                link = product.select_one('a[href]')
                url = urljoin(store["base_url"], link.get('href')) if link else search_url
                results.append({"store": store["name"], "name": name, "price": price, "url": url})
    except:
        pass
    return results

@app.get("/", response_class=HTMLResponse)
async def root():
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Perfume Price Tracker</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui;background:linear-gradient(135deg,#1a1a2e,#16213e);min-height:100vh;color:#fff;padding:20px}
.container{max-width:900px;margin:0 auto}
h1{text-align:center;font-size:2rem;margin:30px 0;color:#e94560}
.search-box{background:rgba(255,255,255,0.1);border-radius:15px;padding:25px;margin:20px 0}
.search-form{display:flex;gap:10px;flex-wrap:wrap}
input{flex:1;min-width:250px;padding:12px 20px;border:none;border-radius:25px;font-size:1rem}
button{padding:12px 30px;border:none;border-radius:25px;background:#e94560;color:#fff;font-weight:bold;cursor:pointer}
button:hover{background:#ff6b6b}
.results{margin-top:20px}
.card{background:rgba(255,255,255,0.05);border-radius:10px;padding:15px;margin:10px 0;border-left:3px solid #e94560}
.card.best{border-color:#10b981;background:rgba(16,185,129,0.1)}
.store{color:#94a3b8;font-size:0.9rem}
.name{font-weight:bold;margin:5px 0}
.price{font-size:1.3rem;color:#10b981;font-weight:bold}
a{color:#3b82f6;text-decoration:none}
.loading{text-align:center;padding:40px;color:#94a3b8}
.tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:15px;justify-content:center}
.tag{background:rgba(255,255,255,0.1);padding:8px 15px;border-radius:15px;cursor:pointer;border:none;color:#fff;font-size:0.85rem}
.tag:hover{background:rgba(233,69,96,0.3)}
</style></head>
<body><div class="container">
<h1>🧴 Perfume Price Tracker</h1>
<div class="search-box">
<form class="search-form" onsubmit="search(event)">
<input type="text" id="q" placeholder="Search perfume (e.g. Creed Aventus)" required>
<button type="submit">🔍 Search</button>
</form>
<div class="tags">
<button class="tag" onclick="quickSearch('Creed Aventus')">Creed Aventus</button>
<button class="tag" onclick="quickSearch('Baccarat Rouge 540')">Baccarat Rouge</button>
<button class="tag" onclick="quickSearch('Parfums de Marly Layton')">PDM Layton</button>
<button class="tag" onclick="quickSearch('Bleu de Chanel')">Bleu de Chanel</button>
</div>
</div>
<div id="results"></div>
</div>
<script>
function quickSearch(t){document.getElementById('q').value=t;search(new Event('submit'))}
async function search(e){
e.preventDefault();
const q=document.getElementById('q').value;
const r=document.getElementById('results');
r.innerHTML='<div class="loading">🔍 Searching stores...</div>';
try{
const res=await fetch('/api/search?q='+encodeURIComponent(q));
const data=await res.json();
if(!data.results.length){r.innerHTML='<div class="loading">No results found</div>';return}
const best=Math.min(...data.results.map(x=>x.price));
r.innerHTML=data.results.map(x=>`
<div class="card ${x.price===best?'best':''}">
<div class="store">${x.store} ${x.price===best?'⭐ BEST PRICE':''}</div>
<div class="name">${x.name}</div>
<div class="price">$${x.price.toFixed(2)}</div>
<a href="${x.url}" target="_blank">View on ${x.store} →</a>
</div>`).join('')}
catch(err){r.innerHTML='<div class="loading">Error searching</div>'}}
</script></body></html>"""

@app.get("/api/search")
async def search_api(q: str = Query(..., min_length=2)):
    results = []
    async with httpx.AsyncClient() as client:
        tasks = [search_store(client, store, q) for store in STORES]
        store_results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in store_results:
            if isinstance(r, list):
                results.extend(r)
    results.sort(key=lambda x: x["price"])
    return {"query": q, "results": results}

@app.get("/health")
async def health():
    return {"status": "ok"}
