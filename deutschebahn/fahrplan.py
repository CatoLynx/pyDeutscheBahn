"""
Copyright 2022 GamingCoookie

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import requests as r
import json
import datetime


class Fahrplan:
    def __init__(self, auth: str):
        self.__token = auth
        self.__request_headers = {'Accept': 'application/json',
                                  'Authorization': 'Bearer {auth}'.format(auth=self.__token)}

    def get_station_by_name(self, name: str, select_first: bool = True) -> list:
        stations = json.loads(r.get(url='https://api.deutschebahn.com/fahrplan-plus/v1/location/{x}'.format(x=name),
                                    headers=self.__request_headers).content)
        for index in range(len(stations)):
            del stations[index]['lon']
            del stations[index]['lat']

        return stations[0] if select_first else stations

    def get_arrival_board(self, board_id: int, date: datetime.datetime or datetime.date) -> list:
        if isinstance(date, datetime.datetime):
            url = 'https://api.deutschebahn.com/fahrplan-plus/v1/arrivalBoard/{bid}?date={date}'.format(
                bid=board_id, date=date.isoformat())
            url.replace(':', '%3A')
        else:
            url = 'https://api.deutschebahn.com/fahrplan-plus/v1/arrivalBoard/{bid}?date={date}'.format(
                bid=board_id, date=date.isoformat())

        board = json.loads(r.get(url=url, headers=self.__request_headers).content)

        return board

    def get_departure_board(self, board_id: int, date: datetime.datetime or datetime.date) -> list:
        if isinstance(date, datetime.datetime):
            url = 'https://api.deutschebahn.com/fahrplan-plus/v1/departureBoard/{bid}?date={date}'.format(
                bid=board_id, date=date.isoformat())
            url.replace(':', '%3A')
        else:
            url = 'https://api.deutschebahn.com/fahrplan-plus/v1/departureBoard/{bid}?date={date}'.format(
                bid=board_id, date=date.isoformat())

        board = json.loads(r.get(url=url, headers=self.__request_headers).content)

        return board

    def get_journey_details(self, journey_id: str) -> list:
        journey_id = journey_id.replace('%', '%25')
        url = 'https://api.deutschebahn.com/fahrplan-plus/v1/journeyDetails/{id}'.format(id=journey_id)

        journey = json.loads(r.get(url=url, headers=self.__request_headers).content)

        return journey
