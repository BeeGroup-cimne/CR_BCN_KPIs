from datetime import datetime

import numpy as np
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb, store_many_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd
from social_ES.utils_INE import INEPopulationAnualCensus


class NationalityResidentsPerBuilding(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):

        # Social
        df = INEPopulationAnualCensus(
            path="/Users/jose/Nextcloud/Beegroup/data/social_ES/data/INEPopulationAnualCensus",
            municipality_code="08019")['Sections']

        self.data["social"] = {
            year: dict(
                zip(
                    group["Municipality code"] + group["District code"] + group["Section code"],  # Claves
                    map(list, zip(
                        group["Population ~ Nationality:España"],
                        group["Population ~ Nationality:French"],
                        group["Population ~ Nationality:British"],
                        group["Population ~ Nationality:Romanian"],
                        group["Population ~ Nationality:Ukrainian"],
                        group["Population ~ Nationality:Other European nationalities"],
                        group["Population ~ Nationality:Moroccan"],
                        group["Population ~ Nationality:Other African nationalities"],
                        group["Population ~ Nationality:Cuban"],
                        group["Population ~ Nationality:Dominican"],
                        group["Population ~ Nationality:Argentinian"],
                        group["Population ~ Nationality:Bolivian"],
                        group["Population ~ Nationality:Colombian"],
                        group["Population ~ Nationality:Ecuadorian"],
                        group["Population ~ Nationality:Peruvian"],
                        group["Population ~ Nationality:Venezuelan"],
                        group["Population ~ Nationality:Other American nationalities"],
                        group["Population ~ Nationality:Chinese"],
                        group["Population ~ Nationality:Other Asian nationalities"],
                        group["Population ~ Nationality:Oceanian"],
                        group["Population ~ Nationality:Stateless"]
                    ))
                )
            )
            for year, group in df.groupby("Year")
        }

        # Residential area
        file_path = "/Users/jose/Nextcloud/Beegroup/data/hypercadaster_ES/results/08900_br_results.pkl"
        df = pd.read_pickle(file_path, compression="gzip")
        self.data["area"] = dict(zip(df['building_reference'], df['br__area_without_communals']))

        # Relation
        # query = f"""MATCH (b:s4bldg__Building)<-[:geosp__sfContains]-(ct:gn__parentADM5)
        #             WITH b, split(ct.uri, "-")[1] AS originalString
        #             WITH b.bigg__cadastralId AS clave, substring(originalString, 0, 5) + substring(originalString, 6) AS valor
        #             RETURN apoc.map.fromPairs(collect([clave, valor])) AS result"""
        #
        # self.data["neo4j_data"] = fetch_data_from_neo4j(query)

        # Relation
        query = f"""MATCH (b:s4bldg__Building)<-[:geosp__sfContains]-(ct:gn__parentADM5)
                    WITH split(b.uri, "-")[1] AS referencia, substring(split(ct.uri, "-")[1], 0, 5) + substring(split(ct.uri, "-")[1], 6) AS clave
                    WITH clave, collect(referencia) AS referencias
                    RETURN apoc.map.fromPairs(collect([clave, referencias])) AS result"""
        self.data["neo4j_data"] = fetch_data_from_neo4j(query)

    def calculate(self):
        self.data['result'] = {year: {} for year in self.data["social"]}

        for census_tract, buildings_list in self.data["neo4j_data"][0]["result"].items():
            census_tract_residential_area = sum(
                (self.data['area'].get(building, {}).get('Residential', 0)
                 if isinstance(self.data['area'].get(building, {}), dict) else 0)
                for building in buildings_list
            )

            if census_tract_residential_area == 0:
                continue

            for building in buildings_list:
                building_residential_area = 0
                building_data = self.data['area'].get(building, {})

                if isinstance(building_data, dict):
                    building_residential_area = building_data.get('Residential', 0)

                if building_residential_area == 0:
                    continue
                for year, social_values in self.data["social"].items():
                    census_tract_values = social_values.get(census_tract,
                                                            [np.nan] * 19)  # Lista con NaN si no hay datos
                    self.data['result'][year][building] = [
                        (building_residential_area / census_tract_residential_area) * value if not np.isnan(
                            value) else np.nan
                        for value in census_tract_values
                    ]
        self.result = self.helper_transform_data(self.data["result"])

    def helper_transform_data(self, data):
        return [
            {
                "calculation_date": datetime(year=int(year), month=1, day=1).date().isoformat(),
                "kpis": {
                    key: value
                    # key: value
                    for key, value in values.items()
                }
            }
            for year, values in data.items()
        ]

    def store_result(self):
        store_many_data_in_mongodb(super().get_mongo_collection_name(), self.result)
