#  Copyright (C) 2024 Robertino Mendes Santiago Junior
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

from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN

from base.board import Board
from game.states.state import State
from game.actors.teacher import Teacher

class Phase03Tutorial(State):
    
    def __init__(self, game) -> None:
        super().__init__(game)
        self.log('Executando Phase03-Tutorial')
        
        self.board = Board(self.game.app)
        self.teacher = Teacher(self.game.game_canvas)
        self.show_teacher = False
        
        self.images = self.load_images()
        self.load_messages()
        
    def load_images(self) -> None:
        return {
            'background': pygame.image.load(os.path.join("images", "phase03-tutorial-background.png")),
        }
        
    def load_messages(self) -> None:
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT        
        
        self.teacher.set_message(
            f"Oi {self.game.student.nickname}. Você está na terceira fase. "+
            "Vou explicar como jogá-la. Preste muita atenção.\n"+
            "\n"+
            "Pressione o botão VERMELHO para continuar", 
            "happy0"
        )
        
        self.teacher.set_message(
            "Nesta fase, você irá jogar contra mim. Iremos alternar quem começará "+
            "a jogar, e cada um escolhe um número por vez. O objetivo é obter "+
            "o maior número de somas 15.\n"+
            "\n"+
            "Pressione o botão VERMELHO para continuar",  
            "neutral1"
        )
        
        self.teacher.set_message(
            "No quadro 'Blocos disponíveis' estão os blocos que você pode selecionar, "+
            "e no quadro 'Blocos do tutor' estão os blocos que eu já selecionei.\n"+
            "\n"+
            "Pressione o botão VERMELHO para continuar",  
            "neutral1",
            position=(screen_width/2, 160)
        )
        
        self.teacher.set_message(
            "Em cada jogada, você deve colocar um bloco numerado sobre a "+
            "plataforma e pressionar o botão VERDE para validar a jogada.\n"+
            "Após a validação, o bloco numerado deve permanecer sobre a plataforma."
            "\n"+
            "Pressione o botão VERMELHO para continuar",  
            "neutral2"
        )
        
        self.teacher.set_message(
            "As possíveis somas produzidas pela combinação dos números "+
            "selecionados por cada um serão exibidas na tela.\n"+
            "\n"+
            "Pressione o botão VERMELHO para continuar",  
            "neutral2"
        )
        
        self.teacher.next_message()
        self.show_teacher = True
    
    def handle_events(self, events) -> None:
        self.game.app.physical_buttons.white_button.set_callback(self.button_white_changed)
        self.game.app.physical_buttons.black_button.set_callback(self.button_black_changed)
        self.game.app.physical_buttons.green_button.set_callback(self.button_green_changed)
        self.game.app.physical_buttons.red_button.set_callback(self.button_red_changed)

        for event in events:
            if event.type == pygame.QUIT:
                self.exit_state()

            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_v:
                    self.button_red_changed(True)
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()
                    
    def update(self, delta_time) -> None:
        pass

    def button_white_changed(self, data) -> None:
        """
        Executed when the white button of the base is pressed
        """
        pass

    def button_green_changed(self, data) -> None:
        """
        Executed when the green button of the base is pressed
        """
        pass

    def button_red_changed(self, data) -> None:
        """
        Executed when the red button of the base is pressed
        """
        if self.teacher.has_next_message():
            self.teacher.next_message()
            self.show_teacher = True
        else:
            self.show_teacher = False
            self.exit_state()


    def button_black_changed(self, data) -> None:
        """
        Executed when the black button of the base is pressed
        """
        pass
    
    def exit_state(self) -> None:
        super().exit_state()
        
    def draw_physical_buttons(self) -> None:
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        baseline_text = screen_height - 35
        baseline_circle = screen_height - 23
        
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        
        pygame.draw.circle(display,RED,(130,baseline_circle),10)
        red_text = font.render("Continuar" if (self.show_teacher and self.teacher.has_next_message()) else "Fechar", True, (0,0,0))
        display.blit(red_text, (145, baseline_text))
        
    def render(self, display) -> None:

        display.fill((255,255,255))

        background = self.images['background']
        display.blit(background, (0,0))
        self.draw_physical_buttons()
        
        if self.show_teacher:
            self.teacher.draw()