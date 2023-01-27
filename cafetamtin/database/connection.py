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

from decimal import Decimal
from datetime import datetime

from pony.converting import str2datetime
from pony.orm import *

import os
from dotenv import load_dotenv

db = Database()
#db.bind(
#    provider = 'mysql',
#    user = os.getenv('DATABASE_USER'),
#    password = os.getenv('DATABASE_PASS'),
#    host = os.getenv('DATABASE_HOST'),
#    database = os.getenv('DATABASE_SCHEMA')
#    )