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

from game.states.state import State
from board.board import Board
from game.actors.teacher import Teacher

from game import BACKGROUND_COLOR
from game import TEXT_COLOR
from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN


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

        self.blocks_in_board = []
        self.blocks_student = [2, 3, 4, 5, 6, 7, 8, 9]
        self.blocks_tutor = [1]

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
        pass
    
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
        self.blocks_in_board = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.blocks_student = []
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

        box_width = 230
        box_height = 415
        color =(238, 238, 238, 255)
        rect_shape = (35, 85, box_width, box_height)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect(), border_radius= 15)
        display.blit(shape, rect_shape)

        rect_shape = (screen_width-box_width-35, 85, box_width, box_height)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect(), border_radius= 15)
        display.blit(shape, rect_shape)

        rect_shape = (screen_width/2-box_width/2, 85, box_width, box_height)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect(), border_radius= 15)
        display.blit(shape, rect_shape)

    def draw_challenge(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        font = pygame.font.SysFont(FONT_NAME, 30, False, False)

        if not self.show_teacher and not self.is_paused:
            offset = 20
            box_width, box_height = 50, 50
            x = 385
            y = 190
            
            for i in range(len(self.blocks_in_board)):
                rect = (x,y,box_width,box_height)
                shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                pygame.draw.rect(shape, (220, 3, 3), shape.get_rect())
                display.blit(shape, rect)
                text = font.render(str(self.blocks_in_board[i]), True, (255,255,255))
                text_rect = text.get_rect(center=(x+box_width/2, y+box_height/2))
                display.blit(text, text_rect)
                if (i+1) % 3 == 0:
                    x = 385
                    y += box_height + offset
                else:
                    x += box_width + offset

            x = 55
            y = 190
            for i in range(len(self.blocks_student)):
                rect = (x,y,box_width,box_height)
                shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                pygame.draw.rect(shape, (220, 3, 3), shape.get_rect())
                display.blit(shape, rect)
                text = font.render(str(self.blocks_student[i]), True, (255,255,255))
                text_rect = text.get_rect(center=(x+box_width/2, y+box_height/2))
                display.blit(text, text_rect)
                if (i+1) % 3 == 0:
                    x = 55
                    y += box_height + offset
                else:
                    x += box_width + offset

            x = 715
            y = 190
            for i in range(len(self.blocks_tutor)):
                rect = (x,y,box_width,box_height)
                shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                pygame.draw.rect(shape, (220, 3, 3), shape.get_rect())
                display.blit(shape, rect)
                text = font.render(str(self.blocks_tutor[i]), True, (255,255,255))
                text_rect = text.get_rect(center=(x+box_width/2, y+box_height/2))
                display.blit(text, text_rect)
                if (i+1) % 3 == 0:
                    x = 715
                    y += box_height + offset
                else:
                    x += box_width + offset

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

            self.draw_challenge()

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