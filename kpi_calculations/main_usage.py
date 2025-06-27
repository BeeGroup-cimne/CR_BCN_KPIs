from datetime import datetime
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd

class MainUsage(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        file_path = "/Users/jose/Nextcloud/Beegroup/data/hypercadaster_ES/08900.pkl"
        hyper_df = pd.read_pickle(file_path, compression="gzip")
        self.data["neo4j_data"] = dict(zip(hyper_df['building_reference'], hyper_df['br__area_with_communals']))

        # query = f"""MATCH (b:s4bldg__Building) RETURN apoc.map.fromPairs(collect([split(b.uri, "-")[1], b.bigg__mainUse])) AS result"""
        # self.data["neo4j_data"] = fetch_data_from_neo4j(query)

    def calculate(self):
        self.result = self.helper_transform_data(self.data["neo4j_data"])

    def create_one_hot_vector(self, key, value):

        # main_usage_dict = {'1_residential': 0, '2_agriculture': 1, '3_industrial': 2, '4_1_office': 3, '4_2_retail': 4,
        #                    '4_3_publicServices': 5, None: 6}
        main_usage_dict = {'Residential': 0, 'Industrial': 1, 'Urbanization and landscaping works, undeveloped land': 2,
                           'Offices': 3, 'Sports facilities': 4, 'Singular building': 5, 'Entertainment venues': 6,
                           'Commercial': 7, 'Warehouse - Parking': 8, 'Leisure and Hospitality': 9, 'Cultural': 10,
                           'Healthcare and Charity': 11, 'Religious': 12}
        one_hot_vector = [0] * len(main_usage_dict)
        for key_2, value_2 in value.items():

            index = main_usage_dict.get(key_2)
            one_hot_vector[index] = value_2
        return one_hot_vector
    def helper_transform_data(self, data):

        mongo_data = {
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": {}
        }

        for key, value in data.items():
            if isinstance(value, dict):
                mongo_data["kpis"][key] = self.create_one_hot_vector(key, value)

        return mongo_data