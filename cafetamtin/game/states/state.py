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
