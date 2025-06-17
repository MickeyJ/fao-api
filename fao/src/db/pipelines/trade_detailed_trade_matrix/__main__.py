from . import trade_detailed_trade_matrix
from fao.src.db.database import run_with_session


def run_all(db):
    print("Running trade_detailed_trade_matrix pipeline")
    trade_detailed_trade_matrix.run(db)


if __name__ == "__main__":
    run_with_session(run_all)
    print("trade_detailed_trade_matrix pipeline complete")