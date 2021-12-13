# Weather application

Self-hosted web app allows user to get current weather condition using a friendly user interface.
This is just a simple app/POC to play with JustPy capabilities, not even a pet project.

# Running

## Option 1: Docker container

In order to avoid issues with python installations, the app can be run within a container.

1. Build an image from Docker file
   `docker build . --tag weather_app`

2. Run docker container: `docker run --publish 8000:8000 --env-file weather_app.env  weather_app`

Please note, you can pass environment variables in different way. The example above illustrates passing *.env file. In
order to do this, please create *.env file and put following variable
inside: `APP_ID=[your API token to access openweathermap]`

Once container is running, please open http://localhost:8000/ in your web browser and follow directions from
application.

## Option 2: Running as a local server

Application can be started from the host OS. In order to do this, please ensure that Python3.9 is installed on your
machine. Next, install required dependencies by executing `pip3 install -r requirements.txt` in the project directory.
Run `python3 weather_app.py`. Open url provided above and enjoy the application.

### Author

[Roman Khachko](https://www.linkedin.com/in/romankhachko)