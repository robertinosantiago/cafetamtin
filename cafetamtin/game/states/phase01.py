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

import sys
import os
import math
import random
import pygame
import logging
from pygame.locals import *
from pony.orm import *
from datetime import datetime, timedelta

from game import BACKGROUND_COLOR
from game import TEXT_COLOR
from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN

from game.states.state import State
from game.actors.teacher import Teacher
from game.actors.student import Student
from base.board import Board
from base.leds import Leds, RainbowThread
from base.facial import FacialThread
from utils.timer import Timer
from utils.confetti import Confetti
from database.models import DBChallengeP1, DBSession, DBSteps, DBUser
from production.error import Error
from production.memory import Memory
from production.type_error import TypeError
from production.phase01_rules import Phase01Rules
from game.states.phase01_feedback import Phase01Feedback


class Phase01(State):
    
    def __init__(self, game):
        super().__init__(game)

        self.memory = Memory()
        self.rules = Phase01Rules(self.memory)
        self.init_working_memory()
                
        #self.facial = self.game.app.facial #FacialThread(self.game.app)
        self.board = Board(self.game.app)
        self.teacher = Teacher(self.game.game_canvas)
        self.show_teacher = False

        self.menu_items = ['Voltar']
        self.menu_selection = 0

        self.lives = 5
        self.score = 0
        self.max_steps = 20
        self.num_terms = 2
        self.incremental_points = 5

        self.min_number = 1
        self.max_number = 10

        self.images = self.load_images()
        
        #self.start_time = pygame.time.get_ticks()
        #self.total_seconds = 10
        self.time_hms = 0, 0, 0
        #self.total_time = self.start_time + self.total_seconds*1000

        self.enable_timer = False
        self.is_paused = False
        self.started = False
        self.end_phase = False

        self.new_challenge = True
        self.challenge = ()
        self.responses = []
        self.operators = self.generate_operators()
        self.generate_new_challenge()
        
        self.leds = Leds()
        self.rainbow = RainbowThread()
        self.confetti = Confetti()
        self.frame_confetti = 1
        
        self.adjust_game_levels()

        self.starting_game()

    @db_session
    def init_working_memory(self):
        session = DBSession(
            start_time = datetime.now()
        )
        session.flush()
        self.memory.add_fact('student', self.game.student)
        self.memory.add_fact('session_id', session.id)
        self.memory.add_fact('game', self.game)
        self.memory.add_fact('num_terms', 2)
        self.memory.add_fact('quantity_corrects', 0)
        self.memory.add_fact('quantity_errors', 0)
        self.memory.add_fact('quantity_same_error', 0)
        self.memory.add_fact('limit_errors', 5)
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
        self.memory.add_fact('score', 0)
        self.memory.add_fact('correct_points', 10)
        self.memory.add_fact('incorrect_points', 5)
        self.memory.add_fact('bonus_points', 5)
        
        self.memory.add_fact('timer_response', Timer())
        
    def load_images(self):
        return {
            'background': pygame.image.load(os.path.join("images", "classroom-background.png")),
            'heart': pygame.image.load(os.path.join("images", "heart.png")),
            'table': pygame.image.load(os.path.join("images", "table.png")),
            'student-desk': pygame.image.load(os.path.join("images", "student-desk.png")),
            'arrow-red': pygame.image.load(os.path.join("images", "arrow-red.png")),
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
                if event.key == pygame.K_f:
                    self.button_green_changed(True)
                    return
                
                if event.key == pygame.K_v:
                    self.button_red_changed(True)
                    
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()

    def update(self, delta_time):
        pass

    def button_white_changed(self, data):
        """
        Executed when the white button of the base is pressed
        """
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

        #self.facial.evaluate()
        self.board.avaliable_board()
        self.board.draw_matrix_board()
        self.check_challenge()

    def button_red_changed(self, data):
        """
        Executed when the red button of the base is pressed
        """
        if self.is_paused:
            return

        if not self.show_teacher:
            self.memory.get_fact('timer_response').pause()
            
            tips_times = self.memory.get_fact('tips_times')
            self.memory.add_fact('tips_times', tips_times + 1)
            
            self.teacher.set_message(
                "Dicas", 
                "neutral0"
            )

        if self.teacher.has_next_message():
            self.teacher.next_message()
            self.show_teacher = True
            #self.leds.turnOff()

        else:
            self.show_teacher = False
            
            if not self.started:
                self.memory.add_fact('reset_timer', True)
                self.enable_timer = self.memory.get_fact('enable_timer')
                self.started = True
                
            #self.leds.central_led()

            if self.memory.get_fact('step') == self.max_steps:
                step = self.memory.get_fact('step')
                step += 1
                step = self.memory.add_fact('step', step)
                self.save_steps(1, 'completed')
                self.save_steps(2, 'not-started')
                
            if self.end_phase and self.memory.get_fact('lives') == 0:
                self.memory.get_fact('lives', -1)
                self.save_steps(1, 'not-completed')
            
            if self.new_challenge:
                #@TODO: verificar o motivo de estar startando quando pausado
                self.memory.get_fact('timer_response').start()
                #now = datetime.now()
                #self.memory.add_fact('start_time', now)
                #self.total_time = self.memory.get_fact('amount_time')
                self.memory.add_fact('end_time', datetime.now() + timedelta(seconds=self.memory.get_fact('amount_time')))
                self.new_challenge = False
            else:
                self.memory.get_fact('timer_response').resume()
                interval = self.memory.get_fact('timer_response').get_time_resumed() - self.memory.get_fact('timer_response').get_time_paused()
                self.memory.add_fact('end_time', self.memory.get_fact('end_time') + timedelta(seconds=interval.seconds))
            
            if self.end_phase and not self.show_teacher:
                self.exit_state()


    def button_black_changed(self, data):
        """
        Executed when the black button of the base is pressed
        """
        pass
    
    def turn_on_led(self):
        pass
        #self.leds.central_led()
        
    def control_timer(self):
        pass

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


    def check_challenge(self):
        blocks = self.board.result_matrix_board()
        
        expression = ''
        numbers, operators, result = self.challenge
        if self.num_terms == 2:
            expression = f'{numbers[0]}{operators[0]}{numbers[1]}={result}'
        else:
            expression = f'{numbers[0]}{operators[0]}{numbers[1]}{operators[1]}{numbers[2]}={result}'
            
        self.memory.add_fact('expression', expression)
        self.memory.add_fact('result', blocks)
        
        self.rules.execute_rules()
        
        feedback = Phase01Feedback(self.game, self.memory)
        feedback.enter_state()
        self.num_terms = self.memory.get_fact('num_terms')
        self.generate_new_challenge()
                
        if self.memory.get_fact('lives') == 0:
            #@colocar a mensagem 'tente novamente' caso haja mais rodadas
            self.teacher.set_message(
                "Infelizmente, você não conseguiu "+
                "realizar todas as operações corretamente. "+
                "Tente novamente!"
                "\n\nPressione o botão VERMELHO para continuar",
                "neutral1"
            )
            self.end_phase = True
        
        if self.memory.get_fact('step') >= self.max_steps and not self.end_phase:
            self.teacher.set_message(
                "Parabéns!!! Você conseguiu realizar "+
                "as operações corretamente. Nos vemos na "+
                "próxima fase."+
                "\n\nPressione o botão VERMELHO para continuar",
                "heart0"
            )
            self.end_phase = True
            self.teacher.next_message()
            self.show_teacher = True
        else:
            self.teacher.clear_messages()
            self.show_teacher = False

    def draw_lifes(self):
        display = self.game.game_canvas
        for i in range(0, self.memory.get_fact('lives')):
            heart = self.images['heart']
            heart_rect = heart.get_rect()
            heart_rect.x = 10 + 50 * i
            heart_rect.y = 5
            display.blit(heart, heart_rect)

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

    def draw_timer(self):
        display = self.game.game_canvas
        timer_font = pygame.font.Font(os.path.join("fonts", "digital-7.ttf"), 40)
        screen_width = self.game.GAME_WIDTH
        reset_timer = self.memory.get_fact('reset_timer')
        end_time = self.memory.get_fact('end_time')
        
        if not self.memory.get_fact('timer_response').is_paused() and not self.show_teacher:
            time_left = max(end_time - datetime.now(), timedelta(0))

            if time_left.seconds > 0:
                self.time_hms = self.convert_time(time_left.seconds)
            else:
                self.end_timer()

            timer_text = timer_font.render(f'{self.time_hms[1]:02d}:{self.time_hms[2]:02d}', True, (255, 0, 0))
            timer_text_rect = timer_text.get_rect(center=(screen_width/2, 20))
            display.blit(timer_text, timer_text_rect)
            
        if reset_timer and not self.show_teacher:
            self.memory.add_fact('reset_timer', False)
            self.memory.get_fact('timer_response').stop()
            self.memory.get_fact('timer_response').start()
            self.memory.add_fact('end_time', datetime.now() + timedelta(seconds=self.memory.get_fact('amount_time')))

    def end_timer(self):
        student: Student = self.memory.get_fact('student')
        if student.inhibitory_capacity_online != Student.INHIBITORY_CAPACITY_LOW:
            self.memory.add_fact('reset_timer', True)
            
            self.memory.get_fact('timer_response').stop()
            
            #@TODO: verificar como baixar o ICC
            
            response = {}
            response['step'] = self.memory.get_fact('step')
            response['reaction_time'] = self.memory.get_fact('timer_response').total_time_seconds()
            response['reaction_time_without_pauses'] = self.memory.get_fact('timer_response').total_time_without_paused_seconds()
            response['paused_counter'] = self.memory.get_fact('timer_response').total_times_paused() - self.memory.get_fact('tips_times')
            response['tips_counter'] = self.memory.get_fact('tips_times')
            response['max_time'] = self.memory.get_fact('average_time')

            response['start_time'] = self.memory.get_fact('timer_response').get_time_started()
            response['end_time'] = self.memory.get_fact('timer_response').get_time_finished()
            response['affective_state'] = ''
            response['affective_quad'] = ''
            
            response['type_error'] = TypeError.ERROR_TIMEOUT
            response['subtype_error'] = TypeError.SUBTYPE_NONE
            
            expression = ''
            numbers, operators, result = self.challenge
            if self.num_terms == 2:
                expression = f'{numbers[0]}{operators[0]}{numbers[1]}={result}'
            else:
                expression = f'{numbers[0]}{operators[0]}{numbers[1]}{operators[1]}{numbers[2]}={result}'
                
            self.memory.add_fact('expression', expression)
            
            part1, part2 = expression.split('=')
        
            response['number01'] = int(part1[0])
            response['operator01'] = part1[1]
            response['number02'] = int(part1[2])
            if len(part1) == 3:
                response['operator02'] = ''
                response['number03'] = 0
            else:
                response['operator02'] = part1[3]
                response['number03'] = int(part1[4])
                
            response['expected_result'] = int(part2)
            response['informed_result'] = -1
            response['is_correct'] = False
            
            self.memory.add_fact('is_correct', False)
            self.memory.get_fact('responses').append(response)
            
            self.save_challenge(response)
            
            history_errors = self.memory.get_fact('history_errors')
            history_errors.append(Error(type=TypeError.ERROR_TIMEOUT, subtype=TypeError.SUBTYPE_NONE))
            self.memory.add_fact('history_errors', history_errors)
            
            quantity_errors = self.memory.get_fact('quantity_errors')
            quantity_errors += 1
            self.memory.add_fact('quantity_errors', quantity_errors)
            
            self.teacher.set_message(
                f"Preste atenção {student.nickname}!!! Tente resolver o "+
                "exercício antes que o tempo acabe. Mantenha o foco "+
                "na resolução dos exercícios."+
                "\n\nPressione o botão VERMELHO para continuar",  
                "neutral1"
            )
            self.teacher.next_message()
            self.show_teacher = True
            #self.memory.add_fact('lives', self.memory.get_fact('lives') - 1)
            self.lose_life()
            
            #@TODO: ajustar o game level
            self.generate_new_challenge()
    
    
    def lose_life(self):
        if self.memory.get_fact('lives') > 0:
            #self.lives -= 1
            self.memory.add_fact('lives', self.memory.get_fact('lives') - 1)
            #self.start_time = pygame.time.get_ticks()
            #self.total_time = self.start_time + self.total_seconds*1000
            #self.new_challenge = True

    def draw_challenge(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT

        font = pygame.font.SysFont(FONT_NAME, 30, False, False)
        instruction_text = font.render('Informe o resultado da operação', True, (220,220,220))
        instruction_text_rect = instruction_text.get_rect(center=(screen_width/2, 120))

        font = pygame.font.SysFont(FONT_NAME, 72, False, False)
        expression = ''
        numbers, operators, result = self.challenge
        if self.num_terms == 2:
            expression = f'{numbers[0]} {operators[0]} {numbers[1]}'
        else:
            expression = f'{numbers[0]} {operators[0]} {numbers[1]} {operators[1]} {numbers[2]}'
        challenge_text = font.render(expression, True, (220,220,220))
        challenge_text_rect = challenge_text.get_rect(center=(screen_width/2, 220))

        if not self.show_teacher and not self.is_paused:
            display.blit(instruction_text, instruction_text_rect)
            display.blit(challenge_text, challenge_text_rect)
        
    def generate_operators(self):
        operators = ['+', '-']
        result = []

        for i in range(0, self.max_steps):
            op = operators[random.randrange(0, len(operators))]
            
            if len(result) > 1:
                if op == result[-1] and op == result[-2]:
                    if op == operators[0]:
                        op = operators[1]
                    else:
                        op = operators[0]
            result.append(op)
        return result
    
    def generate_new_challenge(self):
        self.challenge = self.random_calc()
        self.responses = []
        self.new_challenge = True
        self.memory.add_fact('tips_times', 0)



    def random_calc(self):
        if self.num_terms == 2:
            return self.random_calc_2_terms()
        else:
            return self.random_calc_3_terms()
        
    def random_calc_2_terms(self):
        numbers = random.sample(range(1, 10), 3)
        operators = []
        operators.append(random.choice(['+', '-']))
        result = 0
        
        if operators[0] == '+':
            result = numbers[0] + numbers[1]
        else:
            result = numbers[0] - numbers[1]
            
        if result < 1 or result > 9:
            return self.random_calc_2_terms()
        
        return numbers, operators, result
    
    def random_calc_3_terms(self):
        numbers = random.sample(range(1, 10), 3)
        operators = []
        operators.append(random.choice(['+']))
        operators.append(random.choice(['+', '-']))
        result = 0
        
        if operators[0] == '+':
            if operators[1] == '+':
                result = numbers[0] + numbers[1] + numbers[2]
            else:
                result = numbers[0] + numbers[1] - numbers[2]
        if result < 1 or result > 9:
            return self.random_calc_3_terms()
        
        return numbers, operators, result

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
        #@TODO: pausar o timer
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
        
    def draw_confetti(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        frame = self.confetti.get_image(self.frame_confetti)
        frame_rect = frame.get_rect(center=(screen_width/2, screen_height/2 - 80))
        display.blit(frame, frame_rect)
        self.frame_confetti += 1
        if self.frame_confetti > self.confetti.total_frames:
            self.confetti.visible = False

    def exit_state(self):
        super().exit_state()
        #self.leds.turnOff()
        self.memory.get_fact('timer_response').stop()
    
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
    
    @db_session
    def save_challenge(self, response):
        user = DBUser[self.game.student.id]
        session = DBSession[int(self.memory.get_fact('session_id'))]
        challenge = DBChallengeP1(
            number01 = response['number01'],
            number02 = response['number02'],
            number03 = response['number03'],
            operator01 = response['operator01'],
            operator02 = response['operator02'],
            expected_result = response['expected_result'],
            informed_result = response['informed_result'],
            is_correct = response['is_correct'],
            start_time = response['start_time'],
            end_time = response['end_time'],
            reaction_time = response['reaction_time'],
            reaction_time_without_pauses = response['reaction_time_without_pauses'],
            # @TODO: corrigir o nome desse atributo no modelo
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
        challenge = DBChallengeP1[id]
        challenge.set(affective_state = expression, affective_quad = quad)
        challenge.flush()
        logging.info(f'Atualizado')
        
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
        
        if self.memory.get_fact('lives') > 0 and self.memory.get_fact('step') <= self.max_steps:

            self.draw_challenge()

        #self.draw_timer()
            if self.memory.get_fact('enable_timer') and not self.show_teacher:
                self.draw_timer()
