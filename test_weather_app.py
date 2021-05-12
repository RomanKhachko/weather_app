import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from dotenv import load_dotenv
from justpy import WebPage

from weather_app import WeatherDataRepository, home_page, back_to_home_page, render_result_block, CityWeather, \
    add_search_input, SearchParams, extract_parameters, get_weather_info

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


class TestWeatherUiComponents(unittest.IsolatedAsyncioTestCase):
    '''Verifying the most critical parts to fail fast. Most of these verifications will be covered by couple of E2E tests
        implementing search flow'''

    async def test_home_page_should_be_rendered(self):
        hp = await home_page()
        self.assertEqual('Please select search criteria:', hp.components[0].components[0].text)

    @patch('weather_app.render_search_page')
    async def test_back_to_home_page_should_remove_all_elements_and_render_home_page(self, render_sp_mock):
        msg = Mock()
        msg.page = Mock(WebPage)
        await back_to_home_page(None, msg)
        msg.page.delete_components.assert_called_once()
        render_sp_mock.assert_called_once_with(msg.page)

    async def test_render_result_should_contain_proper_image(self):
        wp = WebPage()
        city_weather = CityWeather(*[None] * 5)
        city_weather.weather = {'icon': '10n'}
        city_weather.weatherMetrics = {"temp": None, "feels_like": None, "humidity": None}
        await render_result_block(wp, city_weather)
        self.assertEqual(3, len(wp.components))
        img_component = next(filter(lambda comp: comp.class_name == "Img", wp.components))
        self.assertTrue('openweathermap.org/img/' in img_component.src)

    async def test_previous_search_block_should_be_removed_when_new_criteria_is_selected(self):
        msg = Mock()
        msg.page = Mock(WebPage)
        search_criteria_div = Mock()
        msg.page.search_criteria_div = search_criteria_div
        element = Mock()
        element.value = SearchParams.zip
        await add_search_input(element, msg)
        msg.page.remove.assert_called_once_with(search_criteria_div)

    @patch('weather_app.render_coordinates_search_fields')
    async def test_search_fields_should_be_rendered_according_to_radio_btn_value(self, render_func):
        msg = Mock()
        msg.page = Mock(WebPage)
        msg.page.search_criteria_div = Mock()
        element = Mock()
        element.value = SearchParams.coordinates
        await add_search_input(element, msg)
        render_func.assert_called_once()


class HelperFunctionsTest(unittest.IsolatedAsyncioTestCase):
    async def test_extract_parameters_should_return_component_name_and_value(self):
        component = Mock()
        component.name = 'test_name'
        component.value = 'test_value'
        params = await extract_parameters([component])
        self.assertEqual(params[component.name], component.value)

    async def test_extract_parameters_should_return_None_on_exception(self):
        component = True
        res = await extract_parameters([component])
        self.assertIsNone(res)

    async def test_get_weather_info_should_return_error_on_empty_input(self):
        result = await get_weather_info(None, None)
        self.assertIsNone(result[0])
        self.assertEqual("Internal error", result[1])

    @patch('weather_app.WeatherDataRepository')
    async def test_get_weather_info_should_choose_api_call_based_on_criteria(self, weather_repo):
        mock_repo = Mock(WeatherDataRepository)
        weather_repo.return_value = mock_repo
        expected_return_value = "Roman's city"
        mock_repo.get_by_city_name.return_value = expected_return_value
        input_values = {"city": None, "state": None, "country": None}
        result = await get_weather_info(SearchParams.city, input_values)
        self.assertEqual(result, expected_return_value)
        mock_repo.get_by_city_name.assert_called_once_with(*[None] * 3)


if __name__ == '__main__':
    unittest.main()
