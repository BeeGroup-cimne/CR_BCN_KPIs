from datetime import datetime
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase

class ConstructionYear(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        query = f"""MATCH (b:s4bldg__Building) RETURN apoc.map.fromPairs(collect([b.bigg__cadastralId, substring(b.bigg__endConstruction, 0, 4)])) AS result"""
        self.data["neo4j_data"] = fetch_data_from_neo4j(query)

    def calculate(self):
        self.result = self.helper_transform_data(self.data["neo4j_data"][0]["result"])

    def helper_transform_data(self, data):
        return {
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": data
        }