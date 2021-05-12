# syntax=docker/dockerfile:1
FROM python:3.9-slim-buster

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY justpy.env justpy.env
COPY weather_app.py weather_app.py

EXPOSE 8000

CMD ["python3", "weather_app.py"]
