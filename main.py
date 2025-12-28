from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import quote_plus

app = FastAPI(title="Perfume Price Tracker")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

STORES = [
    {"name": "FragranceX", "search": "https://www.fragrancex.com/search?q={q}", "discount": "30-50% off retail"},
    {"name": "FragranceNet", "search": "https://www.fragrancenet.com/search?searchTerm={q}", "discount": "35-60% off retail"},
    {"name": "MaxAroma", "search": "https://www.maxaroma.com/search?q={q}", "discount": "20-40% off retail"},
    {"name": "Jomashop", "search": "https://www.jomashop.com/catalogsearch/result/?q={q}", "discount": "15-35% off retail"},
    {"name": "FragranceBuy (CA)", "search": "https://fragrancebuy.ca/search?type=product&q={q}", "discount": "20-35% off retail"},
    {"name": "Venba Fragrance", "search": "https://venbafragrance.com/search?q={q}", "discount": "25-45% off retail"},
    {"name": "Perfume Online (CA)", "search": "https://perfumeonline.ca/search?q={q}", "discount": "25-40% off retail"},
    {"name": "Aura Fragrances", "search": "https://aurafragrances.com/search?q={q}", "discount": "40-60% off retail"},
]

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
button:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(233,69,96,0.4)}
.tags{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px;justify-content:center}
.tag{background:rgba(255,255,255,0.1);padding:10px 20px;border-radius:20px;cursor:pointer;border:none;color:#fff;font-size:0.9rem;transition:background 0.2s}
.tag:hover{background:rgba(233,69,96,0.3)}
.results{margin-top:30px;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}
.store-card{background:rgba(255,255,255,0.05);border-radius:15px;padding:20px;border:1px solid rgba(255,255,255,0.1);transition:transform 0.2s,border-color 0.2s}
.store-card:hover{transform:translateY(-5px);border-color:#e94560}
.store-name{font-size:1.3rem;font-weight:bold;margin-bottom:5px}
.store-discount{color:#10b981;font-size:0.95rem;margin-bottom:15px}
.store-link{display:block;padding:12px 20px;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;text-decoration:none;border-radius:10px;text-align:center;font-weight:600;transition:opacity 0.2s}
.store-link:hover{opacity:0.9}
.info{text-align:center;color:#64748b;font-size:0.85rem;margin-top:30px;line-height:1.6}
.hidden{display:none}
.tip{background:rgba(16,185,129,0.1);border:1px solid #10b981;border-radius:10px;padding:15px;margin:20px 0;text-align:center;color:#10b981}
</style></head>
<body>
<div class="container">
<h1>🧴 Perfume Price Tracker</h1>
<p class="subtitle">Compare prices across 8 gray market stores in US & Canada</p>

<div class="search-box">
<form class="search-form" onsubmit="search(event)">
<input type="text" id="q" placeholder="Enter perfume name (e.g., Creed Aventus, Baccarat Rouge 540)" required>
<button type="submit">🔍 Compare Prices</button>
</form>
<div class="tags">
<button class="tag" onclick="quickSearch('Creed Aventus')">Creed Aventus</button>
<button class="tag" onclick="quickSearch('Baccarat Rouge 540')">Baccarat Rouge 540</button>
<button class="tag" onclick="quickSearch('Parfums de Marly Layton')">PDM Layton</button>
<button class="tag" onclick="quickSearch('Tom Ford Oud Wood')">Oud Wood</button>
<button class="tag" onclick="quickSearch('Bleu de Chanel')">Bleu de Chanel</button>
<button class="tag" onclick="quickSearch('Dior Sauvage')">Sauvage</button>
<button class="tag" onclick="quickSearch('Versace Eros')">Versace Eros</button>
</div>
</div>

<div id="tip" class="tip hidden">
💡 <strong>Tip:</strong> Open each store in a new tab to compare prices side by side!
</div>

<div id="results" class="results"></div>

<p class="info">
These are trusted gray market retailers offering authentic perfumes at discounted prices.<br>
Prices vary by size, availability, and whether it's a tester. Always verify on the store website.
</p>
</div>

<script>
const stores = [
    {name: "FragranceX", search: "https://www.fragrancex.com/search?q={q}", discount: "30-50% off retail", color: "#e94560"},
    {name: "FragranceNet", search: "https://www.fragrancenet.com/search?searchTerm={q}", discount: "35-60% off retail", color: "#8b5cf6"},
    {name: "MaxAroma", search: "https://www.maxaroma.com/search?q={q}", discount: "20-40% off retail", color: "#f59e0b"},
    {name: "Jomashop", search: "https://www.jomashop.com/catalogsearch/result/?q={q}", discount: "15-35% off retail", color: "#10b981"},
    {name: "FragranceBuy (CA)", search: "https://fragrancebuy.ca/search?type=product&q={q}", discount: "20-35% off retail", color: "#3b82f6"},
    {name: "Venba Fragrance", search: "https://venbafragrance.com/search?q={q}", discount: "25-45% off retail", color: "#ec4899"},
    {name: "Perfume Online (CA)", search: "https://perfumeonline.ca/search?q={q}", discount: "25-40% off retail", color: "#06b6d4"},
    {name: "Aura Fragrances", search: "https://aurafragrances.com/search?q={q}", discount: "40-60% off retail", color: "#84cc16"},
];

function quickSearch(term) {
    document.getElementById('q').value = term;
    search(new Event('submit'));
}

function search(e) {
    e.preventDefault();
    const query = document.getElementById('q').value.trim();
    if (!query) return;
    
    document.getElementById('tip').classList.remove('hidden');
    const results = document.getElementById('results');
    
    results.innerHTML = stores.map(store => {
        const url = store.search.replace('{q}', encodeURIComponent(query));
        return `
        <div class="store-card">
            <div class="store-name" style="color:${store.color}">${store.name}</div>
            <div class="store-discount">📉 Typically ${store.discount}</div>
            <a href="${url}" target="_blank" rel="noopener" class="store-link">
                Search "${query}" →
            </a>
        </div>`;
    }).join('');
}
</script>
</body></html>"""

@app.get("/api/stores")
async def get_stores():
    return {"stores": STORES, "total": len(STORES)}

@app.get("/health")
async def health():
    return {"status": "ok"}
