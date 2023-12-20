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

class Student:
    
    INHIBITORY_CAPACITY_LOW = 0
    INHIBITORY_CAPACITY_MEDIUM = 1
    INHIBITORY_CAPACITY_HIGH = 2
    
    def __init__(self, id, name, nickname, age, gender, inhibitory_capacity_test, inhibitory_capacity_online):
        self.id = id
        self.name = name
        self.nickname = nickname
        self.age = age
        self.gender = gender
        self.inhibitory_capacity_test = inhibitory_capacity_test
        self.inhibitory_capacity_online = inhibitory_capacity_online