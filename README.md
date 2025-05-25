> [!WARNING]
> # 🚧 WORK IN PROGRESS 🚧
> This project is under active development and not yet complete. Features may be missing or partially implemented, and documentation may be incomplete. Use at your own risk.


# Food Data ETL for Data Analysis + Dietary Intelligence

**Description:**  
ETL codebase for food data analysis and dietary intelligence, with pipelines for structured ingestion of global food price and nutrition data.

---

## 📦 Project Overview

This project builds a PostgreSQL-based backend system to organize, query, and analyze:

- 🥦 Food commodities and items (FAO CPC codes)  
- 🌍 Area codes and regions (M49 and FAO Area codes)  
- 💰 Item price data by country and year  
- 📈 Consumer food price indices (CPI) and inflation metrics  

It uses official FAO bulk datasets and is designed to scale into deeper layers of nutrition, local pricing, and meal intelligence.

---

## 🗂️ Project Structure

```
app/
├── models/               # SQLAlchemy models (Item, Area, Price, Index, etc.)
├── database.py           # DB connection, session, metadata setup

pipelines/
└── fao_prices_e/         # FAO Prices_E data processing
    ├── items.py          # Ingests Items from Prices_E_ItemCodes.csv
    ├── areas.py          # Ingests Areas from Prices_E_AreaCodes.csv
    └── __init__.py       # Utilities or shared logic
```

Each module contains:  
- `load()`: Load data from CSV/S3  
- `clean()`: Clean and standardize inputs  
- `insert()`: Commit to the database  

---

## ⚙️ Setup

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the root:

```
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fooddb
DB_SCHEMA=food
```

### 3. Run database migrations

```
alembic upgrade head
```

### 4. Populate the database

```
python -m pipelines.fao_prices_e.items
python -m pipelines.fao_prices_e.areas
# (other pipelines in progress)
```

---

## 📊 Data Sources

- https://www.fao.org/faostat/en/#data/PP — FAO Price Statistics  
- https://www.fao.org/faostat/en/#data/CP — FAO Consumer Price Indices  

---

## 🧠 Goals & Future Plans

- [x] Normalize FAO food price data  
- [x] Support schema-aware ingestion  
- [ ] Integrate USDA nutrient data  
- [ ] Add local consumer price scraping  
- [ ] Enable dietary pattern and meal planning intelligence  

---

