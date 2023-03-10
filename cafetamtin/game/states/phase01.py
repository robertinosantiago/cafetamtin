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
import sys
from pygame.locals import *
import os
import random

from game import BACKGROUND_COLOR
from game import TEXT_COLOR
from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN

from game.states.state import State
from game.actors.teacher import Teacher

class Phase01(State):
    
    def __init__(self, game):
        super().__init__(game)

        self.teacher = Teacher(self.game.game_canvas)
        self.show_teacher = False

        self.menu_items = ['Voltar']
        self.menu_selection = 0

        self.lives = 3
        self.score = 0

        self.min_number = 1
        self.max_number = 10
        self.operators = ['+', '-']
        
        self.new_challange = True
        self.challange = ()

        self.images = self.load_images()
        
        self.start_time = pygame.time.get_ticks()
        self.total_seconds = 10
        self.time_hms = 0, 0, 0
        self.total_time = self.start_time + self.total_seconds*1000

        self.enable_timer = False
        self.is_paused = False


    def load_images(self):
        return {
            'background': pygame.image.load(os.path.join("images", "classroom-background.png")),
            'heart': pygame.image.load(os.path.join("images", "heart.png")),
            'table': pygame.image.load(os.path.join("images", "table.png")),
            'student-desk': pygame.image.load(os.path.join("images", "student-desk.png")),
        }

    def handle_events(self, events):
        self.game.app.physical_buttons.white_button.when_pressed = self.button_pause_changed
        self.game.app.physical_buttons.black_button.when_pressed = self.button_abort_changed
        self.game.app.physical_buttons.green_button.when_pressed = self.button_respond_changed
        self.game.app.physical_buttons.red_button.when_pressed = self.button_tips_changed

        for event in events:
            if event.type == pygame.QUIT:
                self.exit_state()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()

    def update(self, delta_time):
        pass

    def button_pause_changed(self):
        if self.show_teacher:
            return
        
        if self.is_paused:
            self.is_paused = False
        else:
            self.is_paused = True

    def button_respond_changed(self):
        pass

    def button_tips_changed(self):
        if self.is_paused:
            return 
        
        if self.show_teacher:
            self.show_teacher = False
        else:
            self.teacher.set_message("Lorem ipsum dolor sit amet, consectetur adipiscing elit. \nFusce ultricies massa elit, nec lacinia mauris ultricies vitae.\nLorem ipsum dolor sit amet, consectetur adipiscing elit. \nFusce ultricies massa elit, nec lacinia mauris ultricies vitae.")
            self.show_teacher = True

    def button_abort_changed(self):
        pass


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

        pygame.draw.circle(display,WHITE,(20,baseline_circle),10)
        white_text = font.render("Pausar", True, (0,0,0))
        display.blit(white_text, (35, baseline_text))

        pygame.draw.circle(display,RED,(130,baseline_circle),10)
        red_text = font.render("Dicas", True, (0,0,0))
        display.blit(red_text, (145, baseline_text))

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
            self.new_challange = True


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
        instruction_text = font.render('Informe o resultado da opera????o', True, (220,220,220))
        instruction_text_rect = instruction_text.get_rect(center=(screen_width/2, 120))
        display.blit(instruction_text, instruction_text_rect)

        if self.new_challange:
            self.challange = self.random_calc()
            self.new_challange = False
        font = pygame.font.SysFont(FONT_NAME, 72, False, False)
        challenge_text = font.render(f'{self.challange[0]} {self.challange[1]} {self.challange[2]}', True, (220,220,220))
        challenge_text_rect = challenge_text.get_rect(center=(screen_width/2, 220))
        display.blit(challenge_text, challenge_text_rect)
        
    def random_calc(self):
        number1 = random.randrange(self.min_number,self.max_number)
        number2 = random.randrange(self.min_number,self.max_number)
        operator = random.choice(self.operators)
        result = 0
        if operator == '+':
            result = number1 + number2
        if operator == '-':
            if number1 < number2:
                aux = number1
                number1 = number2
                number2 = aux
            result = number1 - number2
        return number1, operator, number2, result

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
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        student_desk = self.images['student-desk']

        point_start = 160
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

    def render(self, display):
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        offset_height = 0

        display.fill((255,255,255))

        if self.lives > 0:

            background = self.images['background']
            display.blit(background, (0,0))
            self.draw_table()
            self.draw_student_desk()
            self.draw_lifes()
            self.draw_score()
            self.draw_challenge()
            self.draw_student_name()
            self.draw_physical_buttons()

            if self.enable_timer:
                self.draw_timer()

            if self.show_teacher:
                self.teacher.draw()

            if self.is_paused:
                self.draw_pause()
        else:
            self.exit_state()