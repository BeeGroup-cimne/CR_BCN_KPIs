from connectors.mongodb_connector import store_many_data_in_mongodb
from kpi_calculations.meteo.meteo_base import MeteoBase
from config.config_loader import config
import pandas as pd

import polars as pl
import os
import geopandas as gpd
from shapely.geometry import Point
from tqdm import tqdm
from config.config_loader import config
from datetime import datetime

class HeatingDegreeDays(MeteoBase):
    def __init__(self, kpi_name):
        super().__init__(kpi_name)

    def coords2buildings(unique_coords, coord_reference_system):
        """
        Converts the coords lat_lon to building level (cadastral reference).

        :param unique_coords: array of coordinates [lat_lon]. Eg: ['41.369488_2.162085','41.372276_2.162928','41.346478_2.135073']
        :param coord_reference_system: the code of the Coordinate Reference System (CRS). Eg: "EPSG:4326"
        :return: GeoDataFrame with matched buildings and distances
        """

        # Leer edificios en formato GeoDataFrame
        gdf = gpd.read_file(
            f"{config['paths']['nextcloud']}/Projects/ClimateReady-BCN/WP3-VulnerabilityMap/CRBCN Map UI/NAZKA/residential_buildings_bcn.geojson"
        ).set_geometry("geometry").to_crs(epsg=25831)

        gdf["centroid"] = gdf.geometry.centroid

        # Convertir coordenadas de estaciones meteorológicas en geometrías
        geometry = [Point(float(coord.split("_")[1]), float(coord.split("_")[0])) for coord in
                    tqdm(unique_coords, desc="Processing Coordinates")]
        gdf_ws = gpd.GeoDataFrame({"geometry": geometry, "weatherId": unique_coords},
                                  crs=coord_reference_system).to_crs(epsg=25831)

        gdf_joined = gpd.sjoin_nearest(gdf, gdf_ws, how="inner", distance_col="distance")

        return gdf_joined

    def calculate(self):
        print("calculate")

        folder = "/Users/jose/Nextcloud/Beegroup/data/CR_BCN_meteo/Historical_ERA5Land/Predictions"
        years = sorted({f[11:15] for f in os.listdir(folder)
                        if f.startswith("prediction_") and f.endswith(".parquet")})
        for year in years:

            prediction_df = pl.concat([
                pl.read_parquet(os.path.join(folder, f))
                for f in sorted(os.listdir(folder))
                if f.startswith("prediction_") and f.endswith(".parquet") and f[11:15] == year
            ])

            conversion_gdf = coords2buildings(prediction_df["weatherStation"].unique().to_list(), "EPSG:4326")

            dfs = []
            for station in tqdm(prediction_df['weatherStation'].unique(), desc="Processing Stations"):

                station_df = prediction_df.filter(pl.col("weatherStation") == station)
                # station_df = station_df.drop("temperature")

                # Realizamos el mismo proceso para cada estación
                # station_group_df = station_df.group_by("time").agg([
                #     pl.col("airTemperature").max().alias("temperature")
                # ])
                station_group_df = station_df.with_columns(
                    pl.col("time").cast(pl.Date).alias("date")
                ).group_by("date").agg([
                    pl.col("airTemperature").mean().alias("temperature"),
                    pl.col("weatherStation").first().alias("weatherId")
                ]).sort("date")

                station_group_df = station_group_df.with_columns(
                    pl.when(pl.lit(config['weather_downscaling']['temperature']['degree_days']['heating']) - pl.col("temperature") > 0)
                    .then(pl.lit(config['weather_downscaling']['temperature']['degree_days']['heating']) - pl.col("temperature"))
                    .otherwise(0)
                    .alias("HDD")
                )

                # Agregar a la lista de DataFrames
                dfs.append(station_group_df)

            # Concatenar los DataFrames de todas las estaciones
            weather_df = pl.concat(dfs)

            # weather_df = weather_df.merge(conversion_gdf, on='weatherId', how='inner')
            conversion_gdf.drop(columns=["geometry", "centroid", "fid", "index_right"], inplace=True)

            conversion_gdf = pl.from_pandas(conversion_gdf)
            weather_df = weather_df.drop("temperature")

            weather_df = weather_df.with_columns(pl.col("date").dt.year().alias("year"))

            # Agrupar por 'reference' y 'year' para calcular isAlarm_sum
            result = weather_df.group_by(['weatherId', 'year']).agg(
                pl.sum('HDD').alias('HDD_sum')
            )
            # weather_df = weather_df.filter(pl.col("isAlarm") == True)

            # test_df = weather_df.filter(pl.col("weatherId") == "41.440865_2.19258")
            # test_df = test_df.filter(pl.col("isAlarm") == True)
            # test_df = test_df.join(conversion_gdf, on="weatherId", how="inner")

            result = result.join(conversion_gdf, on="weatherId", how="inner")
            result = helper_transform_data(result)
            store_many_data_in_mongodb("heating_degree_days", result)


def helper_transform_data(result):
    """
    Helper method to transform the data into the expected format.
    Displays the number of alarms by reference for each year.

    :param df: DataFrame with the attrs `reference (str)`, `time (date)`, `isAlarm (bool)`.
    """

    result = result.drop("weatherId")

    return [
        {
            "calculation_date": datetime(year=int(year[0]), month=1, day=1).date().isoformat(),
            "kpis": {row["reference"]: round(row["HDD_sum"], 2) for row in group.iter_rows(named=True)}
        }
        for year, group in result.group_by("year")
    ]
