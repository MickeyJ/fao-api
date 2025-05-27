from fastapi import FastAPI
import uvicorn

# Import all the routers
from api.routers import analysis, visualizations, data

# Create main app
app = FastAPI(
    title="Food Price Analysis API",
    description="API for analyzing global food commodity prices",
    version="1.0.0",
)

# Include all routers
app.include_router(analysis.router)
app.include_router(visualizations.router)
app.include_router(data.router)


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Food Price Analysis API",
        "docs": "/docs",
        "endpoints": {
            "analysis": "/analysis/*",
            "visualizations": "/viz/*",
            "data": "/data/*",
        },
    }


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
