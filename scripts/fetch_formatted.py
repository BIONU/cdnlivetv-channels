import json
import os
import re
from datetime import datetime, timezone
import requests

COUNTRY_NAMES = {
    'us': 'United States', 'es': 'Spain', 'gb': 'United Kingdom', 'fr': 'France',
    'pl': 'Poland', 'de': 'Germany', 'it': 'Italy', 'au': 'Australia',
    'za': 'South Africa', 'pt': 'Portugal', 'gr': 'Greece', 'rs': 'Serbia',
    'hr': 'Croatia', 'br': 'Brazil', 'sa': 'Saudi Arabia',
    'bg': 'Bulgaria', 'se': 'Sweden', 'dk': 'Denmark', 'cz': 'Czech Republic',
    'il': 'Israel', 'nz': 'New Zealand', 'ca': 'Canada',
    'nl': 'Netherlands', 'at': 'Austria', 'ar': 'Argentina', 'mx': 'Mexico',
    'tr': 'Turkey', 'ro': 'Romania', 'cy': 'Cyprus', 'ru': 'Russia',
    'in': 'India', 'be': 'Belgium', 'ae': 'United Arab Emirates', 'hu': 'Hungary',
    'uy': 'Uruguay', 'cl': 'Chile', 'co': 'Colombia', 'eg': 'Egypt',
}

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text

def build_output(channels_data):
    categories = {}
    formatted_channels = []
    skipped = 0
    
    for ch in channels_data:
        code = (ch.get("code") or "").lower()
        name = ch.get("name") or ""
        image = ch.get("image") or ""
        url = ch.get("url") or ""
        
        if not code or not name or not url:
            skipped += 1
            continue
        
        category_name = COUNTRY_NAMES.get(code, code.upper())
        
        if category_name not in categories:
            categories[category_name] = {
                "name": category_name,
                "icon": f"https://flagcdn.com/w80/{code}.png",
            }
        
        formatted_channels.append({
            "category": category_name,
            "codec": "hard",
            "epg_id": slugify(name),
            "name": name,
            "icon": image,
            "url": url,
        })
    
    sorted_categories = dict(sorted(categories.items()))
    formatted_channels.sort(key=lambda x: (x["category"], x["name"].lower()))
    
    return {
        "provider": {
            "name": "CDN Live TV",
            "website": "https://cdnlivetv.tv",
            "source_api": "https://api.cdnlivetv.tv/api/v1/channels/?user=cdnlivetv&plan=free",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "total_categories": len(sorted_categories),
            "total_channels": len(formatted_channels),
            "skipped_channels": skipped,
        },
        "categories": sorted_categories,
        "channels": formatted_channels,
    }

def main():
    api_url = "https://api.cdnlivetv.tv/api/v1/channels/?user=cdnlivetv&plan=free"
    
    print("📥 Fetching data from API...")
    try:
        response = requests.get(api_url, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    
    channels = data.get("channels", [])
    print(f"✅ Retrieved {len(channels)} channels")
    
    print("🔧 Formatting data...")
    result = build_output(channels)
    
    os.makedirs("data", exist_ok=True)
    output_path = "data/channels_formatted.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 Done! Saved to {output_path}")
    print(f"   Categories: {result['provider']['total_categories']}")
    print(f"   Channels  : {result['provider']['total_channels']}")

if __name__ == "__main__":
    main()