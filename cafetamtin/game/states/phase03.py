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
from itertools import combinations

from game.states.state import State
from board.board import Board
from game.actors.teacher import Teacher
from utils.timer import Timer

from game import BACKGROUND_COLOR
from game import TEXT_COLOR
from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN, DARKGREEN


class Phase03(State):

    def __init__(self, game):
        super().__init__(game)
        self.board = Board(self.game.app)
        self.teacher = Teacher(self.game.game_canvas)
        self.show_teacher = False

        self.lives = 3
        self.score = 0
        self.max_steps = 5
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

        self.tips_times = 0

        self.images = self.load_images()

        self.blocks_available = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.blocks_student = {}
        self.blocks_tutor = []

        self.offset = 10
        self.box_width, self.box_height = 40, 40

        self.timer_challenge = Timer()
        self.timer_teacher = Timer()
        self.timer_teacher.start()
        self.timer_response = Timer()

        self.tips_times = 0

    def load_images(self):
        return {
            'heart': pygame.image.load(os.path.join("images", "heart.png")),
        }


    def handle_events(self, events):
        self.game.app.physical_buttons.white_button.when_pressed = self.button_white_changed
        self.game.app.physical_buttons.black_button.when_pressed = self.button_black_changed
        self.game.app.physical_buttons.green_button.when_pressed = self.button_green_changed
        self.game.app.physical_buttons.red_button.when_pressed = self.button_red_changed

        for event in events:
            if event.type == pygame.QUIT:
                self.exit_state()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()

                if event.key == pygame.K_RETURN or event.key == 1073741912:
                    pass

    def button_white_changed(self):
        pass

    def button_black_changed(self):
        pass

    def button_green_changed(self):
        if self.show_teacher:
            return

        if self.is_paused:
            return
        
        self.timer_teacher.resume()
        self.timer_response.stop()
        self.timer_challenge.pause()
        #irá contar o tempo enquanto verifica a resposta?


        self.teacher.set_message("Verificando...", "neutral0")
        self.show_teacher = True

        self.board.avaliable_board()
        self.board.draw_matrix_board()
        self.check_challenge()
    
    def button_red_changed(self):
        if self.is_paused:
            return 
        
        if self.show_teacher:
            if not self.started:
                self.started = True
            self.show_teacher = False

    def update(self, delta_time):
        pass

    def reset_blocks(self):
        self.blocks_available = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.blocks_student = {}
        self.blocks_tutor = []


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

        rect = (0, screen_height - 50, screen_width, screen_height)
        shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, (200, 200, 200), shape.get_rect())
        display.blit(shape, rect)
        
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

    def draw_student_name(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        baseline_text = screen_height - 23

        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        name_text = font.render(self.game.student.nickname, True, (0,0,0))
        name_text_rect = name_text.get_rect(midright=(screen_width-5, baseline_text))
        display.blit(name_text, name_text_rect)

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

        text = font.render(f'Blocos disponíveis: {len(self.blocks_available)}', True, (255,255,255))
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

        if not self.show_teacher and not self.is_paused:
            x = 690
            y = 420
            for i in range(len(self.blocks_tutor)):
                rect = (x,y,self.box_width,self.box_height)
                shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                pygame.draw.rect(shape, (220, 3, 3), shape.get_rect())
                display.blit(shape, rect)
                text = font.render(str(self.blocks_tutor[i]), True, (255,255,255))
                text_rect = text.get_rect(center=(x+self.box_width/2, y+self.box_height/2))
                display.blit(text, text_rect)
                if (i+1) % 5 == 0:
                    x = 690
                    y += self.box_height + self.offset
                else:
                    x += self.box_width + self.offset
            
            x = 400
            y = 420
            
            for i in range(len(self.blocks_available)):
                rect = (x,y,self.box_width,self.box_height)
                shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                pygame.draw.rect(shape, (220, 3, 3), shape.get_rect())
                display.blit(shape, rect)
                text = font.render(str(self.blocks_available[i]), True, (255,255,255))
                text_rect = text.get_rect(center=(x+self.box_width/2, y+self.box_height/2))
                display.blit(text, text_rect)
                if (i+1) % 5 == 0:
                    x = 400
                    y += self.box_height + self.offset
                else:
                    x += self.box_width + self.offset
            
            for key in self.blocks_student.keys():
                pos = self.blocks_student[key]
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

        possibile_sums = []
        if len(self.blocks_student) == 0:
            return
        
        numbers = list(self.blocks_student.keys())

        if len(self.blocks_student) == 1:
            s = {
                'sum': f'{numbers[0]}+?+? = ?', 
                'result': 0, 
                'color': (0,0,0)
            }
            possibile_sums.append(s)

        elif len(self.blocks_student) == 2:
            s = {
                'sum': f'{numbers[0]}+{numbers[1]}+? = ?', 
                'result': 0, 
                'color': (0,0,0)
            }
            possibile_sums.append(s)

        elif len(self.blocks_student) == 3:
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

    def draw_possible_sums_tutor(self):
        display = self.game.game_canvas
        font = pygame.font.SysFont(FONT_NAME, 16, False, False)

        possibile_sums = []
        if len(self.blocks_tutor) == 0:
            return
        
        numbers = self.blocks_tutor

        if len(self.blocks_tutor) == 1:
            s = {
                'sum': f'{numbers[0]}+?+? = ?', 
                'result': 0, 
                'color': (0,0,0)
            }
            possibile_sums.append(s)

        elif len(self.blocks_tutor) == 2:
            s = {
                'sum': f'{numbers[0]}+{numbers[1]}+? = ?', 
                'result': 0, 
                'color': (0,0,0)
            }
            possibile_sums.append(s)

        elif len(self.blocks_tutor) == 3:
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
        if len(self.blocks_available) > 0:
            index = random.randrange(0, len(self.blocks_available))
            removed = self.blocks_available.pop(index)
            self.blocks_tutor.append(removed)
            return removed
        return False

    def check_challenge(self):
        numbers_students = self.board.values_positions()
        
        if len(numbers_students) == 0:
            self.teacher.set_message(
                "Atenção. Você deve colocar\n"+
                "um bloco numérico sobre o tabuleiro\n"+
                "para iniciar.", 
                "neutral0"
            )
            self.show_teacher = True
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
                    "substitituir nenhum bloco. Desfaça"+
                    "a alteração e adicionar um novo bloco.", 
                    "neutral0"
                )
            
            self.show_teacher = True
            self.lives -= 1
        
        elif abs(len(numbers_students) - len(self.blocks_student)) > 1:
            self.teacher.set_message(
                "Atenção. Você deve adicionar apenas\n"+
                "um bloco numérico por vez sobre o\n"+
                "tabuleiro. Escolha apenas um.", 
                "neutral0"
            )
            self.show_teacher = True
            self.lives -= 1

        elif len(self.blocks_student) > len(numbers_students):
            self.teacher.set_message(
                "Atenção. Você retirou um bloco numérico\n"+
                "ao invés de adicionar um novo. Por favor,\n"+
                "recoloque o bloco retirado e adicione um novo.", 
                "neutral0"
            )
            self.show_teacher = True
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
                        f"número {diff[0]}. Essa foi o último"+
                        "número disponível.", 
                        "happy0"
                    )
                self.show_teacher = True
            #verificar o numero que foi colocado
            #verificar se tem algum numeros que o tutor selecionou
            #verificar se já realizou a soma 15

        """
        for key in numbers_students.keys():
            if key in self.blocks_student.keys():
                pass #O estudante já havia selecionado

        self.blocks_student = numbers_students
        for key in numbers_students.keys():
            if key in self.blocks_available:
                self.blocks_available.remove(key)
        
        self.teacher.set_message(
            "Adicionei.", 
            "neutral0"
        )
        self.show_teacher = True
        """

            
    def exit_state(self):
        super().exit_state()
        #self.timer_challenge.stop()
        #self.timer_teacher.stop()

    def render(self, display):
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        offset_height = 0

        display.fill((255,255,255))
        
        self.draw_board()
        self.draw_lifes()
        self.draw_score()
        self.draw_student_name()
        self.draw_physical_buttons()

        if not self.started:
            self.teacher.set_message("Atenção!\nPrepare-se para começar", "neutral1")
            self.show_teacher = True
        
        if self.show_teacher:
            self.teacher.draw()

        if self.is_paused:
            self.draw_pause()
        
        if self.lives > 0 and self.step <= self.max_steps:

            if not self.show_teacher and not self.is_paused:
                self.draw_challenge()
                self.draw_possible_sums_student()
                self.draw_possible_sums_tutor()

            if self.enable_timer:
                self.draw_timer()

        else:
            if not self.show_teacher:
                if self.lives == 0:
                    self.teacher.set_message(
                        "Infelizmente, você não conseguiu\n"+
                        "realizar todas as operações corretamente.\n"+
                        "Tente novamente!", 
                        "neutral1"
                    )
                    self.show_teacher = True
                    self.end_phase = True
                if self.step >= self.max_steps and not self.end_phase:
                    self.teacher.set_message(
                        "Parabéns!!! Você conseguiu realizar\n"+
                        "as operações corretamente. Nos vemos na\n"+
                        "próxima fase.", 
                        "heart0"
                    )
                    self.show_teacher = True
                    self.end_phase = True
                
                if self.end_phase and not self.show_teacher:
                    self.exit_state()