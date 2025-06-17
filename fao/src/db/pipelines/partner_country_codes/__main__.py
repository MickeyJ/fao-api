from . import partner_country_codes
from fao.src.db.database import run_with_session


def run_all(db):
    print("Running partner_country_codes pipeline")
    partner_country_codes.run(db)


if __name__ == "__main__":
    run_with_session(run_all)
    print("partner_country_codes pipeline complete")