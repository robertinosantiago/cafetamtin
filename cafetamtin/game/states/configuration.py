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
from game import BACKGROUND_COLOR
from game import TEXT_COLOR
from game import FONT_NAME

from game.states.state import State
from utils.webcam import Webcam

class Configuration(State):

    def __init__(self, game):
        super().__init__(game)
        self.menu_items = ['Voltar']
        self.menu_selection = 0
        self.webcam = Webcam(0)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.exit_state()

            self.menu_selection = super().menu_selection(event, self.menu_items, self.menu_selection)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()
                if event.key == pygame.K_RETURN:
                    if self.menu_selection == 0:
                        self.exit_state()

    def update(self, delta_time):
        pass

    def render(self, display):
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        offset_height = 0

        display.fill(BACKGROUND_COLOR)

        title_config = font.render('Configurações', True, TEXT_COLOR)
        title_config_rect = title_config.get_rect(center=(screen_width/2, 10))
        display.blit(title_config, title_config_rect)

        text_webcam_aprendiz = font.render('Webcam Aprendiz', True, TEXT_COLOR)
        text_webcam_aprendiz_rect = text_webcam_aprendiz.get_rect(center=(120, 25))
        display.blit(text_webcam_aprendiz, text_webcam_aprendiz_rect)

        display.blit(self.webcam.get_image(), (30,35))
    
        for index, item in enumerate(self.menu_items):
            button = font.render('>>'+item+'<<' if index == self.menu_selection else item, True, TEXT_COLOR)
            button_rect = button.get_rect(center=(screen_width/2, screen_height-30))
            display.blit(button, button_rect)
            offset_height += 1