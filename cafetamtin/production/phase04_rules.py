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

from production.rule import Rule
from production.memory import Memory
from production.inference_engine import InferenceEngine
from production.phase04_checks import Phase04Checks
from production.type_error import TypeError

class Phase04Rules:
    def __init__(self, wm: Memory) -> None:
        self.wm = wm
        self.engine = InferenceEngine()
        self.checks = Phase04Checks()
        self.type_error = TypeError()
        self.define_rules()
    
    def define_rules(self) -> None:
        self.engine.add_rule(
            Rule(
                name= 'Não resolver soma 15 após determinado tempo',
                condition= lambda wm: self.checks.long_time(self.wm),
                action= self.type_error.error_misinterpretation_language
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'três números ímpares que não somam 15',
                condition= lambda wm: self.checks.three_odd_numbers(self.wm),
                action= self.type_error.error_domain_deficiency
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'dois números pares e um ímpar que não somam 15',
                condition= lambda wm: self.checks.two_even_and_one_odd_numbers(self.wm),
                action= self.type_error.error_domain_deficiency
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'três números pares',
                condition= lambda wm: self.checks.three_even_numbers(self.wm),
                action= self.type_error.error_rule_deficiency
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'dois números ímpares e um número par',
                condition= lambda wm: self.checks.two_odd_and_one_even_numbers(self.wm),
                action= self.type_error.error_rule_deficiency
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'Não colocar o 5 no centro',
                condition= lambda wm: self.checks.not_five_in_center(self.wm),
                action= self.type_error.error_indirectly_identifiable
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'Não colocar os pares nos cantos',
                condition= lambda wm: self.checks.not_even_number_in_corners(self.wm),
                action= self.type_error.error_indirectly_identifiable
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'Não produzir soma 15',
                condition= lambda wm: self.checks.no_sum_fifteen(self.wm),
                action= self.type_error.error_uncategorized_solution
            )
        )
        
    def execute_rules(self) -> None:
        self.engine.execute_rules(self.wm)