import logging
import os
from collections import namedtuple
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from urllib.parse import urlencode

import justpy


def config_logger():
    rotating_file_handler = RotatingFileHandler(filename='weather_app.log', backupCount=2, maxBytes=2 * 10 ** 6)
    handlers = [logging.StreamHandler(), rotating_file_handler]
    logging.basicConfig(format='%(asctime)s %(message)s', encoding='utf-8', level=logging.INFO, handlers=handlers)


WeatherDataResponse = namedtuple('WeatherDataResponse', ['city_weather', 'error'])


class WeatherDataRepository:

    def __init__(self, client=justpy) -> None:
        '''

        :param client: by default we'll be using JustPy http client assuming that weather API is always available. However,
        in more real production scenario, client supporting Circuit Breaker pattern might be preferable.
        '''
        self.client = client

    async def get_by_city_name(self, city_name, state_code=None, country_code="US"):
        return await self._get_weather_info(urlencode({'q': f'{city_name},{state_code},{country_code}'}))

    async def get_by_zip(self, zip, country_code="US"):
        return await self._get_weather_info(urlencode({'zip': f'{zip},{country_code}'}))

    async def get_by_coordinates(self, lat, lon):
        return await self._get_weather_info(urlencode({'lat': lat, 'lon': lon}))

    async def _get_weather_info(self, query):
        city_weather = None
        error = None
        try:
            appid = os.getenv('APP_ID')
            result = await self.client.get(f'http://api.openweathermap.org/data/2.5/weather?{query}&appid={appid}')
            if result['cod'] == 200:
                city_weather = CityWeather(result['name'], result['sys']['country'], result['main'], result['coord'],
                                           result['weather'])
            else:
                error = result['message']
        except Exception:
            error = "Internal error"
            logging.exception(error)
        return WeatherDataResponse(city_weather, error)


@dataclass
class CityWeather:
    city: str
    country_code: str
    weatherMetrics: dict
    coord: dict
    weather: dict


if __name__ == '__main__':
    config_logger()
logging.info('Staring application')
