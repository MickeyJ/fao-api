from db.database import run_with_session
from .price_anomaly_detector import detect_price_anomalies

if __name__ == "__main__":
    run_with_session(detect_price_anomalies)
    # raise NotImplementedError(
    #     "Full database creation not yet implemented. Run specific submodules like 'items.py' instead."
    # )
