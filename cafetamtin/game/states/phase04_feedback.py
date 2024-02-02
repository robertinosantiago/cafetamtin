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
import math
import pygame
import random
import logging
from pony.orm import *
from pygame.locals import *
from datetime import datetime
from itertools import combinations

from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN, DARKGREEN

from base.board import Board
from base.facial import FacialThread
from game.states.state import State
from game.actors.teacher import Teacher
from game.actors.student import Student
from production.type_error import TypeError
from production.phase03_checks import Phase03Checks
from production.level_rules import LevelRules
from database.models import DBSession, DBSteps, DBUser #,DBChallengeP3

class Phase04Feedback(State):
    def __init__(self, game, working_memory):
        super().__init__(game, working_memory)
    
        self.rules = LevelRules(self.memory)
        self.board = Board(self.game.app)
        self.teacher = Teacher(self.game.game_canvas)
        self.text_good_play = ['Boa jogada', 'Ótima jogada', 'Estratégia acertada', 'Tacada certeira']
                                
        self.offset = 15
        self.box_width, self.box_height = 50, 50
        
        self.show_error_misinterpretation_language = False
        self.show_error_domain_deficiency = False
        self.show_error_rule_deficiency = False
        self.show_error_operator_use = False
        self.show_error_indirectly_identifiable = False
        self.show_error_uncategorized_solution = False
        
        self.show_possible_sums = False
        
        self.images = self.load_images()
        self.feedback()

    def load_images(self) -> None:
        return {
            'background': pygame.image.load(os.path.join("images", "phase03-tutorial-background.png")),
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
        #self.memory.get_fact('timer_response').start()
        self.memory.add_fact('tips_times', 0)
        #step = self.memory.get_fact('step')
        #step += 1
        #step = self.memory.add_fact('step', step)
        self.memory.add_fact('reset_timer', True)
    
        super().exit_state()
    
    def draw_physical_buttons(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        baseline_text = screen_height - 35
        baseline_circle = screen_height - 23
        
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        
        rect = (0, screen_height - 50, screen_width, screen_height)
        shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, (200, 200, 200), shape.get_rect())
        display.blit(shape, rect)
        
        pygame.draw.circle(display,RED,(130,baseline_circle),10)
        red_text = font.render("Continuar" if (self.show_teacher and self.teacher.has_next_message()) else "Fechar", True, (0,0,0))
        display.blit(red_text, (145, baseline_text))
        
    def draw_error_misinterpretation_language(self):
        pass
    
    def draw_error_domain_deficiency(self):
        pass
    
    def draw_error_rule_deficiency(self):
        pass
    
    def draw_error_operator_use(self):
        pass
    
    def draw_error_indirectly_identifiable(self):
        pass
    
    def draw_error_uncategorized_solution(self):
        pass
    
    def message_teacher_misinterpretation_language(self):
        logging.info(f'Executando função: message_teacher_misinterpretation_language')
        initial_sums = self.__initial_sums__()
        challenges = self.memory.get_fact('challenges')
        
        emotions = ['neutral0', 'neutral1', 'neutral2']
        
        self.teacher.set_message(
            f'{self.game.student.nickname}, nas fases anteriores '+
            'você conseguir encontrar todas as outras somas 15 '+
            'produzidas pela combinação de três números entre '+
            '1 e 9. Que tal relembrar uma?'+
            '\n\nPressione o botão VERMELHO para continuar', 
            emotions[random.randrange(0,len(emotions))],
        )
        
        not_found = []
        for k,v in challenges.items():
            if not challenges[k]['found'] and k not in initial_sums:
                not_found.append(challenges[k]['equation'])
                
        equation = not_found[random.randrange(0, len(not_found))]
        
        self.teacher.set_message(
            f'O resultado da equação {equation} produz o valor '+
            '15. Tente encontrar todas as possíveis combinações. '+
            '\n\nPressione o botão VERMELHO para continuar', 
            emotions[random.randrange(0,len(emotions))],
        )
        
        self.show_error_misinterpretation_language = True
    
    def message_teacher_domain_deficiency(self):
        logging.info(f'Executando função: message_teacher_domain_deficiency')
        
        numbers = self.__student_numbers__()
        wrong_numbers_tree_odd = []
        wrong_numbers_two_even_one_odd = []
        
        for n in numbers:
            if self.__count_odd_numbers__(n) == 3:
                if sum(n) != 15:
                    wrong_numbers_tree_odd.append(n)
            if self.__count_even_numbers__(n) == 2 and self.__count_odd_numbers__(n) == 1:
                if sum(n) != 15:
                    wrong_numbers_two_even_one_odd.append(n)
        
        text_err = ['Puxa', 'Quase', 'Ops', 'Humm']
        
        message = f'{text_err[random.randrange(0,len(text_err))]} {self.game.student.nickname}. \n'
        _sum = 0
        if len(wrong_numbers_tree_odd) > 0:
            _sum = sum(wrong_numbers_tree_odd[0])
            message += 'Apesar de você ter compreendido as propriedades \n'
            message += 'dos números ímpares, ao utilizarmos \n'
            message += 'a expressão '
            message += ' + '.join(str(x) for x in wrong_numbers_tree_odd[0])
        else:
            _sum = sum(wrong_numbers_two_even_one_odd[0])
            message += 'Apesar de você ter compreendido as propriedades\n'
            message += 'dos números ímpares e números pares, ao\n'
            message += 'utilizarmos a expressão '
            message += ' + '.join(str(x) for x in wrong_numbers_two_even_one_odd[0])
        
        message += f' o resultado obtido é {_sum}. \n\n'
        message += 'Como você pode perceber, há uma diferença \n'
        message += f'de {abs(15 - _sum)} unidades em relação ao 15. '
        message += '\n\nPressione o botão VERMELHO para continuar'
        
        emotions = ['neutral0', 'neutral1', 'neutral2']
        self.teacher.set_message(
            message,
            emotions[random.randrange(0,len(emotions))],
            modal=False, 
            position=(730, 200)
        )
        
        self.show_error_domain_deficiency = True
    
    def message_teacher_rule_deficiency(self):
        logging.info(f'Executando função: message_teacher_rule_deficiency')
        
        numbers = self.__student_numbers__()
        wrong_numbers_tree_even = []
        wrong_numbers_two_odd_one_even = []
                
        for n in numbers:
            if self.__count_even_numbers__(n) == 3:
                if sum(n) != 15:
                    wrong_numbers_tree_even.append(n)
            if self.__count_odd_numbers__(n) == 2 and self.__count_even_numbers__(n) == 1:
                if sum(n) != 15:
                    wrong_numbers_two_odd_one_even.append(n)
        
        emotions = ['neutral0', 'neutral1', 'neutral2']
        message = ''
        
        if len(wrong_numbers_tree_even) > 0:
            message += f'Quase {self.game.student.nickname}! '
            message += f'Você informou '
            message += 'a seguinte \ncombinação: ' if len(wrong_numbers_tree_even) == 1 else 'as seguintes \ncombinações: '
            message += ' '.join(str(x) for x in wrong_numbers_tree_even)
            message += '. \n'
            message += 'Essa é uma sequência ' if len(wrong_numbers_tree_even) == 1 else 'Essas são sequências '
            message += 'de três números pares. \n\n'
            message += 'Uma das propriedades dos números pares \n'
            message += 'é que, ao somarmos números pares, sempre \n'
            message += 'obtemos um número par como resultado. \n'
            message += 'No entanto, observe que o número 15 é ímpar.'
            message += '\n\nPressione o botão VERMELHO para continuar'
            
            self.teacher.set_message(
                message,
                emotions[random.randrange(0,len(emotions))],
                modal=False, 
                position=(730, 200)
            )
            
        
        if len(wrong_numbers_tree_even) > 0 and len(wrong_numbers_two_odd_one_even) > 0:
            message = 'Além disso, tem outro detalhe. \n'
        else:
            message = f'Quase {self.game.student.nickname}! '
            
        if len(wrong_numbers_two_odd_one_even) > 0:
            message += 'Você colocou sobre o tabuleiro '
            message += 'a seguinte \ncombinação: ' if len(wrong_numbers_two_odd_one_even) == 1 else 'as seguintes \ncombinações: '
            message += ' '.join(str(x) for x in wrong_numbers_two_odd_one_even)
            message += '. '
            message += 'Essa é uma sequência ' if len(wrong_numbers_two_odd_one_even) == 1 else 'Essas são sequências '
            message += 'de \ndois números ímpares e um número par. '
            message += '\n\nPressione o botão VERMELHO para continuar'
            
            self.teacher.set_message(
                message,
                emotions[random.randrange(0,len(emotions))],
                modal=False, 
                position=(730, 200)
            )
            
            self.teacher.set_message(
                'Assim, se somarmos dois números \n '+
                'ímpares e um número par, o resultado \n'+
                'será sempre par. No entanto, observe \n'+
                'que o número 15 é ímpar.'+
                '\n\nPressione o botão VERMELHO para continuar',
                emotions[random.randrange(0,len(emotions))],
                modal=False, 
                position=(730, 200)
            )
            
            self.teacher.set_message(
                'Confira no quadro "Possíveis somas do estudante"\n'+
                'os valores apresentados e tente resolver o \n'+
                'quadrado mágico. '+
                '\n\nPressione o botão VERMELHO para continuar',
                emotions[random.randrange(0,len(emotions))],
                modal=False, 
                position=(730, 200)
            )
        
        self.show_error_rule_deficiency = True
    
    def message_teacher_operator_use(self):
        logging.info(f'Executando função: message_teacher_operator_use')
        
        self.teacher.set_message('Erro', 'neutral0', modal=False)
        
        self.show_error_operator_use = True
    
    def message_teacher_indirectly_identifiable(self):
        logging.info(f'Executando função: message_teacher_indirectly_identifiable')
        numbers_student = self.memory.get_fact('numbers_student')
        
        emotions = ['neutral0', 'neutral1', 'neutral2']
        
        position = numbers_student.get(5)
        if not position or (position != (4,4)):
            message = f'{self.game.student.nickname} observe que você não \n'
            message += 'colocou o bloco do número 5 no \n'
            message += 'centro do quadrado mágico. \n\n'
            message += 'Para resolver o quadrado mágico é \n'
            message += 'necessário que o número 5 esteja \n'
            message += 'no centro, pois ele aparece em \n'
            message += 'quatro possíveis somas \n'
            message += '(duas diagonais, horizontal e vertical).'
            message += '\n\nPressione o botão VERMELHO para continuar'
            self.teacher.set_message(
                message,
                emotions[random.randrange(0,len(emotions))],
                modal=False, 
                position=(730, 200)
            )
        else:
            numbers_even = {}
            numbers_not_corner = []
        
            for key, values in numbers_student.items():
                if key % 2 == 0:
                    numbers_even[key] = values
                    
            for key, values in numbers_even.items():
                if not self.__position_is_corner__(values):
                    numbers_not_corner.append(key)
                    
            message = f'{self.game.student.nickname} observe que você não \n'
            message += 'colocou '
            message += 'o número ' if len(numbers_not_corner) == 1 else 'os números '
            message += ', '.join(str(x) for x in numbers_not_corner)
            message += ' no canto.\n\n ' if len(numbers_not_corner) == 1 else 'nos cantos.\n\n '
            message += 'Os números pares aparecem em três somas \n'
            message += '(horizontal, vertical e diagonal). \n'
            message += 'Assim, para resolver o quadrado mágico, \n'
            message += 'os números pares devem ser colocados \n'
            message += 'nos cantos.'
            message += '\n\nPressione o botão VERMELHO para continuar'
            self.teacher.set_message(
                message,
                emotions[random.randrange(0,len(emotions))],
                modal=False, 
                position=(730, 200)
            )
            
        self.teacher.set_message(
            'Observe no quadro "Possíveis somas do estudante"\n'+
            'os valores apresentados e tente resolver o \n'+
            'quadrado mágico. '+
            '\n\nPressione o botão VERMELHO para continuar',
            emotions[random.randrange(0,len(emotions))],
            modal=False, 
            position=(730, 200)
        )
        
        self.show_error_indirectly_identifiable = True
    
    def message_teacher_uncategorized_solution(self):
        logging.info(f'Executando função: message_teacher_uncategorized_solution')
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        
        emotions = ['neutral0', 'neutral1', 'neutral2']
        
        self.teacher.set_message(
            'Vejo que você não conseguiu resolver \n'+
            f'nenhuma soma 15, {self.game.student.nickname}. \n'+
            'Vou lhe explicar novamente as regras desta fase. '+
            '\n\nPressione o botão VERMELHO para continuar',
            emotions[random.randrange(0,len(emotions))],
        )
        
        self.teacher.set_message(
            'Você deve colocar os blocos numerados "\n'+
            'no centro do tabuleiro, organizados em \n'+
            '3 linhas e 3 colunas, formando um "quadrado". \n'+
            '\n\nPressione o botão VERMELHO para continuar',
            emotions[random.randrange(0,len(emotions))],
            #position=(screen_width/2, 400),
            image_explication='phase04-rules-games-01.png'
        )
        
        self.teacher.set_message(
            'Os blocos numerados devem ser colocados "\n'+
            'de forma que a soma de cada linha horizontal \n'+
            'deve produzir o resultado 15". \n'+
            '\n\nPressione o botão VERMELHO para continuar',
            emotions[random.randrange(0,len(emotions))],
            #position=(screen_width/2, 400),
            image_explication='phase04-rules-games-02.png'
        )
        
        self.teacher.set_message(
            'Assim como a soma de cada linha vertical "\n'+
            'também deve produzir o resultado 15. \n'+
            '\n\nPressione o botão VERMELHO para continuar',
            emotions[random.randrange(0,len(emotions))],
            #position=(screen_width/2, 400),
            image_explication='phase04-rules-games-03.png'
        )
        
        self.teacher.set_message(
            'Além disso, a soma das linhas diagonais "\n'+
            'devem produzir o resultado 15. \n'+
            '\n\nPressione o botão VERMELHO para continuar',
            emotions[random.randrange(0,len(emotions))],
            #position=(screen_width/2, 400),
            image_explication='phase04-rules-games-04.png'
        )
        
        self.teacher.set_message(
            'Lembre-se das propriedades dos números "\n'+
            'ímpares e pares e tente organizar os \n'+
            'blocos numerados de forma a resolver o \n'+
            '"quadrado mágico".'
            '\n\nPressione o botão VERMELHO para continuar',
            emotions[random.randrange(0,len(emotions))]
        )
        
        self.show_error_uncategorized_solution
        
    def feedback(self):
        errors = self.memory.get_fact('errors')
        challenges = self.memory.get_fact('challenges')
        numbers_student = self.memory.get_fact('numbers_student')
        
        response = {}
        
        response['reaction_time'] = self.memory.get_fact('timer_response').total_time_seconds()
        response['reaction_time_without_pauses'] = self.memory.get_fact('timer_response').total_time_without_paused_seconds()
        response['paused_counter'] = self.memory.get_fact('timer_response').total_times_paused() - self.memory.get_fact('tips_times')
        response['tips_counter'] = self.memory.get_fact('tips_times')
        response['max_time'] = self.memory.get_fact('average_time')

        response['start_time'] = self.memory.get_fact('timer_response').get_time_started()
        response['end_time'] = self.memory.get_fact('timer_response').get_time_finished()
        response['affective_state'] = ''
        response['affective_quad'] = ''
        
        response['type_error'] = ''
        response['subtype_error'] = ''
        
        if len(errors) == 0:
            response['is_correct'] = True
            self.memory.add_fact('is_correct', True)
            
            self.frame_confetti = 1
            self.confetti.visible = True
            
            self.memory.get_fact('student_blocks').update(numbers_student)
            
            count = 0
            numbers = self.__student_numbers__()
            for n in numbers:
                n.sort()
                key = "".join(map(str, n))
                if challenges.get(key) is not None:
                    challenges[key]['found'] = True
                    count += 1
            
            emotions = ['happy0', 'happy1', 'happy2', 'happy3', 'happy4', 'heart0']
            
            if len(numbers) < len(challenges):
                text_err = ['Legal', 'Interessante', 'Muito bom', 'Bacana', 'Parabéns']
                
                message = f'{text_err[random.randrange(0,len(text_err))]} {self.game.student.nickname}. '
                message += f'Você consegui encontrar {count} '
                message += 'soma ' if count == 1 else 'somas '
                message += '15 do quadrado mágico. Agora, tente encontrar todas. '
                message += '\n\nPressione o botão VERMELHO para continuar'
                self.teacher.set_message(
                    message,
                    emotions[random.randrange(0,len(emotions))]
                )
            else:
                self.teacher.set_message(
                    'Parabéns!!!\n\n'+
                    'Você encontrou todas as somas 15 deste desafio.'
                    '\n\nPressione o botão VERMELHO para continuar', 
                    emotions[random.randrange(0,len(emotions))]
                )
                
                step = self.memory.get_fact('step')
                self.memory.add_fact('step', step + 1)
                
                if step < self.memory.get_fact('max_steps'):
                    self.teacher.set_message(
                        f'Vamos ver se você consegue resolver o próximo desafio {self.game.student.nickname}\n\n'
                        'Remova os blocos do tabulerio e organize-os '+
                        'conforme será apresentado. \n\n'+
                        'Não se esqueça de pressionar o botão VERDE para '+
                        'validar o posicionamento inicial.'
                        '\n\nPressione o botão VERMELHO para continuar', 
                        emotions[random.randrange(0,len(emotions))]
                    )
                
                self.memory.add_fact('valid_initial', False)
                self.memory.add_fact('reset_blocks', True)
        else:
            response['is_correct'] = False
            self.memory.add_fact('is_correct', False)
            quantity_corrects = 0
            
            errors = sorted(errors, key=lambda error: error.weight, reverse=True)
            
            error = errors[random.randrange(0, len(errors))]
            print('erro selecionado', error)
            history_errors = self.memory.get_fact('history_errors')
            history_errors.append(error)
            self.memory.add_fact('history_errors', history_errors)
            
            quantity_errors = self.memory.get_fact('quantity_errors')
            quantity_errors += 1
            self.memory.add_fact('quantity_errors', quantity_errors)
            
            response['type_error'] = error.type
            response['subtype_error'] = error.subtype
            
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
                self.message_teacher_indirectly_identifiable()
            elif error.type == TypeError.TYPE_UNCATEGORIZED_SOLUTION:
                self.message_teacher_uncategorized_solution()
            
            self.memory.reset()
            
        self.memory.get_fact('responses').append(response)
        self.memory.add_fact('reset_timer', True)
        
        #self.save_challenge(response)
        #self.memory.add_fact('quantity_corrects', quantity_corrects)
        
        #self.rules.execute_rules()
        #self.adjust_game_levels()
        
        self.teacher.next_message()
        self.show_teacher = True
        
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
                if col >= 2 and col <= 4 and lin >= 2 and lin <= 4:
                    color = (180,180,180,255)
                rect = (x,y,self.box_width,self.box_height)
                shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                pygame.draw.rect(shape, color, shape.get_rect())
                display.blit(shape, rect)

                y += self.box_height + self.offset
            x += self.box_width + self.offset
    
    def draw_challenge(self):
        numbers_student = self.memory.get_fact('numbers_student')
        
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        font = pygame.font.SysFont(FONT_NAME, 30, False, False)

        total_shape_x = self.box_width * self.board.columns + self.offset * (self.board.columns + 1)
        total_shape_y = self.box_height * self.board.lines + self.offset * (self.board.lines + 1)

        pos_x = self.offset * 2
        pos_y = screen_height/2 - total_shape_y / 2

        for key in numbers_student.keys():
            pos = numbers_student[key]
            x = pos_x + self.offset * pos[1] + self.box_width * (pos[1] - 1)
            y = pos_y + self.offset * pos[0] + self.box_height * (pos[0] - 1)
            rect = (x,y,self.box_width,self.box_height)
            shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
            pygame.draw.rect(shape, (220, 3, 3), shape.get_rect())
            display.blit(shape, rect)
            text = font.render(str(key), True, (255,255,255))
            text_rect = text.get_rect(center=(x+self.box_width/2, y+self.box_height/2))
            display.blit(text, text_rect)        
    
    def add_points_score(self):
        score = self.memory.get_fact('score')
        score += self.memory.get_fact('correct_points')
        self.memory.add_fact('score', score)
        
    def remove_points_score(self):
        score = self.memory.get_fact('score')
        score -= self.memory.get_fact('incorrect_points')
        if score < 0:
            score = 0
        self.memory.add_fact('score', score)
        
    def add_bonus_points(self):
        score = self.memory.get_fact('score')
        score += self.memory.get_fact('bonus_points')
        self.memory.add_fact('score', score)
    
    def add_lives(self):
        max_lives = self.memory.get_fact('max_lives')
        lives = self.memory.get_fact('lives')
        if lives < max_lives:
            lives += 1
        self.memory.add_fact('lives', lives)
    
    def remove_lives(self):
        lives = self.memory.get_fact('lives')
        lives -= 1
        self.memory.add_fact('lives', lives)
    
    @db_session
    def save_challenge(self, response) -> None:
        user = DBUser[self.game.student.id]
        session = DBSession[int(self.memory.get_fact('session_id'))]
        challenge = DBChallengeP3(
            number = response['number'],
            other_numbers = response['other_numbers'],
            is_correct = response['is_correct'],
            start_time = response['start_time'],
            end_time = response['end_time'],
            reaction_time = response['reaction_time'],
            reaction_time_without_pauses = response['reaction_time_without_pauses'],
            pauses_counter = response['paused_counter'],
            tips_counter = response['tips_counter'],
            affective_state = response['affective_state'],
            affective_quad = response['affective_quad'],
            type_error = response['type_error'],
            subtype_error = response['subtype_error'],
            user = user,
            session = session
        )
        challenge.flush()
        facialThread = FacialThread(self.game.app, challenge.id, self.update_challenge)
        facialThread.start()
    
    @db_session
    def update_challenge(self, id, expression, quad):
        logging.info(f'Atualizando challenge')
        challenge = DBChallengeP3[id]
        challenge.set(affective_state = expression, affective_quad = quad)
        challenge.flush()
        logging.info(f'Atualizado')
    
    def adjust_game_levels(self):
        student: Student = self.memory.get_fact('student')
        average_time = self.memory.get_fact('average_time')
        amount_time = self.memory.get_fact('amount_time')
        is_correct = self.memory.get_fact('is_correct')
        response = self.memory.get_fact('responses')[-1]
        
        if is_correct:
            self.add_points_score()
        else:
            self.remove_lives()
        
        bonus = False
        if is_correct and response['reaction_time'] < (amount_time / 2):
            bonus = True
        
        if student.inhibitory_capacity_online == Student.INHIBITORY_CAPACITY_LOW:
            self.memory.add_fact('amount_time', average_time)
            self.memory.add_fact('enable_timer', False)
            if bonus:
                self.add_lives()
                self.add_bonus_points()
                
        elif student.inhibitory_capacity_online == Student.INHIBITORY_CAPACITY_MEDIUM:
            self.memory.add_fact('amount_time', average_time)
            self.memory.add_fact('enable_timer', True)
            if bonus:
                self.add_bonus_points()
                
        else:
            self.memory.add_fact('amount_time', math.ceil(average_time * 0.5))
            self.memory.add_fact('enable_timer', True)
            if bonus:
                self.add_bonus_points()
            
            if not is_correct:
                self.remove_points_score()
            
        self.memory.add_fact('reset_timer', True)
        
    def __initial_sums__(self) -> list[str]:
        challenges = self.memory.get_fact('challenges')
        numbers = self.__initial_numbers__()
        
        keys = []
        for n in numbers:
            key = "".join(map(str, n))
            if challenges.get(key) is not None:
                keys.append(key)
        return keys
    
    def __initial_numbers__(self) -> list[int]:
        initial_blocks = self.memory.get_fact('initial_blocks')
        elements = []
        keys = []

        for l in range(2, len(initial_blocks) - 2):
            t = []
            for c in range(2, len(initial_blocks[l]) - 2):
                if initial_blocks[c][l] != 0:
                    t.append(initial_blocks[c][l])
            if len(t) > 0 and elements.count(t) == 0:
                elements.append(t)
            
        for c in range(2, len(initial_blocks) - 2):
            t = []
            for l in range(2, len(initial_blocks[l]) - 2):
                if initial_blocks[c][l] != 0:
                    t.append(initial_blocks[c][l])
            if len(t) > 0 and elements.count(t) == 0:
                elements.append(t)

        t = []
        for c in range(2, len(initial_blocks) - 2):
            if initial_blocks[c][c] != 0:
                t.append(initial_blocks[c][c])
        if len(t) > 0 and elements.count(t) == 0:
            elements.append(t)

        t = []
        for c in range(2, len(initial_blocks) - 2):
            if initial_blocks[c][len(initial_blocks) - 1 - c] != 0:
                t.append(initial_blocks[c][len(initial_blocks) - 1 - c])
        if len(t) > 0 and elements.count(t) == 0:
            elements.append(t)
            
        for n in elements:
            n.sort()
            keys.append(n)
                
        return keys
        
    def __position_is_corner__(self, position : tuple) -> bool:
        return (position[0] == 3 or position[0] == 5) and (position[1] == 3 or position[1] == 5)
        
    def __count_odd_numbers__(self, numbers: list[int]) -> int:
        count = 0
        for n in numbers:
            if n % 2 == 1:
                count += 1
        return count
    
    def __count_even_numbers__(self, numbers: list[int]) -> int:
        count = 0
        for n in numbers:
            if n % 2 == 0:
                count += 1
        return count
    
    def __student_sums__(self) -> list[str]:
        challenges = self.memory.get_fact('challenges')
        numbers = self.__student_numbers__()
        
        keys = []
        for n in numbers:
            n.sort()
            key = "".join(map(str, n))
            if challenges.get(key) is not None:
                keys.append(key)
        return keys
    
    def __student_numbers__(self) -> list[int]:
        numbers_student = self.memory.get_fact('numbers_student')
        elements = []
        keys = []
        
        matrix = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        
        for key in numbers_student.keys():
            l,c = numbers_student[key]
            matrix[l-2][c-2] = key
            
        for l in range(1, len(matrix)-1):
            t = []
            for c in range(1, len(matrix[l]) - 1):
                if matrix[l][c] != 0:
                    t.append(matrix[l][c])
            if len(t) == 3:
                elements.append(t)
                
        for c in range(1, len(matrix) -1):
            t = []
            for l in range(1, len(matrix[c]) -1):
                if matrix[l][c] != 0:
                    t.append(matrix[l][c])
            if len(t) == 3:
                elements.append(t)
        
        t = []
        for l in range(1, len(matrix) - 1):
            if matrix[l][l] != 0:
                t.append(matrix[l][l])
        if len(t) == 3:
                elements.append(t)
                
        t = []
        for l in range(len(matrix)-2, 0, -1):
            if matrix[l][len(matrix) - 1 - l] != 0:
                t.append(matrix[l][len(matrix) - 1 - l])
        if len(t) == 3:
                elements.append(t)
        
        for n in elements:
            #n.sort()
            keys.append(n)
        
        return keys
        
    def render(self, display):        
        display.fill((255,255,255))
        
        self.draw_board()
        self.draw_challenge()
        self.draw_physical_buttons()
        
        if self.show_error_domain_deficiency:
            self.draw_error_domain_deficiency()
        
        if self.show_error_misinterpretation_language:
            self.draw_error_misinterpretation_language()
        
        if self.show_error_operator_use:
            self.draw_error_operator_use()
        
        if self.show_error_rule_deficiency:
            self.draw_error_rule_deficiency()
        
        if self.show_error_indirectly_identifiable:
            self.draw_error_indirectly_identifiable()
            
        if self.show_error_uncategorized_solution:
            self.draw_error_uncategorized_solution()
            
        if self.show_possible_sums:
            self.draw_possible_sums_student()
            self.draw_possible_sums_tutor()
        
        if self.show_teacher:
            self.teacher.draw()
            
        if self.confetti.visible:
            self.draw_confetti()