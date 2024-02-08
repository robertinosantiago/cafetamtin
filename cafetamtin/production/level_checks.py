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

import math
import logging
from pony.orm import *

from production.error import Error
from production.memory import Memory
from production.eficiency import Eficiency
from production.type_error import TypeError
from database.models import DBChallengeP1, DBChallengeP2, DBChallengeP3, DBChallengeP4

class LevelChecks():
    
    def __init__(self) -> None:
        pass
    
    def impulsive_errors(self, wm: Memory):
        logging.info(f'Executando função: impulsive_errors')
        responses = wm.get_fact('responses')
        is_correct = wm.get_fact('is_correct')
        minimum_time = wm.get_fact('minimum_time')
        phase = wm.get_fact('phase')
        
        self.__get_first_quartil_phase01__(wm)
        
        if is_correct:
            return False
        
        if len(responses) < 3:
            return False
        
        if phase == 1:
            minimum_time = self.__get_first_quartil_phase01__(wm)
        if phase == 2:
            minimum_time = self.__get_first_quartil_phase02__(wm)
        if phase == 3:
            minimum_time = self.__get_first_quartil_phase03__(wm)
        if phase == 4:
            minimum_time = self.__get_first_quartil_phase04__(wm)
        
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
        phase = wm.get_fact('phase')
        if phase == 1:
            return self.__count_errors_phase01__(wm)
        if phase == 2:
            return self.__count_errors_phase02__(wm)
        if phase == 3:
            return self.__count_errors_phase03__(wm)
        if phase == 4:
            return self.__count_errors_phase04__(wm)
        return False
    
    def problem_solving_time(self, wm: Memory):
        logging.info(f'Executando função: problem_solving_time')
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
        
        if count == 0:
            return False
                
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
    
    @db_session
    def __count_errors_phase01__(self, wm: Memory):
        responses = wm.get_fact('responses') 
        
        data = select((p.type_error, p.subtype_error, count()) for p in DBChallengeP1 if p.is_correct == 0)
        ordered = sorted(data, key = lambda x: x[2], reverse=True)
        
        return self.__verify_errors_phases__(responses, ordered)
    
    @db_session
    def __count_errors_phase02__(self, wm: Memory):
        responses = wm.get_fact('responses') 
        
        data = select((p.type_error, p.subtype_error, count()) for p in DBChallengeP2 if p.is_correct == 0)
        ordered = sorted(data, key = lambda x: x[2], reverse=True)
        
        return self.__verify_errors_phases__(responses, ordered)
    
    @db_session
    def __count_errors_phase03__(self, wm: Memory):
        responses = wm.get_fact('responses') 
        
        data = select((p.type_error, p.subtype_error, count()) for p in DBChallengeP3 if p.is_correct == 0)
        ordered = sorted(data, key = lambda x: x[2], reverse=True)
        
        return self.__verify_errors_phases__(responses, ordered)
    
    @db_session
    def __count_errors_phase04__(self, wm: Memory):
        responses = wm.get_fact('responses') 
        
        data = select((p.type_error, p.subtype_error, count()) for p in DBChallengeP4 if p.is_correct == 0)
        ordered = sorted(data, key = lambda x: x[2], reverse=True)
        
        return self.__verify_errors_phases__(responses, ordered)
    
    def __verify_errors_phases__(self, responses, ordered) -> bool:
        if len(ordered) == 0:
            return False
        
        if len(responses) < 3:
            return False
        
        count = 0
        for response in responses:
            if response['type_error'] == ordered[0][0] and response['subtype_error'] == ordered[0][1]:
                count += 1
        
        if count == 0:
            return False
                
        return count % 3 == 0
    
    @db_session
    def __get_first_quartil_phase01__(self, wm: Memory):
        minimum_time = wm.get_fact('minimum_time')
        data = DBChallengeP1.select(lambda p: not p.is_correct).order_by(lambda p: p.reaction_time)[:]
        return self.__calculate_quartil__(data, minimum_time)
        
    @db_session
    def __get_first_quartil_phase02__(self, wm: Memory):
        minimum_time = wm.get_fact('minimum_time')
        data = DBChallengeP2.select(lambda p: not p.is_correct).order_by(lambda p: p.reaction_time)[:]
        return self.__calculate_quartil__(data, minimum_time)
    
    @db_session
    def __get_first_quartil_phase03__(self, wm: Memory):
        minimum_time = wm.get_fact('minimum_time')
        data = DBChallengeP3.select(lambda p: not p.is_correct).order_by(lambda p: p.reaction_time)[:]
        return self.__calculate_quartil__(data, minimum_time)
    
    @db_session
    def __get_first_quartil_phase04__(self, wm: Memory):
        minimum_time = wm.get_fact('minimum_time')
        data = DBChallengeP4.select(lambda p: not p.is_correct).order_by(lambda p: p.reaction_time)[:]
        return self.__calculate_quartil__(data, minimum_time)
        
    def __calculate_quartil__(self, data, minimum_time):
        if len(data) == 0:
            return minimum_time
        
        first_quartil = (len(data) + 1) * 0.25
        n1 = int(first_quartil)
        n2 = math.ceil(first_quartil)
        
        if n1 == n2:
            return data[n1].reaction_time
        
        return (data[n1].reaction_time + data[n2].reaction_time) / 2