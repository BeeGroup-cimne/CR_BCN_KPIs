# Number of torrid nights of the year(Tª higher than 25ºC during the nighttime)
import pickle
from datetime import datetime
from connectors.hbase_connector import fetch_data_from_hbase
from connectors.neo4j_connector import fetch_data_from_neo4j
from connectors.mongodb_connector import store_many_data_in_mongodb
from kpi_calculations.kpi_base import KPIBase
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from config.config_loader import config
import math

class MeteoBase(KPIBase):

    def __init__(self, kpi_name, hour_start=0,hour_end=24):
        self.data = {}
        self.hour_start = hour_start
        self.hour_end = hour_end
        super().__init__(mongo_collection_name=kpi_name)


    def process_item(self, key, value, start,end):
        # Obtención de datos desde HBase
        # (key: 41.32283-2.13449) (value: 3192fb9b44723ed5e4bdd079fb3013d527c2208661799b593362da5940fce21c) (start: 1735689600)
        hbase_data = fetch_data_from_hbase(
            row_start=f"""{(start // 10000000) % 4}~{value}~{start}""",
            row_stop=f"""{(end // 10000000) % 4}~{value}~{end}""",
            table_name=config['weather_downscaling']['table_name']
        )
        # Decodificación y limpieza de datos
        decoded_data = [(int(hbase_data[x][0].decode('utf-8').split('~')[-1]),float(hbase_data[x][1][b'v:airTemperature'].decode('utf-8'))) for x in range(len(hbase_data))]
        # Desempaquetar y convertir a diccionario
        return key, decoded_data # lat_lon (forecastingTime, time, temperature)


    def parallel_process(self, start=None, end=None):
        # Utilizar ThreadPoolExecutor para paralelizar el procesamiento
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.process_item, key, value, start, end)
                for key, value in self.data["neo4j_data"][0]["result"].items()
            ]

            # Recuperar resultados de las tareas
            for future in futures:
                try:
                    key, result = future.result()  # Intenta obtener el resultado
                    self.data["result"][key] = result

                except IndexError:
                    self.data["result"][key] = []
        return self.data['result']


    def extract_data(self):
        """
        Extracts data from Neo4j and HBase, it can be specified the range of the time series to extract.
        """
        start = pd.to_datetime(config['weather_downscaling']['start']).value // 10 ** 9
        end = pd.to_datetime(config['weather_downscaling']['end']).value // 10 ** 9

        query = f"""MATCH (n:s4agri__WeatherStation)-[:s4syst__hasSubSystem]->(d:saref__Device)-[:saref__makesMeasurement]->(m:saref__Measurement) RETURN apoc.map.fromPairs(collect([split(n.uri, "Station-")[1], split(m.uri, "-")[1]])) AS result"""
        self.data["neo4j_data"] = fetch_data_from_neo4j(query)
        self.data["result"] = {}
        self.data["result"] = self.parallel_process(start,end)
       

    def coords2buildings(self, unique_coords, coord_reference_system):
        """
        Converts the coords lat_lon to building level (catastral reference).

        :param unique_coords: array of coordinates [lat_lon]. Eg: ['41.369488_2.162085','41.372276_2.162928','41.346478-2.135073']
        :param coord_reference_system: the code of the Coordinate Reference System (CRS). Eg: "EPSG:4326"
        """
        # Read the buildings
        gdf = gpd.read_file(f"{config['base_path']}/Projects/ClimateReady-BCN/WP3-VulnerabilityMap/CRBCN Map UI/NAZKA/residential_buildings_bcn.geojson")
        gdf = gdf.set_geometry("geometry")
        gdf = gdf.to_crs(epsg=25831)
        gdf.geometry = gdf.geometry.centroid

        # Infer the wether stations
        geometry = [Point(float(coord.split("-")[1]), float(coord.split("-")[0])) for coord in unique_coords]
        gdf_ws = gpd.GeoDataFrame({"geometry": geometry,"weatherId": unique_coords}, crs=coord_reference_system)
        gdf_ws.set_geometry("geometry")
        gdf_ws = gdf_ws.to_crs(epsg=25831)

        # Join buildings and weather stations
        gdf_joined = gpd.sjoin_nearest(gdf, gdf_ws, how="inner", distance_col="distance")
        return gdf_joined


    def _process_night(self,temp_conditions):
        """
        Common method to process the meteo data, filter the hours, group by date,
        and apply the temperature condition.

        :param scenario_column_name: Name of the column to store the result (e.g., 'nitTorrida')
        :param temp_conditions: Lambda function defining the temperature condition
        """
        conversion_gdf = self.coords2buildings(self.data['result'].keys(),"EPSG:4326")
        dfs = []
        for key,values in self.data["result"].items():
            df = pd.DataFrame(values, columns=['time', 'temperature'])
            df['hours'] = pd.to_datetime(df['time'],unit='s').dt.hour

            # Obatin the night data, considered between 19:00pm to 06:59am
            df = df[(df['hours'] >= self.hour_start) | (df['hours'] < self.hour_end)]
            df['time'] = pd.to_datetime(df['time'],unit='s').dt.date
            group_df = df.groupby(['time']).agg({'temperature':'max'}).reset_index()

            # Torrid night higher than 20ºC
            group_df['isAlarm'] = temp_conditions(group_df['temperature'])
            group_df.insert(0, 'weatherId', key)
            dfs.append(group_df.drop(columns=['temperature']))

        weather_df =  pd.concat(dfs,ignore_index=True)
        weather_df = weather_df.merge(conversion_gdf, on = 'weatherId',how='inner')
        
        self.result = self.helper_transform_data(weather_df)


    def helper_transform_data(self, df):
        """
        Helper method to transform the data into the expected format. 
        Displays the number of alarms by refernce for each year.

        :param df: DataFrame with the attrs `reference (str)`, `time (date)`, `isAlarm (bool)`.
        """
        df['year'] = pd.to_datetime(df['time']).dt.year
        # df.to_csv(self.mongo_collection_name+'.csv',index=False)
        result = df.groupby(['reference','year']).agg({'isAlarm':'sum'}).reset_index()
        self.result = result.groupby('year').apply(
            lambda x: {
                'calculation_date': datetime(year=int(x['year'].iloc[0]), month=1, day=1).date().isoformat(),
                'kpis': dict(zip(x['reference'], x['isAlarm'].astype(int))) 
            }
        ).reset_index(drop=True)[0]
        return self.result


    def calculate(self):
        """Override this method in child class"""
        pass


