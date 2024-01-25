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

import pygame
import os
import random
import logging
from pony.orm import *
from datetime import datetime
from itertools import combinations

from game.states.state import State
from base.board import Board
from game.actors.teacher import Teacher
from game.actors.student import Student
from utils.timer import Timer
from utils.confetti import Confetti
from database.models import DBSession, DBUser, DBSteps#, DBChallengeP2

from production.error import Error
from production.memory import Memory
from production.type_error import TypeError
from production.phase03_rules import Phase03Rules
from game.states.phase03_feedback import Phase03Feedback

from game import BACKGROUND_COLOR
from game import TEXT_COLOR
from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN, DARKGREEN


class Phase03(State):

    def __init__(self, game):
        super().__init__(game)
        
        self.memory = Memory()
        self.rules = Phase03Rules(self.memory)
        self.init_working_memory()
        
        self.board = Board(self.game.app)
        self.teacher = Teacher(self.game.game_canvas)
        self.show_teacher = False
        self.confetti = Confetti()
        self.frame_confetti = 1

        self.lives = 3
        self.score = 0
        self.max_steps = 2
        self.step = 1
        self.incremental_points = 5

        self.start_time = pygame.time.get_ticks()
        self.total_seconds = 10
        self.time_hms = 0, 0, 0
        self.total_time = self.start_time + self.total_seconds*1000

        self.enable_timer = False
        self.is_paused = False
        self.started = False
        self.end_phase = False
        self.new_challenge = True
        self.reload = False

        self.tips_times = 0

        self.images = self.load_images()

        self.blocks_available = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.blocks_student = {}
        self.blocks_tutor = []
        self.sums_founds_student = []

        self.offset = 10
        self.box_width, self.box_height = 40, 40

        self.timer_challenge = Timer()
        self.timer_teacher = Timer()
        self.timer_teacher.start()
        self.timer_response = Timer()

        self.tips_times = 0
        self.first_gaming()
        self.teacher.next_message()

    def load_images(self):
        return {
            'heart': pygame.image.load(os.path.join("images", "heart.png")),
        }

    @db_session
    def init_working_memory(self):
        session = DBSession(
            start_time = datetime.now()
        )
        session.flush()
        self.memory.add_fact('student', self.game.student)
        self.memory.add_fact('session_id', session.id)
        self.memory.add_fact('game', self.game)
        
        self.memory.add_fact('blocks_available', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.memory.add_fact('blocks_student', {})
        self.memory.add_fact('blocks_tutor', [])
        self.memory.add_fact('sums_founds_student', [])
        
        self.memory.add_fact('tutor_starting', False)
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
        self.memory.add_fact('score', 0)
        self.memory.add_fact('correct_points', 10)
        self.memory.add_fact('incorrect_points', 5)
        self.memory.add_fact('bonus_points', 5)
        
        self.memory.add_fact('timer_challenge', Timer())
        self.memory.add_fact('timer_response', Timer())
        self.memory.add_fact('timer_teacher', Timer())
        self.memory.get_fact('timer_teacher').start()

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

                if event.key == pygame.K_RETURN or event.key == 1073741912:
                    pass

    def button_white_changed(self, data):
        if self.show_teacher:
            return
        
        if self.is_paused:
            self.memory.get_fact('timer_challenge').resume()
            self.memory.get_fact('timer_response').resume()
            self.is_paused = False
        else:
            self.memory.get_fact('timer_challenge').pause()
            self.memory.get_fact('timer_response').pause()
            self.is_paused = True

    def button_black_changed(self, data):
        pass

    def button_green_changed(self, data):
        if self.show_teacher:
            return

        if self.is_paused:
            return
        
        self.memory.get_fact('timer_teacher').resume()
        self.memory.get_fact('timer_response').stop()
        self.memory.get_fact('timer_challenge').stop()
        #irá contar o tempo enquanto verifica a resposta?

        if self.teacher.has_next_message():
            self.teacher.clear_messages()


        self.teacher.set_message(
            "Verificando...\n"+
            "Aguarde.", 
            "neutral0"
        )
        self.teacher.next_message()
        self.show_teacher = True

        self.board.avaliable_board()
        self.board.draw_matrix_board()
        self.check_challenge()
    
    def button_red_changed(self, data):
        if self.is_paused:
            return
        
        if not self.show_teacher:
            self.memory.get_fact('timer_challenge').pause()
            self.memory.get_fact('timer_response').pause()
            self.memory.get_fact('timer_teacher').resume()
            
            tips_times = self.memory.get_fact('tips_times')
            self.memory.add_fact('tips_times', tips_times + 1)
            
            self.teacher.set_message(
                "Dicas", 
                "neutral0"
            )
        
        if self.teacher.has_next_message():
            self.teacher.next_message()
            self.show_teacher = True

        else:
            self.show_teacher = False

            if self.reload:
                self.memory.get_fact('timer_challenge').start()
                self.memory.get_fact('timer_response').start()
                self.reload = False
                if not self.end_phase:
                    self.reset_blocks()
                    self.first_gaming()
                    self.teacher.next_message()
            else:
                self.memory.get_fact('timer_challenge').resume()

            if self.end_phase and not self.show_teacher:
                self.exit_state()

    def first_gaming(self):
        self.teacher.set_message(
                "Atenção!\n"+
                "Prepare-se para começar. Remova todos os blocos que "+
                "possam estar sobre o tabuleiro. \n"+
                "\n"+
                "Pressione o botão VERMELHO para continuar",  
                "neutral1"
        )
        if self.step == 1:
            self.memory.add_fact('tutor_starting', bool(random.getrandbits(1)))
        else:
            tutor_starting = self.memory.get_fact('tutor_starting')
            self.memory.add_fact('tutor_starting', not tutor_starting)

        if self.memory.get_fact('tutor_starting'):
            n = self.next_tutor_number()
            
            self.teacher.set_message(
                "Nesta rodada, eu começo jogando. "+
                f"Observe que já selecionei o número {n}. "+
                "Agora, é sua vez\n."+
                "\n"+
                "Pressione o botão VERMELHO para continuar",
                "neutral2",
                modal=False
            )
        else:
            self.teacher.set_message(
                "Atenção!\n"+
                "Nesta rodada, você começa jogando. "+
                "Prepare-se para começar.\n"+
                "\n"+
                "Pressione o botão VERMELHO para continuar",
                "neutral2"
            )
        
        self.show_teacher = True
        

    def update(self, delta_time):
        pass

    def reset_blocks(self):
        self.memory.add_fact('blocks_available', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.memory.add_fact('blocks_student', {})
        self.memory.add_fact('blocks_tutor', [])
        self.memory.add_fact('sums_founds_student', [])
        
        self.blocks_available = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.blocks_student = {}
        self.blocks_tutor = []
        self.sums_founds_student = []


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
            self.start_time = pygame.time.get_ticks()
            self.total_time = self.start_time + self.memory.get_fact('amount_time')*1000
            
        time_ms = self.total_time - pygame.time.get_ticks()

        if time_ms >= 0:
            self.time_hms = ((time_ms//(1000*60*60))%24, (time_ms//(1000*60))%60, (time_ms//1000)%60)
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
            
            self.memory.get_fact('timer_teacher').resume()
            self.memory.get_fact('timer_response').stop()
            self.memory.get_fact('timer_challenge').stop()
            
            self.memory.add_fact('is_correct', False)
            
            response = {}
            response['number01'] = -1
            #response['number02'] = -1
            #response['number03'] = -1
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
            
            #self.save_challenge(response)
            
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

    def draw_physical_buttons(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        baseline_text = screen_height - 35
        baseline_circle = screen_height - 23
        
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)

        rect = (0, screen_height - 50, screen_width, screen_height)
        shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, (200, 200, 200), shape.get_rect())
        display.blit(shape, rect)
        
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
            white_text = font.render("Pausar" if not self.is_paused else "Continuar", True, (0,0,0))
            display.blit(white_text, (35, baseline_text))

            pygame.draw.circle(display,GREEN,(220,baseline_circle),10)
            green_text = font.render("Responder", True, (0,0,0))
            display.blit(green_text, (235, baseline_text))

    def lose_life(self):
        lives = self.memory.get_fact('lives')
        if lives > 0:
            self.memory.add_fact('lives', lives - 1)
            self.start_time = pygame.time.get_ticks()
            self.total_time = self.start_time + self.total_seconds*1000
            #self.new_challenge = True

    def draw_pause(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        baseline_text = screen_height - 35
        baseline_circle = screen_height - 23
                
        rect_background = (0,0,screen_width,screen_height)
        shape_surf = pygame.Surface(pygame.Rect(rect_background).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (0,0,0,230), shape_surf.get_rect())
        display.blit(shape_surf, rect_background)

        font = pygame.font.SysFont(FONT_NAME, 72, False, False)
        instruction_text = font.render('Pause', True, (220,220,220))
        instruction_text_rect = instruction_text.get_rect(center=(screen_width/2, screen_height/2))
        display.blit(instruction_text, instruction_text_rect)

        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        pygame.draw.circle(display,WHITE,(20,baseline_circle),10)
        white_text = font.render("Continuar", True, WHITE)
        display.blit(white_text, (35, baseline_text))

    def draw_board(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT

        color = (183, 183, 138, 255)
        rect_shape = (0, 55, screen_width,screen_height)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect())
        display.blit(shape, rect_shape)

        total_shape_x = self.box_width * self.board.columns + self.offset * (self.board.columns + 1)
        total_shape_y = self.box_height * self.board.lines + self.offset * (self.board.lines + 1)

        pos_x = self.offset
        pos_y = 100

        pos_x_rect = total_shape_x+pos_x+self.offset
        width_rect = (screen_width-pos_x_rect-self.offset)/2-self.offset/2
        height_rect = (screen_height-pos_y-50)/2+self.offset*2

        color = (220,220,220,255)

        #Bloco das possíveis somas do estudante
        rect_shape = (pos_x_rect, pos_y, width_rect, height_rect)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect(), border_radius= 15)
        display.blit(shape, rect_shape)

        font = pygame.font.SysFont(FONT_NAME, 18, False, False)
        text = font.render('Possíveis somas estudante', True, (0,0,0))
        text_rect = text.get_rect(topleft=(pos_x_rect+self.offset, pos_y+self.offset))
        display.blit(text, text_rect)

        #Bloco das possíveis somas do tutor
        rect_shape = (pos_x_rect+width_rect+self.offset, pos_y, width_rect, height_rect)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect(), border_radius= 15)
        display.blit(shape, rect_shape)

        font = pygame.font.SysFont(FONT_NAME, 18, False, False)
        text = font.render('Possíveis somas tutor', True, (0,0,0))
        text_rect = text.get_rect(topleft=(pos_x_rect+width_rect+self.offset+self.offset, pos_y+self.offset))
        display.blit(text, text_rect)

        height_rect = (screen_height-pos_y-50)/2-self.offset*4
        color = (130,115,0,255)
        
        #Bloco das peças disponíveis
        rect_shape = (pos_x_rect, pos_y+height_rect+self.offset*7, width_rect, height_rect+self.offset)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect(), border_radius= 15)
        display.blit(shape, rect_shape)

        blocks_available = self.memory.get_fact('blocks_available')
        text = font.render(f'Blocos disponíveis: {len(blocks_available)}', True, (255,255,255))
        text_rect = text.get_rect(topleft=(pos_x_rect+self.offset, pos_y+height_rect+self.offset+self.offset*8))
        display.blit(text, text_rect)

        #Bloco das peças tutor
        rect_shape = (pos_x_rect+width_rect+self.offset, pos_y+height_rect+self.offset*7, width_rect, height_rect+self.offset)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect(), border_radius= 15)
        display.blit(shape, rect_shape)

        text = font.render('Blocos do tutor', True, (255,255,255))
        text_rect = text.get_rect(topleft=(pos_x_rect+width_rect+self.offset+self.offset, pos_y+height_rect+self.offset+self.offset*8))
        display.blit(text, text_rect)


        font = pygame.font.SysFont(FONT_NAME, 24, False, False)
        text = font.render(self.game.student.name, True, (255,255,255))
        text_rect = text.get_rect(bottomleft=(pos_x, pos_y))
        display.blit(text, text_rect)


        rect_shape = (pos_x,pos_y,total_shape_x,total_shape_y)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect())
        display.blit(shape, rect_shape)

        pos_x += self.offset
        pos_y += self.offset
        x = pos_x
        
        for col in range(0, self.board.columns):
            y = pos_y
            for lin in range(0, self.board.lines):
                color = (255,255,255,255)
                rect = (x,y,self.box_width,self.box_height)
                shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                pygame.draw.rect(shape, color, shape.get_rect())
                display.blit(shape, rect)

                y += self.box_height + self.offset
            x += self.box_width + self.offset

    def draw_challenge(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        font = pygame.font.SysFont(FONT_NAME, 30, False, False)

        blocks_tutor = self.memory.get_fact('blocks_tutor')
        blocks_student = self.memory.get_fact('blocks_student')
        blocks_available = self.memory.get_fact('blocks_available')

        #if not self.show_teacher and not self.is_paused:
        x = 690
        y = 420
        for i in range(len(blocks_tutor)):
            rect = (x,y,self.box_width,self.box_height)
            shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
            pygame.draw.rect(shape, (220, 3, 3), shape.get_rect())
            display.blit(shape, rect)
            text = font.render(str(blocks_tutor[i]), True, (255,255,255))
            text_rect = text.get_rect(center=(x+self.box_width/2, y+self.box_height/2))
            display.blit(text, text_rect)
            if (i+1) % 5 == 0:
                x = 690
                y += self.box_height + self.offset
            else:
                x += self.box_width + self.offset
        
        x = 400
        y = 420
        
        for i in range(len(blocks_available)):
            rect = (x,y,self.box_width,self.box_height)
            shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
            pygame.draw.rect(shape, (220, 3, 3), shape.get_rect())
            display.blit(shape, rect)
            text = font.render(str(blocks_available[i]), True, (255,255,255))
            text_rect = text.get_rect(center=(x+self.box_width/2, y+self.box_height/2))
            display.blit(text, text_rect)
            if (i+1) % 5 == 0:
                x = 400
                y += self.box_height + self.offset
            else:
                x += self.box_width + self.offset
        
        for key in blocks_student.keys():
            pos = blocks_student[key]
            x = self.offset + self.offset * pos[1] + self.box_width * (pos[1] - 1)
            y = 100 + self.offset * pos[0] + self.box_height * (pos[0] - 1)
            rect = (x,y,self.box_width,self.box_height)
            shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
            pygame.draw.rect(shape, (220, 3, 3), shape.get_rect())
            display.blit(shape, rect)
            text = font.render(str(key), True, (255,255,255))
            text_rect = text.get_rect(center=(x+self.box_width/2, y+self.box_height/2))
            display.blit(text, text_rect)

    def draw_possible_sums_student(self):
        display = self.game.game_canvas
        font = pygame.font.SysFont(FONT_NAME, 16, False, False)
        blocks_student = self.memory.get_fact('blocks_student')

        possibile_sums = []
        if len(blocks_student) == 0:
            return
        
        numbers = list(blocks_student.keys())

        if len(blocks_student) == 1:
            s = {
                'sum': f'{numbers[0]}+?+? = ?', 
                'result': 0, 
                'color': (0,0,0)
            }
            possibile_sums.append(s)

        elif len(blocks_student) == 2:
            s = {
                'sum': f'{numbers[0]}+{numbers[1]}+? = ?', 
                'result': 0, 
                'color': (0,0,0)
            }
            possibile_sums.append(s)

        elif len(blocks_student) == 3:
            result = sum(numbers)
            s = {
                'sum': f'{numbers[0]}+{numbers[1]}+{numbers[2]} = {result}', 
                'result': result, 
                'color': DARKGREEN if result == 15 else RED
            }
            possibile_sums.append(s)
        
        else:
            combs = combinations(numbers, 3)
            for c in combs:
                result = sum(c)
                s = {
                    'sum': f'{c[0]}+{c[1]}+{c[2]} = {result}', 
                    'result': result, 
                    'color': DARKGREEN if result == 15 else RED
                }
                possibile_sums.append(s)

        x = 395
        y = 160
        width = 130
        height = 25
        for i in range(len(possibile_sums)):
            text = font.render(possibile_sums[i]['sum'], True, possibile_sums[i]['color'])
            text_rect = text.get_rect(topleft=(x, y))
            display.blit(text, text_rect)
            if (i+1) % 2 == 0:
                x = 395
                y += height + self.offset
            else:
                x += width + self.offset
    
    def verify_sums_student(self):
        blocks_student = self.memory.get_fact('blocks_student')
        
        numbers = list(blocks_student.keys())
        if len(blocks_student) >= 3:
            combs = combinations(numbers, 3)
            for c in combs:
                l = list(c)
                l.sort()
                result = sum(l)
                if result == 15:
                    key = "".join(map(str, l))
                    if not key in self.memory.get_fact('sums_founds_student'):
                        self.memory.get_fact('sums_founds_student').append(key)
                        self.frame_confetti = 1
                        self.confetti.visible = True
                        return True
        return False


    def draw_possible_sums_tutor(self):
        display = self.game.game_canvas
        font = pygame.font.SysFont(FONT_NAME, 16, False, False)
        blocks_tutor = self.memory.get_fact('blocks_tutor')

        possibile_sums = []
        if len(blocks_tutor) == 0:
            return
        
        numbers = blocks_tutor

        if len(blocks_tutor) == 1:
            s = {
                'sum': f'{numbers[0]}+?+? = ?', 
                'result': 0, 
                'color': (0,0,0)
            }
            possibile_sums.append(s)

        elif len(blocks_tutor) == 2:
            s = {
                'sum': f'{numbers[0]}+{numbers[1]}+? = ?', 
                'result': 0, 
                'color': (0,0,0)
            }
            possibile_sums.append(s)

        elif len(blocks_tutor) == 3:
            result = sum(numbers)
            s = {
                'sum': f'{numbers[0]}+{numbers[1]}+{numbers[2]} = {result}', 
                'result': result, 
                'color': DARKGREEN if result == 15 else RED
            }
            possibile_sums.append(s)
        
        else:
            combs = combinations(numbers, 3)
            for c in combs:
                result = sum(c)
                s = {
                    'sum': f'{c[0]}+{c[1]}+{c[2]} = {result}', 
                    'result': result, 
                    'color': DARKGREEN if result == 15 else RED
                }
                possibile_sums.append(s)

        x = 685
        y = 160
        width = 130
        height = 25
        for i in range(len(possibile_sums)):
            text = font.render(possibile_sums[i]['sum'], True, possibile_sums[i]['color'])
            text_rect = text.get_rect(topleft=(x, y))
            display.blit(text, text_rect)
            if (i+1) % 2 == 0:
                x = 685
                y += height + self.offset
            else:
                x += width + self.offset

    def next_tutor_number(self):
        if len(self.memory.get_fact('blocks_available')) > 0:
            index = random.randrange(0, len(self.memory.get_fact('blocks_available')))
            removed = self.memory.get_fact('blocks_available').pop(index)
            self.memory.get_fact('blocks_tutor').append(removed)
            return removed
        return False

    def check_challenge(self):
        numbers_student = self.board.values_positions()
        self.memory.add_fact('numbers_student', numbers_student)
        
        self.rules.execute_rules()
        
        feedback = Phase03Feedback(self.game, self.memory)
        feedback.enter_state()
        
        self.teacher.clear_messages()
        self.show_teacher = False
        
    def check_challenge_old(self):
        numbers_students = self.board.values_positions()

        if len(numbers_students) == 0:
            self.teacher.set_message(
                "Atenção. Você deve colocar\n"+
                "um bloco numérico sobre o \n"+
                "tabuleiro para iniciar.", 
                "neutral0"
            )
            self.lives -= 1

        elif len(numbers_students) == len(self.blocks_student):
            #verificar troca de mais de uma peça
            diff = [x for x in numbers_students if x not in self.blocks_student]
            if (len(diff)) == 0:
                self.teacher.set_message(
                    "Atenção. Você deve colocar\n"+
                    "um novo bloco numérico sobre\n"+
                    "o tabuleiro a cada tentativa.", 
                    "neutral0"
                )
            else:
                diff2 = [x for x in self.blocks_student if x not in numbers_students]
                self.teacher.set_message(
                    f"Atenção. Você trocou o número {diff2[0]}\n"+
                    f"pelo número {diff[0]}. Você não deve\n"+
                    "substitituir nenhum bloco. Desfaça\n"+
                    "a alteração e adicionar um novo bloco.", 
                    "neutral0"
                )
            
            self.lives -= 1
        
        elif abs(len(numbers_students) - len(self.blocks_student)) > 1:
            self.teacher.set_message(
                "Atenção. Você deve adicionar apenas\n"+
                "um bloco numérico por vez sobre o\n"+
                "tabuleiro. Escolha apenas um.", 
                "neutral0"
            )
            self.lives -= 1

        elif len(self.blocks_student) > len(numbers_students):
            self.teacher.set_message(
                "Atenção. Você retirou um bloco numérico\n"+
                "ao invés de adicionar um novo. Por favor,\n"+
                "recoloque o bloco retirado e adicione um novo.", 
                "neutral0"
            )
            self.lives -= 1

        else:
            diff = [x for x in numbers_students if x not in self.blocks_student]
            
            if diff[0] in self.blocks_tutor:
                self.teacher.set_message(
                    f"Você tentou colocar o número {diff}.\n"+
                    "Esse bloco já foi selecionado\n"+
                    "pelo tutor. Por favor, tente outro.", 
                    "happy0"
                )
                self.lives -= 1
            else:
                self.blocks_student.update(numbers_students)
                for key in self.blocks_student.keys():
                    if key in self.blocks_available:
                        self.blocks_available.remove(key)

                ntutor = self.next_tutor_number()

                if ntutor:
                    self.teacher.set_message(
                        "Muito bem! Você adicionou o\n"+
                        f"número {diff[0]}. O tutor escolheu\n"+
                        f"o número {ntutor}.", 
                        "happy0"
                    )
                else:
                    self.teacher.set_message(
                        "Muito bem! Você adicionou o\n"+
                        f"número {diff[0]}. Esse foi o último\n"+
                        "número disponível.", 
                        "happy0"
                    )
                
                if self.verify_sums_student():
                    self.teacher.set_message(
                        "Ual!!! Com esse bloco, você conseguiu\n"+
                        "realizar a soma 15. Parabéns!", 
                        "heart0"
                    )

        if len(self.blocks_available) == 0 and not self.end_phase:
            self.teacher.set_message(
                "Terminou essa rodada", 
                "neutral0",
                modal=False,
                position=(500, 400)
            )
            self.step += 1
            if self.lives > 0 and self.step <= self.max_steps:
                self.reload = True
        
        if self.lives == 0:
            self.teacher.set_message(
                "Infelizmente, você não conseguiu\n"+
                "realizar todas as operações corretamente.\n"+
                "Tente novamente!", 
                "neutral1"
            )
            self.end_phase = True

        if self.step > self.max_steps and not self.end_phase:
            self.teacher.set_message(
                "Parabéns!!! Você conseguiu realizar\n"+
                "as operações corretamente. Nos vemos na\n"+
                "próxima fase.", 
                "heart0"
            )
            self.end_phase = True
            

        self.teacher.next_message()
        self.show_teacher = True

        #verificar o numero que foi colocado
        #verificar se tem algum numeros que o tutor selecionou
        #verificar se já realizou a soma 15

    

    def exit_state(self):
        super().exit_state()
        self.memory.get_fact('timer_challenge').stop()
        self.memory.get_fact('timer_teacher').stop()

    def render(self, display):
        display.fill((255,255,255))
        
        self.draw_board()
        self.draw_lifes()
        self.draw_score()
        self.draw_student_name()
        self.draw_physical_buttons()

        if self.is_paused:
            self.draw_pause()
            
        if (not self.show_teacher and not self.is_paused) or (self.show_teacher and not self.teacher.modal):
            self.draw_challenge()
            self.draw_possible_sums_student()
            self.draw_possible_sums_tutor()

        if self.show_teacher:
            self.teacher.draw()
            
        if self.confetti.visible:
            self.draw_confetti()
        
        if self.lives > 0 and self.step <= self.max_steps:
            if self.enable_timer:
                self.draw_timer()
    
