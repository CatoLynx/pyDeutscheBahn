"""
Copyright 2020-2024 Julian Metzler

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

import datetime
import pytz
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

    def get_coach_order(self, train, departure, ibnr):
        departure = departure.astimezone(pytz.utc)
        train_type = train.split()[0]
        train_number = train.split()[-1]
        if isinstance(departure, datetime.datetime):
            dep_str = departure.strftime("%Y%m%d%H%M")
        else:
            dep_str = departure
        params = {
            "administrationId": 80,
            "category": train_type,
            "date": departure.strftime("%Y-%m-%d"),
            "evaNumber": ibnr,
            "number": train_number,
            "time": departure.isoformat().replace("+00:00", "Z")
        }
        resp = requests.get("https://www.bahn.de/web/api/reisebegleitung/wagenreihung/vehicle-sequence", params=params)
        data = resp.json()
        if 'error' in data:
            return None
        return data

    def calc_real_times(self, trains, round_delay=False):
        output = []
        for train in trains:
            if train['scheduledDeparture']:
                if round_delay:
                    delay_dep = self.round_delay(train['delayDeparture'], indicate_unspecified=False)
                else:
                    delay_dep = train['delayDeparture']
                departure = datetime.datetime.strptime(train['scheduledDeparture'], "%H:%M")
                departure += datetime.timedelta(minutes=delay_dep)
                train['actualDeparture'] = departure.strftime("%H:%M")
            else:
                train['actualDeparture'] = None
            
            if train['scheduledArrival']:
                if round_delay:
                    delay_arr = self.round_delay(train['delayArrival'], indicate_unspecified=False)
                else:
                    delay_arr = train['delayArrival']
                departure = datetime.datetime.strptime(train['scheduledArrival'], "%H:%M")
                departure += datetime.timedelta(minutes=delay_arr)
                train['actualArrival'] = departure.strftime("%H:%M")
            else:
                train['actualArrival'] = None
            
            output.append(train)
        return output
    
    @staticmethod
    def round_delay(delay, indicate_unspecified=True):
        if delay <= 0:
            return 0
        
        if delay > 210 and indicate_unspecified:
            return -1 # delayed for unspecified amount of time
        
        delay_groups = (list(range(0, 60, 5)) + list(range(60, 1440, 10)))[::-1]
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
