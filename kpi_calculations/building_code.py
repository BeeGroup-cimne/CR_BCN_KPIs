from datetime import datetime
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd

class BuildingCode(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        query = f"""MATCH (b:s4bldg__Building) RETURN apoc.map.fromPairs(collect([split(b.uri, "-")[1], substring(b.bigg__endConstruction, 0, 4)])) AS result"""
        self.data["neo4j_data"] = fetch_data_from_neo4j(query)

    def get_building_code(self, construction_year):
        if construction_year <= 1976:
            return "SL"
        elif construction_year <= 1979:
            return "NTE"
        elif construction_year <= 2005:
            return "NBE"
        elif construction_year <= 2012:
            return "CTE2006"
        elif construction_year <= 2018:
            return "CTE2013"
        else:  # construction_year >= 2019
            return "CTE2019"

    def calculate(self):
        INVALID_VALUES = {None, "--01", "150-", "1-01", "2-01"}
        type_map = {
            'SL': [1, 0, 0, 0, 0, 0],
            'NTE': [0, 1, 0, 0, 0, 0],
            'NBE': [0, 0, 1, 0, 0, 0],
            'CTE2006': [0, 0, 0, 1, 0, 0],
            'CTE2013': [0, 0, 0, 0, 1, 0],
            'CTE2019': [0, 0, 0, 0, 0, 1],
        }
        self.data["result"] = {}
        for k, v in self.data["neo4j_data"][0]['result'].items():
            self.data["result"][k] = type_map[self.get_building_code(int(v) if v not in INVALID_VALUES else 0)]
        self.result = self.helper_transform_data(self.data["result"])

    def helper_transform_data(self, data):
        return{
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": data
        }
