# FAO Data API

> ⚠️ **Work in Progress**: This API is under active development and not yet ready for production use. Features, endpoints, and data structures may change without notice.

## Overview

The FAO Data API provides programmatic access to agricultural and food security datasets from the Food and Agriculture Organization of the United Nations. This API serves as a modern interface to 84+ FAO statistical datasets, making global agricultural data more accessible to researchers, policymakers, and developers.

## Current Status

- ✅ Core ETL pipelines operational
- ✅ Basic API endpoints functional
- ✅ Database schema implemented
- ✅ Deployed to AWS App Runner
- 🚧 Authentication system (in development)
- 🚧 Rate limiting (planned)
- 🚧 Comprehensive documentation (in progress)

## Features

### Available Now
- RESTful API endpoints for all major FAO datasets
- Foreign key relationships between datasets
- Basic filtering and pagination
- JSON response format
- Automated data ingestion from FAO sources

### Datasets Include
- Agricultural production statistics
- Food prices and consumer price indices
- Trade flows (imports/exports)
- Food security indicators
- Climate and environmental data
- Land use and irrigation statistics
- Employment and rural development indicators

## Technology Stack

- **API Framework**: FastAPI (Python 3.10)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Deployment**: AWS App Runner
- **ETL**: Custom Python pipelines with pandas
- **CI/CD**: GitHub Actions
- **IaC**: Terraform

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- pip or conda for package management

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fao-data-api.git
cd fao-data-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials
```

### Database Setup

```bash
# Run database migrations
alembic upgrade head

# Run ETL pipelines to populate data (optional)
python -m fao.src.db.pipelines
```

### Running the API

```bash
# Development server
python -m fao.src.api

# Or with auto-reload
uvicorn fao.src.api.__main__:app --reload --host localhost --port 8000
```

## API Usage

### Base URL
```
http://localhost:8000/v1
```

### Example Endpoints

#### Get Price Data
```bash
GET /v1/prices/prices?area_code=USA&item_code=0111&year=2023
```

#### Get Production Statistics
```bash
GET /v1/production/production_crops_livestock?limit=100&offset=0
```

#### List Available Datasets
```bash
GET /v1/
```

### Response Format
```json
{
  "total_count": 1000,
  "limit": 100,
  "offset": 0,
  "data": [
    {
      "area_code": "USA",
      "item_code": "0111",
      "element": "Producer Price",
      "year": 2023,
      "value": 285.5,
      "unit": "USD/tonne"
    }
  ]
}
```

## Project Structure

```
fao/
├── src/
│   ├── api/           # FastAPI application and routes
│   │   ├── routers/   # Endpoint definitions by dataset
│   │   └── __main__.py
│   └── db/            # Database models and ETL
│       ├── pipelines/ # ETL pipeline modules
│       ├── database.py
│       └── utils.py
├── migrations/        # Alembic database migrations
├── tests/            # Test suite (coming soon)
└── docs/             # Additional documentation
```

## Development

### Contributing

As this project is in active development, we welcome contributions! Please:

1. Check existing issues before creating new ones
2. Follow the existing code style
3. Write tests for new features
4. Update documentation as needed

### Running Tests

```bash
# Tests are being developed
pytest tests/
```

### Code Style

This project uses:
- Black for code formatting
- isort for import sorting
- mypy for type checking (planned)

## Roadmap

### Phase 1 (Current)
- [x] Basic API functionality
- [x] Core datasets integration
- [ ] Error handling improvements
- [ ] Basic test coverage

### Phase 2 (Next)
- [ ] Authentication system
- [ ] Rate limiting
- [ ] Caching layer
- [ ] Advanced query capabilities

### Phase 3 (Future)
- [ ] GraphQL endpoint
- [ ] Bulk export functionality
- [ ] Real-time data updates
- [ ] Client SDKs

## Known Issues

- Large dataset queries may timeout
- Some datasets have incomplete historical data
- API keys not yet implemented
- No request rate limiting

## License

This project is currently under development. License terms will be added upon official release.

## Contact

For questions about this project or the FAO data it serves:
- Project Issues: [GitHub Issues](https://github.com/yourusername/fao-data-api/issues)
- FAO Data Questions: [FAO Statistics](https://www.fao.org/statistics/en/)

## Disclaimer

This is an unofficial API interface to FAO public data. This project is not affiliated with or endorsed by the Food and Agriculture Organization of the United Nations. For official FAO data access, please visit [FAOSTAT](https://www.fao.org/faostat/).

---

**Note**: This README will be updated as the project evolves. Check back regularly for the latest information.