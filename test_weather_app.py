import unittest
from pathlib import Path
from unittest.mock import AsyncMock

from dotenv import load_dotenv

from weather_app import WeatherDataRepository

env_path = Path('.') / 'weather_app.env'
load_dotenv(dotenv_path=env_path)


class TestWeatherDataRepository(unittest.IsolatedAsyncioTestCase):
    CITY = 'Lake Saint Louis'

    async def asyncSetUp(self) -> None:
        self.repo = WeatherDataRepository()

    async def test_search_by_city_name_should_return_weather_details_for_city(self):
        weather_response = await self.repo.get_by_city_name(self.CITY)
        self.verify_weather_details(weather_response)

    async def test_search_by_city_and_state_should_return_weather_details_for_city(self):
        weather_response = await self.repo.get_by_city_name(self.CITY, "MO")
        self.verify_weather_details(weather_response)

    async def test_search_by_not_valid_city_should_return_not_found_message(self):
        weather_response = await self.repo.get_by_city_name(f'{self.CITY}1')
        await self.verify_error(weather_response, "city not found")

    async def test_search_by_zip_should_return_weather_details_for_city(self):
        weather_response = await self.repo.get_by_zip(63367)
        self.verify_weather_details(weather_response)

    async def test_search_by_coordinates_should_return_weather_details_for_city(self):
        weather_response = await self.repo.get_by_coordinates(38.79755, -90.785683)
        self.verify_weather_details(weather_response)

    async def test_error_object_should_be_filled_on_unexpected_payload(self):
        client = AsyncMock()
        client.get.return_value = "EMPTY"
        await self.verify_internal_error(client)

    async def test_exception_during_request_should_produce_error_object_with_internal_error_msg(self):
        '''This is a proper unit test with mocking. Normally, I would cover repository class by unit tests (to exclude dependency on a real data storage (or underlying API).
        However, since in current app they overlap with integration tests, for the sake of speed and simplicity I won't add them.
        Therefore, I covered a few conditions by proper unit tests, since that is hard to cover them using real underlying backend.'''
        client = AsyncMock()
        client.get.side_effect = Exception()
        await self.verify_internal_error(client)

    async def verify_internal_error(self, client):
        self.repo = WeatherDataRepository(client)
        result = await self.repo.get_by_city_name(self.CITY)
        self.verify_error(result, "Internal error")

    async def verify_error(self, weather_response, expected_msg):
        self.assertEqual(weather_response.error, expected_msg)
        self.assertIsNone(weather_response.city_weather)

    def verify_weather_details(self, weather_response):
        self.assertIsNotNone(weather_response.city_weather)
        self.assertIsNone(weather_response.error)
        self.assertEqual(weather_response.city_weather.city, self.CITY)


if __name__ == '__main__':
    unittest.main()
