from datetime import datetime
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd
import numpy as np


class NumberOfFloorsBelowGround(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        file_path = "/Users/jose/Nextcloud/Beegroup/data/hypercadaster_ES/results/08900_br_results.pkl"
        df = pd.read_pickle(file_path, compression="gzip")
        self.data["neo4j_data"] = dict(zip(df['building_reference'], df['br__floors_below_ground']))

    def calculate(self):
        self.result = self.helper_transform_data(self.data["neo4j_data"])

    def helper_transform_data(self, data):
        mongo_data = {
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": {}
        }

        for key, value in data.items():
            try:
                mongo_data["kpis"][key] = int(value)
            except ValueError:
                mongo_data["kpis"][key] = np.nan
        return mongo_data
