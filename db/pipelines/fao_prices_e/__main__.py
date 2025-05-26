from . import items, areas
from db.database import run_with_session


def run_all(db):
    print("Running all pipelines")
    items.run(db)
    areas.run(db)


if __name__ == "__main__":
    run_with_session(run_all)
    print("fao prices pipeline complete")
    # raise NotImplementedError(
    #     "Full fao_prices pipeline not yet implemented. Run specific submodules like 'items.py' instead."
    # )
