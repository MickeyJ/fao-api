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

```yaml
app/
├── models/               # SQLAlchemy models (Item, Area, Price, Index, etc.)
├── database.py           # DB connection, session, metadata setup

pipelines/
└── fao_prices_e/         # FAO Prices_E data processing
    ├── items.py          # Ingests Items from Prices_E_ItemCodes.csv
    ├── areas.py          # Ingests Areas from Prices_E_AreaCodes.csv
    ├── item_prices.py    # Ingests Prices_E_All_Data_(Normalized).csv
    └── __init__.py       # Utilities or shared logic
```

Each module contains:  
- `load()`: Load data from local/S3 CSV file
- `clean()`: Clean and standardize inputs
- `insert()`: Commit to the database  

---

## ⚙️ Setup

### 0. Makefile?

See Makefile for commands. Examples:
```bash
make use-local-db
make db-upgrade
make db-revision msg='add foreign keys 🔀'
```

### 1. Install dependencies

```bash
make initialize # install using pip-tools
```

### 2. Create Database

```sql
CREATE DATABASE fooddb; 
-- depending on the user in your config file,
-- and if using the default public schema,
-- you might need to run this
GRANT USAGE, CREATE ON SCHEMA public TO mynameis;
```

### 3. Configure environment variables 👁️‍🗨️

Create a `.env` file in the root:
*If you know me and actually want to play with this I can share the AWS db info*
```bash
DB_USER=mynameis
DB_PASSWORD=mypwis
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fooddb
```

### 4. Run Database Migrations

```bash
alembic upgrade head
alembic revision --autogenerate -m 'add nutrients table'
# OR
make db-upgrade
make db-revision msg='add nutrients table'
```

### 5. Populate the database
*there are also make commands*
```bash
python -m pipelines.fao_prices_e                # Run entire prices pipeline
python -m pipelines.fao_prices_e.items          # Run individual module
python -m pipelines.fao_prices_e.areas          # ***
python -m pipelines.fao_prices_e.item_prices    # ***
# (other pipelines in progress)
```

### 6. Play with the API

```bash
make api
```

### 7. Terraform own AWS Aurora db (very super optional)
*requires a good deal of other setup I won't get into here*
```bash
cd terraform
terraform init
terraform validate
terraform plan
terraform apply
```
---

## 📊 Data Sources
- https://www.fao.org/faostat/en/         — Bulk availble download here
- https://www.fao.org/faostat/en/#data/PP — FAO Price Statistics  
- https://www.fao.org/faostat/en/#data/CP — FAO Consumer Price Indices  
---

## 🧠 Goals & Future Plans

- [x] Normalize FAO food price data  
- [x] Support schema-aware ingestion  
- [x] Set up remote database  
- [x] Start building an API  
- [ ] Integrate USDA nutrient data  
- [ ] Add local consumer price scraping  
- [ ] Enable dietary pattern and meal planning intelligence  

---

