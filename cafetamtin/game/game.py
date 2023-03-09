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
#
# Based in https://github.com/ChristianD37/YoutubeTutorials

import os, sys, time
import pygame
from pygame.locals import *

from game.states.menu import Menu
from utils.webcam import Webcam

class Game():
    
    def __init__(self, app, fullscreen):
        pygame.init()
        flags = pygame.DOUBLEBUF
        if fullscreen:
            flags |= pygame.FULLSCREEN

        self.app = app

        self.GAME_WIDTH, self.GAME_HEIGHT = 960, 586
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 960, 586
        self.game_canvas = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT), pygame.SRCALPHA)
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), flags)
        self.running, self.playning = True, True
        self.dt, self.previous_time = 0, 0
        self.state_stack = []

        self.student = None

        #pygame.mouse.set_visible(0)
        pygame.display.set_caption('CaFE-TaMTIn')

        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick(60)

        self.load_states()

    def load_states(self):
        self.menu_screen = Menu(self)
        self.state_stack.append(self.menu_screen)

    def get_dt(self):
        now = time.time()
        self.dt = now - self.previous_time
        self.previous_time = now

    def render(self):
        self.state_stack[-1].render(self.game_canvas)
        self.screen.blit(pygame.transform.scale(self.game_canvas, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)), (0, 0))
    
    def update(self):
        self.state_stack[-1].update(self.dt)

    def handle_events(self):
        events = pygame.event.get()
        self.state_stack[-1].handle_events(events)

    def loop(self):
        
        while self.playning:
            #self.get_dt()
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
            pygame.display.flip()
            
            #print("FPS: %0.3f" % clock.get_fps())