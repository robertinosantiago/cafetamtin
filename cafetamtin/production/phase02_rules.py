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
from production.phase02_checks import Phase02Checks
from production.type_error import TypeError

class Phase02Rules:
    
    def __init__(self, wm: Memory) -> None:
        self.wm = wm
        self.engine = InferenceEngine()
        self.phase02checks = Phase02Checks()
        self.type_error = TypeError()
        self.define_rules()
    
    def define_rules(self) -> None:
        self.engine.add_rule(
            Rule(
                name= 'Nenhum numero',
                condition= lambda wm: self.phase02checks.zero_numbers(self.wm),
                action= self.type_error.not_valid
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'Sem soma 15 depois de determinado tempo',
                condition= lambda wm: self.phase02checks.long_time(self.wm),
                action= self.type_error.error_misinterpretation_language,
                weight= 3
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'tres numero impares sem soma 15',
                condition= lambda wm: self.phase02checks.three_odd_numbers(self.wm),
                action= self.type_error.error_domain_deficiency,
                weight= 0
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'dois numeros pares e um numero impar',
                condition= lambda wm: self.phase02checks.two_even_and_one_odd_numbers(self.wm),
                action= self.type_error.error_domain_deficiency,
                weight= 0
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'tres numeros pares',
                condition= lambda wm: self.phase02checks.three_even_numbers(self.wm),
                action= self.type_error.error_rule_deficiency,
                weight= 2
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'dois numeros impares e um numero par',
                condition= lambda wm: self.phase02checks.two_odd_and_one_even_numbers(self.wm),
                action= self.type_error.error_rule_deficiency,
                weight= 2
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'diferente de tres termos',
                condition= lambda wm: self.phase02checks.different_three_numbers(self.wm),
                action= self.type_error.error_indirectly_identifiable,
                weight= 1
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'sequencia de respostas erradas',
                condition= lambda wm: self.phase02checks.many_errors(self.wm),
                action= self.type_error.error_uncategorized_solution,
                weight= 4
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'resposta correta',
                condition= lambda wm: self.phase02checks.is_correct(self.wm),
                action= self.type_error.correct
            )
        )
        
    def execute_rules(self) -> None:
        self.engine.execute_rules(self.wm)