from datetime import datetime
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase

class grossFloorArea(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        query = f"""MATCH (n:s4bldg__Building)-[:geosp__hasArea]->(m:saref__Measurement)-[:saref__relatesToProperty]->(bigg__GrossFloorArea{{uri:"http://bigg-project.eu/ontology#GrossFloorArea"}}) RETURN apoc.map.fromPairs(collect([m.uri, m.saref__hasValue])) AS result limit 2"""
        self.data["neo4j_data"] = fetch_data_from_neo4j(query)

    def calculate(self):
        self.result = self.helper_transform_data(self.data["neo4j_data"][0]["result"])

    def helper_transform_data(self, data):
        mongo_data = {
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": []
        }

        for key, value in data.items():
            start = key.find('Measurement-') + len('Measurement-')
            end = key.find('-GrossFloorArea')
            custom_id = key[start:end]

            kpi_document = {
                "_id": custom_id,
                "v": int(value)
            }
            mongo_data["kpis"].append(kpi_document)
        return mongo_data
