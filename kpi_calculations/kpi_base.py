from connectors.neo4j_connector import fetch_data_from_neo4j
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb

class KPIBase:
    def __init__(self, mongo_collection_name):
        self.mongo_collection_name = mongo_collection_name
        self.data = {}
        self.result = None

    def extract_data(self):
        """Method to extract data from multiple databases, overwritten on each KPI."""
        raise NotImplementedError

    def calculate(self):
        """Method for calculating the KPI, including geometric calculations if necessary."""
        raise NotImplementedError

    def store_result(self):
        """Method to store the result in MongoDB."""
        store_data_in_mongodb(self.mongo_collection_name,  self.result)

    def get_mongo_collection_name(self):
        return self.mongo_collection_name

    def run(self):
        """Execute the complete flow for the KPI: extraction, calculation and storage."""
        self.extract_data()
        self.calculate()
        self.store_result()
