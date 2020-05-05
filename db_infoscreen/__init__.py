"""
Copyright 2020 Julian Metzler

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

from .metadata import version as __version__

import datetime
import requests


class DBInfoscreen:
    def __init__(self, host):
        self.host = host

    def get_trains(self, station):
        resp = requests.get("https://{host}/{station}.json".format(host=self.host, station=station))
        data = resp.json()
        if 'error' in data:
            return []
        return data['departures'] or []

    def get_coach_order(self, train, departure):
        if isinstance(departure, datetime.datetime):
            dep_str = departure.strftime("%Y%m%d%H%M")
        else:
            dep_str = departure
        resp = requests.get("https://www.apps-bahn.de/wr/wagenreihung/1.0/{train}/{departure}".format(train=train, departure=dep_str))
        data = resp.json()
        if 'error' in data:
            return None
        return data

    def calc_real_times(self, trains):
        output = []
        for train in trains:
            if train['scheduledDeparture']:
                departure = datetime.datetime.strptime(train['scheduledDeparture'], "%H:%M")
                departure += datetime.timedelta(minutes=train['delayDeparture'])
                train['actualDeparture'] = departure.strftime("%H:%M")
            else:
                train['actualDeparture'] = None
            
            if train['scheduledArrival']:
                departure = datetime.datetime.strptime(train['scheduledArrival'], "%H:%M")
                departure += datetime.timedelta(minutes=train['delayArrival'])
                train['actualArrival'] = departure.strftime("%H:%M")
            else:
                train['actualArrival'] = None
            
            output.append(train)
        return output
    
    @staticmethod
    def round_delay(delay):
        if delay <= 0:
            return 0
        
        if delay > 210:
            return -1 # delayed for unspecified amount of time
        
        delay_groups = (list(range(0, 60, 5)) + list(range(60, 210, 10)))[::-1]
        for g in delay_groups:
            if delay >= g:
                return g

    @staticmethod
    def time_sort(train):
        now = datetime.datetime.now()
        now_date = now.date()
        now_time = now.time()
        if train['actualDeparture']:
            sort_time = datetime.datetime.strptime(train['actualDeparture'], "%H:%M").time()
        elif train['actualArrival']:
            sort_time = datetime.datetime.strptime(train['actualArrival'], "%H:%M").time()
        else:
            raise ValueError("Train to sort has neither actualDeparture nor actualArrival")

        result = datetime.datetime.combine(now_date, sort_time)
        if now_time >= datetime.time(12, 0) and sort_time < datetime.time(12, 0):
            result += datetime.timedelta(days=1)
        return result