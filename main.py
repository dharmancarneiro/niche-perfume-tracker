from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title="Niche Perfume Price Tracker")

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

HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Niche Perfume Tracker - Compare Preços</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; }
        .header { background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); padding: 40px 20px; text-align: center; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1rem; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .search-box { background: #1e293b; padding: 30px; border-radius: 16px; margin: -30px auto 30px; max-width: 600px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
        .search-box input { width: 100%; padding: 15px 20px; font-size: 1.1rem; border: none; border-radius: 8px; background: #334155; color: white; }
        .search-box input::placeholder { color: #94a3b8; }
        .section-title { font-size: 1.5rem; margin: 30px 0 20px; color: #a78bfa; }
        .deals-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .deal-card { background: #1e293b; border-radius: 16px; padding: 20px; transition: transform 0.2s; }
        .deal-card:hover { transform: translateY(-5px); }
        .deal-badge { background: #ef4444; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; display: inline-block; margin-bottom: 10px; }
        .deal-badge.hot { background: #f97316; }
        .deal-brand { color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }
        .deal-name { font-size: 1.3rem; margin: 8px 0; color: white; }
        .deal-size { color: #64748b; margin-bottom: 15px; }
        .deal-prices { display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px; }
        .deal-price { font-size: 1.8rem; font-weight: bold; color: #22c55e; }
        .deal-original { color: #64748b; text-decoration: line-through; font-size: 1.1rem; }
        .deal-discount { background: #22c55e; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
        .deal-store { color: #94a3b8; margin-top: 10px; }
        .deal-score { float: right; background: #334155; padding: 5px 10px; border-radius: 8px; font-size: 0.85rem; }
        .stores-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
        .store-card { background: #1e293b; padding: 20px; border-radius: 12px; text-align: center; }
        .store-card h3 { margin-bottom: 5px; }
        .store-card p { color: #22c55e; font-weight: bold; }
        .brands-list { display: flex; flex-wrap: wrap; gap: 10px; }
        .brand-tag { background: #334155; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧴 Niche Perfume Tracker</h1>
        <p>Compare preços de perfumes de nicho em 10+ lojas dos EUA/Canadá</p>
    </div>
    <div class="container">
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Buscar perfume... ex: Aventus, Layton, Baccarat" onkeyup="searchPerfumes()">
        </div>
        <h2 class="section-title">🔥 Melhores Promoções</h2>
        <div id="dealsContainer" class="deals-grid"></div>
        <h2 class="section-title">🏪 Lojas Monitoradas</h2>
        <div id="storesContainer" class="stores-grid"></div>
        <h2 class="section-title">🏷️ Marcas de Nicho</h2>
        <div id="brandsContainer" class="brands-list"></div>
    </div>
    <script>
        async function loadDeals() {
            const response = await fetch('/deals');
            const data = await response.json();
            document.getElementById('dealsContainer').innerHTML = data.deals.map(deal => `
                <div class="deal-card">
                    <span class="deal-badge ${deal.discount >= 35 ? 'hot' : ''}">${deal.discount >= 35 ? '🔥 HOT' : 'DEAL'}</span>
                    <span class="deal-score">Score: ${deal.score}</span>
                    <div class="deal-brand">${deal.brand}</div>
                    <div class="deal-name">${deal.name}</div>
                    <div class="deal-size">${deal.size}</div>
                    <div class="deal-prices">
                        <span class="deal-price">$${deal.price}</span>
                        <span class="deal-original">$${deal.original}</span>
                        <span class="deal-discount">-${deal.discount}%</span>
                    </div>
                    <div class="deal-store">📍 ${deal.store}</div>
                </div>
            `).join('');
        }
        async function loadStores() {
            const response = await fetch('/stores');
            const data = await response.json();
            document.getElementById('storesContainer').innerHTML = data.stores.map(store => `
                <div class="store-card"><h3>${store.name}</h3><p>${store.discount}</p></div>
            `).join('');
        }
        async function loadBrands() {
            const response = await fetch('/brands');
            const data = await response.json();
            document.getElementById('brandsContainer').innerHTML = data.brands.map(brand => `
                <span class="brand-tag">${brand}</span>
            `).join('');
        }
        async function searchPerfumes() {
            const q = document.getElementById('searchInput').value;
            if (q.length < 2) { loadDeals(); return; }
            const response = await fetch('/search?q=' + q);
            const data = await response.json();
            document.getElementById('dealsContainer').innerHTML = data.results.map(deal => `
                <div class="deal-card">
                    <span class="deal-badge">ENCONTRADO</span>
                    <div class="deal-brand">${deal.brand}</div>
                    <div class="deal-name">${deal.name}</div>
                    <div class="deal-size">${deal.size}</div>
                    <div class="deal-prices">
                        <span class="deal-price">$${deal.price}</span>
                        <span class="deal-original">$${deal.original}</span>
                        <span class="deal-discount">-${deal.discount}%</span>
                    </div>
                    <div class="deal-store">📍 ${deal.store}</div>
                </div>
            `).join('');
        }
        loadDeals(); loadStores(); loadBrands();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE

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

