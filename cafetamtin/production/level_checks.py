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
import re
from datetime import datetime

from production.memory import Memory
from production.eficiency import Eficiency

class LevelChecks():
    
    def __init__(self) -> None:
        pass
    
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
        
        return count % 3 == 0
    
    def persist_same_error(self, wm: Memory):
        logging.info(f'Executando função: persist_same_error')
        responses = wm.get_fact('responses') 
        
        if len(responses) < 2:
            return False
        
        for i in range(-1,-3,-1):
            if responses[i]['is_correct']:
                return False

        return responses[-1]['type_error'] == responses[-2]['type_error'] and responses[-1]['subtype_error'] == responses[-2]['subtype_error']
    
    def most_common_errors(self, wm: Memory):
        logging.info(f'Executando função: most_common_errors')
        #@TODO: implementar a busca no banco de dados pelo erro mais comum
        return False
    
    def problem_solving_time(self, wm: Memory):
        logging.info(f'Executando função: time_per_step')
        responses = wm.get_fact('responses')
                
        if len(responses) < 3:
            return False
        
        count = 0
        for i in range(-1,-4,-1):
            if responses[i]['is_correct']:
                return False
            
            if responses[i]['reaction_time'] > responses[i]['max_time']:
                count += 1
        
        return count >= 3
    
    def number_attempts(self, wm: Memory):
        logging.info(f'Executando função: number_attemps')
        responses = wm.get_fact('responses')
        
        count = 0
        for response in responses:
            if not response['is_correct']:
                count += 1
                
        return count % 5 == 0
    
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