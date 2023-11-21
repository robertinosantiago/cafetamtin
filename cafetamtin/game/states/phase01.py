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
import random
import pygame
from pygame.locals import *
from pony.orm import *
from datetime import datetime

from game import BACKGROUND_COLOR
from game import TEXT_COLOR
from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN

from game.states.state import State
from game.actors.teacher import Teacher
from base.board import Board
from base.leds import Leds, RainbowThread
from base.facial import FacialThread
from utils.timer import Timer
from utils.confetti import Confetti
from database.models import DBUser, DBSteps, DBChallengeP1, DBResponseP1
from production.memory import Memory
from production.phase01_rules import Phase01Rules
from game.states.phase01_feedback import Phase01Feedback


class Phase01(State):
    
    def __init__(self, game):
        super().__init__(game)

        self.memory = Memory()
        self.rules = Phase01Rules(self.memory)
        self.init_working_memory()
                
        self.facial = self.game.app.facial #FacialThread(self.game.app)
        self.board = Board(self.game.app)
        self.teacher = Teacher(self.game.game_canvas)
        self.show_teacher = False

        self.menu_items = ['Voltar']
        self.menu_selection = 0

        self.lives = 3
        self.score = 0
        self.max_steps = 10
        self.num_terms = 2
        self.step = 1
        self.incremental_points = 5

        self.min_number = 1
        self.max_number = 10

        self.images = self.load_images()
        
        self.start_time = pygame.time.get_ticks()
        self.total_seconds = 10
        self.time_hms = 0, 0, 0
        self.total_time = self.start_time + self.total_seconds*1000

        self.enable_timer = False
        self.is_paused = False
        self.started = False
        self.end_phase = False

        self.new_challenge = True
        self.challenge = ()
        self.responses = []
        self.operators = self.generate_operators()
        self.generate_new_challenge()
        
        # self.timer_challenge = Timer()
        # self.timer_teacher = Timer()
        # self.timer_teacher.start()
        # self.timer_response = Timer()
        
        self.leds = Leds()
        self.rainbow = RainbowThread()
        self.confetti = Confetti()
        self.frame_confetti = 1

        #self.tips_times = 0
        self.starting_game()

    def init_working_memory(self):
        self.memory.add_fact('game', self.game)
        self.memory.add_fact('num_terms', 2)
        self.memory.add_fact('quantity_corrects', 0)
        self.memory.add_fact('quantity_errors', 0)
        self.memory.add_fact('quantity_same_error', 0)
        self.memory.add_fact('limit_errors', 5)
        self.memory.add_fact('history_errors', [])
        self.memory.add_fact('tips_times', 0)
        self.memory.add_fact('timer_challenge', Timer())
        self.memory.add_fact('timer_response', Timer())
        self.memory.add_fact('timer_teacher', Timer())
        self.memory.get_fact('timer_teacher').start()
        
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
            self.memory.get_fact('timer_challenge').resume()
            self.memory.get_fact('timer_response').resume()
            #self.timer_challenge.resume()
            #self.timer_response.resume()
            self.is_paused = False
        else:
            self.memory.get_fact('timer_challenge').pause()
            self.memory.get_fact('timer_challenge').pause()
            #self.timer_challenge.pause()
            #self.timer_response.pause()
            self.is_paused = True

    def button_green_changed(self, data):
        """
        Executed when the green button of the base is pressed
        """
        if self.show_teacher:
            return

        if self.is_paused:
            return
        
        self.memory.get_fact('timer_teacher').resume()
        self.memory.get_fact('timer_response').stop()
        self.memory.get_fact('timer_challenge').stop()
        #irá contar o tempo enquanto verifica a resposta?
        
        #self.timer_teacher.resume()
        #self.timer_response.stop()
        #self.timer_challenge.stop()


        if self.teacher.has_next_message():
            self.teacher.clear_messages()


        self.teacher.set_message(
            "Verificando...\n"+
            "Aguarde.", 
            "neutral0"
        )
        self.teacher.next_message()
        self.show_teacher = True

        #self.facial = FacialThread(self.game.app)
        #self.facial.start()
        self.facial.evaluate()
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
            self.memory.get_fact('timer_challenge').pause()
            self.memory.get_fact('timer_response').pause()
            self.memory.get_fact('timer_teacher').resume()
            
            #self.timer_challenge.pause()
            #self.timer_response.pause()
            #self.timer_teacher.resume()
            
            #self.tips_times += 1
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
                self.started = True
                now = datetime.now()
                self.memory.add_fact('last_execution', now)
            #self.leds.central_led()


            if self.step == self.max_steps:
                self.step += 1
                self.save_steps(1, 'completed')
                self.save_steps(2, 'not-started')
            if self.lives == 0 and self.end_phase:
                self.lives -= 1
                self.save_steps(1, 'not-completed')
            
            if self.new_challenge:
                self.memory.get_fact('timer_challenge').start()
                self.memory.get_fact('timer_response').start()
                
                #self.timer_challenge.start()
                #self.timer_response.start()
                self.new_challenge = False
                self.memory.add_fact('tips_times', 0)
                #self.tips_times = 0
            else:
                self.memory.get_fact('timer_challenge').resume()
                self.memory.get_fact('timer_response').resume()
                
                #self.timer_challenge.resume()
                #self.timer_response.resume()
            
            self.memory.get_fact('timer_teacher').pause()    
            #self.timer_teacher.pause()
            
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
        response = {}
        
        response['total_time'] = self.memory.get_fact('timer_response').total_time_seconds()
        response['time_without_pauses'] = (self.memory.get_fact('timer_response').total_time_seconds() - self.memory.get_fact('timer_response').total_time_paused_seconds())
        response['paused_counter'] = self.memory.get_fact('timer_response').total_times_paused() - self.memory.get_fact('tips_times')
        response['tips_counter'] = self.memory.get_fact('tips_times')
        
        # response['total_time'] = self.timer_response.total_time_seconds()
        # response['time_without_pauses'] = (self.timer_response.total_time_seconds() - self.timer_response.total_time_paused_seconds())
        # response['paused_counter'] = self.timer_response.total_times_paused() - self.tips_times
        # response['tips_counter'] = self.tips_times
        
        expression = ''
        numbers, operators, result = self.challenge
        if self.num_terms == 2:
            expression = f'{numbers[0]}{operators[0]}{numbers[1]}={result}'
        else:
            expression = f'{numbers[0]}{operators[0]}{numbers[1]}{operators[1]}{numbers[2]}={result}'
            
        #self.memory.add_fact('last_execution', datetime.now())
        self.memory.add_fact('expression', expression)
        self.memory.add_fact('result', blocks)
        
        self.rules.execute_rules()
        
        feedback = Phase01Feedback(self.game, self.memory)
        feedback.enter_state()
        self.num_terms = self.memory.get_fact('num_terms')
        self.generate_new_challenge()
        self.step += 1
        
        if self.lives == 0:
            self.teacher.set_message(
                "Infelizmente, você não conseguiu\n"+
                "realizar todas as operações corretamente.\n"+
                "Tente novamente!", 
                "neutral1"
            )
            self.end_phase = True
        
        if self.step >= self.max_steps and not self.end_phase:
            self.teacher.set_message(
                "Parabéns!!! Você conseguiu realizar\n"+
                "as operações corretamente. Nos vemos na\n"+
                "próxima fase.", 
                "heart0"
            )
            self.end_phase = True
            self.teacher.next_message()
            self.show_teacher = True
        else:
            self.teacher.clear_messages()
            self.show_teacher = False
        
        
    
    def check_challenge_old(self):
        numbers = self.board.result_matrix_board()
        response = {}
        response['total_time'] = self.timer_response.total_time_seconds()
        response['time_without_pauses'] = (self.timer_response.total_time_seconds() - self.timer_response.total_time_paused_seconds())
        response['paused_counter'] = self.timer_response.total_times_paused() - self.tips_times
        response['tips_counter'] = self.tips_times
        
        terms, operators, result = self.challenge
        
        if len(numbers) == 0:
            response['informed_result'] = -1
            response['is_correct'] = False

            self.teacher.set_message(
                "Atenção. Você deve colocar\n"+
                "os bloco numérico correspondente\n"+
                "à respostas sobre o tabuleiro.", 
                "neutral0"
            )
            self.lives -= 1

        if len(numbers) == 1:
            if numbers[0] == result:
                
                response['informed_result'] = numbers[0]
                response['is_correct'] = True
                
                emotions = ['happy0', 'happy1', 'happy2', 'heart0']
                self.teacher.set_message(
                    "Parabéns!!!\n"+
                    "Você acertou.", 
                    emotions[random.randrange(0,len(emotions))]
                )
                self.score += self.incremental_points
                
                #rainbow = RainbowThread()
                #rainbow.start()

            else:
                response['informed_result'] = numbers[0]
                response['is_correct'] = False 

                self.teacher.set_message(
                    "Ops. Não era esse o resultado.\n"+
                    "Vamos tentar novamente?", 
                    "neutral0"
                )
                self.lives -= 1

        if len(numbers) >= 2:
            response['informed_result'] = -2
            response['is_correct'] = False 

            self.teacher.set_message(
                "Atenção. Você deve informar\n"+
                "o resultado da operação.", 
                "neutral1"
            )
            
            self.lives -= 1
        
        #self.facial.join()
        
        if response['is_correct']:
            self.frame_confetti = 1
            self.confetti.visible = True
            
        #print("Expressao: ", self.facial.expression)
        self.responses.append(response)
        self.save_challenge()
        self.generate_new_challenge()
        self.step += 1

        if self.lives == 0:
            self.teacher.set_message(
                "Infelizmente, você não conseguiu\n"+
                "realizar todas as operações corretamente.\n"+
                "Tente novamente!", 
                "neutral1"
            )
            self.end_phase = True

        if self.step >= self.max_steps and not self.end_phase:
            self.teacher.set_message(
                "Parabéns!!! Você conseguiu realizar\n"+
                "as operações corretamente. Nos vemos na\n"+
                "próxima fase.", 
                "heart0"
            )
            self.end_phase = True
        
        self.teacher.next_message()
        self.show_teacher = True
        

    def draw_lifes(self):
        display = self.game.game_canvas
        for i in range(0, self.lives):
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
        red_text = font.render("Dicas" if not self.show_teacher else "Fechar", True, (0,0,0))
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
        time_ms = self.total_time - pygame.time.get_ticks()

        if time_ms >= 0:
            self.time_hms = ((time_ms//(1000*60*60))%24, (time_ms//(1000*60))%60, (time_ms//1000)%60)
        else:
            self.lose_life()

        timer_text = timer_font.render(f'{self.time_hms[1]:02d}:{self.time_hms[2]:02d}', True, (255, 0, 0))
        timer_text_rect = timer_text.get_rect(center=(screen_width/2, 20))
        display.blit(timer_text, timer_text_rect)

    def lose_life(self):
        if self.lives > 0:
            self.lives -= 1
            self.start_time = pygame.time.get_ticks()
            self.total_time = self.start_time + self.total_seconds*1000
            #self.new_challenge = True

    def draw_score(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        font = pygame.font.SysFont(FONT_NAME, 30, False, False)
        score_text = font.render(f'Pontos: {self.score:>4}', True, (0,0,0))
        score_text_rect = score_text.get_rect(midright=(screen_width-5, 30))
        display.blit(score_text, score_text_rect)

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

    def draw_student_name(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        baseline_text = screen_height - 23

        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        name_text = font.render(self.game.student.nickname, True, (0,0,0))
        name_text_rect = name_text.get_rect(midright=(screen_width-5, baseline_text))
        display.blit(name_text, name_text_rect)

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
        self.memory.get_fact('timer_challenge').stop()
        self.memory.get_fact('timer_teacher').stop()
        #self.timer_challenge.stop()
        #self.timer_teacher.stop()

    @db_session
    def save_challenge(self):
        user = DBUser[self.game.student.id]
        responses = []
        numbers, operators, result = self.challenge
        number1 = numbers[0]
        number2 = numbers[1]
        number3 = -99 if len(numbers) == 2 else numbers[2]
        operator1 = operators[0]
        operator2 = '' if len(operators) == 1 else operators[1]
        
        challenge = DBChallengeP1(
            number01 = number1,
            operator01 = operator1,
            number02 = number2,
            operator02 = operator2,
            number03 = number3,
            expected_result = result,
            total_time = self.memory.get_fact('timer_challenge').total_time_seconds(),
            #total_time = self.timer_challenge.total_time_seconds(),
            user = user
        )
        
        for r in self.responses:
            data = DBResponseP1(
                informed_result = r['informed_result'],
                is_correct = r['is_correct'],
                total_time = r['total_time'],
                time_without_pauses = r['time_without_pauses'],
                paused_counter = r['paused_counter'],
                tips_counter = r['tips_counter'],
                challengep1 = challenge
            )
            commit()
    
    @db_session
    def save_steps(self, phase, status):
        user = DBUser[self.game.student.id]
        step = DBSteps(
            phase = phase,
            score = self.score,
            lifes = self.lives,
            status = status,
            user = user
        )
        commit()

    def render(self, display):
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        offset_height = 0

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
        
        if self.lives > 0 and self.step <= self.max_steps:

            self.draw_challenge()

            if self.enable_timer:
                self.draw_timer()
