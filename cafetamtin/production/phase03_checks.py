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

import logging
from datetime import datetime
from itertools import combinations

from production.memory import Memory

class Phase03Checks:
    
    def __init__(self) -> None:
        pass
    
    def zero_numbers(self, wm: Memory) -> bool:
        logging.info(f'Executando função: zero_numbers')
        numbers_student = wm.get_fact('numbers_student')
        
        return len(numbers_student) == 0
    
    def number_already_selected(self, wm: Memory) -> bool:
        logging.info(f'Executando função: number_already_selected')
        numbers_student = wm.get_fact('numbers_student')
        blocks_student = wm.get_fact('blocks_student')
        blocks_tutor = wm.get_fact('blocks_tutor')
        
        diff = [x for x in numbers_student if x not in blocks_student]
        
        if len(diff) != 1:
            return False
        
        return diff[0] in blocks_tutor
    
    def do_not_select_number_five_first(self, wm: Memory) -> bool:
        logging.info(f'Executando função: do_not_select_number_five_first')
        numbers_student = wm.get_fact('numbers_student')
        blocks_tutor = wm.get_fact('blocks_tutor')
        
        if 5 in blocks_tutor:
            return False
        
        return len(numbers_student) == 1 and 5 not in numbers_student.keys()
        
        
    def do_not_provide_new_number(self, wm: Memory) -> bool:
        logging.info(f'Executando função: do_not_provide_new_number')
        numbers_student = wm.get_fact('numbers_student')
        blocks_student = wm.get_fact('blocks_student')
        
        if len(numbers_student) != len(blocks_student):
            return False
        
        diff = [x for x in numbers_student if x not in blocks_student]
        
        return len(diff) == 0
    
    def provide_two_or_more_numbers(self, wm: Memory) -> bool:
        logging.info(f'Executando função: provide_two_or_more_numbers')
        numbers_student = wm.get_fact('numbers_student')
        blocks_student = wm.get_fact('blocks_student')
        
        return abs(len(numbers_student) - len(blocks_student)) > 1
    
    def do_not_make_sum_fifteen(self, wm: Memory) -> bool:
        logging.info(f'Executando função: do_not_make_sum_fifteen')
        numbers_student = wm.get_fact('numbers_student')
        blocks_student = wm.get_fact('blocks_student')
        blocks_available = wm.get_fact('blocks_available')
        
        
        if len(numbers_student) < 3:
            return False

        diff = [x for x in numbers_student if x not in blocks_student]

        if len(diff) != 1:
            return False
        
        number = diff[0]

        if len(blocks_student) == 2:
            _sum = sum(blocks_student)

            if number + _sum == 15:
                return False
            
            for n in blocks_available:
                if n != number and  n + _sum == 15:
                    return True
                            
            return False

        if len(blocks_student) >= 3:
            combs = combinations(blocks_student, 2)
            for c in combs:
                if sum(c) + number == 15:
                    return False

            combs = combinations(blocks_student, 2)
            for c in combs:
                for n in blocks_available:
                    if n != number and sum(c) + n == 15:
                        return True 
        
        return False
    
    def do_not_prevent_sum_fifteen(self, wm: Memory) -> bool:
        logging.info(f'Executando função: prevent_sum_fifteen')
        numbers_student = wm.get_fact('numbers_student')
        blocks_student = wm.get_fact('blocks_student')
        blocks_tutor = wm.get_fact('blocks_tutor')
        blocks_available = wm.get_fact('blocks_available')
        
        if len(blocks_tutor) < 2:
            return False
        
        diff = [x for x in numbers_student if x not in blocks_student]

        if len(diff) != 1:
            return False

        if self.is_sum_fifteen(wm):
            return False

        number = diff[0]
        
        combs = combinations(blocks_tutor, 2)
        for c in combs:
                for n in blocks_available:
                    if n != number and sum(c) + n == 15:
                        return True
        
        return False
    
    def is_sum_fifteen(self, wm: Memory) -> bool:
        logging.info(f'Executando função: is_correct')
        numbers_student = wm.get_fact('numbers_student')
        blocks_student = wm.get_fact('blocks_student')
                
        if len(numbers_student) < 3:
            return False

        diff = [x for x in numbers_student if x not in blocks_student]

        if len(diff) != 1:
            return False

        number = diff[0]
        
        if len(blocks_student) == 2:
            _sum = sum(blocks_student)

            if number + _sum == 15:
                return True
        
        if len(blocks_student) >= 3:
            combs = combinations(blocks_student, 2)
            for c in combs:
                if sum(c) + number == 15:
                    return True
        
        return False