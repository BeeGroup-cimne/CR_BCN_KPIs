import math
from datetime import datetime

import numpy as np
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd


class NumberOfFloorsAboveGround(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        file_path = "/Users/jose/Nextcloud/Beegroup/data/hypercadaster_ES/08900.pkl"
        df = pd.read_pickle(file_path, compression="gzip")
        self.data["neo4j_data"] = dict(zip(df['building_reference'], df['br__floors_above_ground']))

    def calculate(self):
        self.result = self.helper_transform_data(self.sanitize_dict(self.data["neo4j_data"]))

    def sanitize_dict(self, data):
        for key, value in data.items():
            if isinstance(value, float):
                if math.isnan(value) or math.isinf(value):
                    data[key] = None
                else:
                    data[key] = round(value, 3)
        return data
    def helper_transform_data(self, data):
        mongo_data = {
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": {}
        }

        for key, value in data.items():
            try:
                mongo_data["kpis"][key] = value
            except ValueError:
                print("error")
                mongo_data["kpis"][key] = None
        return mongo_data
