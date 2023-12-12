import json
import asyncio
from datetime import datetime

import requests
from pyensign.events import Event
from pyensign.ensign import Ensign

# TODO: replace with YOU - your email and app details :)
ME = "(https://rotational.io/data-playground/noaa/, weather@rotational.io)"

# TODO: these are memorable for ME. Replace with the locations of interest to YOU
# LOCS = {  "Denver": {"lat": "39.7392", "long": "-104.9903"}}

# LOCS = {  "Hawai": {"lat": "19.7019", "long": "-155.0895"}}

LOCS = {'Chicago': {"lat": "41.8818", "long": "-87.6231"}}
## https://api.weather.gov/points/64.7511,-147.3494


class WeatherPublisher:

    def __init__(self, topic="test8_noaa-reports-json", interval=3600, locations=LOCS, user=ME):

        self.topic = topic
        self.interval = interval
        self.locations = locations
        self.url = "https://api.weather.gov/points/"
        self.user = {"User-Agent": user}
        self.datatype = "application/json"
        self.ensign = Ensign(
            client_id="",
            client_secret=""
        )

    async def print_ack(self, ack):

        ts = datetime.fromtimestamp(ack.committed.seconds + ack.committed.nanos / 1e9)
        print(f"Event committed at {ts}")

    async def print_nack(self, nack):

        print(f"Event was not committed with error {nack.code}: {nack.error}")

    def compose_query(self, location):

        lat = location.get("lat", None)
        long = location.get("long", None)
        if lat is None or long is None:
            raise Exception("unable to parse latitude/longitude from location")

        return self.url + lat + "," + long

    def run(self):

        asyncio.run(self.recv_and_publish())

    async def recv_and_publish(self):

        await self.ensign.ensure_topic_exists(self.topic)

        while True:
            for location in self.locations.values():
                # Note that we're making a different API call for each location
                # TODO: can these be bundled so that we can make fewer calls?
                query = self.compose_query(location)

                # If successful, the initial response returns a link you can use to
                # retrieve the full hourly forecast
                response = requests.get(query).json()
                forecast_url = self.parse_forecast_link(response)
                forecast = requests.get(forecast_url).json()

                # After we retrieve and unpack the full hourly forecast, we can publish
                # each period of the forecast as a new event
                events = self.unpack_noaa_response(forecast)
                for event in events:
                    await self.ensign.publish(
                        self.topic,
                        event,
                        on_ack=self.print_ack,
                        on_nack=self.print_nack,
                    )
            await asyncio.sleep(self.interval)

    def parse_forecast_link(self, message):

        properties = message.get("properties", None)
        if properties is None:
            raise Exception("unexpected response from api call, no properties")

        forecast_link = properties.get("forecastHourly", None)
        if forecast_link is None:
            raise Exception("unexpected response from api call, no forecast")

        return forecast_link

    def unpack_noaa_response(self, message):

        properties = message.get("properties", None)
        if properties is None:
            raise Exception("unexpected response from forecast request, no properties")

        periods = properties.get("periods", None)
        if periods is None:
            raise Exception("unexpected response from forecast request, no periods")

        for period in periods:
            # There's a lot available! For this example, we'll just parse out a few
            # fields from the NOAA API response:
            data = {
                "location": next(iter(LOCS.keys())),
                "latitude": next(iter(LOCS.values()))['lat'],
                "longitude": next(iter(LOCS.values()))['long'],
                "summary": period.get("shortForecast", None),
                "temperature": period.get("temperature", None),
                "units": period.get("temperatureUnit", None),
                "daytime": period.get("isDaytime", None),
                "dewpoint": period.get("dewpoint", None).get("value", None),
                "probabilityOfPrecipitation": period.get("probabilityOfPrecipitation", None).get("value", None),
                "relativeHumidity": period.get("relativeHumidity", None).get("value", None),
                "windSpeed":period.get("windSpeed", None),
                "start": period.get("startTime", None),
                "end": period.get("endTime", None),
            }

            yield Event(json.dumps(data).encode("utf-8"), mimetype=self.datatype)


if __name__ == "__main__":
    publisher = WeatherPublisher()
    publisher.run()
