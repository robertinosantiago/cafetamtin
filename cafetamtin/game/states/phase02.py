# Copyright (C) 2022 Robertino Mendes Santiago Junior
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

import pygame
import os
import math
import random
import logging
from pony.orm import *
from datetime import datetime, timedelta

from base.board import Board
from base.facial import FacialThread
from game.states.state import State
from game.actors.teacher import Teacher
from game.actors.student import Student
from utils.timer import Timer
from utils.confetti import Confetti
from database.models import DBChallengeP2, DBSession, DBUser, DBSteps

from production.error import Error
from production.memory import Memory
from production.type_error import TypeError
from production.phase02_rules import Phase02Rules
from game.states.phase02_feedback import Phase02Feedback


from game import BACKGROUND_COLOR
from game import TEXT_COLOR
from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN

class Phase02(State):

    def __init__(self, game):
        super().__init__(game)
        
        self.memory = Memory()
        self.rules = Phase02Rules(self.memory)
        self.init_working_memory()
        
        self.board = Board(self.game.app)
        self.teacher = Teacher(self.game.game_canvas)
        self.show_teacher = False

        self.images = self.load_images()
        self.challenges = self.load_challenges()
        self.responses = []

        self.lives = 5
        self.score = 0
        self.max_steps = 8
        self.step = 0
        self.incremental_points = 5

        self.start_time = pygame.time.get_ticks()
        self.total_seconds = 10
        self.time_hms = 0, 0, 0
        self.total_time = self.start_time + self.total_seconds*1000

        self.enable_timer = False
        self.is_paused = False
        self.started = False
        self.new_challenge = True
        self.new_response = True
        self.end_phase = False

        self.timer_challenge = Timer()
        self.timer_teacher = Timer()
        self.timer_teacher.start()
        self.timer_response = Timer()

        self.tips_times = 0

        self.confetti = Confetti()
        self.frame_confetti = 1
        
        self.adjust_game_levels()
        self.starting_game()
        
    @db_session
    def init_working_memory(self):
        score = 0
        user  = DBUser[self.game.student.id]
        if len(user.steps) > 0:
            score = max(s.score for s in user.steps if s.status == 'completed')
            
        session = DBSession(
            start_time = datetime.now()
        )
        session.flush()
        self.memory.add_fact('student', self.game.student)
        self.memory.add_fact('session_id', session.id)
        self.memory.add_fact('game', self.game)
        self.memory.add_fact('challenges', self.load_challenges())
        self.memory.add_fact('quantity_corrects', 0)
        self.memory.add_fact('quantity_errors', 0)
        self.memory.add_fact('quantity_same_error', 0)
        self.memory.add_fact('limit_errors', 2)
        self.memory.add_fact('history_errors', [])
        self.memory.add_fact('tips_times', 0)
        self.memory.add_fact('step', 1)
        self.memory.add_fact('average_time', 60)
        self.memory.add_fact('minimum_time', 5)
        self.memory.add_fact('time_per_step', [])
        self.memory.add_fact('accumulated_time', 0)
        self.memory.add_fact('errors', [])
        self.memory.add_fact('responses', [])
        self.memory.add_fact('reset_timer', True)
        self.memory.add_fact('max_lives', 5)
        self.memory.add_fact('lives', 5)
        self.memory.add_fact('score', score)
        self.memory.add_fact('correct_points', 10)
        self.memory.add_fact('incorrect_points', 5)
        self.memory.add_fact('bonus_points', 5)
        self.memory.add_fact('new_challenge', True)
        self.memory.add_fact('started', False)
        
        self.memory.add_fact('timer_response', Timer())


    def load_images(self):
        return {
            'background': pygame.image.load(os.path.join("images", "classroom-background.png")),
            'heart': pygame.image.load(os.path.join("images", "heart.png")),
            'table': pygame.image.load(os.path.join("images", "table.png")),
            'student-desk': pygame.image.load(os.path.join("images", "student-desk.png")),
        }

    def handle_events(self, events):
        self.game.app.physical_buttons.white_button.set_callback(self.button_white_changed)
        self.game.app.physical_buttons.black_button.set_callback(self.button_black_changed)
        self.game.app.physical_buttons.green_button.set_callback(self.button_green_changed)
        self.game.app.physical_buttons.red_button.set_callback(self.button_red_changed)

        for event in events:
            if event.type == pygame.QUIT:
                self.exit_state()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()

                if event.key == pygame.K_UP:
                    pass

                if event.key == pygame.K_DOWN:
                    pass

                if event.key == pygame.K_RETURN or event.key == 1073741912:
                    pass

    def button_black_changed(self, data):
        pass

    def button_white_changed(self, data):
        if self.show_teacher:
            return
        
        if self.is_paused:
            self.memory.get_fact('timer_response').resume()
            interval = self.memory.get_fact('timer_response').get_time_resumed() - self.memory.get_fact('timer_response').get_time_paused()
            self.memory.add_fact('end_time', self.memory.get_fact('end_time') + timedelta(seconds=interval.seconds))
            self.is_paused = False
        else:
            self.memory.get_fact('timer_response').pause()
            self.is_paused = True

    def button_green_changed(self, data):
        """
        Executed when the green button of the base is pressed
        """
        if self.show_teacher:
            return

        if self.is_paused:
            return
        
        self.memory.get_fact('timer_response').stop()

        if self.teacher.has_next_message():
            self.teacher.clear_messages()


        self.teacher.set_message(
            "Verificando...\n"+
            "Aguarde.", 
            "neutral0"
        )
        self.teacher.next_message()
        self.show_teacher = True

        #TODO: capturar a imagem do rosto
        self.board.avaliable_board()
        self.board.draw_matrix_board()
        self.check_challenge()
        #self.memory.add_fact('started', False)
    
    def button_red_changed(self, data):
        if self.is_paused:
            return
        
        if not self.show_teacher:
            self.memory.get_fact('timer_response').pause()
            
            tips_times = self.memory.get_fact('tips_times')
            self.memory.add_fact('tips_times', tips_times + 1)
            
            self.teacher.set_message(
                'Dicas',
                'neutral1'
            )
            
        if self.teacher.has_next_message():
            self.teacher.next_message()
            self.show_teacher = True
        else:
            self.show_teacher = False
            
            if not self.memory.get_fact('started'):
                self.memory.add_fact('started', True)
                self.memory.add_fact('reset_timer', True)
                self.memory.add_fact('tips_times', 0)
                self.tips_times = 0
            else:
                if self.memory.get_fact('timer_response').is_paused():
                    self.memory.get_fact('timer_response').resume()
                    interval = self.memory.get_fact('timer_response').get_time_resumed() - self.memory.get_fact('timer_response').get_time_paused()
                    self.memory.add_fact('end_time', self.memory.get_fact('end_time') + timedelta(seconds=interval.seconds))
                    
        if self.memory.get_fact('step') >= self.max_steps:
            step = self.memory.get_fact('step')
            step += 1
            step = self.memory.add_fact('step', step)
            self.save_steps(2, 'completed')
            self.save_steps(3, 'not-started')
                
        if self.memory.get_fact('lives') == 0 and self.end_phase:
            self.memory.add_fact('lives', -1)
            #self.save_challenge()
            self.save_steps(2, 'not-completed')
        
        if self.end_phase and not self.show_teacher:
            self.exit_state()


    def load_challenges(self):
        challenges = {
            '159': {'equations': ['1 + 5 + 9', '1 + 9 + 5', '5 + 1 + 9', '5 + 9 + 1', '9 + 1 + 5', '9 + 5 + 1'], 'visible': False, 'index': random.randrange(0, 6)},
            '168': {'equations': ['1 + 6 + 8', '1 + 8 + 6', '6 + 1 + 8', '6 + 8 + 1', '8 + 1 + 6', '8 + 6 + 1'], 'visible': False, 'index': random.randrange(0, 6)},
            '249': {'equations': ['2 + 4 + 9', '2 + 9 + 4', '4 + 2 + 9', '4 + 9 + 2', '9 + 2 + 4', '9 + 4 + 2'], 'visible': False, 'index': random.randrange(0, 6)},
            '258': {'equations': ['2 + 5 + 8', '2 + 8 + 5', '5 + 2 + 8', '5 + 8 + 2', '8 + 2 + 5', '8 + 5 + 2'], 'visible': False, 'index': random.randrange(0, 6)},
            '267': {'equations': ['2 + 6 + 7', '2 + 7 + 6', '6 + 2 + 7', '6 + 7 + 2', '7 + 2 + 6', '7 + 6 + 2'], 'visible': False, 'index': random.randrange(0, 6)},
            '348': {'equations': ['3 + 4 + 8', '3 + 8 + 4', '4 + 3 + 8', '4 + 8 + 3', '8 + 3 + 4', '8 + 4 + 3'], 'visible': False, 'index': random.randrange(0, 6)},
            '357': {'equations': ['3 + 5 + 7', '3 + 7 + 5', '5 + 3 + 7', '5 + 7 + 3', '7 + 3 + 5', '7 + 5 + 3'], 'visible': False, 'index': random.randrange(0, 6)},
            '456': {'equations': ['4 + 5 + 6', '4 + 6 + 5', '5 + 4 + 6', '5 + 6 + 4', '6 + 4 + 5', '6 + 5 + 4'], 'visible': False, 'index': random.randrange(0, 6)},
        }
        return challenges
    
    def count_challenges_visible(self):
        count = 0
        challenges = self.memory.get_fact('challenges')
        for key, value in challenges.items():
            if value['visible']:
                count += 1
        return count
            
        
    def starting_game(self):
        if not self.started:
            self.teacher.set_message(
                "Atenção!\n"+
                "Prepare-se para começar. Tente responder o mais rápido possível. "+
                "\n\nPressione o botão VERMELHO para continuar", 
                "neutral1"
            )
            self.teacher.next_message()
            self.show_teacher = True

    def update(self, delta_time):
        pass

    def draw_physical_buttons(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        baseline_text = screen_height - 35
        baseline_circle = screen_height - 23
        
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        
        pygame.draw.circle(display,RED,(130,baseline_circle),10)
        text = "Dicas"
        if self.show_teacher:
            if self.teacher.has_next_message():
                text = "Continuar"
            else:
                text = "Fechar"
        red_text = font.render(text, True, (0,0,0))
        display.blit(red_text, (145, baseline_text))

        if not self.show_teacher:
            pygame.draw.circle(display,WHITE,(20,baseline_circle),10)
            white_text = font.render("Pausar", True, (0,0,0))
            display.blit(white_text, (35, baseline_text))

            pygame.draw.circle(display,GREEN,(220,baseline_circle),10)
            green_text = font.render("Responder", True, (0,0,0))
            display.blit(green_text, (235, baseline_text))
    
    def draw_lifes(self):
        display = self.game.game_canvas
        for i in range(0, self.memory.get_fact('lives')):
            heart = self.images['heart']
            heart_rect = heart.get_rect()
            heart_rect.x = 10 + 50 * i
            heart_rect.y = 5
            display.blit(heart, heart_rect)
            
    
    def draw_timer(self):
        display = self.game.game_canvas
        timer_font = pygame.font.Font(os.path.join("fonts", "digital-7.ttf"), 40)
        screen_width = self.game.GAME_WIDTH
        reset_timer = self.memory.get_fact('reset_timer')
                
        if reset_timer and not self.show_teacher:
            self.memory.add_fact('reset_timer', False)
            self.memory.get_fact('timer_response').stop()
            self.memory.get_fact('timer_response').start()
            self.memory.add_fact('end_time', datetime.now() + timedelta(seconds=self.memory.get_fact('amount_time')))
        
        if not self.memory.get_fact('timer_response').is_paused() and self.memory.get_fact('timer_response').is_started() and not self.show_teacher:
            time_left = max(self.memory.get_fact('end_time') - datetime.now(), timedelta(0))

            if time_left.seconds > 0:
                self.time_hms = self.convert_time(time_left.seconds)
            else:
                self.end_timer()

            timer_text = timer_font.render(f'{self.time_hms[1]:02d}:{self.time_hms[2]:02d}', True, (255, 0, 0))
            timer_text_rect = timer_text.get_rect(center=(screen_width/2, 20))
            display.blit(timer_text, timer_text_rect)
        
            
    def end_timer(self):
        #@TODO: verificar se é melhor iniciar o Feedback
        student: Student = self.memory.get_fact('student')
        if student.inhibitory_capacity_online != Student.INHIBITORY_CAPACITY_LOW:
            self.memory.add_fact('reset_timer', True)
            
            self.memory.get_fact('timer_response').stop()
            self.memory.add_fact('is_correct', False)
            
            response = {}
            response['number01'] = -1
            response['number02'] = -1
            response['number03'] = -1
            response['is_correct'] = False
            response['start_time'] = self.memory.get_fact('timer_response').get_time_started()
            response['end_time'] = self.memory.get_fact('timer_response').get_time_finished()
        
            response['reaction_time'] = self.memory.get_fact('timer_response').total_time_seconds()
            response['reaction_time_without_pauses'] = self.memory.get_fact('timer_response').total_time_without_paused_seconds()
            response['paused_counter'] = self.memory.get_fact('timer_response').total_times_paused() - self.memory.get_fact('tips_times')
            response['tips_counter'] = self.memory.get_fact('tips_times')
            response['max_time'] = self.memory.get_fact('average_time')

            response['affective_state'] = ''
            response['affective_quad'] = ''
            
            response['type_error'] = TypeError.ERROR_TIMEOUT
            response['subtype_error'] = TypeError.SUBTYPE_NONE
            
            self.memory.get_fact('responses').append(response)
            
            self.save_challenge(response)
            
            history_errors = self.memory.get_fact('history_errors')
            history_errors.append(Error(type=TypeError.ERROR_TIMEOUT, subtype=TypeError.SUBTYPE_NONE))
            self.memory.add_fact('history_errors', history_errors)
            
            quantity_errors = self.memory.get_fact('quantity_errors')
            quantity_errors += 1
            self.memory.add_fact('quantity_errors', quantity_errors)
            
            self.teacher.set_message(
                f"Preste atenção {student.nickname}!!! Tente resolver o \n"+
                "exercício antes que o tempo acabe. Mantenha o foco \n"+
                "na resolução dos exercícios.\n"+
                "\n\nPressione o botão VERMELHO para continuar",  
                "neutral1"
            )
            self.teacher.next_message()
            self.show_teacher = True
            self.lose_life()
            
    def lose_life(self):
        lives = self.memory.get_fact('lives')
        if lives > 0:
            self.memory.add_fact('lives', lives - 1)
            self.start_time = pygame.time.get_ticks()
            self.total_time = self.start_time + self.total_seconds*1000
    
    def draw_table(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT

        table = self.images['table']
        table_rect = table.get_rect(center=(screen_width/2, 410))
        display.blit(table, table_rect)

    def draw_student_desk(self, quantity = 4):
        display = self.game.game_canvas
        student_desk = self.images['student-desk']

        x_coordenate = []
        if (quantity == 1):
            x_coordenate = [160]
        elif (quantity == 2):
            x_coordenate = [160, 580]
        else:
            x_coordenate = [-80, 160, 590, 830]

        for x in x_coordenate:
            student_desk_rect = student_desk.get_rect(topleft=(x,380))
            display.blit(student_desk, student_desk_rect)
    
    def draw_pause(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
                
        rect_background = (0,0,screen_width,screen_height)
        shape_surf = pygame.Surface(pygame.Rect(rect_background).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (0,0,0,230), shape_surf.get_rect())
        display.blit(shape_surf, rect_background)

        font = pygame.font.SysFont(FONT_NAME, 72, False, False)
        instruction_text = font.render('Pause', True, (220,220,220))
        instruction_text_rect = instruction_text.get_rect(center=(screen_width/2, screen_height/2))
        display.blit(instruction_text, instruction_text_rect)
    
    def draw_challenge(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        color = (213, 255, 213)

        font = pygame.font.SysFont(FONT_NAME, 22, False, False)
        instruction_text = font.render('Encontre as somas com 3 números que resultam 15', True, (220,220,220))
        instruction_text_rect = instruction_text.get_rect(center=(screen_width/2, 90))

        if not self.show_teacher and not self.is_paused:
            display.blit(instruction_text, instruction_text_rect)

            i = 1
            width = 140
            height = 60
            offset = 20
            x = 160
            y = 150
            challenges = self.memory.get_fact('challenges')
            for key in challenges.keys():
                rect = (x,y,width,height)
                shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                pygame.draw.rect(shape, color, shape.get_rect(), border_radius= 15)
                display.blit(shape, rect)
                inner_text = '? + ? + ?' if not challenges[key]['visible'] else challenges[key]['equations'][challenges[key]['index']]
                text = font.render(inner_text, True, BLACK if not challenges[key]['visible'] else GREEN)
                text_rect = text.get_rect(center=(x + width/2, y + height/2))
                display.blit(text, text_rect)
                if i % 4 == 0:
                    x = 160
                    y += height + offset
                else:
                    x += width + offset
                i += 1

    def check_challenge(self):
        blocks = self.board.result_matrix_board()
        self.memory.add_fact('result', blocks)
        
        self.rules.execute_rules()
        
        feedback = Phase02Feedback(self.game, self.memory)
        feedback.enter_state()
        
        self.teacher.clear_messages()
        self.show_teacher = False
        
        if self.memory.get_fact('lives') == 0:
            self.teacher.set_message(
                "Infelizmente, você não conseguiu "+
                "encontrar todas as combinações.\n\n"+
                "Tente novamente!\n"
                "\n"+
                "Pressione o botão VERMELHO para continuar", 
                "neutral1"
            )
            self.end_phase = True
            self.teacher.next_message()
            self.show_teacher = True
            

        if self.count_challenges_visible() >= self.max_steps and not self.end_phase:
            self.teacher.set_message(
                "Parabéns!!! Você encontrou todas "+
                "as somas possíveis com 3 números "+
                "que resultam em 15. Nos vemos na "+
                "próxima fase.\n"+
                "\n"+
                "Pressione o botão VERMELHO para continuar",
                "heart0"
            )
            self.end_phase = True
            self.teacher.next_message()
            self.show_teacher = True
    
    @db_session
    def save_challenge(self, response) -> None:
        user = DBUser[self.game.student.id]
        session = DBSession[int(self.memory.get_fact('session_id'))]
        challenge = DBChallengeP2(
            number01 = response['number01'],
            number02 = response['number02'],
            number03 = response['number03'],
            is_correct = response['is_correct'],
            start_time = response['start_time'],
            end_time = response['end_time'],
            reaction_time = response['reaction_time'],
            reaction_time_without_pauses = response['reaction_time_without_pauses'],
            pauses_counter = response['paused_counter'],
            tips_counter = response['tips_counter'],
            affective_state = response['affective_state'],
            affective_quad = response['affective_quad'],
            type_error = response['type_error'],
            subtype_error = response['subtype_error'],
            user = user,
            session = session
        )
        challenge.flush()
        facialThread = FacialThread(self.game.app, challenge.id, self.update_challenge)
        facialThread.start()
    
    @db_session
    def update_challenge(self, id, expression, quad):
        logging.info(f'Atualizando challenge')
        challenge = DBChallengeP2[id]
        challenge.set(affective_state = expression, affective_quad = quad)
        challenge.flush()
        logging.info(f'Atualizado')

    @db_session
    def save_steps(self, phase, status):
        user = DBUser[self.game.student.id]
        step = DBSteps(
            phase = phase,
            score = self.memory.get_fact('score'),
            lifes = self.memory.get_fact('lives'),
            status = status,
            user = user
        )
        commit()

    def adjust_game_levels(self):
        student: Student = self.memory.get_fact('student')
        
        average_time = self.memory.get_fact('average_time')
        
        if student.inhibitory_capacity_online == Student.INHIBITORY_CAPACITY_LOW:
            self.memory.add_fact('amount_time', average_time)
            self.memory.add_fact('enable_timer', False)
        elif student.inhibitory_capacity_online == Student.INHIBITORY_CAPACITY_MEDIUM:
            self.memory.add_fact('amount_time', average_time)
            self.memory.add_fact('enable_timer', True)
        else:
            self.memory.add_fact('amount_time', math.ceil(average_time * 0.5))
            self.memory.add_fact('enable_timer', True)
            
        self.enable_timer = self.memory.get_fact('enable_timer')

    def render(self, display):

        display.fill((255,255,255))

        background = self.images['background']
        display.blit(background, (0,0))
        self.draw_table()
        self.draw_student_desk()
        self.draw_lifes()
        self.draw_score()
        self.draw_student_name()
        self.draw_physical_buttons()
        
        if self.show_teacher:
            self.teacher.draw()

        if self.is_paused:
            self.draw_pause()
        
        if self.confetti.visible:
            self.draw_confetti()
        
        if self.lives > 0 and self.count_challenges_visible() < self.max_steps:
            self.draw_challenge()
            
            if self.memory.get_fact('enable_timer') and not self.show_teacher:
                self.draw_timer()

