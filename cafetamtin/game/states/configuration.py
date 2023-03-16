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
from game import WHITE, BLACK, RED, GREEN

from game.states.state import State
from game.states.menu_mixin import MenuMixin

from board.board import Board

from pony.orm import *
from database.models import DBBoard

from utils import message_box

class Configuration(MenuMixin, State):

    def __init__(self, game):
        super().__init__(game)
        self.menu_items = ['Configurar tabuleiro', 'Voltar']
        self.menu_selection = 0
        self.board = Board(self.game.app)
        self.show_configure_left = False
        self.show_configure_right = False

        self.load_board()

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
                    if self.show_configure_left or self.show_configure_right:
                        self.show_configure_left = False
                        self.show_configure_right = False
                    else:
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
        if self.show_configure_left:
            if self.board.define_left_limits():
                self.show_configure_left = False
                self.show_configure_right = True
        elif self.show_configure_right:
            if self.board.define_right_limits():
                self.show_configure_left = False
                self.show_configure_right = False
                self.board.configure(new_configuration=True)
        else:
            if self.menu_selection == 0:
                self.configure_board()
            if self.menu_selection == 1:
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

    def draw_physical_buttons(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        baseline_text = screen_height - 35
        baseline_circle = screen_height - 23

        font = pygame.font.SysFont(FONT_NAME, 20, False, False)

        if not self.show_configure_left and not self.show_configure_right:
            pygame.draw.circle(display,WHITE,(20,baseline_circle),10)
            white_text = font.render("↑", True, (0,0,0))
            display.blit(white_text, (35, baseline_text))
            
            
            pygame.draw.circle(display,BLACK,(90,baseline_circle),10)
            black_text = font.render("↓", True, (0,0,0))
            display.blit(black_text, (105, baseline_text))

        pygame.draw.circle(display,GREEN,(160,baseline_circle),10)
        green_text = font.render("OK", True, (0,0,0))
        display.blit(green_text, (175, baseline_text))

    @db_session
    def load_board(self):
        for b in DBBoard.select():
            self.board.columns = b.columns
            self.board.lines = b.lines
            self.board.top_left = (b.top_left_x, b.top_left_y)
            self.board.top_right = (b.top_right_x, b.top_right_y)
            self.board.bottom_left = (b.bottom_left_x, b.bottom_left_y)
            self.board.bottom_right = (b.bottom_right_x, b.bottom_right_y)

    def configure_board(self):
        self.show_configure_left = True
        self.show_configure_right = False

    def render(self, display):
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        offset_height = 0

        display.fill(BACKGROUND_COLOR)

        if self.show_configure_left:
            self.board.draw_configure(display, 'left')
        elif self.show_configure_right:
            self.board.draw_configure(display, 'right')
        else:
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

            text_lines = font.render(f'Linhas: {self.board.lines}', True, TEXT_COLOR)
            text_lines_rect = text_lines.get_rect(topleft=(screen_width-350, 310))
            display.blit(text_lines, text_lines_rect)

            text_columns = font.render(f'Colunas: {self.board.columns}', True, TEXT_COLOR)
            text_columns_rect = text_columns.get_rect(topleft=(screen_width-350, 330))
            display.blit(text_columns, text_columns_rect)

            text_tl = font.render(f'({self.board.top_left[0]}, {self.board.top_left[1]})', True, TEXT_COLOR)
            text_tl_rect = text_tl.get_rect(topleft=(screen_width-350, 350))
            display.blit(text_tl, text_tl_rect)

            text_tr = font.render(f'({self.board.top_right[0]}, {self.board.top_right[1]})', True, TEXT_COLOR)
            text_tr_rect = text_tr.get_rect(topright=(screen_width-50, 350))
            display.blit(text_tr, text_tr_rect)

            text_bl = font.render(f'({self.board.bottom_left[0]}, {self.board.bottom_left[1]})', True, TEXT_COLOR)
            text_bl_rect = text_bl.get_rect(topleft=(screen_width-350, 450))
            display.blit(text_bl, text_bl_rect)

            text_br = font.render(f'({self.board.bottom_right[0]}, {self.board.bottom_right[1]})', True, TEXT_COLOR)
            text_br_rect = text_br.get_rect(topright=(screen_width-50, 450))
            display.blit(text_br, text_br_rect)

        
            for index, item in enumerate(self.menu_items):
                button = font.render('>>'+item+'<<' if index == self.menu_selection else item, True, TEXT_COLOR)
                button_rect = button.get_rect(center=(screen_width/2, screen_height-80 + offset_height*30))
                display.blit(button, button_rect)
                offset_height += 1

        self.draw_physical_buttons()