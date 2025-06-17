from . import value_of_production
from fao.src.db.database import run_with_session


def run_all(db):
    print("Running value_of_production pipeline")
    value_of_production.run(db)


if __name__ == "__main__":
    run_with_session(run_all)
    print("value_of_production pipeline complete")