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


from pony.orm import *
from datetime import datetime
from database.connection import db

class DBBoard(db.Entity):
    id = PrimaryKey(int, auto=True)
    lines = Required(int)
    columns = Required(int)
    width = Optional(int)
    height = Optional(int)
    top_left_x = Optional(int)
    top_left_y = Optional(int)
    top_right_x = Optional(int)
    top_right_y = Optional(int)
    bottom_left_x = Optional(int)
    bottom_left_y = Optional(int)
    bottom_right_x = Optional(int)
    bottom_right_y = Optional(int)
    block_width = Optional(int)
    block_height = Optional(int)
    span_cols = Optional(int)
    span_rows = Optional(int)

class DBUser(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    nickname = Required(str)
    age = Required(int)
    gender = Required(str)
    dbphases01 = Set('DBPhase01')

class DBPhase01(db.Entity):
    id = PrimaryKey(int, auto=True)
    number01 = Required(int)
    number02 = Required(int)
    operator = Required(str)
    result = Required(int)
    time_initial = Optional(datetime)
    time_final = Optional(datetime)
    dbuser = Required(DBUser)