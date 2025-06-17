import json
import zipfile
from pathlib import Path
from fao.logger import logger
from sqlalchemy import text
from fao.src.db.database import run_with_session
from fao.src.db.system_models import PipelineProgress
from .area_codes.__main__ import run_all as run_area_codes
from .reporter_country_codes.__main__ import run_all as run_reporter_country_codes
from .partner_country_codes.__main__ import run_all as run_partner_country_codes
from .recipient_country_codes.__main__ import run_all as run_recipient_country_codes
from .item_codes.__main__ import run_all as run_item_codes
from .elements.__main__ import run_all as run_elements
from .flags.__main__ import run_all as run_flags
from .currencies.__main__ import run_all as run_currencies
from .sources.__main__ import run_all as run_sources
from .releases.__main__ import run_all as run_releases
from .sexs.__main__ import run_all as run_sexs
from .indicators.__main__ import run_all as run_indicators
from .population_age_groups.__main__ import run_all as run_population_age_groups
from .surveys.__main__ import run_all as run_surveys
from .purposes.__main__ import run_all as run_purposes
from .donors.__main__ import run_all as run_donors
from .food_groups.__main__ import run_all as run_food_groups
from .geographic_levels.__main__ import run_all as run_geographic_levels
from .aquastat.__main__ import run_all as run_aquastat
from .asti_expenditures.__main__ import run_all as run_asti_expenditures
from .asti_researchers.__main__ import run_all as run_asti_researchers
from .climate_change_emissions_indicators.__main__ import run_all as run_climate_change_emissions_indicators
from .commodity_balances_non_food_2013_old_methodology.__main__ import run_all as run_commodity_balances_non_food_2013_old_methodology
from .commodity_balances_non_food_2010.__main__ import run_all as run_commodity_balances_non_food_2010
from .consumer_price_indices.__main__ import run_all as run_consumer_price_indices
from .cost_affordability_healthy_diet_co_ahd.__main__ import run_all as run_cost_affordability_healthy_diet_co_ahd
from .deflators.__main__ import run_all as run_deflators
from .development_assistance_to_agriculture.__main__ import run_all as run_development_assistance_to_agriculture
from .emissions_agriculture_energy.__main__ import run_all as run_emissions_agriculture_energy
from .emissions_crops.__main__ import run_all as run_emissions_crops
from .emissions_drained_organic_soils.__main__ import run_all as run_emissions_drained_organic_soils
from .emissions_land_use_fires.__main__ import run_all as run_emissions_land_use_fires
from .emissions_land_use_forests.__main__ import run_all as run_emissions_land_use_forests
from .emissions_livestock.__main__ import run_all as run_emissions_livestock
from .emissions_pre_post_production.__main__ import run_all as run_emissions_pre_post_production
from .emissions_totals.__main__ import run_all as run_emissions_totals
from .employment_indicators_agriculture.__main__ import run_all as run_employment_indicators_agriculture
from .employment_indicators_rural.__main__ import run_all as run_employment_indicators_rural
from .environment_bioenergy.__main__ import run_all as run_environment_bioenergy
from .environment_cropland_nutrient_budget.__main__ import run_all as run_environment_cropland_nutrient_budget
from .environment_emissions_intensities.__main__ import run_all as run_environment_emissions_intensities
from .environment_land_cover.__main__ import run_all as run_environment_land_cover
from .environment_livestock_manure.__main__ import run_all as run_environment_livestock_manure
from .environment_livestock_patterns.__main__ import run_all as run_environment_livestock_patterns
from .environment_temperature_change.__main__ import run_all as run_environment_temperature_change
from .exchange_rate.__main__ import run_all as run_exchange_rate
from .fertilizers_detailed_trade_matrix.__main__ import run_all as run_fertilizers_detailed_trade_matrix
from .food_balance_sheets_historic.__main__ import run_all as run_food_balance_sheets_historic
from .food_balance_sheets.__main__ import run_all as run_food_balance_sheets
from .food_aid_shipments_wfp.__main__ import run_all as run_food_aid_shipments_wfp
from .food_security_data.__main__ import run_all as run_food_security_data
from .forestry.__main__ import run_all as run_forestry
from .forestry_pulp_paper_survey.__main__ import run_all as run_forestry_pulp_paper_survey
from .forestry_trade_flows.__main__ import run_all as run_forestry_trade_flows
from .household_consumption_and_expenditure_surveys_food_and_diet.__main__ import run_all as run_household_consumption_and_expenditure_surveys_food_and_diet
from .indicators_from_household_surveys.__main__ import run_all as run_indicators_from_household_surveys
from .individual_quantitative_dietary_data_food_and_diet.__main__ import run_all as run_individual_quantitative_dietary_data_food_and_diet
from .inputs_fertilizers_archive.__main__ import run_all as run_inputs_fertilizers_archive
from .inputs_fertilizers_nutrient.__main__ import run_all as run_inputs_fertilizers_nutrient
from .inputs_fertilizers_product.__main__ import run_all as run_inputs_fertilizers_product
from .inputs_land_use.__main__ import run_all as run_inputs_land_use
from .inputs_pesticides_trade.__main__ import run_all as run_inputs_pesticides_trade
from .inputs_pesticides_use.__main__ import run_all as run_inputs_pesticides_use
from .investment_capital_stock.__main__ import run_all as run_investment_capital_stock
from .investment_country_investment_statistics_profile.__main__ import run_all as run_investment_country_investment_statistics_profile
from .investment_credit_agriculture.__main__ import run_all as run_investment_credit_agriculture
from .investment_foreign_direct_investment.__main__ import run_all as run_investment_foreign_direct_investment
from .investment_government_expenditure.__main__ import run_all as run_investment_government_expenditure
from .investment_machinery_archive.__main__ import run_all as run_investment_machinery_archive
from .investment_machinery.__main__ import run_all as run_investment_machinery
from .macro_statistics_key_indicators.__main__ import run_all as run_macro_statistics_key_indicators
from .minimum_dietary_diversity_for_women_mdd_w_food_and_diet.__main__ import run_all as run_minimum_dietary_diversity_for_women_mdd_w_food_and_diet
from .population.__main__ import run_all as run_population
from .prices_archive.__main__ import run_all as run_prices_archive
from .prices.__main__ import run_all as run_prices
from .production_crops_livestock.__main__ import run_all as run_production_crops_livestock
from .production_indices.__main__ import run_all as run_production_indices
from .sdg_bulk_downloads.__main__ import run_all as run_sdg_bulk_downloads
from .sua_crops_livestock.__main__ import run_all as run_sua_crops_livestock
from .supply_utilization_accounts_food_and_diet.__main__ import run_all as run_supply_utilization_accounts_food_and_diet
from .trade_crops_livestock_indicators.__main__ import run_all as run_trade_crops_livestock_indicators
from .trade_crops_livestock.__main__ import run_all as run_trade_crops_livestock
from .trade_detailed_trade_matrix.__main__ import run_all as run_trade_detailed_trade_matrix
from .trade_indices.__main__ import run_all as run_trade_indices
from .value_of_production.__main__ import run_all as run_value_of_production
from .value_shares_industry_primary_factors.__main__ import run_all as run_value_shares_industry_primary_factors
from .world_census_agriculture.__main__ import run_all as run_world_census_agriculture

def ensure_zips_extracted():
    """Extract ZIP files if needed based on manifest"""
    manifest_path = Path(__file__).parent.parent.parent / "extraction_manifest.json"
    
    if not manifest_path.exists():
        logger.error("⚠️  No extraction manifest found - ZIPs may not be extracted")
        return
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    logger.info("📦 Checking ZIP extractions...")
    
    for extraction in manifest["extractions"]:
        zip_path = Path(extraction["zip_path"])
        extract_dir = Path(extraction["extract_dir"])
        
        # Check if extraction is needed
        if not extract_dir.exists() or not _extraction_is_current(zip_path, extract_dir):
            logger.info(f"📂 Extracting {zip_path.name}...")
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)
        else:
            logger.info(f"✅ {zip_path.name} already extracted")

def _extraction_is_current(zip_path: Path, extract_dir: Path) -> bool:
    """Check if extraction is up to date"""
    if not extract_dir.exists():
        return False
    
    # Simple check: if extract dir is newer than ZIP file
    try:
        zip_mtime = zip_path.stat().st_mtime
        extract_mtime = extract_dir.stat().st_mtime
        return extract_mtime >= zip_mtime
    except (OSError, FileNotFoundError):
        return False

def get_pipeline_status(db) -> dict:
    """Get status of all pipelines from pipeline_progress table"""
    progress_records = db.query(PipelineProgress).all()
    return {p.table_name: p for p in progress_records}

def run_all_pipelines(db):
    ensure_zips_extracted()
    print("🚀 Starting all data pipelines...")
    
    # Get pipeline status
    pipeline_status = get_pipeline_status(db)
    
    # Pipeline mapping
    pipeline_runners = {
        "area_codes": run_area_codes,
        "reporter_country_codes": run_reporter_country_codes,
        "partner_country_codes": run_partner_country_codes,
        "recipient_country_codes": run_recipient_country_codes,
        "item_codes": run_item_codes,
        "elements": run_elements,
        "flags": run_flags,
        "currencies": run_currencies,
        "sources": run_sources,
        "releases": run_releases,
        "sexs": run_sexs,
        "indicators": run_indicators,
        "population_age_groups": run_population_age_groups,
        "surveys": run_surveys,
        "purposes": run_purposes,
        "donors": run_donors,
        "food_groups": run_food_groups,
        "geographic_levels": run_geographic_levels,
        "aquastat": run_aquastat,
        "asti_expenditures": run_asti_expenditures,
        "asti_researchers": run_asti_researchers,
        "climate_change_emissions_indicators": run_climate_change_emissions_indicators,
        "commodity_balances_non_food_2013_old_methodology": run_commodity_balances_non_food_2013_old_methodology,
        "commodity_balances_non_food_2010": run_commodity_balances_non_food_2010,
        "consumer_price_indices": run_consumer_price_indices,
        "cost_affordability_healthy_diet_co_ahd": run_cost_affordability_healthy_diet_co_ahd,
        "deflators": run_deflators,
        "development_assistance_to_agriculture": run_development_assistance_to_agriculture,
        "emissions_agriculture_energy": run_emissions_agriculture_energy,
        "emissions_crops": run_emissions_crops,
        "emissions_drained_organic_soils": run_emissions_drained_organic_soils,
        "emissions_land_use_fires": run_emissions_land_use_fires,
        "emissions_land_use_forests": run_emissions_land_use_forests,
        "emissions_livestock": run_emissions_livestock,
        "emissions_pre_post_production": run_emissions_pre_post_production,
        "emissions_totals": run_emissions_totals,
        "employment_indicators_agriculture": run_employment_indicators_agriculture,
        "employment_indicators_rural": run_employment_indicators_rural,
        "environment_bioenergy": run_environment_bioenergy,
        "environment_cropland_nutrient_budget": run_environment_cropland_nutrient_budget,
        "environment_emissions_intensities": run_environment_emissions_intensities,
        "environment_land_cover": run_environment_land_cover,
        "environment_livestock_manure": run_environment_livestock_manure,
        "environment_livestock_patterns": run_environment_livestock_patterns,
        "environment_temperature_change": run_environment_temperature_change,
        "exchange_rate": run_exchange_rate,
        "fertilizers_detailed_trade_matrix": run_fertilizers_detailed_trade_matrix,
        "food_balance_sheets_historic": run_food_balance_sheets_historic,
        "food_balance_sheets": run_food_balance_sheets,
        "food_aid_shipments_wfp": run_food_aid_shipments_wfp,
        "food_security_data": run_food_security_data,
        "forestry": run_forestry,
        "forestry_pulp_paper_survey": run_forestry_pulp_paper_survey,
        "forestry_trade_flows": run_forestry_trade_flows,
        "household_consumption_and_expenditure_surveys_food_and_diet": run_household_consumption_and_expenditure_surveys_food_and_diet,
        "indicators_from_household_surveys": run_indicators_from_household_surveys,
        "individual_quantitative_dietary_data_food_and_diet": run_individual_quantitative_dietary_data_food_and_diet,
        "inputs_fertilizers_archive": run_inputs_fertilizers_archive,
        "inputs_fertilizers_nutrient": run_inputs_fertilizers_nutrient,
        "inputs_fertilizers_product": run_inputs_fertilizers_product,
        "inputs_land_use": run_inputs_land_use,
        "inputs_pesticides_trade": run_inputs_pesticides_trade,
        "inputs_pesticides_use": run_inputs_pesticides_use,
        "investment_capital_stock": run_investment_capital_stock,
        "investment_country_investment_statistics_profile": run_investment_country_investment_statistics_profile,
        "investment_credit_agriculture": run_investment_credit_agriculture,
        "investment_foreign_direct_investment": run_investment_foreign_direct_investment,
        "investment_government_expenditure": run_investment_government_expenditure,
        "investment_machinery_archive": run_investment_machinery_archive,
        "investment_machinery": run_investment_machinery,
        "macro_statistics_key_indicators": run_macro_statistics_key_indicators,
        "minimum_dietary_diversity_for_women_mdd_w_food_and_diet": run_minimum_dietary_diversity_for_women_mdd_w_food_and_diet,
        "population": run_population,
        "prices_archive": run_prices_archive,
        "prices": run_prices,
        "production_crops_livestock": run_production_crops_livestock,
        "production_indices": run_production_indices,
        "sdg_bulk_downloads": run_sdg_bulk_downloads,
        "sua_crops_livestock": run_sua_crops_livestock,
        "supply_utilization_accounts_food_and_diet": run_supply_utilization_accounts_food_and_diet,
        "trade_crops_livestock_indicators": run_trade_crops_livestock_indicators,
        "trade_crops_livestock": run_trade_crops_livestock,
        "trade_detailed_trade_matrix": run_trade_detailed_trade_matrix,
        "trade_indices": run_trade_indices,
        "value_of_production": run_value_of_production,
        "value_shares_industry_primary_factors": run_value_shares_industry_primary_factors,
        "world_census_agriculture": run_world_census_agriculture,
    }
    
    completed_count = 0
    in_progress_count = 0
    to_run_count = 0
    
    # Check each pipeline
    for pipeline_name, runner in pipeline_runners.items():
        progress = pipeline_status.get(pipeline_name)

        logger.info(f"Pipeline Progress: {progress}")
        
        if progress and progress.status == "completed":
            print(f"✅ Skipping {pipeline_name} - already completed ({progress.total_rows:,} rows)")
            completed_count += 1
        elif progress and progress.status == "in_progress":
            print(f"🔄 Resuming {pipeline_name} from row {progress.last_row_processed:,}/{progress.total_rows:,}")
            runner(db)
            in_progress_count += 1
        else:
            print(f"🆕 Starting {pipeline_name}")
            runner(db)
            to_run_count += 1
    
    print(f"\n✅ Pipeline execution complete!")
    print(f"   Skipped (completed): {completed_count}")
    print(f"   Resumed: {in_progress_count}")
    print(f"   Started fresh: {to_run_count}")

if __name__ == "__main__":
    run_with_session(run_all_pipelines)