from . import trade_indices
from fao.src.db.database import run_with_session


def run_all(db):
    print("Running trade_indices pipeline")
    trade_indices.run(db)


if __name__ == "__main__":
    run_with_session(run_all)
    print("trade_indices pipeline complete")