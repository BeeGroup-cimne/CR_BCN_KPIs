from datetime import datetime

import numpy as np
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb, store_many_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd
from social_ES.utils_INE import INEPopulationAnualCensus, INERentalDistributionAtlas
from config.config_loader import config
from connectors.mongodb_connector import store_data_in_mongodb, store_many_data_in_mongodb, get_mongo_data
from connectors.mongodb_connector import store_data_in_mongodb, store_many_data_in_mongodb
import geopandas as gpd
import math
from pymongo import MongoClient
from config.config_loader import config


class NumClimateSheltersWithin15min(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        collection_name = "climate_shelters"
        self.data["climate_shelters"] = get_mongo_data(collection_name)


    def calculate(self):

        self.data["buildings"] = {}

        for document in self.data["climate_shelters"]:

            ref, shelters = next((k, v) for k, v in document.items() if k != '_id')

            self.data["buildings"][ref] = sum(1 for d in shelters.values() if d < 900)

        self.result = self.helper_transform_data(self.sanitize_dict(self.data["buildings"]))

    def helper_transform_data(self, data):
        mongo_data = {
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": {}
        }

        for key, value in data.items():
            if isinstance(value, int):
                mongo_data["kpis"][key] = value if not math.isnan(value) else None
        return mongo_data

    def sanitize_dict(self, data):
        for key, value in data.items():
            if isinstance(value, float):
                if math.isnan(value) or math.isinf(value):
                    data[key] = None
                else:
                    data[key] = round(value, 2)
        return data
