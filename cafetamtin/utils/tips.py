#  Copyright (C) 2024 Robertino Mendes Santiago Junior
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

from production.error import Error
from production.type_error import TypeError

class Tips:
    
    def __init__(self) -> None:
        self.tips = {}
        self.create_empty_tips()
        
    def create_empty_tips(self):
        self.tips[Error(type=TypeError.TYPE_MISINTERPRETATION_LANGUAGE, subtype=TypeError.SUBTYPE_NONE)] = []
        self.tips[Error(type=TypeError.TYPE_DIRECTLY_IDENTIFIABLE, subtype=TypeError.SUBTYPE_DOMAIN_DEFICIENCY)] = []
        self.tips[Error(type=TypeError.TYPE_DIRECTLY_IDENTIFIABLE, subtype=TypeError.SUBTYPE_RULE_DEFICIECY)] = []
        self.tips[Error(type=TypeError.TYPE_DIRECTLY_IDENTIFIABLE, subtype=TypeError.SUBTYPE_OPERATOR_USAGE)] = []
        self.tips[Error(type=TypeError.TYPE_INDIRECTLY_IDENTIFIABLE, subtype=TypeError.SUBTYPE_NONE)] = []
        self.tips[Error(type=TypeError.TYPE_UNCATEGORIZED_SOLUTION, subtype=TypeError.SUBTYPE_NONE)] = []
        
    def add_tip(self, error: Error, message, image = None):
        self.tips[error].append({'message': message, 'image': image, 'count': 0})
        
    def get_tip(self, error: Error):
        tips = self.tips.get(error)
        tips = sorted(tips, key=lambda x : x['count'])
        tips[0]['count'] = tips[0]['count'] + 1
        self.tips[error] = tips
        return tips[0]