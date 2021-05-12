import logging
import os
from collections import namedtuple
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from urllib.parse import urlencode

import justpy as jp


def configure_logger():
    rotating_file_handler = RotatingFileHandler(filename='weather_app.log', backupCount=2, maxBytes=2 * 10 ** 6)
    handlers = [logging.StreamHandler(), rotating_file_handler]
    logging.basicConfig(force=True, format='{asctime} - {levelname} - {message}', style='{', level=logging.INFO,
                        handlers=handlers)


WeatherDataResponse = namedtuple('WeatherDataResponse', ['city_weather', 'error'])


class WeatherDataRepository:

    def __init__(self, client=jp) -> None:
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
            url = f'http://api.openweathermap.org/data/2.5/weather?{query}&appid={appid}&units=imperial'
            result = await self.client.get(url)
            if result['cod'] == 200:
                city_weather = CityWeather(result['name'], result['sys']['country'], result['main'], result['coord'],
                                           result['weather'][0])
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


class SearchParams:
    city = "city"
    country = "country"
    state = "state"
    zip = "zip"
    lat = "lat"
    lon = "lon"
    coordinates = 'coordinates'


async def home_page():
    # change title and icon
    # provide html + nice stiles for 3 rtadio buttons
    # clicking into each radio button should provide search criteria (input field) and show submit button
    # clicking submit should call submit handler which will do search and print submit results (model)
    # Button new search should render the initial page again

    wp = jp.WebPage()
    await render_search_page(wp)
    return wp


async def render_search_fields(input_fields, parent, notes=""):
    jp.I(a=parent, text=notes, style="font-size:13px")
    jp.Br(a=parent)
    for field in input_fields:
        jp.Label(a=parent, text=f'{field}:')
        jp.Input(type='text', label=field.lower(), name=field.lower(), a=parent)


async def render_city_search_fields(parent):
    input_fields = [SearchParams.city.capitalize(), SearchParams.state.capitalize(), SearchParams.country.capitalize()]
    notes = 'Please note, state code and country code are optional'
    await render_search_fields(input_fields, parent, notes)


async def render_zip_search_fields(parent):
    input_fields = [SearchParams.zip.upper(), SearchParams.country.capitalize()]
    notes = 'Please note, country code is optional'
    await render_search_fields(input_fields, parent, notes)


async def render_coordinates_search_fields(parent):
    input_fields = [SearchParams.lon.capitalize(), SearchParams.lat.capitalize()]
    notes = 'Please enter Longitude and Latitude'
    await render_search_fields(input_fields, parent, notes)


async def add_search_input(self, msg):
    if msg.page.search_criteria_div: msg.page.remove(msg.page.search_criteria_div)
    parent_div = jp.Div(classes='m-2 p-2 flex-wrap', a=msg.page)
    div = jp.Div(classes='border m-2 p-2 flex-wrap', a=parent_div)
    msg.page.search_criteria_div = parent_div
    search_criteria = {SearchParams.city: render_city_search_fields, SearchParams.zip: render_zip_search_fields,
                       SearchParams.coordinates: render_coordinates_search_fields}
    search_key = self.value.lower()
    await search_criteria[search_key](div)
    btn_classes = 'w-32 mr-2 mb-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full'
    btn = jp.Button(name='search', text="Search", classes=btn_classes, a=parent_div, click=search_btn_clicked)
    filtered_components = [component for component in div.components if component.class_name == 'Input']
    btn.search_info = (filtered_components, search_key)


async def search_btn_clicked(self, msg):
    msg.page.delete_components()
    input_values = await extract_parameters(self.search_info[0])
    result = await get_weather_info(self.search_info[1], input_values)
    await render_result_block(msg.page, result[0]) if result[0] else await render_error_block(msg.page, result[1])
    btn_classes = 'w-32 mr-2 mb-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full'
    jp.Button(text="New search", classes=btn_classes, a=msg.page, click=back_to_home_page)


async def extract_parameters(components):
    input_values = {}
    try:
        for component in components:
            input_values[component.name] = component.value
    except Exception:
        logging.exception("Error during input value extraction")
        return None
    return input_values


async def get_weather_info(search_criteria, input_values):
    if not input_values: return (None, "Internal error")
    repo = WeatherDataRepository()
    if (search_criteria == SearchParams.city):
        res = await repo.get_by_city_name(input_values[SearchParams.city], input_values[SearchParams.state],
                                          input_values[SearchParams.country])
    elif (search_criteria == SearchParams.zip):
        res = await repo.get_by_zip(input_values[SearchParams.zip], input_values[SearchParams.country])
    elif (search_criteria == SearchParams.coordinates):
        res = await repo.get_by_coordinates(input_values[SearchParams.lat], input_values[SearchParams.lon])
    return res


async def render_result_block(page, city_weather):
    paragraph_design = "relative w-64 bg-blue-500 m-2 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
    city_details_div = jp.Div(a=page, classes='m-2 p-2 flex-wrap')
    for metric in [f'{city_weather.city}, {city_weather.country_code}', f'coordinates: {city_weather.coord}']:
        jp.P(classes=paragraph_design, text=metric, a=city_details_div)
    condition_img = jp.Img(src=f'http://openweathermap.org/img/wn/{city_weather.weather["icon"]}@2x.png', a=page)
    condition_img.height = 150
    condition_img.width = 150
    weather_details_div = jp.Div(a=page, classes='m-2 p-2 flex-wrap')
    for metric in [f'current temperature: {city_weather.weatherMetrics["temp"]} F',
                   f'Feels like: {city_weather.weatherMetrics["feels_like"]} F',
                   f'Humidity {city_weather.weatherMetrics["humidity"]}%']:
        jp.P(classes=paragraph_design, text=metric, a=weather_details_div)


async def render_error_block(page, error_msg):
    jp.P(text=error_msg, a=page)


async def back_to_home_page(self, msg):
    msg.page.delete_components()
    await render_search_page(msg.page)


async def render_search_page(wp):
    search_types = [SearchParams.city.capitalize(), SearchParams.zip.upper(), SearchParams.coordinates.capitalize()]
    outer_div = jp.Div(classes='border m-2 p-2 w-64', a=wp)
    jp.P(a=outer_div, text='Please select search criteria:')
    for search_type in search_types:
        label = jp.Label(classes='inline-block mb-1 p-1', a=outer_div)
        jp.Input(type='radio', name='search_criteria', value=search_type, a=label, change=add_search_input)
        jp.Span(classes='ml-1', a=label, text=search_type)
    wp.search_criteria_div = None


if __name__ == '__main__':
    configure_logger()
    logging.info('Staring application')
    jp.justpy(home_page)
