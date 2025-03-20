from kpi_calculations.ancients_residents_per_building import AncientsResidentsPerBuilding
from kpi_calculations.ancients_residents_per_building_m2 import AncientsResidentsPerBuildingM2
from kpi_calculations.ancients_residents_per_census_tract import AncientsResidentsPerCensusTract
from kpi_calculations.annual_net_incomes_household_per_building import AnnualNetIncomesHouseholdPerBuilding
from kpi_calculations.annual_net_incomes_household_per_census_tract import AnnualNetIncomesHouseholdPerCensusTract
from kpi_calculations.average_weekly_electricity_load_curve import AverageWeeklyElectricityLoadCurve
from kpi_calculations.building_code import BuildingCode
from kpi_calculations.building_residents_birthplace import BuildingResidentsBirthplace
from kpi_calculations.building_roof_area import BuildingRoofArea
from kpi_calculations.children_residents_per_building import ChildrenResidentsPerBuilding
from kpi_calculations.children_residents_per_building_m2 import ChildrenResidentsPerBuildingM2
from kpi_calculations.children_residents_per_census_tract import ChildrenResidentsPerCensusTract
from kpi_calculations.common_to_total_area_ratio import CommonToTotalAreaRatio
from kpi_calculations.cooling_thermal_demand_intensity import CoolingThermalDemandIntensity
from kpi_calculations.distance_from_facade_to_adjacent_buildings_by_orientation import \
    DistanceFromFacadeToAdjacentBuildingsByOrientation
from kpi_calculations.dwelings_number import DwelingsNumber
from kpi_calculations.effective_construction_year import EffectiveConstructionYear
from kpi_calculations.facade_area_exposed_by_orientation import FacadeAreaExposedByOrientation
from kpi_calculations.female_residents_per_building import FemaleResidentsPerBuilding
from kpi_calculations.female_residents_per_building_m2 import FemaleResidentsPerBuildingM2
from kpi_calculations.female_residents_per_census_tract import FemaleResidentsPerCensusTract

from kpi_calculations.foreign_residents_per_census_tract import ForeignResidentsPerCensusTract
from kpi_calculations.grossFloorArea import grossFloorArea
from kpi_calculations.grid_vegetation_index import GridVegetationIndex
from kpi_calculations.ground_floor_commercial_premises import GroundFloorCommercialPremises
from kpi_calculations.ground_floor_commercial_premises_list import GroundFloorCommercialPremisesList
from kpi_calculations.heating_thermal_demand_intensity import HeatingThermalDemandIntensity
from kpi_calculations.household_rental_price_per_building import HouseholdRentalPricePerBuilding
from kpi_calculations.income_sources_typology import IncomeSourcesTypologyPerCensusTract
from kpi_calculations.male_residents_per_building import MaleResidentsPerBuilding
from kpi_calculations.male_residents_per_census_tract import MaleResidentsPerCensusTract
from kpi_calculations.meteo.cold_waves import ColdWaves
from kpi_calculations.meteo.heat_waves import HeatWaves
from kpi_calculations.meteo.hellish_nights import HellishNights
from kpi_calculations.meteo.torrid_nights import TorridNights
from kpi_calculations.meteo.tropical_nights import TropicalNights
from kpi_calculations.meteo_model_data.average_dwelling_area import AverageDwellingArea
from kpi_calculations.nacionality_residents_per_building import NationalityResidentsPerBuilding
from kpi_calculations.nacionality_residents_per_census_tract import NacionalityResidentsPerCensusTract
from kpi_calculations.native_residents_per_building import NativeResidentsPerBuilding
from kpi_calculations.native_residents_per_census_tract import NativeResidentsPerCensusTract
from kpi_calculations.number_of_floors_above_ground import NumberOfFloorsAboveGround
from kpi_calculations.number_of_floors_below_ground import NumberOfFloorsBelowGround
from kpi_calculations.primary_energy_by_certificate import PrimaryEnergyByCertificate
from kpi_calculations.residential_common_area_ratio import ResidentialCommonAreaRatio
from kpi_calculations.residents_per_census_tract import ResidentsPerCensusTract
from kpi_calculations.residents_per_building import ResidentsPerBuilding
from kpi_calculations.total_energy_consumption_intensity import TotalEnergyConsumptionIntensity
from kpi_calculations.total_residential_area import TotalResidentialArea
from kpi_calculations.vegetation_index import VegetationIndex
from kpi_calculations.gross_floor_area import GrossFloorArea
from kpi_calculations.main_usage import MainUsage
from kpi_calculations.construction_year import ConstructionYear
from kpi_calculations.annual_electricity_consumption import AnnualElectricityConsumption
from kpi_calculations.window_to_wall_ratio import WindowToWallRatio


def main():

    ###### CENSUS TRACT ######
    ##nacionality_residents_per_census_tract
    # nacionality_residents_per_census_tract = NacionalityResidentsPerCensusTract(kpi_name='nacionality_residents_per_census_tract')
    # nacionality_residents_per_census_tract.run()

    ##residents_per_census_tract
    # residents_per_census_tract = ResidentsPerCensusTract(kpi_name='residents_per_census_tract')
    # residents_per_census_tract.run()

    ##male_residents_per_census_tract
    # male_residents_per_census_tract = MaleResidentsPerCensusTract(kpi_name='male_residents_per_census_tract')
    # male_residents_per_census_tract.run()

    ##female_residents_per_census_tract
    # female_residents_per_census_tract = FemaleResidentsPerCensusTract(kpi_name='female_residents_per_census_tract')
    # female_residents_per_census_tract.run()

    ##native_residents_per_census_tract
    # native_residents_per_census_tract = NativeResidentsPerCensusTract(kpi_name='native_residents_per_census_tract')
    # native_residents_per_census_tract.run()

    ##foreign_residents_per_census_tract
    # foreign_residents_per_census_tract = ForeignResidentsPerCensusTract(kpi_name='foreign_residents_per_census_tract')
    # foreign_residents_per_census_tract.run()

    ##children_residents_per_census_tract
    # children_residents_per_census_tract = ChildrenResidentsPerCensusTract(kpi_name='children_residents_per_census_tract')
    # children_residents_per_census_tract.run()

    ##ancients_residents_per_census_tract
    # ancients_residents_per_census_tract = AncientsResidentsPerCensusTract(kpi_name='ancients_residents_per_census_tract')
    # ancients_residents_per_census_tract.run()

    # income_sources_typology
    # income_sources_typology_per_census_tract = IncomeSourcesTypologyPerCensusTract(kpi_name='income_sources_typology_per_census_tract')
    # income_sources_typology_per_census_tract.run()

    # annual_net_incomes_household_per_census_tract
    # annual_net_incomes_household_per_census_tract = AnnualNetIncomesHouseholdPerCensusTract(kpi_name='annual_net_incomes_household_per_census_tract')
    # annual_net_incomes_household_per_census_tract.run()

    # annual_net_incomes_household_per_census_tract
    # household_rental_price_per_census_tract = HouseholdRentalPricePerCensusTract(kpi_name='household_rental_price_per_census_tract')
    # household_rental_price_per_census_tract.run()


###### Building ######

    # children_residents_per_building_m2
    # children_residents_per_building_m2 = ChildrenResidentsPerBuildingM2(kpi_name="children_residents_per_building_m2")
    # children_residents_per_building_m2.run()

    # ancients_residents_per_building_m2
    # ancients_residents_per_building_m2 = AncientsResidentsPerBuildingM2(kpi_name="ancients_residents_per_building_m2")
    # ancients_residents_per_building_m2.run()

    # female_residents_per_building_m2
    # female_residents_per_building_m2 = FemaleResidentsPerBuildingM2(kpi_name="female_residents_per_building_m2")
    # female_residents_per_building_m2.run()

    # total_energy_consumption_intensity
    # window_to_wall_ratio = WindowToWallRatio(kpi_name="window_to_wall_ratio")
    # window_to_wall_ratio.run()

    # total_energy_consumption_intensity
    # total_energy_consumption_intensity = TotalEnergyConsumptionIntensity(kpi_name="total_energy_consumption_intensity")
    # total_energy_consumption_intensity.run()

    # cooling_thermal_demand_intensity
    # cooling_thermal_demand_intensity = CoolingThermalDemandIntensity(kpi_name="cooling_thermal_demand_intensity")
    # cooling_thermal_demand_intensity.run()

    # heating_thermal_demand_intensity
    # heating_thermal_demand_intensity = HeatingThermalDemandIntensity(kpi_name="heating_thermal_demand_intensity")
    # heating_thermal_demand_intensity.run()

    # primary_energy_by_certificate
    # primary_energy_by_certificate = PrimaryEnergyByCertificate(kpi_name="primary_energy_by_certificate")
    # primary_energy_by_certificate.run()

    # annual_net_incomes_household_per_building
    # annual_net_incomes_household_per_building = AnnualNetIncomesHouseholdPerBuilding(kpi_name="annual_net_incomes_household_per_building")
    # annual_net_incomes_household_per_building.run()

    # tropical_nights
    # tropical_nights = TropicalNights(kpi_name="tropical_nights")
    # tropical_nights.run()

    # torrid_nights
    # torrid_nights = TorridNights(kpi_name="torrid_nights")
    # torrid_nights.run()

    # hellish_nights
    # hellish_nights = HellishNights(kpi_name="hellish_nights")
    # hellish_nights.run()

    # heat_waves
    heat_waves = HeatWaves(kpi_name="heat_waves")
    heat_waves.run()

    # cold_waves
    # cold_waves = ColdWaves(kpi_name='cold_waves')
    # cold_waves.run()

    # household_rental_price_per_building
    # household_rental_price_per_building = HouseholdRentalPricePerBuilding(kpi_name='household_rental_price_per_building')
    # household_rental_price_per_building.run()

    # nacionality_residents_per_building
    # nacionality_residents_per_building = NationalityResidentsPerBuilding(kpi_name='nacionality_residents_per_building')
    # nacionality_residents_per_building.run()

    # building_code
    # building_code = BuildingCode(kpi_name='building_code')
    # building_code.run()

    # average_weekly_electricity_load_curve
    # average_weekly_electricity_load_curve = AverageWeeklyElectricityLoadCurve(kpi_name='average_weekly_electricity_load_curve')
    # average_weekly_electricity_load_curve.run()

    # building_residents_birthplace
    # building_residents_birthplace = BuildingResidentsBirthplace(kpi_name='building_residents_birthplace')
    # building_residents_birthplace.run()

    # native_residents_per_building
    # native_residents_per_building = NativeResidentsPerBuilding(kpi_name='native_residents_per_building')
    # native_residents_per_building.run()

    # ancients_residents_per_building
    # ancients_residents_per_building = AncientsResidentsPerBuilding(kpi_name='ancients_residents_per_building')
    # ancients_residents_per_building.run()

    # children_residents_per_building
    # children_residents_per_building = ChildrenResidentsPerBuilding(kpi_name='children_residents_per_building')
    # children_residents_per_building.run()

    # female_residents_per_building
    # female_residents_per_building = FemaleResidentsPerBuilding(kpi_name='female_residents_per_building')
    # female_residents_per_building.run()

    # male_residents_per_building
    # male_residents_per_building = MaleResidentsPerBuilding(kpi_name='male_residents_per_building')
    # male_residents_per_building.run()

    # residents_per_building
    # residents_per_building = ResidentsPerBuilding(kpi_name='residents_per_building')
    # residents_per_building.run()

    ##ground_floor_commercial_premises_list
    # ground_floor_commercial_premises_list = GroundFloorCommercialPremisesList(kpi_name='ground_floor_commercial_premises_list')
    # ground_floor_commercial_premises_list.run()

    ##ground_floor_commercial_premises
    # ground_floor_commercial_premises = GroundFloorCommercialPremises(kpi_name='ground_floor_commercial_premises')
    # ground_floor_commercial_premises.run()

    ##distance_from_facade_to_adjacent_buildings_by_orientation
    # distance_from_facade_to_adjacent_buildings_by_orientation = DistanceFromFacadeToAdjacentBuildingsByOrientation(kpi_name='distance_from_facade_to_adjacent_buildings_by_orientation')
    # distance_from_facade_to_adjacent_buildings_by_orientation.run()

    ##facade area exposed by orientation
    # facade_area_exposed_by_orientation = FacadeAreaExposedByOrientation(kpi_name='facade_area_exposed_by_orientation')
    # facade_area_exposed_by_orientation.run()

    ##residential common area ratio
    # common_to_total_area_ratio = CommonToTotalAreaRatio(kpi_name='common_to_total_area_ratio')
    # common_to_total_area_ratio.run()

    ##residential common area ratio
    # residential_common_area_ratio = ResidentialCommonAreaRatio(kpi_name='residential_common_area_ratio')
    # residential_common_area_ratio.run()

    ##building roof area
    # building_roof_area = BuildingRoofArea(kpi_name='building_roof_area')
    # building_roof_area.run()

    ##total residential area
    # total_residential_area = TotalResidentialArea(kpi_name='total_residential_area')
    # total_residential_area.run()

    ##average dwelling area
    # average_dwelling_area = AverageDwellingArea(kpi_name='average_dwelling_area')
    # average_dwelling_area.run()

    ##effective construction year
    # effective_construction_year = EffectiveConstructionYear(kpi_name='effective_construction_year')
    # effective_construction_year.run()

    ##dwelings number
    # dwelings_number = DwelingsNumber(kpi_name='dwelings_number')
    # dwelings_number.run()

    ###number of floors below ground
    # number_of_floors_below_ground = NumberOfFloorsBelowGround(kpi_name='number_of_floors_below_ground')
    # number_of_floors_below_ground.run()

    ##number of floors above ground
    # number_of_floors_above_ground = NumberOfFloorsAboveGround(kpi_name='number_of_floors_above_ground')
    # number_of_floors_above_ground.run()

    ##annual_electricity_consumption_household
    # annual_electricity_consumption = AnnualElectricityConsumption(kpi_name='annual_electricity_consumption')
    # annual_electricity_consumption.run()

    ##construction_year
    # construction_year = ConstructionYear(kpi_name='construction_year')
    # construction_year.run()

    ##main_usage
    # main_usage = MainUsage(kpi_name='main_usage')
    # main_usage.run()

    ##gross_floor_area
    # gross_floor_area = GrossFloorArea(kpi_name='gross_floor_area')
    # gross_floor_area.run()

    ##vegetation_index
    # vegetation_index = VegetationIndex(kpi_name='vegetation_index')
    # vegetation_index.run()

    ##vegetation_index_ui
    # vegetation_index_ui = VegetationIndexUI(kpi_name='vegetation_index_ui')
    # vegetation_index_ui.run()

    ##grid_vegetation_index
    # grid_vegetation_index = GridVegetationIndex(kpi_name='grid_vegetation_index')
    # grid_vegetation_index.run()

    ##grossFloorAreaTest
    # gross_floor_area = GrossFloorArea(kpi_name='grossFloorArea')
    # gross_floor_area.run()

if __name__ == "__main__":
    main()