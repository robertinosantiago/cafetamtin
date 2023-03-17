# Copyright (C) 2023 Robertino Mendes Santiago Junior
# 
# This file is part of CaFE-TaMTIn Approach.
# 
# CaFE-TaMTIn Approach is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# CaFE-TaMTIn Approach is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with CaFE-TaMTIn Approach.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime

class Timer:

    def __init__(self):
        self.__timer = {
            'time_started': None,
            'time_finished': None,
            'time_paused': None,
            'time_resumed': None,
            'paused': False,
            'started': False,
            'times_paused': 0,
            'total_time': 0,
            'total_time_paused': 0
        }

    def start(self):
        t = datetime.now()
        self.__timer['time_started'] = t
        self.__timer['started'] = True
        self.__timer['time_finished'] = None
        self.__timer['time_paused'] = None
        self.__timer['time_resumed'] = None
        self.__timer['paused'] = False
        self.__timer['times_paused'] = 0
        self.__timer['total_time'] = 0
        self.__timer['total_time_paused'] = 0
    
    def stop(self):
        if self.__timer['paused']:
            self.resume()

        if self.__timer['started']:
            t = datetime.now()
            s = t - self.__timer['time_started']
            self.__timer['time_finished'] = t
            self.__timer['total_time'] += s.total_seconds()
            self.__timer['started'] = False

    def pause(self):
        if not self.__timer['paused'] and self.__timer['started']:
            t = datetime.now()
            s = t - self.__timer['time_started'] 
            self.__timer['total_time'] += s.total_seconds()
            self.__timer['time_paused'] = t
            self.__timer['times_paused'] += 1
            self.__timer['time_finished'] = t
            self.__timer['paused'] = True

    def resume(self):
        if self.__timer['paused'] and self.__timer['started']:
            t = datetime.now()
            s = t - self.__timer['time_paused']
            self.__timer['time_started'] = t
            self.__timer['time_resumed'] = t
            self.__timer['total_time_paused'] += s.total_seconds()
            self.__timer['paused'] = False

    def total_time_seconds(self):
        return self.__timer['total_time'] + self.__timer['total_time_paused']
    
    def total_times_paused(self):
        return self.__timer['times_paused']

    def total_time_paused_seconds(self):
        return self.__timer['total_time_paused']
