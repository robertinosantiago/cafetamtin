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

from game.states.state import State
from game.states.menu_mixin import MenuMixin
from game.states.phase01 import Phase01
from utils.text_input import TextInputVisualizer
from utils.text_input import TextInputManager
from game.actors.student import Student

from pony.orm import *
from database.models.user import User


from game import BACKGROUND_COLOR
from game import TEXT_COLOR
from game import ERROR_COLOR
from game import FONT_NAME

class NewPlayer(MenuMixin, State):
    def __init__(self, game):
        super().__init__(game) # or  State.__init__(self, game)
        self.menu_items = ['Avançar', 'Voltar']
        self.menu_selection = 0
        manager = TextInputManager(validator= lambda input: len(input) <= 3)
        self.input_number_player = TextInputVisualizer(manager=manager)
        self.error_message = ''
        self.show_error_message = False
    
    def is_empty_input(self):
        return len(self.input_number_player.value) == 0

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
            
        self.input_number_player.update(events)

    def execute_action_menu(self):
        if self.menu_selection == 0:
            if self.is_empty_input():
                self.show_error_message = True
                self.error_message = 'Campo obrigatório'
            else:
                try:
                    self.load_user(int(self.input_number_player.value))
                    self.show_error_message = False
                    self.input_number_player.value = ''
                    new_state = Phase01(self.game)
                    new_state.enter_state()
                except ObjectNotFound:
                    self.show_error_message = True
                    self.error_message = 'Código de estudante inválido'
                except ValueError:
                    self.show_error_message = True
                    self.error_message = 'Código de estudante inválido'
                    
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
    
    @db_session
    def load_user(self, user_id):
        if user_id:
            user = User[user_id]
            student = Student(user.name, user.nickname, user.age, user.gender)
            self.game.student = student

    def render(self, display):
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        offset_height = 0

        display.fill(BACKGROUND_COLOR)

        text_enter_number = font.render('Informe o código de aluno', True, TEXT_COLOR)
        text_enter_number_rect = text_enter_number.get_rect(center=(screen_width/2, screen_height/2 - 100))
        display.blit(text_enter_number, text_enter_number_rect)

        display.blit(self.input_number_player.surface, (screen_width/2-self.input_number_player.surface.get_width()/2,screen_height/2 - 60))

        if self.show_error_message:        
            text_error_number = font.render(self.error_message, True, ERROR_COLOR)
            text_error_number_rect = text_error_number.get_rect(center=(screen_width/2, screen_height/2 - 10))
            display.blit(text_error_number, text_error_number_rect)
    
        for index, item in enumerate(self.menu_items):
            button = font.render('>>'+item+'<<' if index == self.menu_selection else item, True, TEXT_COLOR)
            button_rect = button.get_rect(center=(screen_width/2, screen_height/2 + 50  + offset_height*30))
            display.blit(button, button_rect)
            offset_height += 1