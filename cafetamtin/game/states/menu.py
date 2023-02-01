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
from game.states.about import About
from game.states.configuration import Configuration
from game.states.new_player import NewPlayer

from game import BACKGROUND_COLOR
from game import TEXT_COLOR
from game import FONT_NAME

class Menu(State):
    def __init__(self, game):
        super().__init__(game) # or  State.__init__(self, game)
        self.menu_items = ['Novo jogo', 'Configurações', 'Sobre', 'Sair']
        self.menu_selection = 0
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.exit_game()

            self.menu_selection = super().menu_selection(event, self.menu_items, self.menu_selection)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_game()
                    
                if event.key == pygame.K_RETURN or event.key == 1073741912:
                    if self.menu_selection == 0:
                        new_state = NewPlayer(self.game)
                        new_state.enter_state()
                    if self.menu_selection == 1:
                        new_state = Configuration(self.game)
                        new_state.enter_state()
                    if self.menu_selection == 2:
                        new_state = About(self.game)
                        new_state.enter_state()
                    if self.menu_selection == 3:
                        self.exit_game()

    def exit_game(self):
        self.game.playning = False
        self.game.running = False

    def update(self, delta_time):
        pass


    def render(self, display):
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        offset_height = 0

        display.fill(BACKGROUND_COLOR)
    
        for index, item in enumerate(self.menu_items):
            button = font.render('>>'+item+'<<' if index == self.menu_selection else item, True, TEXT_COLOR)
            button_rect = button.get_rect(center=(screen_width/2, screen_height/2  + offset_height*30))
            display.blit(button, button_rect)
            offset_height += 1