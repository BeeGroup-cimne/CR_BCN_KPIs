import math
from datetime import datetime

from config.config_loader import config
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import pickle
from datetime import datetime
import pandas as pd
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
from concurrent.futures import ThreadPoolExecutor


class ClimateSheltersFilterInfo(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data_endesa(self):
        query = f"""MATCH (b:s4bldg__Building)<-[:saref__isMeasurementOf]-(m:saref__Measurement)<-[:saref__makesMeasurement]-(d:saref__Device) 
                        WHERE m.uri ENDS WITH "Electricity"
                        RETURN SPLIT(b.uri, "Building-")[1] AS reference, SPLIT(d.uri, "Device-")[1] AS hash"""
        data["neo4j_data"] = fetch_data_from_neo4j(query)
        return {record["reference"]: record["hash"] for record in data["neo4j_data"]}

        result = helper_transform_data(b, datetime(2022, 1, 1).date().isoformat())
        store_data_in_mongodb("annual_electricity_consumption", result)

    def extract_data(self):

        df_consumptions = pd.read_excel('data/Dades vulnerabilitat energètica habitatges_CIMNE.xlsx', engine='openpyxl')
        file_path = f"{config['paths']['nextcloud']}/data/hypercadaster_ES/08900.pkl"
        df_hyper = pd.read_pickle(file_path, compression="gzip")
        main_usage_list = ["Residential", "Industrial", "Offices", "Commercial", "Sports facilities",
                           "Entertainment venues",
                           "Leisure and Hospitality", "Healthcare and Charity", "Cultural", "Religious",
                           "Singular building",
                           "Agricultural warehouse", "Agricultural industrial", "Agricultural"]

        data = {}
        data["neo4j_data"] = {}
        data["neo4j_data"]["building_spaces"] = dict(zip(
            df_hyper["building_reference"],
            df_hyper["br__building_spaces"].map(
                lambda d: sum(d.get(k, 0) for k in main_usage_list) if isinstance(d, dict) else 0)
        ))
        data["neo4j_data"]["area_by_usage"] = dict(zip(
            df_hyper["building_reference"],
            df_hyper["br__area_without_communals"].map(
                lambda d: sum(d.get(k, 0) for k in main_usage_list) if isinstance(d, dict) else 0)
        ))

        df_consumptions["calculated"] = ((df_consumptions["FE_€_TOTAL"] / 0.177) * df_consumptions["REFCAT"].map(
                                        lambda x: data["neo4j_data"]["building_spaces"].get(x, 0))
                                        ) / df_consumptions["REFCAT"].map(lambda x: data["neo4j_data"]["area_by_usage"].get(x, 1))

        df_consumptions2 = df_consumptions.dropna(subset=["calculated"])
        df_consumptions2.drop(df_consumptions[df_consumptions["calculated"] == 0].index, inplace=True)
        data["result"] = dict(
            zip(df_consumptions2['REFCAT'], df_consumptions2["calculated"]))

        b = sanitize_dict(data["result"])

        result = helper_transform_data(b, datetime(2017, 1, 1).date().isoformat())
        store_data_in_mongodb("annual_electricity_consumption", result)

        # df_consumptions = df_consumptions["FE_€_TOTAL"]*0,177
        # FE_€_TOTAL*0,177 * numero de viviendas de hyper
        # luego dividir por la suma de estos usos.
        # "V": "Residential",
        #     "I": "Industrial",
        #     "O": "Offices",
        #     "C": "Commercial",
        #     "K": "Sports facilities",
        #     "T": "Entertainment venues",
        #     "G": "Leisure and Hospitality",
        #     "Y": "Healthcare and Charity",
        #     "E": "Cultural",
        #     "R": "Religious",
        #     "P": "Singular building",
        #     "B": "Agricultural warehouse",
        #     "J": "Agricultural industrial",
        #     "Z": "Agricultural"

        data = {}
        hash_dict = get_reference_hash()
        file_path = f"{config['paths']['nextcloud']}/data/hypercadaster_ES/08900.pkl"
        df = pd.read_pickle(file_path, compression="gzip")
        self.data["building_area"] = dict(
            zip(df['building_reference'], df["br__above_ground_built_area"] + df["br__below_ground_built_area"]))

        data2 = parallel_process(hash_dict)
        b = sanitize_dict(data["result"])
        result = helper_transform_data(b)
        start = pd.to_datetime("2017/1/1").value // 10 ** 9
        store_data_in_mongodb("annual_electricity_consumption", result)

    def calculate(self):
        self.result = self.helper_transform_data(self.data["neo4j_data"][0]["result"])

    def unpickle_data(pickled_data):
        return pickle.loads(pickled_data)

    def process_item(key, value, start):
        # Obtención de datos desde HBase
        hbase_data = fetch_data_from_hbase(
            row_start=f"""{(start // 10000000) % 4}~{value}~{start}""",
            row_stop=f"""{(start // 10000000) % 4}~{value}~{start}""",
            table_name="harmonized_online_EnergyConsumptionGridElectricity_100_SUM_P1Y_CRBCN"
        )

        # Decodificación y limpieza de datos
        decoded_data = float(hbase_data[0][1][b'v:electricityValue'].decode('utf-8'))

        # Desempaquetar y convertir a diccionario
        return key, decoded_data

    def sanitize_dict(data):
        for key, value in data.items():
            if isinstance(value, float):
                if math.isnan(value) or math.isinf(value):
                    data[key] = None
                else:
                    data[key] = round(value, 2)
        return data

    def parallel_process(hash_dict):
        start = pd.to_datetime("2017/1/1").value // 10 ** 9
        data["result"] = {}
        # Utilizar ThreadPoolExecutor para paralelizar el procesamiento
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(process_item, key, value, start)
                for key, value in hash_dict.items()
            ]

            for future in futures:
                try:
                    key, result = future.result()
                    print(key, result)
                    data["result"][key] = round(result / data["building_area"][key], 2)
                    # print(data["result"][key])

                except (IndexError, ZeroDivisionError, KeyError):
                    data["result"][key] = None
        return data

    def helper_transform_data(data, date):
        return {
            "calculation_date": date if date else datetime.now().date().isoformat(),
            "kpis": data
        }
