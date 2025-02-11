from datetime import datetime
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase

class MainUsage(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        query = f"""MATCH (b:s4bldg__Building) RETURN apoc.map.fromPairs(collect([split(b.uri, "-")[1], b.bigg__mainUse])) AS result"""
        self.data["neo4j_data"] = fetch_data_from_neo4j(query)

    def calculate(self):
        self.result = self.helper_transform_data(self.data["neo4j_data"][0]["result"])

    def create_one_hot_vector(self, key):
        main_usage_dict = {'Residential': 0, 'Agriculture': 1, 'Industrial': 2, 'Retail': 3, 'PublicServices': 4, None: 5}
        one_hot_vector = [0] * len(main_usage_dict)
        index = main_usage_dict.get(key, main_usage_dict[None])
        one_hot_vector[index] = 100
        return one_hot_vector
    def helper_transform_data(self, data):

        mongo_data = {
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": {}
        }

        for key, value in data.items():
            mongo_data["kpis"][key] = self.create_one_hot_vector(value)

        return mongo_data