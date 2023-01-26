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

class State():
    def __init__(self, game):
        self.game = game
        self.previous_state = None

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
    
    def exit_state(self):
        self.game.state_stack.pop()

    def menu_selection (self, event, menu_items, menu_selection):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if menu_selection == 0:
                    menu_selection = len(menu_items)-1
                else:
                    menu_selection -= 1

            if event.key == pygame.K_DOWN:
                if menu_selection >= len(menu_items)-1:
                    menu_selection = 0
                else:
                    menu_selection += 1
        return menu_selection