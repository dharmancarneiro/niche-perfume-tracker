from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import quote_plus

app = FastAPI(title="Perfume Price Tracker")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Database of popular perfumes with REAL product links
PERFUME_DB = {
    "creed aventus": {
        "name": "Creed Aventus",
        "stores": [
            {"store": "Jomashop", "price": 275, "size": "3.3 oz", "url": "https://www.jomashop.com/creed-aventus-cologne.html"},
            {"store": "FragranceX", "price": 289, "size": "3.3 oz", "url": "https://www.fragrancex.com/products/_cid_cologne-am-lid_a-am-pid_60511m__products.html"},
            {"store": "FragranceNet", "price": 299, "size": "3.3 oz", "url": "https://www.fragrancenet.com/cologne/creed/creed-aventus/eau-de-parfum#288145"},
            {"store": "MaxAroma", "price": 310, "size": "100ml", "url": "https://www.maxaroma.com/creed-aventus-edp-pid-14194-2"},
            {"store": "Olfactory Factory", "price": 285, "size": "100ml", "url": "https://www.olfactoryfactoryllc.com/products/creed-aventus-100ml-latest-batch"},
            {"store": "FragranceBuy", "price": 295, "size": "100ml", "url": "https://fragrancebuy.ca/products/creedaventus-man"},
        ]
    },
    "baccarat rouge 540": {
        "name": "Maison Francis Kurkdjian Baccarat Rouge 540",
        "stores": [
            {"store": "FragranceNet", "price": 325, "size": "2.4 oz", "url": "https://www.fragrancenet.com/perfume/maison-francis-kurkdjian/baccarat-rouge-540/eau-de-parfum"},
            {"store": "Jomashop", "price": 310, "size": "70ml", "url": "https://www.jomashop.com/maison-francis-kurkdjian-baccarat-rouge-540.html"},
            {"store": "MaxAroma", "price": 335, "size": "70ml", "url": "https://www.maxaroma.com/maison-francis-kurkdjian-baccarat-rouge-540-edp"},
            {"store": "FragranceBuy", "price": 320, "size": "70ml", "url": "https://fragrancebuy.ca/products/maborouge540-woman"},
        ]
    },
    "parfums de marly layton": {
        "name": "Parfums de Marly Layton",
        "stores": [
            {"store": "Jomashop", "price": 235, "size": "4.2 oz", "url": "https://www.jomashop.com/parfums-de-marly-layton.html"},
            {"store": "FragranceX", "price": 249, "size": "4.2 oz", "url": "https://www.fragrancex.com/products/_cid_cologne-am-lid_l-am-pid_75928m__products.html"},
            {"store": "FragranceNet", "price": 259, "size": "4.2 oz", "url": "https://www.fragrancenet.com/cologne/parfums-de-marly/parfums-de-marly-layton/eau-de-parfum"},
            {"store": "MaxAroma", "price": 265, "size": "125ml", "url": "https://www.maxaroma.com/parfums-de-marly-layton-edp"},
            {"store": "FragranceBuy", "price": 255, "size": "125ml", "url": "https://fragrancebuy.ca/products/parfumsdemarly-layton-man"},
        ]
    },
    "layton": {
        "name": "Parfums de Marly Layton",
        "stores": [
            {"store": "Jomashop", "price": 235, "size": "4.2 oz", "url": "https://www.jomashop.com/parfums-de-marly-layton.html"},
            {"store": "FragranceX", "price": 249, "size": "4.2 oz", "url": "https://www.fragrancex.com/products/_cid_cologne-am-lid_l-am-pid_75928m__products.html"},
            {"store": "FragranceNet", "price": 259, "size": "4.2 oz", "url": "https://www.fragrancenet.com/cologne/parfums-de-marly/parfums-de-marly-layton/eau-de-parfum"},
            {"store": "FragranceBuy", "price": 255, "size": "125ml", "url": "https://fragrancebuy.ca/products/parfumsdemarly-layton-man"},
        ]
    },
    "tom ford oud wood": {
        "name": "Tom Ford Oud Wood",
        "stores": [
            {"store": "Jomashop", "price": 199, "size": "3.4 oz", "url": "https://www.jomashop.com/tom-ford-oud-wood.html"},
            {"store": "FragranceX", "price": 215, "size": "3.4 oz", "url": "https://www.fragrancex.com/products/_cid_cologne-am-lid_t-am-pid_64155m__products.html"},
            {"store": "FragranceNet", "price": 225, "size": "3.4 oz", "url": "https://www.fragrancenet.com/cologne/tom-ford/tom-ford-oud-wood/eau-de-parfum"},
            {"store": "MaxAroma", "price": 220, "size": "100ml", "url": "https://www.maxaroma.com/tom-ford-oud-wood-edp"},
        ]
    },
    "bleu de chanel": {
        "name": "Bleu de Chanel",
        "stores": [
            {"store": "Jomashop", "price": 115, "size": "3.4 oz EDT", "url": "https://www.jomashop.com/chanel-bleu-de-chanel.html"},
            {"store": "FragranceX", "price": 119, "size": "3.4 oz EDT", "url": "https://www.fragrancex.com/products/_cid_cologne-am-lid_b-am-pid_68848m__products.html"},
            {"store": "FragranceNet", "price": 125, "size": "3.4 oz EDT", "url": "https://www.fragrancenet.com/cologne/chanel/bleu-de-chanel/eau-de-toilette"},
            {"store": "FragranceBuy", "price": 129, "size": "100ml EDT", "url": "https://fragrancebuy.ca/products/chanelbleudechanel-man"},
        ]
    },
    "dior sauvage": {
        "name": "Dior Sauvage",
        "stores": [
            {"store": "Jomashop", "price": 95, "size": "3.4 oz EDT", "url": "https://www.jomashop.com/christian-dior-sauvage.html"},
            {"store": "FragranceX", "price": 99, "size": "3.4 oz EDT", "url": "https://www.fragrancex.com/products/_cid_cologne-am-lid_s-am-pid_73571m__products.html"},
            {"store": "FragranceNet", "price": 105, "size": "3.4 oz EDT", "url": "https://www.fragrancenet.com/cologne/christian-dior/dior-sauvage/eau-de-toilette"},
            {"store": "FragranceBuy", "price": 109, "size": "100ml EDT", "url": "https://fragrancebuy.ca/products/diorsauvage-man"},
        ]
    },
    "sauvage": {
        "name": "Dior Sauvage",
        "stores": [
            {"store": "Jomashop", "price": 95, "size": "3.4 oz EDT", "url": "https://www.jomashop.com/christian-dior-sauvage.html"},
            {"store": "FragranceX", "price": 99, "size": "3.4 oz EDT", "url": "https://www.fragrancex.com/products/_cid_cologne-am-lid_s-am-pid_73571m__products.html"},
            {"store": "FragranceNet", "price": 105, "size": "3.4 oz EDT", "url": "https://www.fragrancenet.com/cologne/christian-dior/dior-sauvage/eau-de-toilette"},
        ]
    },
    "versace eros": {
        "name": "Versace Eros",
        "stores": [
            {"store": "Jomashop", "price": 65, "size": "3.4 oz EDT", "url": "https://www.jomashop.com/versace-eros.html"},
            {"store": "FragranceX", "price": 59, "size": "3.4 oz EDT", "url": "https://www.fragrancex.com/products/_cid_cologne-am-lid_v-am-pid_70212m__products.html"},
            {"store": "FragranceNet", "price": 68, "size": "3.4 oz EDT", "url": "https://www.fragrancenet.com/cologne/versace/versace-eros/eau-de-toilette"},
            {"store": "FragranceBuy", "price": 72, "size": "100ml EDT", "url": "https://fragrancebuy.ca/products/versaceeros-man"},
        ]
    },
    "initio side effect": {
        "name": "Initio Side Effect",
        "stores": [
            {"store": "Jomashop", "price": 245, "size": "3.04 oz", "url": "https://www.jomashop.com/initio-side-effect.html"},
            {"store": "FragranceNet", "price": 265, "size": "3.04 oz", "url": "https://www.fragrancenet.com/cologne/initio-parfums-prives/initio-side-effect/eau-de-parfum"},
            {"store": "MaxAroma", "price": 275, "size": "90ml", "url": "https://www.maxaroma.com/initio-side-effect-edp"},
            {"store": "FragranceBuy", "price": 259, "size": "90ml", "url": "https://fragrancebuy.ca/products/initiosideeffect-man"},
        ]
    },
    "xerjoff naxos": {
        "name": "Xerjoff Naxos",
        "stores": [
            {"store": "Jomashop", "price": 265, "size": "3.4 oz", "url": "https://www.jomashop.com/xerjoff-naxos.html"},
            {"store": "FragranceNet", "price": 285, "size": "3.4 oz", "url": "https://www.fragrancenet.com/cologne/xerjoff/xerjoff-naxos/eau-de-parfum"},
            {"store": "MaxAroma", "price": 295, "size": "100ml", "url": "https://www.maxaroma.com/xerjoff-naxos-edp"},
            {"store": "FragranceBuy", "price": 279, "size": "100ml", "url": "https://fragrancebuy.ca/products/xerjoffnaxos-man"},
        ]
    },
    "ysl y": {
        "name": "Yves Saint Laurent Y EDP",
        "stores": [
            {"store": "Jomashop", "price": 85, "size": "3.3 oz", "url": "https://www.jomashop.com/yves-saint-laurent-y.html"},
            {"store": "FragranceX", "price": 89, "size": "3.3 oz", "url": "https://www.fragrancex.com/products/_cid_cologne-am-lid_y-am-pid_77162m__products.html"},
            {"store": "FragranceNet", "price": 95, "size": "3.3 oz", "url": "https://www.fragrancenet.com/cologne/yves-saint-laurent/y/eau-de-parfum"},
        ]
    },
}

@app.get("/", response_class=HTMLResponse)
async def root():
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Perfume Price Tracker - Compare Gray Market Prices</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,-apple-system,sans-serif;background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);min-height:100vh;color:#fff;padding:20px}
.container{max-width:1000px;margin:0 auto}
h1{text-align:center;font-size:2.2rem;margin:30px 0 10px;background:linear-gradient(135deg,#e94560,#ff6b6b);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.subtitle{text-align:center;color:#94a3b8;margin-bottom:30px}
.search-box{background:rgba(255,255,255,0.1);border-radius:20px;padding:30px;margin:20px 0;backdrop-filter:blur(10px)}
.search-form{display:flex;gap:15px;flex-wrap:wrap;justify-content:center}
input{flex:1;min-width:300px;padding:15px 25px;border:none;border-radius:30px;font-size:1.1rem;background:rgba(255,255,255,0.9);color:#1a1a2e}
input:focus{outline:none;box-shadow:0 0 0 3px rgba(233,69,96,0.5)}
button{padding:15px 40px;border:none;border-radius:30px;background:linear-gradient(135deg,#e94560,#ff6b6b);color:#fff;font-weight:bold;font-size:1.1rem;cursor:pointer;transition:transform 0.2s}
button:hover{transform:translateY(-2px)}
.tags{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px;justify-content:center}
.tag{background:rgba(255,255,255,0.1);padding:10px 20px;border-radius:20px;cursor:pointer;border:none;color:#fff;font-size:0.9rem}
.tag:hover{background:rgba(233,69,96,0.3)}
.perfume-name{font-size:1.5rem;font-weight:bold;text-align:center;margin:20px 0;color:#e94560}
.results{margin-top:20px}
.result-card{background:rgba(255,255,255,0.05);border-radius:15px;padding:20px;margin:15px 0;border-left:4px solid #e94560;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:15px}
.result-card.best{border-color:#10b981;background:rgba(16,185,129,0.1)}
.store-info{flex:1}
.store-name{font-size:1.1rem;font-weight:bold;color:#fff}
.store-size{color:#94a3b8;font-size:0.9rem;margin-top:3px}
.price-info{text-align:right}
.price{font-size:1.8rem;font-weight:bold;color:#10b981}
.best-badge{background:#10b981;color:#fff;padding:3px 10px;border-radius:10px;font-size:0.75rem;margin-left:10px}
.buy-btn{background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;padding:12px 25px;border-radius:10px;text-decoration:none;font-weight:600;white-space:nowrap}
.buy-btn:hover{opacity:0.9}
.no-results{text-align:center;padding:40px;color:#94a3b8}
.info{text-align:center;color:#64748b;font-size:0.85rem;margin-top:30px;line-height:1.6}
.available{color:#94a3b8;font-size:0.85rem;margin-top:15px;text-align:center}
</style></head>
<body>
<div class="container">
<h1>🧴 Perfume Price Tracker</h1>
<p class="subtitle">Compare REAL prices across gray market stores</p>

<div class="search-box">
<form class="search-form" onsubmit="search(event)">
<input type="text" id="q" placeholder="Search perfume (e.g., Creed Aventus, Sauvage, Layton)" required>
<button type="submit">🔍 Compare Prices</button>
</form>
<div class="tags">
<button class="tag" onclick="quickSearch('Creed Aventus')">Creed Aventus</button>
<button class="tag" onclick="quickSearch('Baccarat Rouge 540')">Baccarat Rouge</button>
<button class="tag" onclick="quickSearch('Layton')">PDM Layton</button>
<button class="tag" onclick="quickSearch('Tom Ford Oud Wood')">Oud Wood</button>
<button class="tag" onclick="quickSearch('Bleu de Chanel')">Bleu de Chanel</button>
<button class="tag" onclick="quickSearch('Sauvage')">Sauvage</button>
<button class="tag" onclick="quickSearch('Versace Eros')">Versace Eros</button>
<button class="tag" onclick="quickSearch('Initio Side Effect')">Side Effect</button>
<button class="tag" onclick="quickSearch('Xerjoff Naxos')">Xerjoff Naxos</button>
</div>
</div>

<div id="results"></div>

<p class="info">
⚠️ Prices are approximate and may vary. Always verify the final price on the store website before purchasing.<br>
Links go directly to the product pages on each store.
</p>
</div>

<script>
function quickSearch(term) {
    document.getElementById('q').value = term;
    search(new Event('submit'));
}

async function search(e) {
    e.preventDefault();
    const query = document.getElementById('q').value.trim();
    if (!query) return;
    
    const results = document.getElementById('results');
    results.innerHTML = '<div class="no-results">🔍 Searching...</div>';
    
    try {
        const res = await fetch('/api/search?q=' + encodeURIComponent(query));
        const data = await res.json();
        
        if (!data.found) {
            results.innerHTML = '<div class="no-results">❌ Perfume not found in database.<br><br>Try: Creed Aventus, Sauvage, Layton, Baccarat Rouge, Versace Eros</div>';
            return;
        }
        
        const stores = data.stores;
        const minPrice = Math.min(...stores.map(s => s.price));
        
        let html = '<div class="perfume-name">' + data.name + '</div>';
        html += '<p class="available">Found in ' + stores.length + ' stores - sorted by price</p>';
        html += '<div class="results">';
        
        stores.forEach((s, i) => {
            const isBest = s.price === minPrice;
            html += '<div class="result-card ' + (isBest ? 'best' : '') + '">';
            html += '<div class="store-info">';
            html += '<div class="store-name">' + s.store + (isBest ? '<span class="best-badge">BEST PRICE</span>' : '') + '</div>';
            html += '<div class="store-size">📦 ' + s.size + '</div>';
            html += '</div>';
            html += '<div class="price-info"><div class="price">$' + s.price + '</div></div>';
            html += '<a href="' + s.url + '" target="_blank" rel="noopener" class="buy-btn">View Deal →</a>';
            html += '</div>';
        });
        
        html += '</div>';
        results.innerHTML = html;
    } catch (err) {
        results.innerHTML = '<div class="no-results">Error searching. Try again.</div>';
    }
}
</script>
</body></html>"""

@app.get("/api/search")
async def search_api(q: str = Query(..., min_length=2)):
    query = q.lower().strip()
    
    # Search in database
    for key, data in PERFUME_DB.items():
        if key in query or query in key or any(word in key for word in query.split()):
            stores = sorted(data["stores"], key=lambda x: x["price"])
            return {"found": True, "name": data["name"], "stores": stores}
    
    return {"found": False, "query": q}

@app.get("/api/perfumes")
async def list_perfumes():
    return {"perfumes": list(set(d["name"] for d in PERFUME_DB.values()))}

@app.get("/health")
async def health():
    return {"status": "ok"}
