import json
from datetime import datetime
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
import geopandas as gpd
import pandas as pd

class WindowToWallRatio(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):
        epc_df = pd.read_parquet("data/epc_predictor_results.parquet")
        self.data["neo4j_data"] = dict(zip(epc_df['building_reference'], round(epc_df['WindowToWallRatio'], 2)))

    def calculate(self):
        self.result = self.helper_transform_data(self.data["neo4j_data"])

    def helper_transform_data(self, data):
        return {
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": data
        }