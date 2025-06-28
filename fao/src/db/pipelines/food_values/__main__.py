from . import food_values
from fao.src.db.database import run_with_session


def run_all(db):
    print("Running food_values pipeline")
    food_values.run(db)


if __name__ == "__main__":
    run_with_session(run_all)
    print("food_values pipeline complete")