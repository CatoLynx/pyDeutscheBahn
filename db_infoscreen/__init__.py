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
        return data['departures']

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