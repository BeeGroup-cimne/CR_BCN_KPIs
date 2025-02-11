import math
import pickle
from datetime import datetime
from itertools import islice

import numpy as np
import pandas as pd
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from kpi_calculations.kpi_base import KPIBase
from concurrent.futures import ThreadPoolExecutor
from shapely.geometry import shape
from shapely.ops import unary_union
import geopandas as gpd
from shapely.geometry import Point, box

class VegetationIndex(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)
    # ["darker", "dark", "medium", "light", "lighter"]

    def unpickle_data(pickled_data):
        return pickle.loads(pickled_data)

    def process_item(key, value, start):
        # Obtención de datos desde HBase
        hbase_data = fetch_data_from_hbase(
            row_start=f"""{(start // 10000000) % 4}~{value}~{start}""",
            row_stop=f"""{(start // 10000000) % 4}~{value}~{start}""",
            table_name="harmonized_online_Ndvi_100_SUM_P1Y_CRBCN"
        )

        # Decodificación y limpieza de datos
        decoded_data = hbase_data[0][1][b'v:pickle'].decode('utf-8')
        cleaned_data = bytes(decoded_data[2:-1], 'utf-8').decode('unicode_escape').encode('latin1')

        # Desempaquetar y convertir a diccionario
        return key, unpickle_data(cleaned_data).to_list()

    def parallel_process(data):
        start = pd.to_datetime("2022/1/1").value // 10 ** 9
        data["result"] = {}
        # nuevo_dict = dict(islice(data["neo4j_data"][0]["cadastral_hash_dict"].items(), 100))
        # Utilizar ThreadPoolExecutor para paralelizar el procesamiento
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(process_item, key, value, start)
                for key, value in data["neo4j_data"][0]["cadastral_hash_dict"].items()
            ]

            # Recuperar resultados de las tareas
            for future in futures:
                try:
                    key, result = future.result()  # Intenta obtener el resultado
                    data["result"][key] = [round(num, 2) for num in result]

                except IndexError:
                    data["result"][key] = []

        return data

    def extract_data(self):
        # Obtener datos de Neo4j
        data = {}
        data["neo4j_data"] = []
        # result = []
        query = f"""MATCH (b:s4bldg__Building)<-[:s4agri__isDeployedAtSpace]-(s4agri__Deployment)-[:ssn__hasDeployment]->(bigg__NdviSystem)-[:s4syst__hasSubSystem]->(bigg__NdviDevice)-[:saref__makesMeasurement]-(m:saref__Measurement)
                WITH split(b.uri, "-")[1] AS cadastralId, m.bigg__hash AS hash
                RETURN apoc.map.fromPairs(collect([cadastralId, hash])) AS cadastral_hash_dict"""

        data["neo4j_data"] = fetch_data_from_neo4j(query)
        data["result"] = {}

        data2 = parallel_process(data)

        result = helper_transform_data(data["result"])
        store_data_in_mongodb("vegetation_index", result)

    def helper_transform_data(data):
        return {
            "calculation_date": datetime.now().date().isoformat(),
            "kpis": data
        }

    # def calculate(self):
    # # Procesar datos geométricos de Neo4j con Geopandas y Shapely
    # geometries = [shape(feature) for feature in self.data["neo4j_data"]]
    #
    # # Crear un GeoDataFrame y calcular área y distancia
    # gdf = gpd.GeoDataFrame(geometry=geometries)
    # total_area = gdf.geometry.area.sum()
    #
    # # Calcular distancias entre centros geométricos
    # distances = []
    # for geom in geometries:
    #     for other_geom in geometries:
    #         if geom != other_geom:
    #             distances.append(geom.centroid.distance(other_geom.centroid))

    # Almacenar el resultado en self.result
    # self.result = {
    #     "total_area": total_area,
    #     "average_distance": sum(distances) / len(distances) if distances else None
    # }
