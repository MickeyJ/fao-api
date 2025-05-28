from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from . import current_version_prefix

# Import all the routers
from api.routers import analysis, visualizations, data


api_map = {
    "message": "Food Price Analysis API",
    "version": "1.0.0",
    "docs": "/docs",
    "endpoints": {
        "data": data.router_map,
        "analysis": f"/{current_version_prefix}/analysis/*",
        "visualizations": f"/{current_version_prefix}/viz/*",
    },
}


# Create main app
app = FastAPI(
    title="Food Price Analysis API",
    description="API for analyzing global food commodity prices",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://app.mickeymalotte.com",
    ],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include all routers with v1 prefix
app.include_router(analysis.router, prefix=f"/{current_version_prefix}")
app.include_router(visualizations.router, prefix=f"/{current_version_prefix}")
app.include_router(data.router, prefix=f"/{current_version_prefix}")


# Root endpoint
@app.get("/")
def root():
    return api_map


# Make it runnable with: python -m api
if __name__ == "__main__":
    import uvicorn
    import signal
    import sys

    def signal_handler(sig, frame):
        print("\nShutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    uvicorn.run("api.__main__:app", host="localhost", port=8000, reload=True)
