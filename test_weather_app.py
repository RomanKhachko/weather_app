import unittest

from weather_app import WeatherDataRepository


class TestWeatherDataRepository(unittest.IsolatedAsyncioTestCase):
    CITY = 'Lake Saint Louis'

    async def asyncSetUp(self) -> None:
        self.repo = WeatherDataRepository()

    async def test_search_by_city_name_should_return_weather_details_for_city(self):
        weather_details = await self.repo.get_by_city_name(self.CITY)
        self.assertIsNotNone(weather_details)

    async def test_search_by_city_and_state_should_return_weather_details_for_city(self):
        weather_details = await self.repo.get_by_city_name(self.CITY, "MO")
        self.verify_weather_details(weather_details)

    async def test_search_by_not_valid_city_should_return_not_found_message(self):
        weather_details = await self.repo.get_by_city_name(f'{self.CITY}1')
        self.assertEqual(weather_details.message, "city not found")
        self.assertEqual(weather_details.cod, 404)

    async def test_search_by_zip_should_return_weather_details_for_citye(self):
        weather_details = await self.repo.get_by_zip(63367)
        self.verify_weather_details(weather_details)

    async def test_search_by_not_valid_zip_should_return_not_found_message(self):
        weather_details = await self.repo.get_by_zip(49000)
        self.assertEqual(weather_details.message, "city not found")

    async def test_search_by_coordinates_should_return_weather_details_for_citye(self):
        weather_details = await self.repo.get_by_coordinates(38.79755, -90.785683)
        self.verify_weather_details(weather_details)

    def verify_weather_details(self, weather_details):
        self.assertIsNotNone(weather_details)
        self.assertEqual(weather_details.city, self.CITY)


if __name__ == '__main__':
    unittest.main()
