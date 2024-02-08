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
from production.phase03_checks import Phase03Checks
from production.type_error import TypeError

class Phase03Rules:
    
    def __init__(self, wm: Memory) -> None:
        self.wm = wm
        self.engine = InferenceEngine()
        self.checks = Phase03Checks()
        self.type_error = TypeError()
        self.define_rules()
    
    def define_rules(self) -> None:
        self.engine.add_rule(
            Rule(
                name= 'Informar número já selecionado pelo tutor',
                condition= lambda wm: self.checks.number_already_selected(self.wm),
                action= self.type_error.error_misinterpretation_language,
                weight= 2
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'Não completar soma 15 quando possível',
                condition= lambda wm: self.checks.do_not_make_sum_fifteen(self.wm),
                action= self.type_error.error_domain_deficiency,
                weight= 0
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'Evitar que o tutor some 15',
                condition= lambda wm: self.checks.do_not_prevent_sum_fifteen(self.wm),
                action= self.type_error.error_domain_deficiency,
                weight= 0
            )
        )

        self.engine.add_rule(
            Rule(
                name= 'Não selecionar o número 5 primeiro',
                condition= lambda wm: self.checks.do_not_select_number_five_first(self.wm),
                action= self.type_error.error_indirectly_identifiable,
                weight= 1
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'Não informar nenhum número novo',
                condition= lambda wm: self.checks.do_not_provide_new_number(self.wm),
                action= self.type_error.error_uncategorized_solution,
                weight= 4
            )
        )
        
        self.engine.add_rule(
            Rule(
                name= 'Informar dois ou mais números',
                condition= lambda wm: self.checks.provide_two_or_more_numbers(self.wm),
                action= self.type_error.error_uncategorized_solution,
                weight= 3
            )
        )
        
    def execute_rules(self) -> None:
        self.engine.execute_rules(self.wm)