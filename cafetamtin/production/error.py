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

import time
from datetime import datetime

class Error:
    
    def __init__(self, type = None, subtype = None, weight=0):
        self.type = type
        self.subtype = subtype
        self.timestamp = time.time()
        self.weight = weight
        
    def __repr__(self):
        date_time = datetime.fromtimestamp(self.timestamp)
        strtime = date_time.strftime("%d/%m/%Y %H:%M") 
        return f"Error type: {self.type}, subtype: {self.subtype}, datetime: {strtime}"
    
    def __eq__(self, other):
        if isinstance(other, Error):
            return (self.type == other.type and self.subtype == other.subtype)
        return False