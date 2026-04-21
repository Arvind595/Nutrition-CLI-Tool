# 🍎 Nutrition CLI Tool

A command-line tool to fetch detailed food nutrition data using the USDA FoodData Central API.

---

## 🚀 Features

* Full nutrient breakdown (macros + micros)
* Multiple search results with selection
* Pretty table output (tabulate)
* CSV and Excel export
* Local caching (24h TTL)
* Retry handling for API rate limits (HTTP 429)

---

## 🧰 Tech Stack

* Python 3
* requests
* tabulate
* openpyxl

---

## 🔑 API Source

Powered by USDA FoodData Central API (via api.data.gov)

Get your free API key:
https://fdc.nal.usda.gov/api-key-signup.html

---

## 📦 Installation

```bash
git clone https://github.com/your-username/nutrition-cli.git
cd nutrition-cli
pip install -r requirements.txt
```

---

## ⚙️ Setup

Set your API key:

### Windows (CMD)

```bash
set FDC_API_KEY=your_api_key
```

### Linux / Mac

```bash
export FDC_API_KEY=your_api_key
```

---

## ▶️ Usage

### Search for a food

```bash
python nutrition_cli.py search "apple"
```

### Limit number of results

```bash
python nutrition_cli.py search "milk" --limit 3
```

### Export to CSV

```bash
python nutrition_cli.py search "banana" --csv banana.csv
```

### Export to Excel

```bash
python nutrition_cli.py search "rice" --xlsx rice.xlsx
```

---

## 🧾 Example Output

```
Food: Apples, raw

+----------------------+--------+--------+
| Nutrient             | Value  | Unit   |
+----------------------+--------+--------+
| Energy               | 52     | kcal   |
| Protein              | 0.26   | g      |
| Carbohydrate         | 13.81  | g      |
| Fiber                | 2.4    | g      |
| Vitamin C            | 4.6    | mg     |
+----------------------+--------+--------+
```

---

## 🧠 How It Works

1. Search food via API
2. Select result
3. Fetch full nutrient data
4. Cache locally
5. Display + optional export

---

## ⚠️ Notes

* Cache file: `nutrition_cache.json`
* Cache expires after 24 hours
* Handles API rate limiting with exponential backoff

---

## 📌 Future Improvements

* Non-interactive mode (`--index`)
* Batch processing
* Web UI / REST API
* Nutrition comparison between foods

---

## 📄 License

MIT License
