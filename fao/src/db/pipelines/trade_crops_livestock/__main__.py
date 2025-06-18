from . import trade_crops_livestock
from fao.src.db.database import run_with_session


def run_all(db):
    print("Running trade_crops_livestock pipeline")
    trade_crops_livestock.run(db)


if __name__ == "__main__":
    run_with_session(run_all)
    print("trade_crops_livestock pipeline complete")