from datetime import datetime
import math
import numpy as np

from config.config_loader import config
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd

class AverageDwellingArea(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        file_path = f"{config['paths']['nextcloud']}/data/hypercadaster_ES/08900.pkl"
        df = pd.read_pickle(file_path, compression="gzip")
        self.data["neo4j_data"] = dict(zip(df['building_reference'], df['br__mean_building_space_area_without_communals']))
        # query = f"""MATCH (n:s4bldg__Building)-[:geosp__hasArea]->(m:saref__Measurement)-[:saref__relatesToProperty]->(bigg__GrossFloorArea{{uri:"http://bigg-project.eu/ontology#GrossFloorArea"}}) RETURN apoc.map.fromPairs(collect([m.uri, m.saref__hasValue])) AS result"""
        # self.data["neo4j_data"] = fetch_data_from_neo4j(query)

    def calculate(self):
        for ref_cat, types in self.data["neo4j_data"].items():
            try:
                residential_count = types.get('Residential', 0)
                self.data["neo4j_data"][ref_cat] = residential_count
            except:
                self.data["neo4j_data"][ref_cat] = np.nan

        self.result = self.helper_transform_data(self.sanitize_dict(self.data["neo4j_data"]))

    def helper_transform_data(self, data):
        mongo_data = {
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": {}
        }

        for key, value in data.items():
            mongo_data["kpis"][key] = value
        return mongo_data

    def sanitize_dict(self, data):
        for key, value in data.items():
            if isinstance(value, float):
                if math.isnan(value) or math.isinf(value):
                    data[key] = None
                else:
                    data[key] = round(value, 2)
        return data