from datetime import datetime
import math
import numpy as np

from config.config_loader import config
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import pandas as pd


class ResidentialCommonAreaRatio(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        file_path = f"{config['paths']['nextcloud']}/data/hypercadaster_ES/08900.pkl"
        hyper_df = pd.read_pickle(file_path, compression="gzip")
        self.data["neo4j_data"] = dict(zip(hyper_df["building_reference"], hyper_df["br__area_with_communals"]))

    def calculate(self):

        # for ref_cat, area_by_type in data["neo4j_data"].items():
        #     if isinstance(area_by_type, dict) and ref_cat == "8008627DF2880G":
        #         break
        #     try:
        #         for type in area_by_type:
        #             data["neo4j_data"][ref_cat]
        #             data["neo4j_data"][ref_cat][type] = area_by_type.get(type, 0) / sum(area_by_type.values()) if area_by_type else None
        #     except:
        #         self.data["neo4j_data"][ref_cat] = np.nan

        # dataa = sanitize_dict(data["neo4j_data"])
        self.result = self.helper_transform_data(self.sanitize_dict(self.data["neo4j_data"]))

    def create_one_hot_vector(self, key, value):

        main_usage_dict = {'Residential': 0, 'Industrial': 1, 'Urbanization and landscaping works, undeveloped land': 2,
                           'Offices': 3, 'Sports facilities': 4, 'Singular building': 5, 'Entertainment venues': 6,
                           'Commercial': 7, 'Warehouse - Parking': 8, 'Leisure and Hospitality': 9, 'Cultural': 10,
                           'Healthcare and Charity': 11, 'Religious': 12}
        one_hot_vector = [0] * len(main_usage_dict)

        total = sum(value.values())
        if total != 0:
            for key_2, value_2 in value.items():

                index = main_usage_dict.get(key_2)

                one_hot_vector[index] = round((value_2/total)*100, 2)
            return one_hot_vector
        else:
            return None

    def helper_transform_data(self, data):

        mongo_data = {
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": {}
        }

        for key, value in data.items():
            if isinstance(value, dict):
                mongo_data["kpis"][key] = self.create_one_hot_vector(key, value)

        return mongo_data

    def sanitize_dict(self, data):
        for key, value in data.items():
            if isinstance(value, float):
                if math.isnan(value) or math.isinf(value):
                    data[key] = None
                else:
                    data[key] = round(value, 2)
        return data