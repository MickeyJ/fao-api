from . import trade_crops_livestock_indicators
from fao.src.db.database import run_with_session


def run_all(db):
    print("Running trade_crops_livestock_indicators pipeline")
    trade_crops_livestock_indicators.run(db)


if __name__ == "__main__":
    run_with_session(run_all)
    print("trade_crops_livestock_indicators pipeline complete")