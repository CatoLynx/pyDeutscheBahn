"""
Copyright 2022 Julian Metzler

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

import csv
import os


class DS100:
    def __init__(self, filename = None):
        self.ds100 = {}
        filename = filename or os.path.join(os.path.dirname(__file__), "ds100.csv")
        with open(filename, encoding='utf-8') as f:
            # Original header:
            # Abk;Name;Kurzname;Typ;Betr-Zust;Primary location code;UIC;RB;gültig von;gültig bis;Netz-Key;Fpl-rel;Fpl-Gr
            field_names = [
                'code',
                'name',
                'short_name',
                'type',
                'op_status',
                'pri_loc_code',
                'rics_code',
                'regional_area',
                'valid_from',
                'valid_till',
                'unique_key',
                'schedule_relevance',
                'schedule_edit_boundary'
            ]
            f.readline() # Skip header row since we manually define the header
            reader = csv.DictReader(f, fieldnames=field_names, delimiter=";")
            for row in reader:
                self.ds100[row['code']] = dict(row)
    
    def get(self, code):
        return self.ds100.get(code)
    
    def search_name(self, search_str):
        results = []
        for code, data in self.ds100.items():
            if search_str.lower() in data['name'].lower():
                results.append(data.copy())
        return results
    
    def filter(self, func):
        return {k: v for k, v in self.ds100.items() if func(v)}
    
    def all(self):
        return self.ds100
