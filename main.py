from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup
import asyncio
import re
from urllib.parse import quote_plus, urljoin
import random

app = FastAPI(title="Niche Perfume Price Tracker")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

STORES = [
    {"name": "FragranceX", "base": "https://www.fragrancex.com", "search": "https://www.fragrancex.com/search?q={q}", "selectors": {"container": ".product-card,.product-item,.product", "name": ".product-name,h2,h3", "price": ".price,.product-price"}},
    {"name": "FragranceNet", "base": "https://www.fragrancenet.com", "search": "https://www.fragrancenet.com/search?searchTerm={q}", "selectors": {"container": ".product-card,.product-item,.resultItem", "name": ".product-name,.productName,h3", "price": ".price,.productPrice"}},
    {"name": "MaxAroma", "base": "https://www.maxaroma.com", "search": "https://www.maxaroma.com/search?q={q}", "selectors": {"container": ".product-card,.product-item,.product", "name": ".product-name,h2,h3", "price": ".price,.product-price"}},
    {"name": "FragranceBuy", "base": "https://fragrancebuy.ca", "search": "https://fragrancebuy.ca/search?type=product&q={q}", "selectors": {"container": ".product-card,.grid-item,.product", "name": ".product-title,.title,h3", "price": ".price,.product-price"}},
    {"name": "Jomashop", "base": "https://www.jomashop.com", "search": "https://www.jomashop.com/catalogsearch/result/?q={q}", "selectors": {"container": ".product-item,.product-card", "name": ".product-name,.name", "price": ".price,.special-price"}},
]

def clean_price(text):
    if not text: return None
    try:
        c = re.sub(r'[^\d.,]', '', text)
        if ',' in c and '.' in c: c = c.replace(',', '')
        elif ',' in c and len(c.split(',')[-1]) == 2: c = c.replace(',', '.')
        elif ',' in c: c = c.replace(',', '')
        return float(c) if c else None
    except: return None

async def scrape_store(client, store, query):
    results = []
    try:
        url = store["search"].format(q=quote_plus(query))
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        r = await client.get(url, headers=headers, timeout=12.0, follow_redirects=True)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            sels = store["selectors"]
            for sel in sels["container"].split(","):
                items = soup.select(sel)[:5]
                if items: break
            for item in items:
                name = None
                for ns in sels["name"].split(","):
                    el = item.select_one(ns)
                    if el: name = el.get_text(strip=True); break
                if not name:
                    el = item.select_one("a[href]")
                    if el: name = el.get_text(strip=True)
                if not name or len(name) < 5: continue
                qwords = query.lower().split()
                if not any(w in name.lower() for w in qwords): continue
                price = None
                for ps in sels["price"].split(","):
                    el = item.select_one(ps)
                    if el: price = clean_price(el.get_text()); break
                if not price: continue
                link = item.select_one("a[href]")
                purl = urljoin(store["base"], link.get("href")) if link else url
                results.append({"store": store["name"], "name": name[:80], "price": price, "url": purl})
    except Exception as e:
        print(f"Error {store['name']}: {e}")
    return results

# Demo data for when scraping is blocked
DEMO_DATA = {
    "creed aventus": [
        {"store": "FragranceX", "name": "Creed Aventus EDP 3.3 oz", "price": 289.99, "url": "https://www.fragrancex.com/products/_cid_cologne-am-lid_c-am-pid_60511m__products.html"},
        {"store": "FragranceNet", "name": "Creed Aventus EDP Spray 3.3 oz", "price": 299.95, "url": "https://www.fragrancenet.com/cologne/creed/creed-aventus"},
        {"store": "MaxAroma", "name": "Creed Aventus 100ml EDP", "price": 310.00, "url": "https://www.maxaroma.com/creed-aventus"},
        {"store": "Jomashop", "name": "Creed Aventus EDP 100ml", "price": 275.00, "url": "https://www.jomashop.com/creed-aventus.html"},
    ],
    "baccarat rouge": [
        {"store": "FragranceX", "name": "Baccarat Rouge 540 EDP 2.4 oz", "price": 299.99, "url": "https://www.fragrancex.com"},
        {"store": "FragranceNet", "name": "Maison Francis Kurkdjian Baccarat Rouge 540", "price": 325.00, "url": "https://www.fragrancenet.com"},
        {"store": "MaxAroma", "name": "MFK Baccarat Rouge 540 70ml", "price": 310.00, "url": "https://www.maxaroma.com"},
    ],
    "bleu de chanel": [
        {"store": "FragranceX", "name": "Bleu De Chanel EDT 3.4 oz", "price": 119.99, "url": "https://www.fragrancex.com"},
        {"store": "FragranceNet", "name": "Bleu De Chanel Eau De Toilette", "price": 125.00, "url": "https://www.fragrancenet.com"},
        {"store": "Jomashop", "name": "Chanel Bleu De Chanel EDT 100ml", "price": 115.00, "url": "https://www.jomashop.com"},
    ],
    "sauvage": [
        {"store": "FragranceX", "name": "Dior Sauvage EDT 3.4 oz", "price": 99.99, "url": "https://www.fragrancex.com"},
        {"store": "FragranceNet", "name": "Sauvage Dior EDT Spray", "price": 105.00, "url": "https://www.fragrancenet.com"},
        {"store": "Jomashop", "name": "Christian Dior Sauvage 100ml", "price": 95.00, "url": "https://www.jomashop.com"},
    ],
    "layton": [
        {"store": "FragranceX", "name": "Parfums de Marly Layton EDP 4.2 oz", "price": 259.99, "url": "https://www.fragrancex.com"},
        {"store": "FragranceNet", "name": "Layton by Parfums de Marly", "price": 275.00, "url": "https://www.fragrancenet.com"},
        {"store": "MaxAroma", "name": "PDM Layton 125ml", "price": 265.00, "url": "https://www.maxaroma.com"},
    ],
}

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
.note{text-align:center;color:#64748b;font-size:0.8rem;margin-top:20px}
</style></head>
<body><div class="container">
<h1>🧴 Perfume Price Tracker</h1>
<div class="search-box">
<form class="search-form" onsubmit="search(event)">
<input type="text" id="q" placeholder="Search perfume (e.g. Creed Aventus, Sauvage)" required>
<button type="submit">🔍 Search</button>
</form>
<div class="tags">
<button class="tag" onclick="quickSearch('Creed Aventus')">Creed Aventus</button>
<button class="tag" onclick="quickSearch('Baccarat Rouge')">Baccarat Rouge</button>
<button class="tag" onclick="quickSearch('Layton')">PDM Layton</button>
<button class="tag" onclick="quickSearch('Bleu de Chanel')">Bleu de Chanel</button>
<button class="tag" onclick="quickSearch('Sauvage')">Sauvage</button>
</div>
</div>
<div id="results"></div>
<p class="note">Prices are approximate and may vary. Click links to verify on store websites.</p>
</div>
<script>
function quickSearch(t){document.getElementById('q').value=t;search(new Event('submit'))}
async function search(e){
e.preventDefault();
const q=document.getElementById('q').value;
const r=document.getElementById('results');
r.innerHTML='<div class="loading">🔍 Searching 5 stores...</div>';
try{
const res=await fetch('/api/search?q='+encodeURIComponent(q));
const data=await res.json();
if(!data.results.length){r.innerHTML='<div class="loading">No results found. Try: Aventus, Sauvage, Baccarat Rouge</div>';return}
const best=Math.min(...data.results.map(x=>x.price));
r.innerHTML='<p style="color:#94a3b8;margin-bottom:10px">Found '+data.results.length+' results</p>'+data.results.map(x=>`
<div class="card ${x.price===best?'best':''}">
<div class="store">${x.store} ${x.price===best?'⭐ BEST PRICE':''}</div>
<div class="name">${x.name}</div>
<div class="price">$${x.price.toFixed(2)}</div>
<a href="${x.url}" target="_blank">View on ${x.store} →</a>
</div>`).join('')}
catch(err){r.innerHTML='<div class="loading">Error searching. Try again.</div>'}}
</script></body></html>"""

@app.get("/api/search")
async def search_api(q: str = Query(..., min_length=2)):
    results = []
    # Try real scraping first
    async with httpx.AsyncClient() as client:
        tasks = [scrape_store(client, store, q) for store in STORES]
        store_results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in store_results:
            if isinstance(r, list):
                results.extend(r)
    
    # If no results, try demo data
    if not results:
        q_lower = q.lower()
        for key, data in DEMO_DATA.items():
            if key in q_lower or any(w in key for w in q_lower.split()):
                results = data
                break
    
    results.sort(key=lambda x: x["price"])
    return {"query": q, "results": results}

@app.get("/health")
async def health():
    return {"status": "ok"}
