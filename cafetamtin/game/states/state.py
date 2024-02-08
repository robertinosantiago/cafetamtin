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
from gpiozero import Button

from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN, YELLOW
from utils.confetti import Confetti

class State():
    def __init__(self, game, memory = None):
        self.game = game
        self.memory = memory
        self.previous_state = None
        self.confetti = Confetti()
        self.frame_confetti = 1

    def update(self, delta_time):
        pass

    def render(self, surface):
        pass

    def handle_events(self, events):
        pass

    def enter_state(self):
        if len(self.game.state_stack) > 1:
            self.previous_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)
    
    def exit_state(self, stages = 1):
        for i in range(0, stages):
            self.game.state_stack.pop()
            
    def blit_text(self, text, pos, color, size):
        display = self.game.game_canvas
        font = pygame.font.SysFont(FONT_NAME, size, False, False)
        text = font.render(text, True, color)
        text_rect = text.get_rect(center=(pos[0], pos[1]))
        display.blit(text, text_rect)
        
    def blit_box(self, text, pos, color, size):
        display = self.game.game_canvas
        rect = (pos[0], pos[1], self.box_width, self.box_height)
        shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect())
        display.blit(shape, rect)
        self.blit_text(text, (pos[0]+self.box_width/2, pos[1]+self.box_height/2), WHITE, size)

    def draw_arrow_right(self, message, pos, angle, color, size):
        display = self.game.game_canvas
        font = pygame.font.SysFont('DejaVu Sans', size, False, False)
        text = font.render(f'{message}'+u' \u2192', True, color)
        text = pygame.transform.rotate(text, angle)
        text_rect = text.get_rect(topright=pos)
        display.blit(text, text_rect)
    
        
    def draw_arrow_left(self, message, pos, angle, color, size):
        display = self.game.game_canvas
        font = pygame.font.SysFont('DejaVu Sans', size, False, False)
        text = font.render(u'\u2190 '+f'{message}', True, color)
        text = pygame.transform.rotate(text, angle)
        text_rect = text.get_rect(topleft=pos)
        display.blit(text, text_rect)
        
    def draw_circle(self, pos, radius, color):
        display = self.game.game_canvas
        pygame.draw.circle(display,color,pos,radius)
        
    def draw_confetti(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        frame = self.confetti.get_image(self.frame_confetti)
        frame_rect = frame.get_rect(center=(screen_width/2, screen_height/2 - 80))
        display.blit(frame, frame_rect)
        self.frame_confetti += 1
        if self.frame_confetti > self.confetti.total_frames:
            self.confetti.visible = False
            
    def draw_score(self):
        score = self.memory.get_fact('score')
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        font = pygame.font.SysFont(FONT_NAME, 30, False, False)
        score_text = font.render(f'Pontos: {score:>4}', True, (0,0,0))
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

        #rect = (0, screen_height - 50, screen_width, screen_height)
        #shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        #pygame.draw.rect(shape, (0,0,0,255), shape.get_rect())
        #display.blit(shape, rect)

        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        pygame.draw.circle(display,WHITE,(20,baseline_circle),10)
        white_text = font.render("Continuar", True, WHITE)
        display.blit(white_text, (35, baseline_text))
        
    def convert_time(self, seconds: int):
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return int(hours), int(minutes), int(seconds)
