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

from production.rule import Rule
from production.inference_engine import InferenceEngine
from production.phase01_checks import Phase01Checks
from production.error import Error
from production.type_error import TypeError

from datetime import datetime

class Phase01Levels:
    
    def __init__(self, wm):
        self.wm = wm
        self.engine = InferenceEngine()
        self.phase01checks = Phase01Checks()
        self.define_rules()
        
    def define_rules(self):
        self.engine.add_rule(
            Rule(
                name = 'Erros de impulsividade',
                condition=lambda wm: self.phase01checks.impulsive_errors(self.wm),
                action=self.decrease_inhibitory_control
            )
        )
        
    def decrease_inhibitory_control(self, wm, rule_name, weight):
        pass
    
    def increase_inhibitory_control(self, wm, rule_name, weight):
        pass