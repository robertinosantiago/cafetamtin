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
from pony.orm import *
from pygame.locals import *

from production.rule import Rule
from database.models import DBUser
from production.memory import Memory
from game.actors.student import Student
from production.level_checks import LevelChecks
from production.inference_engine import InferenceEngine

class LevelRules():
    
    def __init__(self, wm: Memory) -> None:
        self.wm = wm
        self.engine = InferenceEngine()
        self.checks = LevelChecks()
        self.define_rules()
        
    def define_rules(self):
        self.engine.add_rule(
            Rule(
                name = 'Erros de impulsividade',
                condition=lambda wm: self.checks.impulsive_errors(self.wm),
                action=self.decrease_inhibitory_control
            )
        )
        self.engine.add_rule(
            Rule(
                name = 'Insistir no mesmo erro',
                condition=lambda wm: self.checks.persist_same_error(self.wm),
                action=self.decrease_inhibitory_control
            )
        )
        self.engine.add_rule(
            Rule(
                name = 'Cometer erros mais comuns',
                condition=lambda wm: self.checks.most_common_errors(self.wm),
                action=self.decrease_inhibitory_control
            )
        )
        self.engine.add_rule(
            Rule(
                name = 'Tempo de resolução de problemas',
                condition=lambda wm: self.checks.problem_solving_time(self.wm),
                action=self.decrease_inhibitory_control
            )
        )
        self.engine.add_rule(
            Rule(
                name = 'Número de tentativas / comportamento motor',
                condition=lambda wm: self.checks.number_attempts(self.wm),
                action=self.decrease_inhibitory_control
            )
        )
        self.engine.add_rule(
            Rule(
                name = 'Baixa eficiência',
                condition=lambda wm: self.checks.is_student_efficiency_low(self.wm),
                action=self.decrease_inhibitory_control
            )
        )
        self.engine.add_rule(
            Rule(
                name = 'Eficiência média',
                condition=lambda wm: self.checks.is_student_efficiency_medium(self.wm),
                action=self.medium_inhibitory_control
            )
        )
        self.engine.add_rule(
            Rule(
                name = 'Alta eficiência',
                condition=lambda wm: self.checks.is_student_efficiency_high(self.wm),
                action=self.increase_inhibitory_control
            )
        )
        
    def decrease_inhibitory_control(self, wm: Memory, rule_name, weight):
        logging.info(f'Executando função: decrease_inhibitory_control')
        logging.info(f'Disparado por: {rule_name}')
        student: Student = wm.get_fact('student')
        logging.info(f'Atual Student ICC: {student.inhibitory_capacity_online}')
        
        if student.inhibitory_capacity_online == Student.INHIBITORY_CAPACITY_MEDIUM:
            student.inhibitory_capacity_online = Student.INHIBITORY_CAPACITY_LOW
        
        if student.inhibitory_capacity_online == Student.INHIBITORY_CAPACITY_HIGH:
            student.inhibitory_capacity_online = Student.INHIBITORY_CAPACITY_MEDIUM
        
        wm.add_fact('student', student)
        logging.info(f'Novo Student ICC: {student.inhibitory_capacity_online}')
        
            
    def increase_inhibitory_control(self, wm, rule_name, weight):
        logging.info(f'Executando função: increase_inhibitory_control')
        logging.info(f'Disparado por: {rule_name}')
        student: Student = wm.get_fact('student')
        logging.info(f'Atual Student ICC: {student.inhibitory_capacity_online}')
        
        if student.inhibitory_capacity_online == Student.INHIBITORY_CAPACITY_MEDIUM:
            student.inhibitory_capacity_online = Student.INHIBITORY_CAPACITY_HIGH
        
        if student.inhibitory_capacity_online == Student.INHIBITORY_CAPACITY_LOW:
            student.inhibitory_capacity_online = Student.INHIBITORY_CAPACITY_MEDIUM
        
        wm.add_fact('student', student)
        logging.info(f'Novo Student ICC: {student.inhibitory_capacity_online}')
        
    def medium_inhibitory_control(self, wm, rule_name, weight):
        logging.info(f'Executando função: medium_inhibitory_control')
        logging.info(f'Disparado por: {rule_name}')
        student: Student = wm.get_fact('student')
        logging.info(f'Atual Student ICC: {student.inhibitory_capacity_online}')
        
        responses = wm.get_fact('responses')
        if responses[-1]['is_correct']:
            student.inhibitory_capacity_online = Student.INHIBITORY_CAPACITY_MEDIUM
        
        wm.add_fact('student', student)
        logging.info(f'Novo Student ICC: {student.inhibitory_capacity_online}')
    
    def execute_rules(self):
        self.engine.execute_rules(self.wm)
        self.update_inhibitory_capacity_user(self.wm)
        
    @db_session
    def update_inhibitory_capacity_user(self, wm : Memory):
        student: Student = wm.get_fact('student')
        user = DBUser[student.id]
        user.inhibitory_capacity_online = student.inhibitory_capacity_online
        commit()