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
    steps = Set('DBSteps')
    challenges_p1 = Set('DBChallengeP1')
    challenges_p2 = Set('DBChallengeP2')

class DBChallengeP1(db.Entity):
    id = PrimaryKey(int, auto=True)
    number01 = Required(int)
    operator01 = Required(str, 1)
    number02 = Required(int)
    operator02 = Optional(str, nullable=True)
    number03 = Optional(int)
    expected_result = Required(int)
    total_time = Required(float)
    responsesp1 = Set('DBResponseP1')
    user = Required(DBUser)

class DBResponseP1(db.Entity):
    id = PrimaryKey(int, auto=True)
    informed_result = Required(int)
    is_correct = Required(bool)
    total_time = Required(float)
    time_without_pauses = Required(float)
    paused_counter = Required(int)
    tips_counter = Required(int)
    distractors = Optional(int)
    affective_state = Optional(str)
    affective_quad = Optional(str)
    type_er = Optional(str)
    type_error = Optional(str)
    challengep1 = Required(DBChallengeP1)

class DBChallengeP2(db.Entity):
    id = PrimaryKey(int, auto=True)
    number01 = Required(int)
    number02 = Required(int)
    number03 = Required(int)
    total_time = Required(float)
    user = Required(DBUser)
    responsesp2 = Set('DBResponseP2')


class DBResponseP2(db.Entity):
    id = PrimaryKey(int, auto=True)
    number01 = Optional(int)
    number02 = Optional(int)
    number03 = Optional(int)
    is_correct = Optional(bool)
    total_time = Optional(float)
    time_without_pauses = Optional(float)
    paused_counter = Optional(int)
    tips_counter = Optional(int)
    distractors = Optional(int)
    affective_state = Optional(str)
    affective_quad = Optional(str)
    type_er = Optional(str)
    type_error = Optional(str)
    challengep2 = Required(DBChallengeP2)

class DBSteps(db.Entity):
    id = PrimaryKey(int, auto=True)
    phase = Required(int)
    score = Optional(int)
    lifes = Optional(int)
    status = Optional(str)
    user = Optional(DBUser)