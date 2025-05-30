from db.database import run_with_session
from .fao_prices_e.__main__ import run_all as run_fao_prices_e
from .fao_exchange_rate_e.__main__ import run_all as run_fao_exchange_rate_e


def run_all_pipelines(db):
    """Run all data pipelines in sequence."""
    print("🚀 Starting all data pipelines...")

    # Run FAO Prices pipeline
    run_fao_prices_e(db)

    # Run FAO Exchange Rate pipeline
    run_fao_exchange_rate_e(db)

    print("✅ All pipelines complete!")


if __name__ == "__main__":
    run_with_session(run_all_pipelines)
