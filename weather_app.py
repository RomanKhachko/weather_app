import logging
from logging.handlers import RotatingFileHandler

import justpy


def config_logger():
    rotating_file_handler = RotatingFileHandler(filename='weather_app.log', backupCount=2, maxBytes=2 * 10 ** 6)
    handlers = [logging.StreamHandler(), rotating_file_handler]
    logging.basicConfig(format='%(asctime)s %(message)s', encoding='utf-8', level=logging.INFO, handlers=handlers)


class WeatherDataRepository:

    def __init__(self, client=justpy) -> None:
        '''

        :param client: by default we'll be using JustPy http client assuming that weather API is always available. However,
        in more real production scenario, client supporting Circuit Breaker pattern might be preferable.
        '''
        self.client = client

    async def get_by_city_name(self, city_name, state_code=None, country_code="US"):
        # if state is specified, country should be specified too
        # todo (future improvement): to get unambiguous results and avoid confusion like O'Fallon, MO vs O'Fallon, IL, it's better to get city id
        # from 'city.list.json' and use this ID to perform search or at least use returned id to show the exact city to the user
        pass

    async def get_by_zip(self, zip, country_code="US"):
        pass

    async def get_by_coordinates(self, lat, lon):
        pass


if __name__ == '__main__':
    config_logger()
    logging.info('Staring application')
