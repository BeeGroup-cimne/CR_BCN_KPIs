from datetime import datetime

import numpy as np
from social_ES.utils_INE import INEPopulationAnualCensus

from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb, store_many_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd


class MaleResidentsPerCensusTract(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        # Social
        df = INEPopulationAnualCensus(
            path="/Users/jose/Nextcloud/Beegroup/data/social_ES/data/INEPopulationAnualCensus",
            municipality_code="08019")['Sections']

        self.data["social"] = {
            year: dict(zip(group["Municipality code"] + group["District code"] + group["Section code"],
                           group["Population ~ Sex:Males"]))
            for year, group in df.groupby("Year")
        }

    def calculate(self):
        self.result = self.helper_transform_data(self.data["social"])

    def helper_transform_data(self, data):
        return [
            {
                "calculation_date": datetime(year=year, month=1, day=1).date().isoformat(),
                "kpis": {
                    key: int(value) if isinstance(value, (int, float)) or str(value).isdigit() else np.nan
                    for key, value in values.items()
                }
            }
            for year, values in data.items()
        ]

    def store_result(self):
        store_many_data_in_mongodb(super().get_mongo_collection_name(), self.result)
