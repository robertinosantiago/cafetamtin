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
import os

from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN

from base.board import Board
from game.states.state import State
from game.actors.teacher import Teacher

class Phase01Tutorial(State):
    
    def __init__(self, game):
        super().__init__(game)
        self.log('Executando Phase01-Tutorial')
        
        self.board = Board(self.game.app)
        self.teacher = Teacher(self.game.game_canvas)
        self.show_teacher = False
        
        self.images = self.load_images()
        self.load_messages()
        
        
    def load_images(self):
        return {
            'background': pygame.image.load(os.path.join("images", "classroom-background.png")),
        }
        
    def load_messages(self):
        self.teacher.set_message(
            f"Olá {self.game.student.nickname}, meu nome é Monique e estou aqui para lhe auxiliar. "+
            "Vou apresentar a você cada fase disponível no jogo.\n\n"+
            "Você irá interagir com o jogo por meio dos blocos numerados e "+
            "os botões coloridos da plataforma. As ações disponíveis no momento "+
            "de cada botão estão descritos na barra inferior do jogo. "+
            "\n\nPressione o botão VERMELHO para continuar", 
            "neutral2"
        )
        
        self.teacher.set_message(
            "Nesta fase, serão exibidas operações matemáticas "+
            "de adição e subtração no centro da tela. "+
            "Sua missão é informar o resultado da operação "+
            "utilizando os blocos numerados disponíveis.\n"+
            "\n"+
            "Pressione o botão VERMELHO para continuar",  
            "neutral1"
        )
        
        self.teacher.set_message(
            "No exemplo acima, é exibida a operação de adição "+
            "entre os números 3 e 2. Neste caso, o bloco com "+
            "o número 5 deve ser colocado sobre o tabuleiro.\n\n"+
            "Após, deve ser pressionado o botão VERDE para "+
            "verificar se a resposta está correta. O resultado "+
            "será exibido na tela.\n"+
            "\n"+
            "Pressione o botão VERMELHO para continuar",  
            "neutral1",
            "phase01-adiction-example.png"
        )
        
        self.teacher.next_message()
        self.show_teacher = True
        
    def handle_events(self, events):
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
                    
    def update(self, delta_time):
        pass

    def button_white_changed(self, data):
        """
        Executed when the white button of the base is pressed
        """
        pass

    def button_green_changed(self, data):
        """
        Executed when the green button of the base is pressed
        """
        pass

    def button_red_changed(self, data):
        """
        Executed when the red button of the base is pressed
        """
        if self.teacher.has_next_message():
            self.teacher.next_message()
            self.show_teacher = True
        else:
            self.show_teacher = False
            self.exit_state()


    def button_black_changed(self, data):
        """
        Executed when the black button of the base is pressed
        """
        pass
    
    def exit_state(self):
        super().exit_state()
        
    def draw_physical_buttons(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        baseline_text = screen_height - 35
        baseline_circle = screen_height - 23
        
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        
        pygame.draw.circle(display,RED,(130,baseline_circle),10)
        red_text = font.render("Continuar" if (self.show_teacher and self.teacher.has_next_message()) else "Fechar", True, (0,0,0))
        display.blit(red_text, (145, baseline_text))

        # if not self.show_teacher:
        #     pygame.draw.circle(display,WHITE,(20,baseline_circle),10)
        #     white_text = font.render("Pausar", True, (0,0,0))
        #     display.blit(white_text, (35, baseline_text))

        #     pygame.draw.circle(display,GREEN,(220,baseline_circle),10)
        #     green_text = font.render("Responder", True, (0,0,0))
        #     display.blit(green_text, (235, baseline_text))
        
    def render(self, display):
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        offset_height = 0

        display.fill((255,255,255))

        background = self.images['background']
        display.blit(background, (0,0))
        self.draw_physical_buttons()
        
        if self.show_teacher:
            self.teacher.draw()