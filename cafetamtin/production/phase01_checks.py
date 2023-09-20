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


import logging
import re
from datetime import datetime

from production.error import Error

class Phase01Checks:
    
    def __init__(self):
        pass
    
    def zero_numbers(self, wm):
        logging.info(f'Executando função: zero_numbers')
        result = wm.get_fact('result')
        return len(result) == 0
        
    def more_numbers(self, wm):
        logging.info(f'Executando função: more_numbers')
        result = wm.get_fact('result')
        return len(result) > 1
            
    def one_number(self, wm):
        result = wm.get_fact('result')
        logging.info(f'Executando função: one_number')
        return len(result) == 1
    
    def union_terms(self, wm):
        logging.info(f'Executando função: union_terms')
        expression = wm.get_fact('expression')
        result = wm.get_fact('result')
        
        valid = wm.get_fact('valid')
                
        if not valid:
            part1, part2 = expression.split('=')
            
            r = re.compile(r'[^0-9]')
            numbers_expression = r.sub('', part1).strip()
                        
            result = ''.join(str(e) for e in result).strip()
            
            print(numbers_expression, '<>', result)

            return result == numbers_expression
        
        return False
    
    def switched_operators(self, wm):
        logging.info(f'Executando função: switched_operators')
        
        expression = wm.get_fact('expression')
        result = wm.get_fact('result')
        valid = wm.get_fact('valid')
        
        if valid:
            result = int(result[0])
            part1, part2 = expression.split('=')
            
            count_plus = part1.count('+')
            count_minus = part1.count('-')
            
            is_switched = False
            
            if count_plus + count_minus == 1:
                n1, op, n2 = part1
                n1 = int(n1)
                n2 = int(n2)
                if op == '+':
                    if n1 - n2 == result:
                        is_switched = True
                else:
                    if n1 + n2 == result:
                        is_switched = True
            else:
                n1, op1, n2, op2, n3 = part1
                n1 = int(n1)
                n2 = int(n2)
                n3 = int(n3)
                
                if op1 == '+':
                    if n1 - n2 + n3 == result:
                        is_switched = True
                    if n1 - n2 - n3 == result:
                        is_switched = True
                    if op2 == '+':
                        if n1 + n2 - n3 == result:
                            is_switched = True
                    else:
                        if n1 + n2 + n3 == result:
                            is_switched = True
                elif op1 == '-':
                    if n1 + n2 + n3 == result:
                        is_switched = True
                    if n1 + n2 - n3 == result:
                        is_switched = True
                    if op2 == '+':
                        if n1 - n2 - n3 == result:
                            is_switched = True
                    else:
                        if n1 - n2 + n3 == result:
                            is_switched = True
            
            return is_switched
        
        return False
                
    def wrong_answer(self, wm):
        logging.info(f'Executando função: wrong_answer')
        
        expression = wm.get_fact('expression')
        result = wm.get_fact('result')
        valid = wm.get_fact('valid')
            
        if valid:
            result = int(result[0])
            part1, part2 = expression.split('=')
            n = int(part2[0])
            
            return n != result
                
        return False
        
    def long_time(self, wm):
        logging.info(f'Executando função: long_time')
        valid = wm.get_fact('valid')
        
        in_time = False
        now = datetime.now()
        
        if valid:
            last_execution = wm.get_fact('last_execution')
            total_time = now - last_execution
            seconds = total_time.total_seconds()
            '''
            @ToDo calcular o tempo gasto teto em tempo de execução
            '''
            in_time = seconds > 4
                
        wm.add_fact('last_execution', now)
        return in_time
    
    def is_correct(self, wm):
        logging.info(f'Executando função: is_correct')
        correct = wm.get_fact('correct')
        print("Correct: ", correct)
