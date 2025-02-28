from kpi_calculations.meteo.meteo_base import MeteoBase
from config.config_loader import config

class TropicalNights(MeteoBase):
    # Default: from [19,7) hours, that is, from 7pm to 6:59am
    def __init__(self, kpi_name, hour_start=19, hour_end=7):
        super().__init__(kpi_name, hour_start, hour_end)

    def calculate(self):
        temp_conditions = lambda temp: (temp > config['weather_downscaling']['temperature']['tropical_night']['min']) & (temp <= config['weather_downscaling']['temperature']['tropical_night']['max'])
        self._process_night(temp_conditions=temp_conditions)    

# gross_floor_area = TropicalNights(kpi_name="tropical_night")
# gross_floor_area.run()