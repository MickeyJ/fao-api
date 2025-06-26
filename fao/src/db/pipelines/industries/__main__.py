from . import industries
from fao.src.db.database import run_with_session


def run_all(db):
    print("Running industries pipeline")
    industries.run(db)


if __name__ == "__main__":
    run_with_session(run_all)
    print("industries pipeline complete")