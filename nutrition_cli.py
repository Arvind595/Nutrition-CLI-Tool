#!/usr/bin/env python3

import requests
import time
import json
import os
import argparse
from datetime import datetime, timedelta
import csv

from tabulate import tabulate

try:
    import openpyxl
except ImportError:
    openpyxl = None

API_KEY = os.getenv("FDC_API_KEY") or "YOUR_API_KEY"
BASE_URL = "https://api.nal.usda.gov/fdc/v1"
CACHE_FILE = "nutrition_cache.json"
CACHE_TTL_HOURS = 24

# -------------------- Cache --------------------

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_cached(cache, key):
    if key in cache:
        entry = cache[key]
        ts = datetime.fromisoformat(entry["timestamp"])
        if datetime.now() - ts < timedelta(hours=CACHE_TTL_HOURS):
            return entry["data"]
    return None

def set_cache(cache, key, data):
    cache[key] = {
        "timestamp": datetime.now().isoformat(),
        "data": data
    }

# -------------------- Retry Logic --------------------

def request_with_retry(url, params=None, max_retries=5):
    delay = 1
    for _ in range(max_retries):
        r = requests.get(url, params=params)

        if r.status_code == 200:
            return r.json()

        elif r.status_code == 429:
            print(f"Rate limited. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2

        else:
            r.raise_for_status()

    raise Exception("Max retries exceeded")

# -------------------- API --------------------

def search_food(food_name, page_size=5):
    url = f"{BASE_URL}/foods/search"
    params = {
        "api_key": API_KEY,
        "query": food_name,
        "pageSize": page_size
    }
    return request_with_retry(url, params)

def get_food_details(fdc_id):
    url = f"{BASE_URL}/food/{fdc_id}"
    params = {"api_key": API_KEY}
    return request_with_retry(url, params)

def extract_all_nutrients(food):
    nutrients = food.get("foodNutrients", [])
    result = []

    for n in nutrients:
        name = n.get("nutrient", {}).get("name") or n.get("nutrientName")
        value = n.get("amount") or n.get("value")
        unit = n.get("nutrient", {}).get("unitName") or n.get("unitName")

        if name and value is not None:
            result.append({
                "Nutrient": name,
                "Value": value,
                "Unit": unit
            })

    return result

# -------------------- Export --------------------

def export_csv(filename, nutrients):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Nutrient", "Value", "Unit"])
        writer.writeheader()
        writer.writerows(nutrients)
    print(f"Exported to {filename}")

def export_excel(filename, nutrients):
    if not openpyxl:
        print("openpyxl not installed. Install with: pip install openpyxl")
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Nutrition"

    ws.append(["Nutrient", "Value", "Unit"])
    for n in nutrients:
        ws.append([n["Nutrient"], n["Value"], n["Unit"]])

    wb.save(filename)
    print(f"Exported to {filename}")

# -------------------- Output --------------------

def print_output(name, nutrients):
    print(f"\nFood: {name}\n")

    if not nutrients:
        print("No nutrient data available")
        return

    table = [[n["Nutrient"], n["Value"], n["Unit"]] for n in nutrients]

    print(tabulate(
        table,
        headers=["Nutrient", "Value", "Unit"],
        tablefmt="grid"
    ))

# -------------------- CLI --------------------

def cmd_search(args, cache):
    data = search_food(args.food, args.limit)

    foods = data.get("foods", [])
    if not foods:
        print("No results")
        return

    print("\nResults:")
    for i, f in enumerate(foods):
        print(f"{i+1}. {f['description']} (fdcId={f['fdcId']})")

    choice = int(input("\nSelect item number: ")) - 1
    if choice < 0 or choice >= len(foods):
        print("Invalid selection")
        return

    selected = foods[choice]
    cache_key = str(selected["fdcId"])

    cached = get_cached(cache, cache_key)
    if cached:
        print("(cached)")
        nutrients = cached
    else:
        details = get_food_details(selected["fdcId"])
        nutrients = extract_all_nutrients(details)
        set_cache(cache, cache_key, nutrients)
        save_cache(cache)

    print_output(selected["description"], nutrients)

    if args.csv:
        export_csv(args.csv, nutrients)

    if args.xlsx:
        export_excel(args.xlsx, nutrients)

# -------------------- Main --------------------

def main():
    parser = argparse.ArgumentParser(description="Nutrition CLI Tool")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("search", help="Search food")
    p.add_argument("food", help="Food name")
    p.add_argument("--limit", type=int, default=5, help="Number of results")
    p.add_argument("--csv", help="Export to CSV file")
    p.add_argument("--xlsx", help="Export to Excel file")

    args = parser.parse_args()
    cache = load_cache()

    if args.command == "search":
        cmd_search(args, cache)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
