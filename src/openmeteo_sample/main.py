import openmeteo_requests

import requests_cache
import pandas

from retry_requests import retry

cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo_client = openmeteo_requests.Client(session=retry_session)

OPENMETEO_API_URL = "https://api.open-meteo.com/v1/forecast"

# 東京スカイツリーの天気
params = {
    "latitude": 35.71,
    "longitude": 139.81,
    "current": ["temperature_2m", "relative_humidity_2m", "precipitation"],
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation_probability",
        "precipitation",
        "weather_code",
        "wind_speed_10m",
    ],
    "forecast_days": 1,
}

responses = openmeteo_client.weather_api(OPENMETEO_API_URL, params)

# Process first location.  Add a for-loop for multiple locations or weather models
response = responses[0]

print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")


# The order variable needs to be the same as requested.
current = response.Current()
current_temperature = current.Variables(0).Value()
current_relative_humidity = current.Variables(1).Value()
current_precipitation = current.Variables(2).Value()

# The order variable needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity = hourly.Variables(1).ValuesAsNumpy()
hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()
hourly_precipitation = hourly.Variables(3).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(4).ValuesAsNumpy()
hourly_wind_speed = hourly.Variables(5).ValuesAsNumpy()

hourly_dataframe = pandas.DataFrame(
    {
        "date": pandas.date_range(
            start=pandas.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pandas.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pandas.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        ),
        "temperature": hourly_temperature,
        "relative_humidity": hourly_relative_humidity,
        "precipitation_probability": hourly_precipitation_probability,
        "precipitation": hourly_precipitation,
        "weather_code": hourly_weather_code,
        "wind_speed": hourly_wind_speed,
    }
)
print(hourly_dataframe)
