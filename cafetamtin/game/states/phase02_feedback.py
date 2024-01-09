# Copyright (C) 2023 Robertino Mendes Santiago Junior
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

from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN, YELLOW

from base.board import Board
from game.states.state import State
from game.actors.teacher import Teacher
from game.actors.student import Student
from production.type_error import TypeError
from production.phase01_levels import Phase01Levels
from database.models import DBChallengeP1, DBSession, DBSteps, DBUser

class Phase02Feedback(State):
    def __init__(self, game, working_memory):
        super().__init__(game)
        self.memory = working_memory
        self.rules = Phase01Levels(self.memory)
        self.board = Board(self.game.app)
        self.teacher = Teacher(self.game.game_canvas)
                        
        self.box_width, self.box_height = 60, 60
        
        self.show_error_misinterpretation_language = False
        self.show_error_domain_deficiency = False
        self.show_error_rule_deficiency = False
        self.show_error_operator_use = False
        self.show_error_indirectly_identifiable = False
        self.show_error_uncategorized_solution = False
        
        self.combinations = {
            1: 2,
            2: 3,
            3: 2,
            4: 3,
            5: 4,
            6: 3,
            7: 2,
            8: 3,
            9: 2
        }
        
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
        self.memory.get_fact('timer_response').start()
        self.memory.add_fact('tips_times', 0)
        step = self.memory.get_fact('step')
        step += 1
        step = self.memory.add_fact('step', step)
        self.memory.add_fact('reset_timer', True)
    
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
        
    def draw_error_misinterpretation_language(self):
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        self.blit_text('Número de vezes que cada número aparece nas combinações de soma', (screen_width/2, 90), WHITE, 18)
        
        offset = 5
        x = 190
        y = 110
        for i in self.combinations:
            self.blit_box(str(i), (x,y), (220, 3, 3), 40)
            self.draw_arrow_left(f'{self.combinations[i]} vezes', (x + self.box_width+offset, y+20), 0, YELLOW, 18)
            
            if (i) % 3 == 0:
                x += self.box_height + offset + 150
                y = 110 
            else:
                y += self.box_width + offset
    
    def draw_error_domain_deficiency(self):
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        
        result = self.memory.get_fact('result')
        part1 = f'{result[0]}+{result[1]}+{result[2]}'
        
        self.__draw_informed_numbers()
        
        self.blit_text(f'Resolução: {part1}', (450, 90), WHITE, 18)
        self.blit_text(str(part1[0]), (450, 130), WHITE, 40)
        self.blit_text(str(part1[1]), (427, 150), YELLOW, 40)
        self.blit_text(str(part1[2]), (450, 180), WHITE, 40)
        self.blit_text('____', (450, 187), WHITE, 40)
        
        exp = [str(part1[0]),str(part1[1]),str(part1[2])]
        exp = ''.join(exp)
        result_part1 = str(eval(exp))
        self.blit_text(result_part1, (450, 230), WHITE, 40)
        
        self.draw_arrow_right('Adição', (405, 160), 45, YELLOW, 18)
                
        
        exp = [result_part1, str(part1[3]), str(part1[4])]
        exp = ''.join(exp)
        
        self.blit_text(str(result_part1), (650, 130), WHITE, 40)
        self.blit_text(str(part1[3]), (630, 150), YELLOW, 40)
        self.blit_text(str(part1[4]), (650, 180), WHITE, 40)
        self.blit_text('____', (650, 187), WHITE, 40)
        self.blit_text(str(eval(exp)), (650, 230), WHITE, 40)
        
        self.draw_arrow_right('Adição', (610, 160), 45, YELLOW, 18)
        
        diff = abs(15 - sum(result))
        message = f'Diferença entre a soma dos números informados e o número 15: {diff}'
        self.blit_text(message, (screen_width/2, 270), YELLOW, 18)
    
    def draw_error_rule_deficiency(self):
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        
        result = self.memory.get_fact('result')
        
        self.__draw_informed_numbers()
        
        self.blit_box(str(result[0]), (550,100), (220, 3, 3), 40)
        self.draw_arrow_left('Número par  ' if result[0] % 2 == 0 else 'Número ímpar', (630, 120), 0, YELLOW, 18)
        
        self.blit_box(str(result[1]), (550,180), (220, 3, 3), 40)
        self.draw_arrow_left('Número par  ' if result[1] % 2 == 0 else 'Número ímpar', (630, 200), 0, YELLOW, 18)
        
        self.blit_box(str(result[2]), (550,260), (220, 3, 3), 40)
        self.draw_arrow_left('Número par  ' if result[2] % 2 == 0 else 'Número ímpar', (630, 280), 0, YELLOW, 18)
        
    
    def draw_error_operator_use(self):
        pass
    
    def draw_error_indirectly_identifiable(self):
        result = self.memory.get_fact('result')
        
        if len(result) != 0:
            self.__draw_informed_numbers()
            
        self.blit_box('?', (450,110), (220, 3, 3), 40)
        self.blit_text('+', (530, 140), YELLOW, 40)
        self.blit_box('?', (550,110), (220, 3, 3), 40)
        self.blit_text('+', (630, 140), YELLOW, 40)
        self.blit_box('?', (650,110), (220, 3, 3), 40)
        self.blit_text('= 15', (760, 140), YELLOW, 40)
            
    
    def draw_error_uncategorized_solution(self):
        display = self.game.game_canvas
        
        self.blit_text('Exemplo de soma: 5 + 3 + 2', (240, 80), WHITE, 18)
        
        x = 200
        y = 120
        self.draw_circle((x,y), 10, YELLOW)
        self.draw_circle((x+40,y), 10, YELLOW)
        self.draw_circle((x+80,y), 10, YELLOW)
        self.draw_circle((x+20,y+40), 10, YELLOW)
        self.draw_circle((x+60,y+40), 10, YELLOW)
        
        self.blit_text('+', (x+150,y+20), YELLOW, 40)
        
        self.draw_circle((x+220,y), 10, BLACK)
        self.draw_circle((x+260,y), 10, BLACK)
        self.draw_circle((x+240,y+40), 10, BLACK)
        
        self.blit_text('=', (x+330,y+20), YELLOW, 40)
        
        self.draw_circle((x+410,y), 10, WHITE)
        self.draw_circle((x+450,y), 10, WHITE)
        self.draw_circle((x+490,y), 10, WHITE)
        self.draw_circle((x+530,y), 10, WHITE)
        self.draw_circle((x+410,y+40), 10, WHITE)
        self.draw_circle((x+450,y+40), 10, WHITE)
        self.draw_circle((x+490,y+40), 10, WHITE)
        self.draw_circle((x+530,y+40), 10, WHITE)
        
        x = 180
        y = 250
        
        self.draw_circle((x,y), 10, WHITE)
        self.draw_circle((x+40,y), 10, WHITE)
        self.draw_circle((x+80,y), 10, WHITE)
        self.draw_circle((x+120,y), 10, WHITE)
        self.draw_circle((x,y+40), 10, WHITE)
        self.draw_circle((x+40,y+40), 10, WHITE)
        self.draw_circle((x+80,y+40), 10, WHITE)
        self.draw_circle((x+120,y+40), 10, WHITE)
        
        
        self.blit_text('+', (x+170,y+20), YELLOW, 40)
        
        self.draw_circle((x+240,y+20), 10, GREEN)
        self.draw_circle((x+280,y+20), 10, GREEN)
        
        self.blit_text('=', (x+350,y+20), YELLOW, 40)
        
        self.draw_circle((x+420,y), 10, RED)
        self.draw_circle((x+460,y), 10, RED)
        self.draw_circle((x+500,y), 10, RED)
        self.draw_circle((x+540,y), 10, RED)
        self.draw_circle((x+580,y), 10, RED)
        self.draw_circle((x+420,y+40), 10, RED)
        self.draw_circle((x+460,y+40), 10, RED)
        self.draw_circle((x+500,y+40), 10, RED)
        self.draw_circle((x+540,y+40), 10, RED)
        self.draw_circle((x+580,y+40), 10, RED)
        
    
    def __draw_informed_numbers(self):        
        result = self.memory.get_fact('result')
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
        
    
    def message_teacher_misinterpretation_language(self):
        logging.info(f'Executando função: message_teacher_misinterpretation_language')
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        
        self.teacher.set_message(
            'As somas de 15 com três números permitem que cada '+
            'número apareça em diversas combinações.'+
            '\n\nPressione o botão VERMELHO para continuar',
            'neutral1', modal=False, position=(screen_width/2,370)
        )
        
        self.teacher.set_message(
            'Aqui, estão exibidas as unidades de 1 a 9. '+
            'Cada um destes números pode ser utilizado em uma '+
            'combinação de três números cuja soma resulta em 15.'+
            '\n\nPressione o botão VERMELHO para continuar',
            'neutral1', modal=False, position=(screen_width/2,370)
        )
        
        index = random.randint(1, 9)
        
        self.teacher.set_message(
            f'Por exemplo, o número {index} está presente em {self.combinations[index]} '+
            'combinações de 3 números cuja soma resulta em 15.'+
            '\n\nPressione o botão VERMELHO para continuar',
            'neutral1', modal=False, position=(screen_width/2,370)
        )
        
        self.show_error_misinterpretation_language = True
    
    def message_teacher_domain_deficiency(self):
        logging.info(f'Executando função: message_teacher_domain_deficiency')
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT        

        result = self.memory.get_fact('result')
        expression = f'{result[0]} + {result[1]} + {result[2]}'
        _sum = sum(result)
        
        self.teacher.set_message(
            f'Ah.. Essa combinação de números não resulta 15. '+
            f'Ao utilizarmos a expressão {expression} o resultado obtido '+
            f'é {_sum}. Como você pode perceber, há uma diferença de {abs(15 - _sum)} ' +
            f'unidades em relação ao 15.'+
            '\n\nPressione o botão VERMELHO para continuar',
            'neutral1', modal=False, position=(screen_width/2,370)
        )
        
        self.show_error_domain_deficiency = True
    
    def message_teacher_rule_deficiency(self):
        logging.info(f'Executando função: message_teacher_rule_deficiency')
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        result = self.memory.get_fact('result')
        
        if self.__count_even_numbers__(result) == 3:
            self.teacher.set_message(
                f'Você informou três números pares: {result[0]},{result[1]} e {result[2]}.'+
                'Uma das propriedades dos números pares é que, ao somarmos '+
                'números pares, sempre obtemos um número par como resultado. '+
                'No entanto, observe que o número 15 é ímpar.'+
                '\n\nPressione o botão VERMELHO para continuar',
                'neutral1', modal=False, position=(screen_width/2,370)
            )
        
        if self.__count_odd_numbers__(result) == 2 and self.__count_even_numbers__(result) == 1:
            even_numbers , odd_numbers = self.__sort_even_odd_numbers__(result)
            self.teacher.set_message(
                f'Você informou dois números ímpares ({odd_numbers[0]} e {odd_numbers[1]}) '+
                f'e um número par ({even_numbers[0]}). '+
                'Uma das propriedades dos números ímpares é que, '+
                'ao somarmos dois números ímpares, sempre obtemos '+
                'um número par como resultado.'+
                '\n\nPressione o botão VERMELHO para continuar',
                'neutral1', modal=False, position=(screen_width/2,370)
            )
            self.teacher.set_message(
                'Assim, se somarmos dois números ímpares e um número par, '+
                'o resultado será sempre par. No entanto, '+
                'observe que o número 15 é ímpar.'+
                '\n\nPressione o botão VERMELHO para continuar',
                'neutral2', modal=False, position=(screen_width/2,370)
            )
        self.teacher.set_message(
            'Perceba que, neste caso, para obter um resultado ímpar, '+
            'é necessário somar três números ímpares ou '+
            'somar dois números pares e um número ímpar.'+
            '\n\nPressione o botão VERMELHO para continuar',
            'neutral2', modal=False, position=(screen_width/2,370)
        )
        
        self.show_error_rule_deficiency = True
    
    
    def message_teacher_operator_use(self):
        logging.info(f'Executando função: message_teacher_operator_use')
    
    def message_teacher_indirectly_identifiable(self):
        logging.info(f'Executando função: message_teacher_indirectly_identifiable')
        result = self.memory.get_fact('result')
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT        

        if len(result) == 0:
            self.teacher.set_message(
                'Atenção! Você não colocou nenhum bloco sobre o tabuleiro. '+
                'Nesta fase, é necessário colocar três blocos numerados '+
                'a cada jogada sobre o tabuleiro. A soma dessa combinação '+
                'de blocos deve resultar no número 15.'+
                '\n\nPressione o botão VERMELHO para continuar',
                'neutral0', modal=False, position=(screen_width/2,370)
            )
        else:
            _sum = sum(result)
            if _sum == 15:
                self.teacher.set_message(
                    f'Atenção! Apesar de a soma desses {len(result)} números resultar em 15, '+
                    'nesta fase é necessário que o resultado da soma 15 seja '+
                    'produzido pela combinação de 3 blocos. '+
                    '\n\nPressione o botão VERMELHO para continuar',
                    'happy4', modal=False, position=(screen_width/2,370)
                )
            else:
                self.teacher.set_message(
                    'Atenção! Nesta fase, é necessário colocar apenas três '+
                    'blocos numerados sobre o tabuleiro a cada jogada. '+
                    'A soma dessa combinação de blocos deve resultar no número 15.'+
                    '\n\nPressione o botão VERMELHO para continuar',
                    'neutral2', modal=False, position=(screen_width/2,370)
                )
        
        self.show_error_indirectly_identifiable = True
        
    
    def message_teacher_uncategorized_solution(self):
        logging.info(f'Executando função: message_teacher_uncategorized_solution')
        result = self.memory.get_fact('result')
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        
        self.teacher.set_message(
            'Para resolver uma operação de adição com três números, '+
            'vamos considerar o exemplo acima. Precisamos somar '+
            '5 bolas amarelas, 3 bolas pretas e 2 bolas verdes, '+
            'formando a expressão\n 5 + 3 + 2.'+
            '\n\nPressione o botão VERMELHO para continuar',
            'neutral1', modal=False, position=(screen_width/2,370)
        )
        
        self.teacher.set_message(
            'Para encontrar o total de bolas existentes, podemos '+
            'fazer as adições por pares de cores. Assim, primeiro '+
            'somamos as bolas amarelas e pretas (5 + 3 = 8).'+
            '\n\nPressione o botão VERMELHO para continuar',
            'neutral0', modal=False, position=(screen_width/2,370)
        )
        
        self.teacher.set_message(
            'Agora, somamos o resultado anterior com as bolas verdes '+
            '(8 + 2 = 10). Portanto, ao somar as bolas amarelas, '+
            'pretas e verdes (5 + 3 + 2), temos um total de 10 bolas.'+
            '\n\nPressione o botão VERMELHO para continuar',
            'neutral2', modal=False, position=(screen_width/2,370)
        )
        
        self.show_error_uncategorized_solution = True
    
    
    def feedback(self):
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        errors = self.memory.get_fact('errors')
        result = self.memory.get_fact('result')
        correct = self.memory.get_fact('correct')
        valid = self.memory.get_fact('valid')
        quantity_corrects = self.memory.get_fact('quantity_corrects')
        num_terms = self.memory.get_fact('num_terms')
        
        response = {}
        
        response['reaction_time'] = self.memory.get_fact('timer_response').total_time_seconds()
        response['reaction_time_without_pauses'] = self.memory.get_fact('timer_response').total_time_without_paused_seconds()
        response['paused_counter'] = self.memory.get_fact('timer_response').total_times_paused() - self.memory.get_fact('tips_times')
        response['tips_counter'] = self.memory.get_fact('tips_times')

        response['start_time'] = self.memory.get_fact('timer_response').get_time_started()
        response['end_time'] = self.memory.get_fact('timer_response').get_time_finished()
        response['affective_state'] = ''
        response['affective_quad'] = ''
        
        response['type_error'] = ''
        response['subtype_error'] = ''
        
        if len(result) == 3:
            response['number01'] = result[0]
            response['number02'] = result[1]
            response['number03'] = result[2]
        else:
            response['number01'] = -1
            response['number02'] = -1
            response['number03'] = -1
            
            if len(result) == 1:
                response['number01'] = result[0]
            if len(result) == 2:
                response['number01'] = result[0]
                response['number02'] = result[1]
        
        self.memory.get_fact('time_per_step').append(response['reaction_time'])
        
        if (len(errors) == 0 and correct):
            numbers = result
            numbers.sort()
            key = "".join(map(str, numbers))
            challenges = self.memory.get_fact('challenges')
            if challenges.get(key) is not None:
                if challenges[key]['visible']:
                    response['is_correct'] = False
                                        
                    self.teacher.set_message(
                        'Atenção. Apesar da soma entre os números '+
                        f'{numbers[0]}+{numbers[1]}+{numbers[2]} resultar 15, '+
                        'você já havia informado esses números anteriormente. '+
                        '\n\n'+
                        'Tente encontrar as outras combinações possíveis.'+
                        '\n\nPressione o botão VERMELHO para continuar', 
                        'happy0'
                    )
                    lives = self.memory.get_fact('lives')
                    lives -= 1
                    self.memory.add_fact('lives', lives)
                else:
                    response['is_correct'] = True
                    self.memory.add_fact('is_correct', True)
                    
                    emotions = ['happy0', 'happy1', 'happy2', 'happy3', 'happy4', 'heart0']
                    self.teacher.set_message(
                        "Parabéns!!!\n\n"+
                        "Sua resposta está correta. Quando somados, "+
                        f"os valores {numbers[0]}, {numbers[1]} e {numbers[2]} "+
                        "produzem o resultado 15."+
                        '\n\nPressione o botão VERMELHO para continuar', 
                        emotions[random.randrange(0,len(emotions))]
                    )
                    challenges[key]['visible'] = True
                    self.memory.add_fact('challenges', challenges)
                    self.frame_confetti = 1
                    self.confetti.visible = True
                    quantity_corrects += 1
                    self.memory.add_fact('quantity_errors', 0)
                    
        
        else:
            response['is_correct'] = False
            self.memory.add_fact('is_correct', False)
            quantity_corrects = 0
            print(errors)
            errors = sorted(errors, key=lambda error: error.weight, reverse=True)
            print(errors)
            error = errors[0]
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
        #self.save_challenge(response)
        self.memory.add_fact('quantity_corrects', quantity_corrects)
        
        #self.rules.execute_rules()
        #self.adjust_game_levels()
        self.teacher.next_message()
        self.show_teacher = True
    
    def __count_odd_numbers__(self, numbers) -> int:
        count = 0
        for n in numbers:
            if n % 2 == 1:
                count += 1
        return count
    
    def __count_even_numbers__(self, numbers) -> int:
        count = 0
        for n in numbers:
            if n % 2 == 0:
                count += 1
                
        return count
    
    def __sort_even_odd_numbers__(self, numbers) -> int:
        even = []
        odd = []
        
        for n in numbers:
            if n % 2 == 0:
                even.append(n)
            else:
                odd.append(n)
        
        return even, odd
    
    def adjust_game_levels(self):
        pass
    
    def render(self, display):        
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
        
        if self.show_error_indirectly_identifiable:
            self.draw_error_indirectly_identifiable()
            
        if self.show_error_uncategorized_solution:
            self.draw_error_uncategorized_solution()
        
        if self.show_teacher:
            self.teacher.draw()
            
        if self.confetti.visible:
            self.draw_confetti()