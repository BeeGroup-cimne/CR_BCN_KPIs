import math
from datetime import datetime

import numpy as np

from config.config_loader import config
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd

class AdiabaticWallArea(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        file_path = f"{config['paths']['nextcloud']}/data/hypercadaster_ES/08900.pkl"
        hyper_df = pd.read_pickle(file_path, compression="gzip")
        self.data["adiabatic"] = dict(zip(hyper_df['building_reference'], hyper_df['br__adiabatic_wall']))

        # query = f"""MATCH (n:s4bldg__Building)-[:geosp__hasArea]->(m:saref__Measurement)-[:saref__relatesToProperty]->(bigg__GrossFloorArea{{uri:"http://bigg-project.eu/ontology#GrossFloorArea"}}) RETURN apoc.map.fromPairs(collect([m.uri, m.saref__hasValue])) AS result"""
        # self.data["neo4j_data"] = fetch_data_from_neo4j(query)

    def calculate(self):
        self.data["result"] = {}
        for ref, value in self.data["adiabatic"].items():
            if isinstance(value, float):
                self.data["result"][ref] = value

        self.result = self.helper_transform_data(self.sanitize_dict(self.data["result"]))

    def helper_transform_data(self, data):
        mongo_data = {
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": {}
        }

        for key, value in data.items():
            if isinstance(value, float):
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