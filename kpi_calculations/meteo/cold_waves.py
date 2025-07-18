from kpi_calculations.meteo.meteo_base import MeteoBase
from config.config_loader import config
import pandas as pd


class ColdWaves(MeteoBase):
    def __init__(self, kpi_name):
        super().__init__(kpi_name)

    def calculate(self):
        # shows alarm if three consecutive days have a temperature lower than 0ºC
        conversion_gdf = self.coords2buildings(self.data['result'].keys(), "EPSG:4326")
        dfs = []
        for key, values in self.data["result"].items():
            df = pd.DataFrame(values, columns=['time', 'temperature'])
            df['time'] = pd.to_datetime(df['time'], unit='s').dt.date
            group_df = df.groupby(['time']).agg({'temperature': 'min'}).reset_index()  # min temperature per day
            group_df['isAlarm'] = group_df['temperature'].rolling(window=3, min_periods=1).max() < \
                                  config['weather_downscaling']['temperature']['cold_wave']
            group_df.insert(0, 'weatherId', key)
            dfs.append(group_df)

        weather_df = pd.concat(dfs, ignore_index=True)
        weather_df = weather_df.merge(conversion_gdf, on='weatherId', how='inner')
        self.result = self.helper_transform_data(weather_df)
