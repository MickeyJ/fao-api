from . import currency
from db.database import run_with_session


def run_all(db):
    print("Running fao_exchange_rate_e pipeline")
    currency.run(db)


if __name__ == "__main__":
    run_with_session(run_all)
    print("fao prices pipeline complete")
