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
from game.states.menu_mixin import MenuMixin

class Configuration(MenuMixin, State):

    def __init__(self, game):
        super().__init__(game)
        self.menu_items = ['Voltar']
        self.menu_selection = 0
        

    def handle_events(self, events):
        self.game.app.physical_buttons.white_button.when_pressed = self.buttonUpChanged
        self.game.app.physical_buttons.black_button.when_pressed = self.buttonDownChanged
        self.game.app.physical_buttons.green_button.when_pressed = self.buttonOkChanged
        self.game.app.physical_buttons.red_button.when_pressed = self.buttonPauseChanged

        for event in events:
            if event.type == pygame.QUIT:
                self.exit_state()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()

                if event.key == pygame.K_UP:
                    self.menu_selection =  self.move_menu_up(self.menu_items, self.menu_selection)

                if event.key == pygame.K_DOWN:
                    self.menu_selection = self.move_menu_down(self.menu_items, self.menu_selection)

                if event.key == pygame.K_RETURN or event.key == 1073741912:
                    self.execute_action_menu()

    def exit_state(self):
        super().exit_state()
        self.game.app.camera_student.release()
        self.game.app.camera_board.release()

    def execute_action_menu(self):
        if self.menu_selection == 0:
            self.exit_state()

    def buttonUpChanged(self):
        self.menu_selection = self.move_menu_up(self.menu_items, self.menu_selection)

    def buttonDownChanged(self):
        self.menu_selection = self.move_menu_down(self.menu_items, self.menu_selection)

    def buttonOkChanged(self):
        self.execute_action_menu()
    
    def buttonPauseChanged(self):
        pass

    def update(self, delta_time):
        pass

    def render(self, display):
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        offset_height = 0

        display.fill(BACKGROUND_COLOR)

        title_config = font.render('Configurações', True, TEXT_COLOR)
        title_config_rect = title_config.get_rect(center=(screen_width/2, 20))
        display.blit(title_config, title_config_rect)

        text_webcam_student = font.render('Webcam Aprendiz', True, TEXT_COLOR)
        text_webcam_student_rect = text_webcam_student.get_rect(center=(120, 35))
        display.blit(text_webcam_student, text_webcam_student_rect)
        display.blit(self.game.app.camera_student.get_image(), (30,50))

        text_webcam_board = font.render('Webcam Tabuleiro', True, TEXT_COLOR)
        text_webcam_board_rect = text_webcam_board.get_rect(center=(screen_width-260, 35))
        display.blit(text_webcam_board, text_webcam_board_rect)
        display.blit(self.game.app.camera_board.get_image(), (screen_width-320-30,50))
    
        for index, item in enumerate(self.menu_items):
            button = font.render('>>'+item+'<<' if index == self.menu_selection else item, True, TEXT_COLOR)
            button_rect = button.get_rect(center=(screen_width/2, screen_height-30))
            display.blit(button, button_rect)
            offset_height += 1