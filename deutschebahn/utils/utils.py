"""
Copyright 2023 Julian Metzler

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

import errno
import os
import signal

from functools import wraps


def timeout(seconds, error_message = os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


def route_from(route, station):
    start_found = False
    new_route = []
    for stop in route:
        if not start_found:
            start_found = stop['name'].startswith(station)
        if start_found:
            new_route.append(stop)
    return new_route


def route_remove_cancelled(route):
    # Filter all cancelled stops from a route
    return [stop for stop in route if not stop.get('isCancelled')]


def get_display_delay(delay, bins):
    """
    Calculate displayed delay by rounding into provided bins.
    Example bins:
    [
        # Format: (from, to, display)
        # -1 as an upper bound means
        # "perform only lower bounds check"
        ( 0,  4,  0), # round delays from 0 to 4 minutes to 0
        ( 5,  9,  5), # round delays from 5 to 9 minutes to 5
        (10, 14, 10), # etc.
        (15, 19, 15),
        (20, 24, 20),
        (25, 29, 25),
        (30, 34, 30),
        (35, 39, 35),
        (40, 44, 40),
        (45, 49, 45),
        (50, 59, 50),
        (60, 69, 60),
        (70, 79, 70),
        (80, 89, 80),
        (90, 99, 90),
        (100, -1, -1)
    ]
    """
    for _bin in bins:
        if _bin[1] == -1:
            if delay >= _bin[0]:
                return _bin[2]
        else:
            if delay >= _bin[0] and delay <= _bin[1]:
                return _bin[2]
    return delay