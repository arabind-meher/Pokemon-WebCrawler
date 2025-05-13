# 🕸️ Pokémon WebCrawler

A Scrapy-based web crawler for extracting detailed information about Pokémon from [pokemondb.net](https://pokemondb.net). This project scrapes structured data including forms, types, stats, and more, and stores it in a local MongoDB database.

---

## 📦 Features

- Crawls Pokémon data starting from a **single Pokémon page**
- Extracts structured data:
  - Name, Form, Types, Species
  - Pokédex Index (National and Regional)
  - Height, Weight, Abilities
  - Training and Breeding Information
  - Base Stats and Total Stats
- Stores data in MongoDB (`pokemon_db.pokedex`)
- Uses `.env` configuration for secure DB connection
- Modular codebase with clean separation (spider, pipeline, DB client)

---

## 🚀 Technologies Used

- Python 3.12+
- [Scrapy](https://scrapy.org/)
- [MongoDB](https://www.mongodb.com/)
- [pymongo](https://pypi.org/project/pymongo/)
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## 📂 Project Structure

```
pokemon_scraper/
├── spiders/
│   └── pokemon_spider.py        # Scrapes Pokémon data
├── items.py                     # Defines the data structure
├── pipelines.py                 # Handles MongoDB insertion
├── connection.py                # MongoDB client using .env
├── middlewares.py              # Default Scrapy middlewares
├── settings.py                  # Scrapy configuration
.env                             # MongoDB connection settings (not committed)
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/Pokemon-WebCrawler.git
cd Pokemon-WebCrawler
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add MongoDB configuration to `.env` file
Create a `.env` file in the project root:
```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=pokemon_db
```

### 5. Run MongoDB
Ensure MongoDB is running locally on `localhost:27017`.

### 6. Start the crawler
```bash
scrapy crawl pokemon
```

---

## 📊 Crawl Summary

- **Total Pages Crawled**: 1,025  
- **Total Pokémon Entries Extracted**: 1,215 (including alternate forms)

---

## 🧪 Sample Output (MongoDB document)

```json
{
  "name": "Bulbasaur",
  "form": null,
  "index": 1,
  "types": ["Grass", "Poison"],
  "species": "Seed Pokémon",
  "height": "0.7 m",
  "weight": "6.9 kg",
  "abilities": ["Overgrow", "Chlorophyll"],
  "local_index": {
    "Kanto": 1
  },
  "training": {
    "EV yield": "1 Special Attack",
    "Base EXP": "64"
  },
  "breeding": {
    "Egg group": "Monster, Grass"
  },
  "base_stats": {
    "HP": 45,
    "Attack": 49,
    "Defense": 49,
    "Total": 318
  }
}
```

---

## 📌 Notes

- The crawler currently starts from a **manually specified Pokémon page** (e.g., `https://pokemondb.net/pokedex/wo-chien`).
- Crawling the full Pokédex using `/pokedex/all` is not yet implemented.
- All Pokémon forms are stored separately — no deduplication is performed.

---

## 🙋‍♂️ Author

**Arabind Meher**  
- [GitHub](https://github.com/arabind-meher)  
- [LinkedIn](https://www.linkedin.com/in/arabind-meher/)
