from kpi_calculations.adiabatic_wall_area import AdiabaticWallArea
from kpi_calculations.adiabatic_walls_ratio import AdiabaticWallsRatio
from kpi_calculations.ancients_residents_per_building import AncientsResidentsPerBuilding
from kpi_calculations.ancients_residents_per_building_m2 import AncientsResidentsPerBuildingM2
from kpi_calculations.ancients_residents_per_census_tract import AncientsResidentsPerCensusTract
from kpi_calculations.annual_electricity_consumption import AnnualElectricityConsumption
from kpi_calculations.annual_net_incomes_household_per_building import AnnualNetIncomesHouseholdPerBuilding
from kpi_calculations.annual_net_incomes_household_per_census_tract import AnnualNetIncomesHouseholdPerCensusTract
from kpi_calculations.average_dwelling_area import AverageDwellingArea
from kpi_calculations.average_weekly_electricity_load_curve import AverageWeeklyElectricityLoadCurve
from kpi_calculations.building_code import BuildingCode
from kpi_calculations.building_residents_birthplace import BuildingResidentsBirthplace
from kpi_calculations.building_roof_area import BuildingRoofArea
from kpi_calculations.children_residents_per_building import ChildrenResidentsPerBuilding
from kpi_calculations.children_residents_per_building_m2 import ChildrenResidentsPerBuildingM2
from kpi_calculations.children_residents_per_census_tract import ChildrenResidentsPerCensusTract
from kpi_calculations.common_to_total_area_ratio import CommonToTotalAreaRatio
from kpi_calculations.construction_year import ConstructionYear
from kpi_calculations.cooling_thermal_demand_intensity import CoolingThermalDemandIntensity
from kpi_calculations.distance_from_facade_to_adjacent_buildings_by_orientation import \
    DistanceFromFacadeToAdjacentBuildingsByOrientation
from kpi_calculations.dwelings_number import DwelingsNumber
from kpi_calculations.effective_construction_year import EffectiveConstructionYear
from kpi_calculations.elevation_above_sea_level import ElevationAboveSeaLevel
from kpi_calculations.exterior_wall_area import ExteriorWallArea
from kpi_calculations.exterior_wall_contact_facing_north_ratio import ExteriorWallContactFacingNorthRatio
from kpi_calculations.exterior_wall_contact_facing_south_ratio import ExteriorWallContactFacingSouthRatio
from kpi_calculations.exterior_wall_contact_ratio import ExteriorWallContactRatio
from kpi_calculations.facade_area_exposed_by_orientation import FacadeAreaExposedByOrientation
from kpi_calculations.facade_area_ratio_by_orientation import FacadeAreaRatioByOrientation
from kpi_calculations.female_residents_per_building import FemaleResidentsPerBuilding
from kpi_calculations.female_residents_per_building_m2 import FemaleResidentsPerBuildingM2
from kpi_calculations.female_residents_per_census_tract import FemaleResidentsPerCensusTract
from kpi_calculations.foreign_residents_per_census_tract import ForeignResidentsPerCensusTract
from kpi_calculations.gini_index_incomes import GiniIndexIncomes
from kpi_calculations.gross_floor_area import GrossFloorArea
from kpi_calculations.ground_floor_commercial_premises import GroundFloorCommercialPremises
from kpi_calculations.ground_floor_commercial_premises_list import GroundFloorCommercialPremisesList
from kpi_calculations.heating_thermal_demand_intensity import HeatingThermalDemandIntensity
from kpi_calculations.household_rental_price_per_building import HouseholdRentalPricePerBuilding
from kpi_calculations.income_distribution_p80_p20 import IncomeDistributionP80P20
from kpi_calculations.income_sources_typology import IncomeSourcesTypologyPerCensusTract
from kpi_calculations.main_usage import MainUsage
from kpi_calculations.male_residents_per_building import MaleResidentsPerBuilding
from kpi_calculations.male_residents_per_census_tract import MaleResidentsPerCensusTract
from kpi_calculations.meteo.cold_waves import ColdWaves
from kpi_calculations.meteo.heat_waves import HeatWaves
from kpi_calculations.meteo.hellish_nights import HellishNights
from kpi_calculations.meteo.torrid_nights import TorridNights
from kpi_calculations.meteo.tropical_nights import TropicalNights
from kpi_calculations.min_time_to_closest_climate_shelter import MinTimeToClosestClimateShelter
from kpi_calculations.nacionality_residents_per_building import NationalityResidentsPerBuilding
from kpi_calculations.nacionality_residents_per_census_tract import NacionalityResidentsPerCensusTract
from kpi_calculations.native_residents_per_building import NativeResidentsPerBuilding
from kpi_calculations.native_residents_per_census_tract import NativeResidentsPerCensusTract
from kpi_calculations.num_climate_shelters import NumClimateShelters
from kpi_calculations.num_climate_shelters_within_10min import NumClimateSheltersWithin10min
from kpi_calculations.num_climate_shelters_within_15min import NumClimateSheltersWithin15min
from kpi_calculations.num_climate_shelters_within_20min import NumClimateSheltersWithin20min
from kpi_calculations.num_climate_shelters_within_30min import NumClimateSheltersWithin30min
from kpi_calculations.number_of_floors_above_ground import NumberOfFloorsAboveGround
from kpi_calculations.number_of_floors_below_ground import NumberOfFloorsBelowGround
from kpi_calculations.percentage_population_over_65 import PercentagePopulationOver65
from kpi_calculations.percentage_population_under_18 import PercentagePopulationUnder18
from kpi_calculations.percentage_single_person_households import PercentageSinglePersonHouseholds
from kpi_calculations.primary_energy_by_certificate import PrimaryEnergyByCertificate
from kpi_calculations.residential_common_area_ratio import ResidentialCommonAreaRatio
from kpi_calculations.residents_per_building import ResidentsPerBuilding
from kpi_calculations.residents_per_census_tract import ResidentsPerCensusTract
from kpi_calculations.total_energy_consumption_intensity import TotalEnergyConsumptionIntensity
from kpi_calculations.total_residential_area import TotalResidentialArea
from kpi_calculations.vegetation_index import VegetationIndex
from kpi_calculations.vegetation_index_ui import VegetationIndexUI
from kpi_calculations.window_to_wall_ratio import WindowToWallRatio


def main():

    ###### CENSUS TRACT ######
    #nacionality_residents_per_census_tract
    nacionality_residents_per_census_tract = NacionalityResidentsPerCensusTract(kpi_name='nacionality_residents_per_census_tract')
    nacionality_residents_per_census_tract.run()

    #residents_per_census_tract
    residents_per_census_tract = ResidentsPerCensusTract(kpi_name='residents_per_census_tract')
    residents_per_census_tract.run()

    #male_residents_per_census_tract
    male_residents_per_census_tract = MaleResidentsPerCensusTract(kpi_name='male_residents_per_census_tract')
    male_residents_per_census_tract.run()

    #female_residents_per_census_tract
    female_residents_per_census_tract = FemaleResidentsPerCensusTract(kpi_name='female_residents_per_census_tract')
    female_residents_per_census_tract.run()

    #native_residents_per_census_tract
    native_residents_per_census_tract = NativeResidentsPerCensusTract(kpi_name='native_residents_per_census_tract')
    native_residents_per_census_tract.run()

    #foreign_residents_per_census_tract
    foreign_residents_per_census_tract = ForeignResidentsPerCensusTract(kpi_name='foreign_residents_per_census_tract')
    foreign_residents_per_census_tract.run()

    #children_residents_per_census_tract
    children_residents_per_census_tract = ChildrenResidentsPerCensusTract(kpi_name='children_residents_per_census_tract')
    children_residents_per_census_tract.run()

    #ancients_residents_per_census_tract
    ancients_residents_per_census_tract = AncientsResidentsPerCensusTract(kpi_name='ancients_residents_per_census_tract')
    ancients_residents_per_census_tract.run()

    # income_sources_typology
    income_sources_typology_per_census_tract = IncomeSourcesTypologyPerCensusTract(kpi_name='income_sources_typology_per_census_tract')
    income_sources_typology_per_census_tract.run()

    # annual_net_incomes_household_per_census_tract
    annual_net_incomes_household_per_census_tract = AnnualNetIncomesHouseholdPerCensusTract(kpi_name='annual_net_incomes_household_per_census_tract')
    annual_net_incomes_household_per_census_tract.run()

    # annual_net_incomes_household_per_census_tract
    # household_rental_price_per_census_tract = HouseholdRentalPricePerCensusTract(kpi_name='household_rental_price_per_census_tract')
    # household_rental_price_per_census_tract.run()


###### Building ######

    # walls_area_by_type
    walls_area_by_type = FacadeAreaRatioByOrientation(kpi_name="walls_area_by_type")
    walls_area_by_type.run()

    # walls_ratio_by_type
    walls_ratio_by_type = FacadeAreaRatioByOrientation(kpi_name="walls_ratio_by_type")
    walls_ratio_by_type.run()

    # num_climate_shelters
    num_climate_shelters = NumClimateShelters(kpi_name="num_climate_shelters")
    num_climate_shelters.run()

    # num_climate_shelters_within_30min
    num_climate_shelters_within_30min = NumClimateSheltersWithin30min(kpi_name="num_climate_shelters_within_30min")
    num_climate_shelters_within_30min.run()

    # num_climate_shelters_within_20min
    num_climate_shelters_within_20min = NumClimateSheltersWithin20min(kpi_name="num_climate_shelters_within_20min")
    num_climate_shelters_within_20min.run()

    # num_climate_shelters_within_20min
    num_climate_shelters_within_15min = NumClimateSheltersWithin15min(kpi_name="num_climate_shelters_within_15min")
    num_climate_shelters_within_15min.run()

    # num_climate_shelters_within_10min
    num_climate_shelters_within_10min = NumClimateSheltersWithin10min(kpi_name="num_climate_shelters_within_10min")
    num_climate_shelters_within_10min.run()

    # min_time_to_closest_climate_shelter
    min_time_to_closest_climate_shelter = MinTimeToClosestClimateShelter(kpi_name="min_time_to_closest_climate_shelter")
    min_time_to_closest_climate_shelter.run()

    # income_distribution_p80_p20
    income_distribution_p80_p20 = IncomeDistributionP80P20(kpi_name="income_distribution_p80_p20")
    income_distribution_p80_p20.run()

    # gini_index_incomes
    gini_index_incomes = GiniIndexIncomes(kpi_name="gini_index_incomes")
    gini_index_incomes.run()

    # percentage_single_person_households
    percentage_single_person_households = PercentageSinglePersonHouseholds(kpi_name="percentage_single_person_households")
    percentage_single_person_households.run()

    # percentage_population_under_18
    percentage_population_under_18 = PercentagePopulationUnder18(kpi_name="percentage_population_under_18")
    percentage_population_under_18.run()

    # percentage_population_over_65
    percentage_population_over_65 = PercentagePopulationOver65(kpi_name="percentage_population_over_65")
    percentage_population_over_65.run()

    # adiabatic_wall_area
    adiabatic_wall_area = AdiabaticWallArea(kpi_name="adiabatic_wall_area")
    adiabatic_wall_area.run()

    # exterior_wall_area
    exterior_wall_area = ExteriorWallArea(kpi_name="exterior_wall_area")
    exterior_wall_area.run()

    # adiabatic_walls_ratio
    adiabatic_walls_ratio = AdiabaticWallsRatio(kpi_name="adiabatic_walls_ratio")
    adiabatic_walls_ratio.run()

    # exterior_wall_contact_facing_north_ratio
    exterior_wall_contact_facing_north_ratio = ExteriorWallContactFacingNorthRatio(kpi_name="exterior_wall_contact_facing_north_ratio")
    exterior_wall_contact_facing_north_ratio.run()

    # exterior_wall_contact_facing_south_ratio
    exterior_wall_contact_facing_south_ratio = ExteriorWallContactFacingSouthRatio(kpi_name="exterior_wall_contact_facing_south_ratio")
    exterior_wall_contact_facing_south_ratio.run()

    # exterior_wall_contact_ratio
    exterior_wall_contact_ratio = ExteriorWallContactRatio(kpi_name="exterior_wall_contact_ratio")
    exterior_wall_contact_ratio.run()

    #  elevation_above_sea_level
    elevation_above_sea_level = ElevationAboveSeaLevel(kpi_name="elevation_above_sea_level")
    elevation_above_sea_level.run()

    # children_residents_per_building_m2
    children_residents_per_building_m2 = ChildrenResidentsPerBuildingM2(kpi_name="children_residents_per_building_m2")
    children_residents_per_building_m2.run()

    # ancients_residents_per_building_m2
    ancients_residents_per_building_m2 = AncientsResidentsPerBuildingM2(kpi_name="ancients_residents_per_building_m2")
    ancients_residents_per_building_m2.run()

    # female_residents_per_building_m2
    female_residents_per_building_m2 = FemaleResidentsPerBuildingM2(kpi_name="female_residents_per_building_m2")
    female_residents_per_building_m2.run()

    # window_to_wall_ratio
    window_to_wall_ratio = WindowToWallRatio(kpi_name="window_to_wall_ratio")
    window_to_wall_ratio.run()

    # total_energy_consumption_intensity
    total_energy_consumption_intensity = TotalEnergyConsumptionIntensity(kpi_name="total_energy_consumption_intensity")
    total_energy_consumption_intensity.run()

    # cooling_thermal_demand_intensity
    cooling_thermal_demand_intensity = CoolingThermalDemandIntensity(kpi_name="cooling_thermal_demand_intensity")
    cooling_thermal_demand_intensity.run()

    # heating_thermal_demand_intensity
    heating_thermal_demand_intensity = HeatingThermalDemandIntensity(kpi_name="heating_thermal_demand_intensity")
    heating_thermal_demand_intensity.run()

    # primary_energy_by_certificate
    primary_energy_by_certificate = PrimaryEnergyByCertificate(kpi_name="primary_energy_by_certificate")
    primary_energy_by_certificate.run()

    # annual_net_incomes_household_per_building
    annual_net_incomes_household_per_building = AnnualNetIncomesHouseholdPerBuilding(kpi_name="annual_net_incomes_household_per_building")
    annual_net_incomes_household_per_building.run()

    # tropical_nights
    tropical_nights = TropicalNights(kpi_name="tropical_nights")
    tropical_nights.run()

    # torrid_nights
    torrid_nights = TorridNights(kpi_name="torrid_nights")
    torrid_nights.run()

    # hellish_nights
    hellish_nights = HellishNights(kpi_name="hellish_nights")
    hellish_nights.run()

    # heat_waves
    heat_waves = HeatWaves(kpi_name="heat_waves")
    heat_waves.run()

    # cold_waves
    cold_waves = ColdWaves(kpi_name='cold_waves')
    cold_waves.run()

    # household_rental_price_per_building
    household_rental_price_per_building = HouseholdRentalPricePerBuilding(kpi_name='household_rental_price_per_building')
    household_rental_price_per_building.run()

    # nacionality_residents_per_building
    nacionality_residents_per_building = NationalityResidentsPerBuilding(kpi_name='nacionality_residents_per_building')
    nacionality_residents_per_building.run()

    # building_code
    building_code = BuildingCode(kpi_name='building_code')
    building_code.run()

    # average_weekly_electricity_load_curve
    average_weekly_electricity_load_curve = AverageWeeklyElectricityLoadCurve(kpi_name='average_weekly_electricity_load_curve')
    average_weekly_electricity_load_curve.run()

    # building_residents_birthplace
    building_residents_birthplace = BuildingResidentsBirthplace(kpi_name='building_residents_birthplace')
    building_residents_birthplace.run()

    # native_residents_per_building
    native_residents_per_building = NativeResidentsPerBuilding(kpi_name='native_residents_per_building')
    native_residents_per_building.run()

    # ancients_residents_per_building
    ancients_residents_per_building = AncientsResidentsPerBuilding(kpi_name='ancients_residents_per_building')
    ancients_residents_per_building.run()

    # children_residents_per_building
    children_residents_per_building = ChildrenResidentsPerBuilding(kpi_name='children_residents_per_building')
    children_residents_per_building.run()

    # female_residents_per_building
    female_residents_per_building = FemaleResidentsPerBuilding(kpi_name='female_residents_per_building')
    female_residents_per_building.run()

    # male_residents_per_building
    male_residents_per_building = MaleResidentsPerBuilding(kpi_name='male_residents_per_building')
    male_residents_per_building.run()

    # residents_per_building
    residents_per_building = ResidentsPerBuilding(kpi_name='residents_per_building')
    residents_per_building.run()

    ##ground_floor_commercial_premises_list
    ground_floor_commercial_premises_list = GroundFloorCommercialPremisesList(kpi_name='ground_floor_commercial_premises_list')
    ground_floor_commercial_premises_list.run()

    ##ground_floor_commercial_premises
    ground_floor_commercial_premises = GroundFloorCommercialPremises(kpi_name='ground_floor_commercial_premises')
    ground_floor_commercial_premises.run()

    ##distance_from_facade_to_adjacent_buildings_by_orientation
    distance_from_facade_to_adjacent_buildings_by_orientation = DistanceFromFacadeToAdjacentBuildingsByOrientation(kpi_name='distance_from_facade_to_adjacent_buildings_by_orientation')
    distance_from_facade_to_adjacent_buildings_by_orientation.run()

    ##facade area exposed by orientation
    facade_area_exposed_by_orientation = FacadeAreaExposedByOrientation(kpi_name='facade_area_exposed_by_orientation')
    facade_area_exposed_by_orientation.run()

    ##residential common area ratio
    common_to_total_area_ratio = CommonToTotalAreaRatio(kpi_name='common_to_total_area_ratio')
    common_to_total_area_ratio.run()

    ##residential common area ratio
    residential_common_area_ratio = ResidentialCommonAreaRatio(kpi_name='residential_common_area_ratio')
    residential_common_area_ratio.run()

    ##building roof area
    building_roof_area = BuildingRoofArea(kpi_name='building_roof_area')
    building_roof_area.run()

    ##total residential area
    total_residential_area = TotalResidentialArea(kpi_name='total_residential_area')
    total_residential_area.run()

    ##average dwelling area
    average_dwelling_area = AverageDwellingArea(kpi_name='average_dwelling_area')
    average_dwelling_area.run()

    ##effective construction year
    effective_construction_year = EffectiveConstructionYear(kpi_name='effective_construction_year')
    effective_construction_year.run()

    ##dwelings number
    dwelings_number = DwelingsNumber(kpi_name='dwelings_number')
    dwelings_number.run()

    ###number of floors below ground
    number_of_floors_below_ground = NumberOfFloorsBelowGround(kpi_name='number_of_floors_below_ground')
    number_of_floors_below_ground.run()

    ##number of floors above ground
    number_of_floors_above_ground = NumberOfFloorsAboveGround(kpi_name='number_of_floors_above_ground')
    number_of_floors_above_ground.run()

    ##annual_electricity_consumption_household
    annual_electricity_consumption = AnnualElectricityConsumption(kpi_name='annual_electricity_consumption')
    annualelectricity_consumption.run()

    ##construction_year
    construction_year = ConstructionYear(kpi_name='construction_year')
    construction_year.run()

    ##main_usage
    main_usage = MainUsage(kpi_name='main_usage')
    main_usage.run()

    ##gross_floor_area
    gross_floor_area = GrossFloorArea(kpi_name='gross_floor_area')
    gross_floor_area.run()

    ##vegetation_index
    vegetation_index = VegetationIndex(kpi_name='vegetation_index')
    vegetation_index.run()

    #vegetation_index_ui
    vegetation_index_ui = VegetationIndexUI(kpi_name='vegetation_index_ui')
    vegetation_index_ui.run()

    #grid_vegetation_index
    # grid_vegetation_index = GridVegetationIndex(kpi_name='grid_vegetation_index')
    # grid_vegetation_index.run()

    #grossFloorAreaTest
    gross_floor_area = GrossFloorArea(kpi_name='grossFloorArea')
    gross_floor_area.run()

if __name__ == "__main__":
    main()