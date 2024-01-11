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
        
        #@TODO: verificar como reagir quando já aconteceu isso
        
        return count >= 3
    
    def persist_same_error(self, wm: Memory):
        logging.info(f'Executando função: persist_same_error')
        #@TODO: verificar como reagir quando acerta. Zera os erros?
        #trocar para analizar o response
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
        
        #@TODO: corrigir para comparar com o tempo máximo e usar o response
        return time_per_step[-1] == time_per_step[-2] and time_per_step[-2] == time_per_step[-3]
    
    def number_attempts(self, wm: Memory):
        logging.info(f'Executando função: number_attemps')
        history_errors = wm.get_fact('history_errors')
        #@TODO: trocar para analizar o response
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