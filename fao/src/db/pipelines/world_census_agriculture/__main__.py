from . import world_census_agriculture
from fao.src.db.database import run_with_session


def run_all(db):
    print("Running world_census_agriculture pipeline")
    world_census_agriculture.run(db)


if __name__ == "__main__":
    run_with_session(run_all)
    print("world_census_agriculture pipeline complete")