from datetime import datetime

import numpy as np
from social_ES.utils_INE import INEPopulationAnualCensus

from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb, store_many_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd

class NacionalityResidentsPerCensusTract(KPIBase):
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



        # query = f"""MATCH (n:s4bldg__Building)-[:geosp__hasArea]->(m:saref__Measurement)-[:saref__relatesToProperty]->(bigg__GrossFloorArea{{uri:"http://bigg-project.eu/ontology#GrossFloorArea"}}) RETURN apoc.map.fromPairs(collect([m.uri, m.saref__hasValue])) AS result"""
        # self.data["neo4j_data"] = fetch_data_from_neo4j(query)

    def calculate(self):
        self.result = self.helper_transform_data(self.data["social"])

    def helper_transform_data(self, data):
        return [
            {
                "calculation_date": datetime(year=year, month=1, day=1).date().isoformat(),
                "kpis": {
                    key: value
                    for key, value in values.items()
                }
            }
            for year, values in data.items()
        ]

    def store_result(self):
        store_many_data_in_mongodb(super().get_mongo_collection_name(), self.result)
