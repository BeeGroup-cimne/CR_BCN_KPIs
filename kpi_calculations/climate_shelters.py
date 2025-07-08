from datetime import datetime

import numpy as np
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.mongodb_connector import store_data_in_mongodb, store_many_data_in_mongodb
from connectors.neo4j_connector import fetch_data_from_neo4j
from connectors.open_route_service_connector import get_isochrones
from kpi_calculations.kpi_base import KPIBase
import pandas as pd
from social_ES.utils_INE import INEPopulationAnualCensus
from config.config_loader import config
from pyproj import Proj, Transformer
import geopandas as gpd
from pyproj import Proj, transform
from shapely.geometry import Point
from tqdm import tqdm
from pymongo import MongoClient
from config.config_loader import config



class ClimateShelters(KPIBase):
    def __init__(self, kpi_name):
        super().__init__(mongo_collection_name=kpi_name)

    def extract_data(self):

        query = f"""MATCH (n:ns1__ClimateSheltersBuildingSpace)-[:geosp__hasGeometry]->(p:geo__Point)
                    WHERE p.ns1__x_coordinate IS NOT NULL AND p.ns1__y_coordinate IS NOT NULL
                    WITH n.ns1__climateShelterId AS id, [p.ns1__x_coordinate, p.ns1__y_coordinate] AS coords
                    WITH collect([id, coords]) AS pairs
                    RETURN apoc.map.fromPairs(pairs) AS result"""
        self.data["neo4j_data"] = fetch_data_from_neo4j(query)[0]["result"]

        file_path = f"{config['paths']['nextcloud']}/data/hypercadaster_ES/08900.pkl"
        df = pd.read_pickle(file_path, compression="gzip")
        gdf = gpd.GeoDataFrame(df, geometry='br__building_footprint_geometry')
        gdf.set_crs("EPSG:25831")

        self.data["cadaster_data"] = dict(zip(df['building_reference'], df['location']))
        utm_proj = Proj(init='epsg:25831')
        wgs84_proj = Proj(init='epsg:4326')

        a = {
            key: list(transform(utm_proj, wgs84_proj, point.x, point.y))  # Convierte (x, y) -> (long, lat)
            for key, point in data["cadaster_data"].items()
            if point is not None
        }

    def calculate(self):
        locations = []
        ranges = [60, 120, 180, 240, 300, 450, 600, 750, 900, 1050, 1200, 1350, 1500, 1650, 1800]
        utm_proj = Proj(init='epsg:25831')
        wgs84_proj = Proj(init='epsg:4326')
        resultados_globales = {}
        for climate_shelter_id, coordinates_list in tqdm(data["neo4j_data"].items(), desc="Climate Shelters"):

            try:
                isochrones = get_isochrones([utm_to_latlon(coordinates_list[0], coordinates_list[1], 31)], ranges)
                results = classify_points_in_isochrones_with_ids(isochrones, a)
            except Exception as e:
                print(e)

            for building_id, time in results.items():
                if time is None:
                    continue
                if building_id not in resultados_globales:
                    resultados_globales[building_id] = {}
                resultados_globales[building_id][climate_shelter_id] = time


        # for k, v in resultados_globales.items():
        #     store_data_in_mongodb("climate_shelters", helper_transform_data(k, v))

        store_result(helper_transform_data(resultados_globales))

    def classify_points_in_isochrones_with_ids(isochrones, points_dict):
        gdf_iso = gpd.GeoDataFrame.from_features(isochrones["features"])
        gdf_iso = gdf_iso.sort_values(by='value')  # De menor a mayor (más específico primero)

        results = {}

        for point_id, coords in points_dict.items():
            point = Point(coords)  # coords = [lon, lat]
            assigned_interval = None

            for _, row in gdf_iso.iterrows():
                if row.geometry.contains(point):
                    assigned_interval = row['value']
                    break

            results[point_id] = assigned_interval

        return results

    def utm_to_latlon(easting, northing, zone_number, northern_hemisphere=True):
        zone_letter = 'N' if northern_hemisphere else 'S'
        proj_utm = Proj(proj='utm', zone=zone_number, hemisphere=zone_letter)
        transformer = Transformer.from_proj(proj_utm, 'epsg:4326', always_xy=True)
        lon, lat = transformer.transform(easting, northing)
        return [lon, lat]

    def helper_transform_data(data):
        return [
            {
                year: value
            }
            for year, value in data.items()
        ]

    def store_result(data):

        client = MongoClient(config["mongo_db"]["uri"])
        db = client[config["mongo_db"]["db"]]
        collection = db["climate_shelters"]
        collection.insert_many(data)
