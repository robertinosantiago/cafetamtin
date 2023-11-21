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
from datetime import datetime

from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN, YELLOW

from game.actors.teacher import Teacher
from base.board import Board
from game.states.state import State
from utils.confetti import Confetti
from production.type_error import TypeError

class Phase01Feedback(State):
    
    def __init__(self, game, working_memory):
        super().__init__(game)
        self.memory = working_memory
        self.board = Board(self.game.app)
        self.teacher = Teacher(self.game.game_canvas)
        self.confetti = Confetti()
        self.frame_confetti = 1
                
        self.box_width, self.box_height = 60, 60
        
        self.show_error_misinterpretation_language = False
        self.show_error_operator_use = False
        self.show_error_rule_deficiency = False
        self.show_error_uncategorized_solution = False
        self.show_error_domain_deficiency = False
        
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
        self.memory.add_fact('last_execution', datetime.now())
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
        text_rect = text.get_rect(topright=pos)
        display.blit(text, text_rect)
    
        
    def draw_arrow_left(self, message, pos, angle, color, size):
        display = self.game.game_canvas
        font = pygame.font.SysFont('DejaVu Sans', size, False, False)
        text = font.render(u'\u2190 '+f'{message}', True, color)
        text = pygame.transform.rotate(text, angle)
        text_rect = text.get_rect(topleft=pos)
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
        
        self.blit_text('Números informados', (215, 90), WHITE, 18)
        
        offset = 5
        x = 120
        y = 110
        for i in range(len(result)):
            self.blit_box(str(result[i]), (x,y), (220, 3, 3), 40)
            if (i+1) % 3 == 0:
                x = 120
                y += self.box_height + offset
            else:
                x += self.box_width + offset
            
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
        
        self.draw_arrow_right('Adição' if part1[1] == '+' else 'Subtração', (400, 160), 45, YELLOW, 18)
        self.draw_arrow_left('Parcela' if part1[1] == '+' else 'Minuendo', (450, 125), 0, YELLOW, 18)
        self.draw_arrow_left('Parcela' if part1[1] == '+' else 'Subtraendo', (450, 175), 0, YELLOW, 18)
        self.draw_arrow_left('Soma ou' if part1[1] == '+' else 'Resto ou', (460, 225), 0, YELLOW, 18)
        self.blit_text('total' if part1[1] == '+' else 'diferença', (505, 250), YELLOW, 18)
        
        if count_plus + count_minus == 2:
            exp = [result_part1, str(part1[3]), str(part1[4])]
            exp = ''.join(exp)
            
            self.blit_text(str(result_part1), (710, 130), WHITE, 40)
            self.blit_text(str(part1[3]), (690, 150), YELLOW, 40)
            self.blit_text(str(part1[4]), (710, 180), WHITE, 40)
            self.blit_text('____', (710, 187), WHITE, 40)
            self.blit_box(str(eval(exp)), (680, 215), (220, 3, 3), 40)
            
            self.draw_arrow_right('Adição' if part1[3] == '+' else 'Subtração', (680, 160), 45, YELLOW, 18)
            self.draw_arrow_left('Parcela' if part1[3] == '+' else 'Minuendo', (735, 125), 0, YELLOW, 18)
            self.draw_arrow_left('Parcela' if part1[3] == '+' else 'Subtraendo', (735, 175), 0, YELLOW, 18)
            self.draw_arrow_left('Soma ou' if part1[3] == '+' else 'Resto ou', (745, 230), 0, YELLOW, 18)
            self.blit_text('total' if part1[3] == '+' else 'diferença', (790, 255), YELLOW, 18)
    
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
        
        self.draw_arrow_right('Adição' if part1[1] == '+' else 'Subtração', (405, 160), 45, YELLOW, 18)
                
        if count_plus + count_minus == 2:
            exp = [result_part1, str(part1[3]), str(part1[4])]
            exp = ''.join(exp)
            
            self.blit_text(str(result_part1), (650, 130), WHITE, 40)
            self.blit_text(str(part1[3]), (630, 150), YELLOW, 40)
            self.blit_text(str(part1[4]), (650, 180), WHITE, 40)
            self.blit_text('____', (650, 187), WHITE, 40)
            self.blit_text(str(eval(exp)), (650, 230), WHITE, 40)
            
            self.draw_arrow_right('Adição' if part1[3] == '+' else 'Subtração', (610, 160), 45, YELLOW, 18)
            
    def draw_error_misinterpretation_language(self):
        '''
        display = self.game.game_canvas
        box_width, box_height = 30, 30
        offset = 3
        
        total_shape_x = box_width * self.board.columns + offset * (self.board.columns + 1)
        total_shape_y = box_height * self.board.lines + offset * (self.board.lines + 1)
        
        pos_x = 130
        pos_y = 85
        color = (130,115,0,255)
        
        rect_shape = (pos_x,pos_y,total_shape_x,total_shape_y)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect())
        display.blit(shape, rect_shape)

        pos_x += offset
        pos_y += offset
        x = pos_x
        
        for col in range(0, self.board.columns):
            y = pos_y
            for lin in range(0, self.board.lines):
                color = (255,255,255,255)
                rect = (x,y,box_width,box_height)
                shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                pygame.draw.rect(shape, color, shape.get_rect())
                display.blit(shape, rect)

                y += box_height + offset
            x += box_width + offset
        '''
        pass
    
    def draw_error_domain_deficiency(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        
        expression = self.memory.get_fact('expression')
        result = self.memory.get_fact('result')
        result = int(result[0])
        part1, part2 = expression.split('=')
        
        self.draw_error_operator_use()
        
        diff = abs(result - int(part2))
        message = f'Diferença entre resultado informado e resultado esperado: {diff}'
        self.blit_text(message, (screen_width/2, 270), YELLOW, 18)
        
        
        
    def message_teacher_misinterpretation_language(self):
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        
        self.teacher.set_message(
            'Humm.. Parece que você está com dificuldades em jogar. '+ 
            'Vou dar uma breve explicação sobre o jogo. '+
            'Nesta fase, serão exibidas, no centro da tela, operações matemáticas '+
            'de adição e subtração. Você deverá colocar sobre o tabuleiro o bloco '+
            'numérico correspondente ao resultado da operação'+
            '\n\nPressione o botão VERMELHO para continuar',
            'neutral1'
        )
        self.teacher.set_message(
            'Neste exemplo, é exibida a operação de adição envolvendo os termos 3 e 2. '+
            'Essa soma produz o número 5 como resultado. Então, você deve colocar '+
            'o bloco com o número 5 sobre o tabuleiro e pressionar o botão VERDE '+
            'para verificar se a resposta está correta. '+
            '\n\nPressione o botão VERMELHO para continuar',
            'happy0',
            'phase01-misinterpretation-language01.png'
        )
        self.teacher.set_message(
            'Neste segundo exemplo, é exibida uma operação matemática envolvendo os '+
            'operadores de adição e subtração. Assim, podemos realizar primeiro a '+
            'adição (6+2), produzindo o resultado 8. '+
            '\n\nPressione o botão VERMELHO para continuar',
            'happy0',
            'phase01-misinterpretation-language02.png'
        )
        self.teacher.set_message(
            'Agora, podemos realizar a operação de subtração (8-7), produzindo o '+
            'resultado 1. Dessa forma, o bloco com o número 1 deve ser colocado sobre '+
            'o tabuleiro e, após, o botão VERDE deve ser pressionado para verificar '+
            'se o resultado está correto.'+
            '\n\nPressione o botão VERMELHO para fechar',
            'happy1',
            'phase01-misinterpretation-language02.png'
        )
        self.show_error_misinterpretation_language = True

    def message_teacher_uncategorized_solution(self):
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        self.teacher.set_message(
            'Ops. Não era essa a resposta esperado. Parece que você não compreendeu bem os conceitos de adição e subtração. ' +
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
        
    def message_teacher_operator_use(self):
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        expression = self.memory.get_fact('expression')
        part1, part2 = expression.split('=')
        count_plus = part1.count('+')
        count_minus = part1.count('-')
        result = self.memory.get_fact('result')
        if len(result) > 0:
            result = int(result[0])
        else:
            result = 0
        exp = [str(part1[0]),str(part1[1]),str(part1[2])]
        exp = ''.join(exp)
        result_exp = str(eval(exp))
            
        message = 'Ops. Você não observou corretamente os operadores envolvidos na operação. '
        if count_minus + count_plus == 1:
            message += f'Perceba que o operador envolvido na operação é o símbolo "{part1[1]}" representando uma {"adição" if part1 == "+" else "subtração"}. '
        else:
            exp = [result_exp, str(part1[3]), str(part1[4])]
            exp = ''.join(exp)
            result_exp = str(eval(exp))
            
            message += f'Perceba que o primeiro operador envolvido na operação é o símbolo "{part1[1]}" representando uma {"adição" if part1[1] == "+" else "subtração"}. '
            message += f'O segundo operador é o símbolo "{part1[3]}" representando uma {"adição" if part1[3] == "+" else "subtração"}. '
        message += '\n\nPressione o botão VERMELHO para continuar'
        
        self.teacher.set_message(message, 'neutral1', modal=False, position=(screen_width/2,370))
            
        self.teacher.set_message(
            f'Assim, a operação matemática {part1} resulta em {result_exp}. Tente novamente. '+
            '\n\nPressione o botão VERMELHO para continuar',
            'neutral1', modal=False, position=(screen_width/2,370)
        )
        self.show_error_operator_use = True
        
    def message_teacher_rule_deficiency(self):
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        expression = self.memory.get_fact('expression')
        part1, part2 = expression.split('=')
        count_plus = part1.count('+')
        count_minus = part1.count('-')
        result = self.memory.get_fact('result')
        
        message = 'Atenção! Você deve informar o resultado da operação matemática exibida. Ao invés disso, você colocou os blocos '
        for i in range(len(result)):
            message += f'{result[i]}'
            if i < len(result) - 2:
                message += ', '
            elif i < len(result) - 1:
                message += ' e '
        message += ' sobre o tabuleiro. \n\nPressione o botão VERMELHO para continuar'
        self.teacher.set_message(message, 'neutral1', modal=False, position=(screen_width/2,370))
        self.teacher.set_message(
            'Perceba que você deve colocar apenas UM bloco sobre o tabuleiro. '+
            '\n\nPressione o botão VERMELHO para continuar',
            'neutral1', modal=False, position=(screen_width/2,370)
        )
        
        self.show_error_rule_deficiency = True
        
    def message_teacher_domain_deficiency(self):
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT        
        expression = self.memory.get_fact('expression')
        result = self.memory.get_fact('result')
        result = int(result[0])
        part1, part2 = expression.split('=')
        
        
        self.teacher.set_message(
            f'Ah.. Você não acertou. Você informou como resposta o número {result}. '+
            f'Porém, como você pode perceber na resolução acima, a resposta correta é o número {int(part2)}. ' +
            '\n\nPressione o botão VERMELHO para continuar',
            'neutral1', modal=False, position=(screen_width/2,370)
        )
        
        self.show_error_domain_deficiency = True
        
    def feedback(self):
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        errors = self.memory.get_fact('errors')
        expression = self.memory.get_fact('expression')
        result = self.memory.get_fact('result')
        correct = self.memory.get_fact('correct')
        valid = self.memory.get_fact('valid')
        quantity_corrects = self.memory.get_fact('quantity_corrects')
        num_terms = self.memory.get_fact('num_terms')
        
        
        if len(result) > 0:
            result = int(result[0])
        else:
            result = 0
        part1, part2 = expression.split('=')
        
        count_plus = part1.count('+')
        count_minus = part1.count('-')
        
        if (len(errors) == 0 and correct and valid):
            emotions = ['happy0', 'happy1', 'happy2', 'happy3', 'happy4', 'heart0']
            self.teacher.set_message('Parabéns!!!\n'+
                f'Sua resposta está correta. O resultado da operaçao {part1} é {result}. '+
                '\n\nPressione o botão VERMELHO para continuar', 
                emotions[random.randrange(0,len(emotions))]
            )
            self.frame_confetti = 1
            self.confetti.visible = True
            quantity_corrects += 1
            
            
            if quantity_corrects >= 5 and num_terms == 2:
                num_terms = 3
                self.memory.add_fact('num_terms', num_terms)
            
        else:
            quantity_corrects = 0
            errors = sorted(errors, key=lambda error: error.weight, reverse=True)
            error = errors[0]
            history_errors = self.memory.get_fact('history_errors')
            history_errors.append(error)
            self.memory.add_fact('history_errors', history_errors)
            
            quantity_errors = self.memory.get_fact('quantity_errors')
            quantity_errors += 1
            self.memory.add_fact('quantity_errors', quantity_errors)
            
            if error.type == TypeError.TYPE_MISINTERPRETATION_LANGUAGE:
                self.message_teacher_misinterpretation_language()
            elif error.type == TypeError.TYPE_DIRECTLY_IDENTIFIABLE:
                if error.subtype == TypeError.SUBTYPE_DOMAIN_DEFICIENCY:
                    self.message_teacher_domain_deficiency()
                elif error.subtype == TypeError.SUBTYPE_RULE_DEFICIECY:
                    self.message_teacher_rule_deficiency()
                elif error.subtype == TypeError.SUBTYPE_OPERATOR_USAGE:
                    self.message_teacher_operator_use()
            elif error.type == TypeError.TYPE_INDIRECTLY_IDENTIFIABLE:
                pass
            elif error.type == TypeError.TYPE_UNCATEGORIZED_SOLUTION:
                self.message_teacher_uncategorized_solution()
                
            self.memory.reset()
            
            
            #self.message_teacher_domain_deficiency()
            #self.message_teacher_misinterpretation_language()
            #self.message_teacher_uncategorized_solution()
            #self.message_teacher_operator_use()
            #self.message_teacher_rule_deficiency()
            
        self.memory.add_fact('quantity_corrects', quantity_corrects)
        self.teacher.next_message()
        self.show_teacher = True
        
    def draw_confetti(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        frame = self.confetti.get_image(self.frame_confetti)
        frame_rect = frame.get_rect(center=(screen_width/2, screen_height/2 - 80))
        display.blit(frame, frame_rect)
        self.frame_confetti += 1
        if self.frame_confetti > self.confetti.total_frames:
            self.confetti.visible = False
        
    def render(self, display):
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        offset_height = 0
        
        display.fill((255,255,255))
        
        background = self.images['background']
        display.blit(background, (0,0))
        
        self.draw_physical_buttons()
        
        if self.show_error_domain_deficiency:
            self.draw_error_domain_deficiency()
        
        if self.show_error_misinterpretation_language:
            self.draw_error_misinterpretation_language()
        
        if self.show_error_operator_use:
            self.draw_error_operator_use()
        
        if self.show_error_rule_deficiency:
            self.draw_error_rule_deficiency()
            
        if self.show_error_uncategorized_solution:
            self.draw_error_uncategorized_solution()
        
        if self.show_teacher:
            self.teacher.draw()
            
        if self.confetti.visible:
            self.draw_confetti()
        