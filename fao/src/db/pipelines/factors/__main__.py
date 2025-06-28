from . import factors
from fao.src.db.database import run_with_session


def run_all(db):
    print("Running factors pipeline")
    factors.run(db)


if __name__ == "__main__":
    run_with_session(run_all)
    print("factors pipeline complete")