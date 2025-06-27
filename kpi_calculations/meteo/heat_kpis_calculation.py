import os

from connectors.mongodb_connector import store_many_data_in_mongodb
from kpi_calculations.meteo.heat_kpis import interpolate_heat_index
from kpi_calculations.meteo.meteo_base import MeteoBase
from config.config_loader import config
import pandas as pd

import geopandas as gpd
from shapely.geometry import Point
from tqdm import tqdm
from config.config_loader import config
from datetime import datetime

import os
from collections import defaultdict
import os
import polars as pl

from kpi_calculations.utils import plot_static_features_maps


class HeatKpisCalculation(MeteoBase):
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

        nextcloud_root_dir = os.path.expanduser('~/Nextcloud/Beegroup/data/CR_BCN_meteo')
        predictions_dir = f'{nextcloud_root_dir}/Historical_ERA5Land/Predictions'
        plots_dir = f'{nextcloud_root_dir}/Plots_validation'
        os.makedirs(plots_dir, exist_ok=True)

        files = os.listdir(predictions_dir)
        files_by_ym = sorted(
            [f for f in files if f.endswith(".parquet")],
            key=lambda x: int(x.replace("prediction_", "").replace(".parquet", ""))
        )

        df = None

        for file in files_by_ym:
            print(file)
            df_ = pl.read_parquet(f"{predictions_dir}/{file}")

            tdb = df_["airTemperature"].to_list()
            rh = [r * 100 for r in df_["relativeHumidity"].to_list()]

            hi_values = interpolate_heat_index(tdb, rh)

            df_ = df_.with_columns(
                pl.Series("heatIndex", hi_values)
            )

            df_ = df_.with_columns([
                pl.col("time").dt.hour().alias("hour"),
                pl.col("time").dt.date().alias("date")
            ])

            # Define masks for night (0–8, 21–23) and daylight (9–20)
            night_mask = (pl.col("hour") <= 8) | (pl.col("hour") >= 21)
            day_mask = (pl.col("hour") >= 9) & (pl.col("hour") <= 20)

            # Nighttime stats per day and location
            night_stats = (
                df_.filter(night_mask)
                .group_by(["date", "weatherStation"])
                .agg([
                    pl.col("heatIndex").min().alias("night_temp_min"),
                    pl.col("heatIndex").mean().alias("night_temp_mean"),
                    pl.col("heatIndex").max().alias("night_temp_max")
                ])
            )

            # Daylight stats per day and location
            day_stats = (
                df_.filter(day_mask)
                .group_by(["date", "weatherStation"])
                .agg([
                    pl.col("heatIndex").min().alias("day_temp_min"),
                    pl.col("heatIndex").mean().alias("day_temp_mean"),
                    pl.col("heatIndex").max().alias("day_temp_max")
                ])
            )

            # Merge both on date and locationName
            daily_temp_stats = night_stats.join(day_stats, on=["date", "weatherStation"], how="full").sort(
                ["weatherStation", "date"])
            daily_temp_stats = daily_temp_stats.with_columns(
                pl.col("date").alias("time")
            )

            if df is None:
                df = daily_temp_stats
            else:
                df = pl.concat([df, daily_temp_stats])

        # Drop duplicate/unnecessary columns
        df_cleaned = df.drop(["date", "date_right", "weatherStation_right"])

        # Define the threshold
        threshold = 33

        # Apply transformation
        result = (
            df_cleaned
            .sort("time")
            .group_by("weatherStation")
            .agg([
                pl.col("time"),
                pl.col("day_temp_max").rolling_min(window_size=3, min_periods=1).alias("rolling_min_day_temp_max"),
                pl.col("day_temp_max"),
                pl.col("day_temp_mean")
            ])
            .explode(["time", "rolling_min_day_temp_max", "day_temp_max",
                      "day_temp_mean"])  # to flatten the nested structure
            .with_columns([
                (pl.col("rolling_min_day_temp_max") > threshold).alias("heatWave"),
                (pl.col("day_temp_max") < 27).alias("safeMaxTemperature"),
                ((pl.col("day_temp_max") >= 27) & (pl.col("day_temp_max") < 33)).alias("cautionMaxTemperature"),
                ((pl.col("day_temp_max") >= 33) & (pl.col("day_temp_max") < 41)).alias("extremeCautionMaxTemperature"),
                ((pl.col("day_temp_max") >= 41) & (pl.col("day_temp_max") < 52)).alias("hazardousMaxTemperature"),
                ((pl.col("day_temp_max") >= 52) & (pl.col("day_temp_max") < 92)).alias(
                    "extremeHazardousMaxTemperature"),
                (pl.col("day_temp_max") >= 92).alias("beyondHumanLimitMaxTemperature"),
                (pl.col("day_temp_mean") < 27).alias("safeAverageTemperature"),
                ((pl.col("day_temp_mean") >= 27) & (pl.col("day_temp_mean") < 33)).alias("cautionAverageTemperature"),
                ((pl.col("day_temp_mean") >= 33) & (pl.col("day_temp_mean") < 41)).alias(
                    "extremeCautionAverageTemperature"),
                ((pl.col("day_temp_mean") >= 41) & (pl.col("day_temp_mean") < 52)).alias("hazardousAverageTemperature"),
                ((pl.col("day_temp_mean") >= 52) & (pl.col("day_temp_mean") < 92)).alias("extremeHazardousAverageTemperature"),
                (pl.col("day_temp_mean") >= 92).alias("beyondHumanLimitAverageTemperature")
            ])
        )

        result_by_year = (
            result
            .with_columns([
                pl.col("time").dt.year().alias("year")
            ])
            .group_by(["weatherStation", "year"])
            .agg([
                pl.col("heatWave").sum(),
                pl.col("safeMaxTemperature").sum(),
                pl.col("cautionMaxTemperature").sum(),
                pl.col("extremeCautionMaxTemperature").sum(),
                pl.col("hazardousMaxTemperature").sum(),
                pl.col("extremeHazardousMaxTemperature").sum(),
                pl.col("beyondHumanLimitMaxTemperature").sum(),
                pl.col("safeAverageTemperature").sum(),
                pl.col("cautionAverageTemperature").sum(),
                pl.col("extremeCautionAverageTemperature").sum(),
                pl.col("hazardousAverageTemperature").sum(),
                pl.col("extremeHazardousAverageTemperature").sum(),
                pl.col("beyondHumanLimitAverageTemperature").sum()
            ])
            .sort(["weatherStation", "year"])
        )

        conversion_gdf = coords2buildings(result_by_year["weatherStation"].unique().to_list(), "EPSG:4326")
        conversion_gdf.drop(columns=["geometry", "centroid", "fid", "index_right"], inplace=True)

        conversion_gdf = pl.from_pandas(conversion_gdf)
        result = result_by_year.join(conversion_gdf, left_on="weatherStation", right_on="weatherId", how="inner")

        store_many_data_in_mongodb("heat_waves", heat_waves_helper_transform_data(result, "heatWave"))
        store_many_data_in_mongodb("heat_max_temperature_kpis", helper_transform_data(result, ["safeMaxTemperature",
                                                                                               "cautionMaxTemperature",
                                                                                               "extremeCautionMaxTemperature",
                                                                                               "hazardousMaxTemperature",
                                                                                               "extremeHazardousMaxTemperature",
                                                                                               "beyondHumanLimitMaxTemperature"]))
        store_many_data_in_mongodb("heat_avg_temperature_kpis", helper_transform_data(result, ["safeAverageTemperature",
                                                                                               "cautionAverageTemperature",
                                                                                               "extremeCautionAverageTemperature",
                                                                                               "hazardousAverageTemperature",
                                                                                               "extremeHazardousAverageTemperature",
                                                                                               "beyondHumanLimitAverageTemperature"]))

        for y in result_by_year["year"].unique():
            result_one_year = result_by_year.filter(pl.col("year") == y).drop(["year"]).to_pandas().set_index(
                "weatherStation")
            plot_static_features_maps(result_one_year, crs="EPSG:4326", cmap="viridis", markersize=1,
                                      output_pdf=f"{plots_dir}/heat_indexes_{y}.pdf")

    def heat_waves_helper_transform_data(result, kpi_columns: list[str]):
        """
        Helper method to transform the data into the expected format.
        Displays the number of alarms by reference for each year.

        :param df: DataFrame with the attrs `reference (str)`, `time (date)`, `isAlarm (bool)`.
        """

        # Convertir a diccionario con la estructura deseada
        return [
            {
                "calculation_date": datetime(year=int(year[0]), month=1, day=1).date().isoformat(),
                "kpis": {
                    row["reference"]: row[kpi_columns] for row in
                    group.iter_rows(named=True)}
            }
            for year, group in result.group_by("year")
        ]

    def helper_transform_data(result, kpi_columns: list[str]):
        """
        Helper method to transform the data into the expected format.
        Displays the number of alarms by reference for each year.

        :param df: DataFrame with the attrs `reference (str)`, `time (date)`, `isAlarm (bool)`.
        """

        # Convertir a diccionario con la estructura deseada
        return [
            {
                "calculation_date": datetime(year=int(year[0]), month=1, day=1).date().isoformat(),
                "kpis": {
                    row["reference"]: [row[kpi] for kpi in kpi_columns] for row in
                    group.iter_rows(named=True)}
            }
            for year, group in result.group_by("year")
        ]



