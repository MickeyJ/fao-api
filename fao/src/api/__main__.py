from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fao.src.core import settings
from ..core.middleware import add_version_headers
from . import api_map

# Import all the routers
from .routers.other import other_api
from .routers.population import population_api
from .routers.indicators import indicators_api
from .routers.food import food_api
from .routers.asti import asti_api
from .routers.commodity import commodity_api
from .routers.emissions import emissions_api
from .routers.employment import employment_api
from .routers.environment import environment_api
from .routers.forestry import forestry_api
from .routers.inputs import inputs_api
from .routers.investment import investment_api
from .routers.prices import prices_api
from .routers.production import production_api


# Create main app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
)

# Custom middleware
app.middleware("http")(add_version_headers)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(other_api)
app.include_router(population_api)
app.include_router(indicators_api)
app.include_router(food_api)
app.include_router(asti_api)
app.include_router(commodity_api)
app.include_router(emissions_api)
app.include_router(employment_api)
app.include_router(environment_api)
app.include_router(forestry_api)
app.include_router(inputs_api)
app.include_router(investment_api)
app.include_router(prices_api)
app.include_router(production_api)


# Import custom routers (this section preserved during regeneration)
try:
    from fao.src.api_custom.routers import custom_routers
    for custom_router in custom_routers:
        app.include_router(custom_router)
    print(f"✅ Loaded {len(custom_routers)} custom routers")
except ImportError as e:
    print("ℹ️  No custom routers found")
except Exception as e:
    print(f"⚠️  Error loading custom routers: {e}")

# Root endpoint with version info
@app.get("/")
def root():
    return {
        "version": settings.api_version,
        "version_prefix": settings.api_version_prefix,
        "versions": "/versions",
        "headers": {
            "X-API-Version": "Current API version",
            "X-API-Version-Major": "Major version (v1, v2, etc)",
        }
    }

# Version-specific root endpoint
@app.get(f"/{settings.api_version_prefix}")
def version_root():
    return {
        "version": settings.api_version,
        "status": "active",
        "endpoints": api_map["endpoints"]
    }

if __name__ == "__main__":
    import uvicorn
    import signal
    import sys

    def signal_handler(sig, frame):
        print("\nShutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    uvicorn.run(
        "fao.src.api.__main__:app", 
        host=settings.api_host, 
        port=settings.api_port, 
        reload=True
    )