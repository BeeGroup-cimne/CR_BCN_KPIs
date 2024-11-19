from datetime import datetime
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase

class MainUsage(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        query = f"""MATCH (b:s4bldg__Building) RETURN apoc.map.fromPairs(collect([b.bigg__cadastralId, b.bigg__mainUse])) AS result"""
        self.data["neo4j_data"] = fetch_data_from_neo4j(query)

    def calculate(self):
        self.result = self.helper_transform_data(self.data["neo4j_data"][0]["result"])

    def helper_transform_data(self, data):
        mongo_data = {
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": []
        }

        for key, value in data.items():
            kpi_document = {
                "_id": key,
                "v": value
            }
            mongo_data["kpis"].append(kpi_document)
        return mongo_data
