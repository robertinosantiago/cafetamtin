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
from production.memory import Memory

class Eficiency:
    LOW = 0
    MEDIUM = 1
    HIGH = 2

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
            x = r.sub('', part1).strip()
            n = [int(i) for i in x]
            n.sort()
            numbers_expression = ''.join(str(e) for e in n).strip()
            
            result.sort()
            result = ''.join(str(e) for e in result).strip()

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
        
        
        time = wm.get_fact('timer_response').total_time_seconds()
        max_time = wm.get_fact('average_time')
        
        print("time: ", time, "max: ", max_time)
        
        valid = wm.get_fact('valid')
        
        return time > max_time
        
    def long_time_old(self, wm):
        logging.info(f'Executando função: long_time')
        valid = wm.get_fact('valid')
        
        in_time = False
        end_time = datetime.now()
        
        
        start_time = wm.get_fact('start_time')
        total_time = end_time - start_time
        seconds = total_time.total_seconds()
        
        print('start_time: ' + start_time.strftime("%d-%m-%Y %H:%M:%S"))
        print('end_time: ' + end_time.strftime("%d-%m-%Y %H:%M:%S"))
        print(f'total seconds: {seconds}')
        '''
        @ToDo calcular o tempo gasto teto em tempo de execução
        '''
        #in_time = seconds > 4
                
        wm.add_fact('end_time', end_time)
        return in_time
    
    def many_errors(self, wm):
        logging.info(f'Executando função: many_errors')
        quantity_errors = wm.get_fact('quantity_errors')
        limit_errors = wm.get_fact('limit_errors')
        if (quantity_errors > limit_errors):
            wm.add_fact('quantity_errors', 0)
            return True
        return False
        
    
    def is_correct(self, wm):
        logging.info(f'Executando função: is_correct')
        expression = wm.get_fact('expression')
        result = wm.get_fact('result')
        valid = wm.get_fact('valid')
            
        if valid:
            result = int(result[0])
            part1, part2 = expression.split('=')
            n = int(part2[0])
            
            return n == result
                
        return False
    
    def impulsive_errors(self, wm: Memory):
        logging.info(f'Executando função: impulsive_errors')
        responses = wm.get_fact('responses')
        is_correct = wm.get_fact('is_correct')
        minimum_time = wm.get_fact('minimum_time')
        
        if is_correct:
            return False
        
        if len(responses) < 3:
            return False
        
        count = 0
        for response in responses:
            if not response['is_correct']:
                if response['reaction_time'] < minimum_time:
                    count += 1
        
        #@TODO: verificar como reagir quando já aconteceu isso
        
        return count >= 3
    
    def persist_same_error(self, wm: Memory):
        logging.info(f'Executando função: persist_same_error')
        #@TODO: verificar como reagir quando acerta. Zera os erros?
        history_errors = wm.get_fact('history_errors')
        if len(history_errors) < 2:
            return False
        
        return history_errors[-1] == history_errors[-2]
    
    def most_common_errors(self, wm: Memory):
        logging.info(f'Executando função: most_common_errors')
        return False
    
    def problem_solving_time(self, wm: Memory):
        logging.info(f'Executando função: time_per_step')
        time_per_step = wm.get_fact('time_per_step')
        if len(time_per_step) < 3:
            return False
        
        return time_per_step[-1] == time_per_step[-2] and time_per_step[-2] == time_per_step[-3]
    
    def number_attempts(self, wm: Memory):
        logging.info(f'Executando função: number_attemps')
        history_errors = wm.get_fact('history_errors')
        return len(history_errors) >= 5
    
    def is_student_efficiency_high(self, wm: Memory):
        logging.info(f'Executando função: is_student_efficiency_high')
        return self.student_efficiency(wm) == Eficiency.HIGH
    
    def is_student_efficiency_medium(self, wm: Memory):
        logging.info(f'Executando função: is_student_efficiency_medium')
        return self.student_efficiency(wm) == Eficiency.MEDIUM
    
    def is_student_efficiency_low(self, wm: Memory):
        logging.info(f'Executando função: is_student_efficiency_low')
        return self.student_efficiency(wm) == Eficiency.LOW
    
    def student_efficiency(self, wm: Memory):
        corrects = self.__get_corrects(wm)
        #step = wm.get_fact('step')
        step = len(wm.get_fact('responses'))
        index =  float(corrects) / float(step)
        logging.info(f'Student efficiency: {corrects} div {step} = {index}')
        if index <= 0.33:
            return Eficiency.LOW
        elif index > 0.66:
            return Eficiency.HIGH
        return Eficiency.MEDIUM
    
    def __get_corrects(self, wm: Memory):
        responses = wm.get_fact('responses')
        corrects = 0
        for response in responses:
            if response['is_correct']:
                corrects += 1
                
        return corrects
        
        
    
