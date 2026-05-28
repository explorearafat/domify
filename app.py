from flask import Flask, render_template, request, jsonify
from concurrent.futures import ThreadPoolExecutor
import requests
import random
import re

app = Flask(__name__)

TLD_INFO = {
    ".com": "Commercial",
    ".net": "Network",
    ".org": "Organization",
    ".info": "Information",
    ".biz": "Business",
    ".co": "Company",
    ".io": "Tech Startup",
    ".dev": "Developer Platform",
    ".app": "Application",
    ".tech": "Technology",
    ".cloud": "Cloud Platform",
    ".software": "Software Company",
    ".systems": "System Services",
    ".digital": "Digital Brand",
    ".solutions": "Solutions Provider",
    ".tools": "Online Tools",
    ".site": "Website Platform",
    ".online": "Online Presence",
    ".website": "Website",
    ".store": "Online Store",
    ".host": "Hosting Platform",
    ".ai": "Artificial Intelligence",
    ".bot": "Automation Bot",
    ".ml": "Machine Learning",
    ".vision": "Vision Technology",
    ".future": "Future Technology",
    ".xyz": "Modern Brand",
    ".world": "Global Brand",
    ".space": "Creative Space",
    ".one": "Single Platform",
    ".live": "Live Platform",
    ".today": "Daily Service",
    ".now": "Instant Platform",
    ".plus": "Premium Service",
    ".pro": "Professional Brand",
    ".vip": "VIP Service",
    ".elite": "Elite Brand",
    ".club": "Community Club",
    ".studio": "Creative Studio",
    ".finance": "Finance Platform",
    ".money": "Money Service",
    ".bank": "Banking Platform",
    ".capital": "Capital Service",
    ".exchange": "Exchange Platform",
    ".investments": "Investment Service",
    ".chat": "Chat Platform",
    ".social": "Social Network",
    ".media": "Media Platform",
    ".network": "Networking Service",
    ".community": "Community Platform",
    ".shop": "Online Shop",
    ".shopping": "Shopping Platform",
    ".market": "Marketplace",
    ".sale": "Sales Platform",
    ".deals": "Deals Website",
    ".academy": "Educational Academy",
    ".education": "Education Platform",
    ".school": "School Platform",
    ".study": "Study Resource",
    ".tv": "Media Streaming",
    ".video": "Video Platform",
    ".music": "Music Platform",
    ".fun": "Entertainment Website",
    ".games": "Gaming Platform",
    ".security": "Cyber Security",
    ".safe": "Security Platform",
    ".protection": "Protection Service",
    ".health": "Healthcare Platform",
    ".care": "Care Service",
    ".clinic": "Medical Clinic",
    ".food": "Food Brand",
    ".cafe": "Cafe Website",
    ".restaurant": "Restaurant Platform",
    ".crypto": "Cryptocurrency Platform",
    ".coin": "Crypto Coin",
    ".wallet": "Digital Wallet",
    ".us": "United States",
    ".uk": "United Kingdom",
    ".bd": "Bangladesh",
    ".in": "India",
    ".jp": "Japan",
    ".ca": "Canada",
    ".x": "Next Generation Brand",
    ".zone": "Custom Zone",
    ".agency": "Creative Agency",
    ".group": "Business Group",
    ".team": "Team Platform",
    ".works": "Professional Works",
    ".services": "Service Provider",
    ".expert": "Expert Service",
    ".guru": "Professional Guru"
}

GENERATORS = [
    "labs",
    "base",
    "stack",
    "works",
    "space",
    "studio",
    "verse",
    "forge",
    "core",
    "nest",
    "tech",
    "cloud",
    "sync",
    "byte",
    "node",
    "data",
    "net",
    "host",
    "dev",
    "system",
    "ai",
    "mind",
    "brain",
    "neural",
    "gen",
    "logic",
    "prompt",
    "vision",
    "gpt",
    "matrix",
    "pay",
    "bank",
    "cash",
    "coin",
    "vault",
    "fund",
    "finance",
    "money",
    "wallet",
    "capital",
    "chat",
    "talk",
    "link",
    "social",
    "connect",
    "meet",
    "wave",
    "buzz",
    "loop",
    "circle",
    "ly",
    "ify",
    "io",
    "up",
    "go",
    "hq",
    "x",
    "pro",
    "plus",
    "max",
    "nova",
    "zen",
    "prime",
    "ultra",
    "elite",
    "alpha",
    "orbit",
    "quant",
    "pulse",
    "spark"
]

def check_domain(domain):
    try:
        url = f"https://dns.google/resolve?name={domain}"
        response = requests.get(url, timeout=2)
        data = response.json()
        available = "Answer" not in data
        return {
            "domain": domain,
            "available": available,
            "price": random.choice([
                "$8.99/year", "$10.99/year", "$12.99/year", "$14.99/year", "$9.49/year"
            ])
        }
    except:
        return {
            "domain": domain,
            "available": False,
            "price": "$12.99/year"
        }

def clean_input(text):
    text = text.lower().strip()
    text = text.replace("https://", "")
    text = text.replace("http://", "")
    text = text.replace("www.", "")
    text = text.split("/")[0]
    text = re.sub(r'[^a-z0-9.-]', '', text)
    return text

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query", "")
    query = clean_input(query)

    results = []
    suggestions = []
    message = ""

    if not query:
        return jsonify({"message": "Please enter a valid keyword", "results": [], "suggestions": []})

    if "." in query:
        result = check_domain(query)
        results.append(result)
        extension = "." + query.split(".")[-1]
        extension_name = TLD_INFO.get(extension, "Domain")
        if result["available"]:
            message = f'Your "{query}" is available for your {extension_name} website. Secure it now.'
        else:
            message = f'"{query}" is already taken. Here are some smart alternatives.'
            base = query.split(".")[0]
            generated = []
            for word in GENERATORS:
                generated.append(f"{base}{word}.com")
                generated.append(f"{word}{base}.com")
            generated = list(set(generated))[:12]
            with ThreadPoolExecutor(max_workers=12) as executor:
                suggestions = list(executor.map(check_domain, generated))
    else:
        domains = [f"{query}{tld}" for tld in TLD_INFO.keys()]
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(check_domain, domains))
        available_any = any(item["available"] for item in results)
        if available_any:
            first_avail = next(item for item in results if item["available"])
            ext = "." + first_avail["domain"].split(".")[-1]
            ext_name = TLD_INFO.get(ext, "Domain")
            message = f'Your "{first_avail["domain"]}" is available for your {ext_name} website. Great find!'
        else:
            message = "No direct domains available. Try these creative alternatives below."
            generated = []
            for word in GENERATORS:
                generated.append(f"{query}{word}.com")
                generated.append(f"{word}{query}.com")
            generated = list(set(generated))[:12]
            with ThreadPoolExecutor(max_workers=12) as executor:
                suggestions = list(executor.map(check_domain, generated))

    return jsonify({
        "message": message,
        "results": results,
        "suggestions": suggestions
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)