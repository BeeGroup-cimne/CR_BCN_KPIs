import math
from datetime import datetime

import numpy as np

from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd

class ExteriorWallArea(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        file_path = "/Users/jose/Nextcloud/Beegroup/data/hypercadaster_ES/08900.pkl"
        hyper_df = pd.read_pickle(file_path, compression="gzip")
        self.data["air_contact"] = dict(zip(hyper_df['building_reference'], hyper_df['br__air_contact_wall']))

        # query = f"""MATCH (n:s4bldg__Building)-[:geosp__hasArea]->(m:saref__Measurement)-[:saref__relatesToProperty]->(bigg__GrossFloorArea{{uri:"http://bigg-project.eu/ontology#GrossFloorArea"}}) RETURN apoc.map.fromPairs(collect([m.uri, m.saref__hasValue])) AS result"""
        # self.data["neo4j_data"] = fetch_data_from_neo4j(query)

    def calculate(self):
        self.data["result"] = {}
        for ref, value in data["air_contact"].items():
            if isinstance(value, dict):
                data["result"][ref] = sum(list(value.values()))

        self.result = helper_transform_data(sanitize_dict(data["result"]))
        store_data_in_mongodb("exterior_wall_area", result)

    def helper_transform_data(data):
        mongo_data = {
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": {}
        }

        for key, value in data.items():
            mongo_data["kpis"][key] = value if not math.isnan(value) else None
        return mongo_data

    def sanitize_dict(data):
        for key, value in data.items():
            if isinstance(value, float):
                if math.isnan(value) or math.isinf(value):
                    data[key] = None
                else:
                    data[key] = round(value, 2)
        return data