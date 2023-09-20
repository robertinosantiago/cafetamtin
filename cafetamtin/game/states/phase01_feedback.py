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
import random
import os

from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN, YELLOW

from game.actors.teacher import Teacher
from game.states.state import State
from utils.confetti import Confetti

class Phase01Feedback(State):
    
    def __init__(self, game, working_memory):
        super().__init__(game)
        self.memory = working_memory
        self.teacher = Teacher(self.game.game_canvas)
        self.confetti = Confetti()
        self.frame_confetti = 1
        self.box_width, self.box_height = 60, 60
        
        self.show_error_operator_use = False
        self.show_error_rule_deficiency = False
        self.show_error_uncategorized_solution = False
        
        self.images = self.load_images()
        self.feedback()
        
    def load_images(self):
        return {
            'background': pygame.image.load(os.path.join("images", "classroom-background.png")),
            'heart': pygame.image.load(os.path.join("images", "heart.png")),
            'table': pygame.image.load(os.path.join("images", "table.png")),
            'student-desk': pygame.image.load(os.path.join("images", "student-desk.png")),
        }
        
    def handle_events(self, events):
        self.game.app.physical_buttons.white_button.set_callback(self.button_white_changed)
        self.game.app.physical_buttons.black_button.set_callback(self.button_black_changed)
        self.game.app.physical_buttons.green_button.set_callback(self.button_green_changed)
        self.game.app.physical_buttons.red_button.set_callback(self.button_red_changed)

        for event in events:
            if event.type == pygame.QUIT:
                self.exit_state()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("escape")
                    self.exit_state()
                    
    def update(self, delta_time):
        pass
    
    
    def button_white_changed(self, data):
        """
        Executed when the white button of the base is pressed
        """
        pass
    
    def button_black_changed(self, data):
        """
        Executed when the black button of the base is pressed
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
            self.teacher.clear_messages()
            self.exit_state()
    
    def exit_state(self):
        super().exit_state()
        
    def draw_confetti(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        frame = self.confetti.get_image(self.frame_confetti)
        frame_rect = frame.get_rect(center=(screen_width/2, screen_height/2 - 80))
        display.blit(frame, frame_rect)
        self.frame_confetti += 1
        if self.frame_confetti > self.confetti.total_frames:
            self.confetti.visible = False
    
    def draw_physical_buttons(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        baseline_text = screen_height - 35
        baseline_circle = screen_height - 23
        
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        
        pygame.draw.circle(display,RED,(130,baseline_circle),10)
        red_text = font.render("Continuar" if (self.show_teacher and self.teacher.has_next_message()) else "Fechar", True, (0,0,0))
        display.blit(red_text, (145, baseline_text))

    def blit_text(self, text, pos, color, size):
        display = self.game.game_canvas
        font = pygame.font.SysFont(FONT_NAME, size, False, False)
        text = font.render(text, True, color)
        text_rect = text.get_rect(center=(pos[0], pos[1]))
        display.blit(text, text_rect)
        
    def blit_box(self, text, pos, color, size):
        display = self.game.game_canvas
        rect = (pos[0], pos[1], self.box_width, self.box_height)
        shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect())
        display.blit(shape, rect)
        self.blit_text(text, (pos[0]+self.box_width/2, pos[1]+self.box_height/2), WHITE, size)

    def draw_arrow_right(self, message, pos, angle, color, size):
        display = self.game.game_canvas
        font = pygame.font.SysFont('DejaVu Sans', size, False, False)
        text = font.render(f'{message}'+u' \u2192', True, color)
        text = pygame.transform.rotate(text, angle)
        text_rect = text.get_rect(midright=pos)
        display.blit(text, text_rect)
    
        
    def draw_arrow_left(self, message, pos, angle, color, size):
        display = self.game.game_canvas
        font = pygame.font.SysFont('DejaVu Sans', size, False, False)
        text = font.render(u'\u2190 '+f'{message}', True, color)
        text = pygame.transform.rotate(text, angle)
        text_rect = text.get_rect(midleft=pos)
        display.blit(text, text_rect)
        
    def draw_circle(self, pos, radius, color):
        display = self.game.game_canvas
        pygame.draw.circle(display,color,pos,radius)
        
    def draw_error_uncategorized_solution(self):
        display = self.game.game_canvas
        
        x = 200
        y = 90
        self.draw_circle((x,y), 10, YELLOW)
        self.draw_circle((x+40,y), 10, YELLOW)
        self.draw_circle((x+80,y), 10, YELLOW)
        self.draw_circle((x+20,y+40), 10, YELLOW)
        self.draw_circle((x+60,y+40), 10, YELLOW)
        
        self.blit_text('+', (x+150,y+20), YELLOW, 40)
        
        self.draw_circle((x+220,y), 10, YELLOW)
        self.draw_circle((x+260,y), 10, YELLOW)
        self.draw_circle((x+240,y+40), 10, YELLOW)
        
        self.blit_text('=', (x+330,y+20), YELLOW, 40)
        
        self.draw_circle((x+400,y), 10, WHITE)
        self.draw_circle((x+440,y), 10, WHITE)
        self.draw_circle((x+480,y), 10, WHITE)
        self.draw_circle((x+520,y), 10, WHITE)
        self.draw_circle((x+560,y), 10, WHITE)
        self.draw_circle((x+440,y+40), 10, WHITE)
        self.draw_circle((x+480,y+40), 10, WHITE)
        self.draw_circle((x+520,y+40), 10, WHITE)
        
        x = 200
        y = 250
        self.draw_circle((x,y), 10, YELLOW)
        self.draw_circle((x+40,y), 10, YELLOW)
        self.draw_circle((x+80,y), 10, YELLOW)
        self.draw_circle((x+20,y+40), 10, YELLOW)
        self.draw_circle((x+60,y+40), 10, YELLOW)
        
        self.blit_text('-', (x+150,y+20), YELLOW, 40)
        
        self.draw_circle((x+220,y), 10, YELLOW)
        self.draw_circle((x+260,y), 10, YELLOW)
        self.draw_circle((x+240,y+40), 10, YELLOW)
        
        self.blit_text('=', (x+330,y+20), YELLOW, 40)
        
        self.draw_circle((x+480,y), 10, WHITE)
        self.draw_circle((x+520,y), 10, WHITE)
        
        
    
    def draw_error_rule_deficiency(self):
        display = self.game.game_canvas
        
        expression = self.memory.get_fact('expression')
        result = self.memory.get_fact('result')
        #result = int(result[0])
        part1, part2 = expression.split('=')
        
        self.blit_text('Números informados', (230, 90), WHITE, 18)
        offset = 0
        for i in range(len(result)):
            self.blit_box(str(result[i]), (120+self.box_width*i+offset,110), (220, 3, 3), 40)
            offset += 5
            
        self.blit_text(f'Resolução: {part1}', (430, 90), WHITE, 18)
        self.blit_text(str(part1[0]), (430, 130), WHITE, 40)
        self.blit_text(str(part1[1]), (407, 150), YELLOW, 40)
        self.blit_text(str(part1[2]), (430, 180), WHITE, 40)
        self.blit_text('____', (430, 187), WHITE, 40)
        
        count_plus = part1.count('+')
        count_minus = part1.count('-')
        
        exp = [str(part1[0]),str(part1[1]),str(part1[2])]
        exp = ''.join(exp)
        result_part1 = str(eval(exp))
        if count_plus + count_minus == 1:
            self.blit_box(result_part1, (400, 215), (220, 3, 3), 40)
        else:
            self.blit_text(result_part1, (430, 230), WHITE, 40)
        
        self.draw_arrow_right('Adição' if part1[1] == '+' else 'Subtração', (400, 190), 45, YELLOW, 18)
        self.draw_arrow_left('Parcela' if part1[1] == '+' else 'Minuendo', (450, 130), 0, YELLOW, 18)
        self.draw_arrow_left('Parcela' if part1[1] == '+' else 'Subtraendo', (450, 180), 0, YELLOW, 18)
        self.draw_arrow_left('Soma ou' if part1[1] == '+' else 'Resto ou', (460, 230), 0, YELLOW, 18)
        self.blit_text('total' if part1[1] == '+' else 'diferença', (505, 250), YELLOW, 18)
        
        if count_plus + count_minus == 2:
            exp = [result_part1, str(part1[3]), str(part1[4])]
            exp = ''.join(exp)
            
            self.blit_text(str(result_part1), (710, 130), WHITE, 40)
            self.blit_text(str(part1[3]), (690, 150), YELLOW, 40)
            self.blit_text(str(part1[4]), (710, 180), WHITE, 40)
            self.blit_text('____', (710, 187), WHITE, 40)
            self.blit_box(str(eval(exp)), (680, 215), (220, 3, 3), 40)
            
            self.draw_arrow_right('Adição' if part1[3] == '+' else 'Subtração', (680, 195), 45, YELLOW, 18)
            self.draw_arrow_left('Parcela' if part1[3] == '+' else 'Minuendo', (735, 130), 0, YELLOW, 18)
            self.draw_arrow_left('Parcela' if part1[3] == '+' else 'Subtraendo', (735, 180), 0, YELLOW, 18)
            self.draw_arrow_left('Soma ou' if part1[3] == '+' else 'Resto ou', (745, 230), 0, YELLOW, 18)
            self.blit_text('total' if part1[3] == '+' else 'diferença', (790, 250), YELLOW, 18)
    
    def draw_error_operator_use(self):
        display = self.game.game_canvas
        
        expression = self.memory.get_fact('expression')
        result = self.memory.get_fact('result')
        result = int(result[0])
        part1, part2 = expression.split('=')
        
        self.blit_text('Número informado', (230, 90), WHITE, 18)
        self.blit_box(str(result), (205,110), (220, 3, 3), 40)
        
        
        self.blit_text(f'Resolução: {part1}', (450, 90), WHITE, 18)
        self.blit_text(str(part1[0]), (450, 130), WHITE, 40)
        self.blit_text(str(part1[1]), (427, 150), YELLOW, 40)
        self.blit_text(str(part1[2]), (450, 180), WHITE, 40)
        self.blit_text('____', (450, 187), WHITE, 40)
        
        exp = [str(part1[0]),str(part1[1]),str(part1[2])]
        exp = ''.join(exp)
        result_part1 = str(eval(exp))
        self.blit_text(result_part1, (450, 230), WHITE, 40)
        
        count_plus = part1.count('+')
        count_minus = part1.count('-')
        
        if part1[1] == '+':
            self.draw_arrow_right('Adição', (370, 200), 45, YELLOW, 26)
        if part1[1] == '-':
            self.draw_arrow_right('Subtração', (360, 210), 45, YELLOW, 26)
        
        if count_plus + count_minus == 2:
            exp = [result_part1, str(part1[3]), str(part1[4])]
            exp = ''.join(exp)
            
            self.blit_text(str(result_part1), (650, 130), WHITE, 40)
            self.blit_text(str(part1[3]), (630, 150), YELLOW, 40)
            self.blit_text(str(part1[4]), (650, 180), WHITE, 40)
            self.blit_text('____', (650, 187), WHITE, 40)
            self.blit_text(str(eval(exp)), (650, 230), WHITE, 40)

    def message_teacher_uncategorized_solution(self):
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        self.teacher.set_message(
            'A adição é uma operação matemática utilizada para combinar ou juntar dois ou mais valores. '+
            'O símbolo "+" é utilizado para representar a operação de adição. '+
            '\n\nPressione o botão VERMELHO para continuar',
            'neutral1', modal=False, position=(screen_width/2,370)
        )
        self.teacher.set_message(
            'A subtração é uma operação matemática utilizada para encontrar a diferença entre dois ou mais valores. '+
            'O símbolo "-" é utilizado para representar a operação de subtração. '+
            '\n\nPressione o botão VERMELHO para continuar', 'neutral1', modal=False, position=(screen_width/2,370)
        )
        self.teacher.set_message(
            'Observe as operações ilustradas acima. Na primeira, temos 5 bolinhas e queremos adicionar mais 3 bolinhas, '+
            'resultando em 8 bolinhas. Na segunda operação, temos 5 bolinhas e retiramos 3 bolinhas, resultando em 2 bolinhas. '+
            '\n\nPressione o botão VERMELHO para continuar', 
            'neutral1', modal=False, position=(screen_width/2,370)
        )
        self.show_error_uncategorized_solution = True
        
    def feedback(self):
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        errors = self.memory.get_fact('errors')
        expression = self.memory.get_fact('expression')
        result = self.memory.get_fact('result')
        if len(result) > 0:
            result = int(result[0])
        else:
            result = 0
        part1, part2 = expression.split('=')
        
        count_plus = part1.count('+')
        count_minus = part1.count('-')
        
        if (len(errors) == 0):
            emotions = ['happy0', 'happy1', 'happy2', 'happy3', 'happy4', 'heart0']
            self.teacher.set_message('Parabéns!!!\n'+
                f'Sua resposta está correta. O resultado da operaçao {part1} é {result}.', 
                emotions[random.randrange(0,len(emotions))]
            )
            
        else:
            self.message_teacher_uncategorized_solution()
            
            
            
            #self.teacher.set_message('Ops... Você não acertou!, ', 'neutral1', modal=False, position=(400,400))
            #self.teacher.set_message(f'Observe os operadores envolvidos na operação {part1}.', 'neutral1', modal=False, position=(400,400))
            #self.teacher.set_message(f'Agora observe a resolução acima.', 'neutral1', modal=False, position=(400,400))
            
            #self.show_error_operator_use = True
            #self.show_error_rule_deficiency = True
            #self.show_error_uncategorized_solution = True
            
        
        self.teacher.next_message()
        self.show_teacher = True
        
    def render(self, display):
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        offset_height = 0
        
        display.fill((255,255,255))
        
        background = self.images['background']
        display.blit(background, (0,0))
        
        self.draw_physical_buttons()
        
        if self.show_error_operator_use:
            self.draw_error_operator_use()
        
        if self.show_error_rule_deficiency:
            self.draw_error_rule_deficiency()
            
        if self.show_error_uncategorized_solution:
            self.draw_error_uncategorized_solution()
        
        if self.confetti.visible:
            self.draw_confetti()
        
        if self.show_teacher:
            self.teacher.draw()
            
        