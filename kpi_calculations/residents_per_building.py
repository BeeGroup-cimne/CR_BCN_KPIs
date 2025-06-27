from datetime import datetime

import numpy as np
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb, store_many_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd
from social_ES.utils_INE import INEPopulationAnualCensus
from config.config_loader import config

class ResidentsPerBuilding(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):

        # Social
        social_df = INEPopulationAnualCensus(
            path=f"{config['paths']['nextcloud']}/data/social_ES/data/INEPopulationAnualCensus",
            municipality_code="08019")['Sections']

        self.data["social"] = {
            year: dict(zip(group["Municipality code"] + group["District code"] + group["Section code"],
                           group["Population"]))
            for year, group in social_df.groupby("Year")
        }

        # Residential area
        file_path = f"{config['paths']['nextcloud']}/data/hypercadaster_ES/08900.pkl"
        hyper_df = pd.read_pickle(file_path, compression="gzip")
        self.data["area"] = dict(zip(hyper_df['building_reference'], hyper_df['br__area_without_communals']))
        main_usage_list = ["Residential"]
        self.data["building_spaces"] = dict(zip(
            hyper_df["building_reference"],
            hyper_df["br__building_spaces"].map(
                lambda d: sum(d.get(k, 0) for k in main_usage_list) if isinstance(d, dict) else 0)
        ))

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
                (self.data['area'].get(building, {}).get('Residential', 0) if isinstance(
                    self.data['area'].get(building, {}),
                    dict)
                 else 0)
                for building in buildings_list
            )
            if census_tract_residential_area == 0:
                continue

            for building in buildings_list:
                building_residential_area = 0
                building_data = self.data['area'].get(building, {})
                if isinstance(building_data, dict):
                    building_residential_area = building_data.get('Residential', 0)

                building_spaces_data = self.data['building_spaces'].get(building, 0)
                if building_spaces_data == 0:
                    continue

                for year, social_value in self.data["social"].items():
                    self.data['result'][year][building] = (
                            (building_residential_area / census_tract_residential_area) * social_value.get(
                        census_tract, np.nan)) / building_spaces_data

        self.result = self.helper_transform_data(self.data["result"])

    def helper_transform_data(self, data):
        return [
            {
                "calculation_date": datetime(year=int(year), month=1, day=1).date().isoformat(),
                "kpis": {
                    key: round(value, 2)
                    for key, value in values.items()
                }
            }
            for year, values in data.items()
        ]

    def store_result(self):
        store_many_data_in_mongodb(super().get_mongo_collection_name(), self.result)
