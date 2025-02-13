from datetime import datetime

import numpy as np
from social_ES.utils_INE import INEPopulationAnualCensus, INERentalDistributionAtlas

from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb, store_many_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd


class IncomeSourcesTypologyPerCensusTract(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        # Rental distribution
        df = INERentalDistributionAtlas(
            path="/Users/jose/Nextcloud/Beegroup/data/social_ES/data/INERentalDistributionAtlas",
            municipality_code="08019", years=None)['Sections']

        self.data["rental"] = {
            year: dict(zip(group["Municipality code"] + group["District code"] + group["Section code"],
                           group[[
                               "Fuente de ingreso: prestaciones por desempleo",
                               "Fuente de ingreso: otras prestaciones",
                               "Fuente de ingreso: pensiones",
                               "Fuente de ingreso: salario",
                               "Fuente de ingreso: otros ingresos"
                           ]].values.tolist()
                           ))
            for year, group in df.groupby("Year")
        }

    def calculate(self):
        self.result = self.helper_transform_data(self.data["rental"])

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
