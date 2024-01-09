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
from pony.orm import *

from game.states.state import State
from game.states.phase01 import Phase01
from game.states.phase02 import Phase02
from game.states.phase03 import Phase03
from game.states.phase04 import Phase04
from game.states.phase01_tutorial import Phase01Tutorial
from game.states.phase02_tutorial import Phase02Tutorial
from database.models import DBUser, DBSteps

from game import BACKGROUND_COLOR
from game import TEXT_COLOR
from game import TEXT_DISABLE_COLOR
from game import FONT_NAME
from game import RED, GREEN

class Phases(State):

    def __init__(self, game):
        super().__init__(game)
        self.images = self.load_images()
        self.current_phase, self.current_score = self.load_current_phase_score()
        self.reload = True
        
    def load_images(self):
        return {
            'phase01': {
                'not-started': pygame.image.load(os.path.join("images", "phase01-not-started.png")),
                'started': pygame.image.load(os.path.join("images", "phase01-started.png")),
                'completed': pygame.image.load(os.path.join("images", "phase01-completed.png")),
            },
            'phase02': {
                'not-started': pygame.image.load(os.path.join("images", "phase02-not-started.png")),
                'started': pygame.image.load(os.path.join("images", "phase02-started.png")),
                'completed': pygame.image.load(os.path.join("images", "phase02-completed.png")),
            },
            'phase03': {
                'not-started': pygame.image.load(os.path.join("images", "phase03-not-started.png")),
                'started': pygame.image.load(os.path.join("images", "phase03-started.png")),
                'completed': pygame.image.load(os.path.join("images", "phase03-completed.png")),
            },
            'phase04': {
                'not-started': pygame.image.load(os.path.join("images", "phase04-not-started.png")),
                'started': pygame.image.load(os.path.join("images", "phase04-started.png")),
                'completed': pygame.image.load(os.path.join("images", "phase04-completed.png")),
            },
        }

    @db_session
    def load_current_phase_score(self):
        user = DBUser[self.game.student.id]
        phase = 1
        score = 0
        if len(user.steps) > 0:
            phase = max(s.phase for s in user.steps)
            score = max(s.score for s in user.steps)
        return phase, score

    def handle_events(self, events):
        self.game.app.physical_buttons.white_button.set_callback(self.buttonUpChanged)
        self.game.app.physical_buttons.black_button.set_callback(self.buttonDownChanged)
        self.game.app.physical_buttons.green_button.set_callback(self.buttonOkChanged)
        self.game.app.physical_buttons.red_button.set_callback(self.buttonExitChanged)

        for event in events:
            if event.type == pygame.QUIT:
                self.exit_state()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()

                if event.key == pygame.K_RETURN or event.key == 1073741912:
                    self.execute_action_menu()

    def buttonUpChanged(self, data):
        pass

    def buttonDownChanged(self, data):
        pass

    def buttonOkChanged(self, data):
        self.execute_action_menu()
    
    def buttonExitChanged(self, data):
        self.exit_state()

    def update(self, delta_time):
        pass

    @db_session
    def execute_action_menu(self):
        user = DBUser[self.game.student.id]
        if len(user.steps) == 0:
            step = DBSteps(phase = 1, score = 0, lifes = 3, status = 'started', user = user)
        if self.current_phase <= 1:
            new_state = Phase01(self.game)
            new_state.enter_state()    
            new_state = Phase01Tutorial(self.game)
            #new_state = Phase01(self.game)
        elif self.current_phase == 2:
            new_state = Phase02(self.game)
            new_state.enter_state()    
            new_state = Phase02Tutorial(self.game)
        elif self.current_phase == 3:
            new_state = Phase03(self.game)
        elif self.current_phase == 4:
            new_state = Phase04(self.game)
        
        self.reload = True
        new_state.enter_state()

    def draw_button_phases(self):
        display = self.game.game_canvas
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        slice_width = screen_width / 4
        offset_width = slice_width / 2

        status_phase = 'started' if self.current_phase <= 1 else 'completed'
        phase01 = self.images['phase01'][status_phase]
        phase01_rect = phase01.get_rect(center=(offset_width, screen_height/2))
        display.blit(phase01, phase01_rect)
        text = font.render('Fase 01', True, TEXT_COLOR)
        text_rect = text.get_rect(center=(offset_width, phase01_rect.bottom + 20))
        display.blit(text, text_rect)
        if status_phase == 'completed':
            text = font.render('Concluído', True, TEXT_COLOR)
            text_rect = text.get_rect(center=(offset_width, text_rect.bottom + 20))
            display.blit(text, text_rect)

        status_phase = 'not-started' if self.current_phase < 2 else ('started' if self.current_phase == 2 else 'completed')
        phase02 = self.images['phase02'][status_phase]
        phase02_rect = phase02.get_rect(center=(offset_width+slice_width, screen_height/2))
        display.blit(phase02, phase02_rect)
        text = font.render('Fase 02', True, TEXT_DISABLE_COLOR if status_phase == 'not-started' else TEXT_COLOR)
        text_rect = text.get_rect(center=(offset_width+slice_width, phase01_rect.bottom + 20))
        display.blit(text, text_rect)
        if status_phase == 'completed':
            text = font.render('Concluído', True, TEXT_COLOR)
            text_rect = text.get_rect(center=(offset_width+slice_width, text_rect.bottom + 20))
            display.blit(text, text_rect)

        status_phase = 'not-started' if self.current_phase < 3 else ('started' if self.current_phase == 3 else 'completed')
        phase03 = self.images['phase03'][status_phase]
        phase03_rect = phase03.get_rect(center=(offset_width+slice_width*2, screen_height/2))
        display.blit(phase03, phase03_rect)
        text = font.render('Fase 03', True, TEXT_DISABLE_COLOR if status_phase == 'not-started' else TEXT_COLOR)
        text_rect = text.get_rect(center=(offset_width+slice_width*2, phase01_rect.bottom + 20))
        display.blit(text, text_rect)
        if status_phase == 'completed':
            text = font.render('Concluído', True, TEXT_COLOR)
            text_rect = text.get_rect(center=(offset_width+slice_width*2, text_rect.bottom + 20))
            display.blit(text, text_rect)

        status_phase = 'not-started' if self.current_phase < 4 else ('started' if self.current_phase == 4 else 'completed')
        phase04 = self.images['phase04'][status_phase]
        phase04_rect = phase04.get_rect(center=(offset_width+slice_width*3, screen_height/2))
        display.blit(phase04, phase04_rect)
        text = font.render('Fase 04', True, TEXT_DISABLE_COLOR if status_phase == 'not-started' else TEXT_COLOR)
        text_rect = text.get_rect(center=(offset_width+slice_width*3, phase01_rect.bottom + 20))
        display.blit(text, text_rect)
        if status_phase == 'completed':
            text = font.render('Concluído', True, TEXT_COLOR)
            text_rect = text.get_rect(center=(offset_width+slice_width*3, text_rect.bottom + 20))
            display.blit(text, text_rect)

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
        
        pygame.draw.circle(display,GREEN,(20,baseline_circle),10)
        text = font.render("Iniciar", True, (0,0,0))
        display.blit(text, (35, baseline_text))

        pygame.draw.circle(display,RED,(120,baseline_circle),10)
        text = font.render("Voltar", True, (0,0,0))
        display.blit(text, (135, baseline_text))
    
    def render(self, display):
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        
        display.fill(BACKGROUND_COLOR)
        if self.reload:
            self.current_phase, self.current_score = self.load_current_phase_score()
            self.reload = False
        self.draw_button_phases()
        self.draw_physical_buttons()

