from . import value_shares_industry_primary_factors
from fao.src.db.database import run_with_session


def run_all(db):
    print("Running value_shares_industry_primary_factors pipeline")
    value_shares_industry_primary_factors.run(db)


if __name__ == "__main__":
    run_with_session(run_all)
    print("value_shares_industry_primary_factors pipeline complete")