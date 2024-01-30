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

import os
import pygame
import random
from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN

from base.board import Board
from game.states.state import State
from game.actors.teacher import Teacher

class Phase04Tutorial(State):
    
    def __init__(self, game) -> None:
        super().__init__(game)
        
        self.board = Board(self.game.app)
        self.teacher = Teacher(self.game.game_canvas)
        self.show_teacher = False
        
        self.offset = 15
        self.box_width, self.box_height = 50, 50
        
        self.images = self.load_images()
        self.load_messages()
        
    def load_images(self) -> None:
        return {
            'background': pygame.image.load(os.path.join("images", "phase03-tutorial-background.png")),
            'arrow-left':pygame.image.load(os.path.join("images", "phase04-tutoring-arrow-red-left.png")),
        }
        
    def load_messages(self) -> None:
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT        
        emotions = ['happy0', 'neutral1', 'neutral2']
        
        self.teacher.set_message(
            f'Esta é a quarta e última fase, {self.game.student.nickname}. '+
            'Vou lhe explicar como jogar. Preste muita atenção.\n'+
            '\n'+
            'Pressione o botão VERMELHO para continuar', 
            emotions[random.randrange(0,len(emotions))]
        )
        
        self.teacher.set_message(
            'Serão exibidas aqui, na plataforma, combinações \n'+
            'de blocos que serão usadas como base para \n'+
            'a construção do quadrado mágico. Você deve \n'+
            'colocar os blocos sobre a plataforma \n'+
            'conforme estarão dispostos aqui.'+
            '\n\n'+
            'Depois de posicionar os blocos solicitados, \n'+
            'você deve pressionar o botão VERDE para \n'+
            'validar a configuração inicial. '+
            '\n\nPressione o botão VERMELHO para continuar',
            emotions[random.randrange(0,len(emotions))],
            modal=False,
            position=(730, 100),
            image_explication='phase04-tutoring-arrow-red-left.png'
        )
        
        self.teacher.set_message(
            'No quadro "Possíveis somas do estudante", será \n'+
            'exibido o "quadrado mágico" com indicação das \n'+
            'somas de 15 realizadas. Neste quadro, ainda é possível \n'+
            'visualizar a diferença existente entre cada eixo \n'+
            '(horizontal, vertical e diagonal) e o valor 15. \n'+
            'Use esses valores para planejar suas jogadas.'
            '\n\nPressione o botão VERMELHO para continuar',
            emotions[random.randrange(0,len(emotions))],
            modal=False,
            position=(260, 100),
            image_explication='phase04-tutoring-arrow-red-right.png'
        )
        
        self.teacher.set_message(
            'A cada rodada, você deverá completar o quadrado '+
            'mágico com os blocos restantes. As combinações '+
            'iniciais são alteradas no início de cada nova rodada.'+
            '\n\nPressione o botão VERMELHO para continuar', 
            emotions[random.randrange(0,len(emotions))]
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
        
    def draw_board(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT

        color = (183, 183, 138, 255)
        rect_shape = (0, 55, screen_width,screen_height)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect())
        display.blit(shape, rect_shape)

        total_shape_x = self.box_width * self.board.columns + self.offset * (self.board.columns + 1)
        total_shape_y = self.box_height * self.board.lines + self.offset * (self.board.lines + 1)

        pos_x = self.offset * 2
        pos_y = screen_height/2 - total_shape_y / 2

        pos_x_rect = total_shape_x+pos_x+self.offset
        width_rect = (screen_width-pos_x_rect-self.offset)
        height_rect = (screen_height-pos_y-50)

        color = (220,220,220,255)

        rect_shape = (pos_x_rect, pos_y, width_rect, height_rect)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect(), border_radius= 15)
        display.blit(shape, rect_shape)

        font = pygame.font.SysFont(FONT_NAME, 18, False, False)
        text = font.render('Possíveis somas do estudante', True, (0,0,0))
        text_rect = text.get_rect(topleft=(pos_x_rect+self.offset, pos_y+self.offset))
        display.blit(text, text_rect)

        color = (130,115,0,255)

        rect_shape = (pos_x,pos_y,total_shape_x,total_shape_y)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect())
        display.blit(shape, rect_shape)

        pos_x += self.offset
        pos_y += self.offset
        x = pos_x
        
        for col in range(0, self.board.columns):
            y = pos_y
            for lin in range(0, self.board.lines):
                color = (255,255,255,255)
                rect = (x,y,self.box_width,self.box_height)
                shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                pygame.draw.rect(shape, color, shape.get_rect())
                display.blit(shape, rect)

                y += self.box_height + self.offset
            x += self.box_width + self.offset
        
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

        self.draw_board()
        self.draw_physical_buttons()
        
        if self.show_teacher:
            self.teacher.draw()