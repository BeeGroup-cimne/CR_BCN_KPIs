from datetime import datetime

import numpy as np
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb, store_many_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd
from social_ES.utils_INE import INEPopulationAnualCensus, INERentalDistributionAtlas
from config.config_loader import config


class PercentagePopulationUnder18(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):

        # Rental
        df = INERentalDistributionAtlas(
            path=f"{config['paths']['nextcloud']}/data/social_ES/data/INERentalDistributionAtlas",
            municipality_code="08019", years=None)['Sections']
        self.data["rental"] = {
            year: dict(zip(group["Municipality code"] + group["District code"] + group["Section code"],
                           group["Percentage of the population under the age of 18"]
                           ))
            for year, group in df.groupby("Year")
        }


        # Relation
        query = f"""MATCH (b:s4bldg__Building)<-[:geosp__sfContains]-(ct:gn__parentADM5)
                    WITH split(b.uri, "-")[1] AS referencia, substring(split(ct.uri, "-")[1], 0, 5) + substring(split(ct.uri, "-")[1], 6) AS clave
                    WITH clave, collect(referencia) AS referencias
                    RETURN apoc.map.fromPairs(collect([clave, referencias])) AS result"""
        self.data["neo4j_data"] = fetch_data_from_neo4j(query)


    def calculate(self):

        self.data['result'] = {year: {} for year in self.data["rental"]}
        for census_tract, buildings_list in self.data["neo4j_data"][0]["result"].items():

            for building in buildings_list:
                for year, rental_value in self.data["rental"].items():
                    self.data['result'][year][building] = rental_value[census_tract]

        self.result = self.helper_transform_data(self.data["result"])

    def helper_transform_data(self, data):
        return [
            {
                "calculation_date": datetime(year=int(year), month=1, day=1).date().isoformat(),
                "kpis": {
                    key: round(value, 2)
                    # key: value
                    for key, value in values.items()
                }
            }
            for year, values in data.items()
        ]

    def store_result(self):
        store_many_data_in_mongodb(super().get_mongo_collection_name(), self.result)
