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

from rule import Rule
from inference_engine import InferenceEngine
from phase01_checks import Phase01Checks
from error import Error
from type_error import TypeError

from datetime import datetime

class Phase01Rules:
    
    def __init__(self, wm):
        self.wm = wm
        self.engine = InferenceEngine()
        self.phase01checks = Phase01Checks()
        self.type_error = TypeError()
        self.define_rules()
        
    def define_rules(self):
        self.engine.add_rule(
            Rule(
                name = 'Nenhum numero',
                condition=lambda wm: self.phase01checks.zero_numbers(self.wm),
                action=self.type_error.not_valid
            )
        )
        
        self.engine.add_rule(
            Rule(
                name = 'Mais de um numero',
                condition=lambda wm: self.phase01checks.more_numbers(self.wm),
                action=self.type_error.not_valid
            )
        )
        
        self.engine.add_rule(
            Rule(
                name = 'Apenas um numero',
                condition=lambda wm: self.phase01checks.one_number(self.wm),
                action=self.type_error.valid
            )
        )
        
        self.engine.add_rule(
            Rule(
                name = 'Juncao de termos',
                condition=lambda wm: self.phase01checks.union_terms(self.wm),
                action=self.type_error.error_rule_deficiency
            )
        )
        
        self.engine.add_rule(
            Rule(
                name = 'Troca de operadores',
                condition=lambda wm: self.phase01checks.switched_operators(self.wm),
                action=self.type_error.error_operator_usage
            )
        )
        
        self.engine.add_rule(
            Rule(
                name = 'Resposta errada',
                condition=lambda wm: self.phase01checks.wrong_answer(self.wm),
                action=self.type_error.error_domain_deficiency
            )
        )
        
        self.engine.add_rule(
            Rule(
                name = 'Demora para responder',
                condition=lambda wm: self.phase01checks.long_time(self.wm),
                action=self.type_error.error_misinterpretation_language
            )
        )
        
        self.engine.add_rule(
            Rule(
                name = 'Resposta correta',
                condition=lambda wm: self.phase01checks.is_correct(self.wm),
                action=self.type_error.error_misinterpretation_language
            )
        )
        
    def execute_rules(self):
        self.engine.execute_rules(self.wm)