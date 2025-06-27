from datetime import datetime
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd
import math


class EffectiveConstructionYear(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        file_path = "/Users/jose/Nextcloud/Beegroup/data/hypercadaster_ES/08900.pkl"
        df = pd.read_pickle(file_path, compression="gzip")
        self.data["neo4j_data"] = dict(zip(df['building_reference'], df['br__mean_building_space_effective_year']))
        # query = f"""MATCH (n:s4bldg__Building)-[:geosp__hasArea]->(m:saref__Measurement)-[:saref__relatesToProperty]->(bigg__GrossFloorArea{{uri:"http://bigg-project.eu/ontology#GrossFloorArea"}}) RETURN apoc.map.fromPairs(collect([m.uri, m.saref__hasValue])) AS result"""
        # self.data["neo4j_data"] = fetch_data_from_neo4j(query)

    def calculate(self):
        self.data["result"] = {}
        for ref, uses in self.data["neo4j_data"].items():
            if type(uses) is dict:
                if "Residential" in uses.keys():
                    self.data["result"][ref] = uses["Residential"]

        self.result = self.helper_transform_data(self.sanitize_dict(self.data["result"]))

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