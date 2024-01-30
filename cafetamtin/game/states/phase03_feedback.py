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
from database.models import DBSession, DBSteps, DBUser ,DBChallengeP3

class Phase03Feedback(State):
    def __init__(self, game, working_memory):
        super().__init__(game, working_memory)
    
        self.rules = LevelRules(self.memory)
        self.board = Board(self.game.app)
        self.teacher = Teacher(self.game.game_canvas)
        self.text_good_play = ['Boa jogada', 'Ótima jogada', 'Estratégia acertada', 'Tacada certeira']
                                
        #self.box_width, self.box_height = 60, 60
        self.offset = 10
        self.box_width, self.box_height = 40, 40

        
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
        blocks_tutor = self.memory.get_fact('blocks_tutor')
        blocks_available = self.memory.get_fact('blocks_available')
        numbers_student = self.memory.get_fact('numbers_student')
        
        number_informed = self.number_informed()
        
        emotions = ['neutral0', 'neutral1', 'neutral2']
        text_err = ['Ops', 'Opa', 'Ah', 'Puxa']

        numbers_student.pop(number_informed)
        
        message = f'{text_err[random.randrange(0,len(text_err))]} {self.game.student.nickname}. '
        message += f'Você colocou sobre a plataforma o número {number_informed}. '
        message += 'Eu já selecionei este número'
        temp_numbers_tutor = [x for x in blocks_tutor if x != number_informed]
        if len(temp_numbers_tutor) == 0:
            message += '. '
        else:
            message += ', assim como '
            message += 'o número ' if len(temp_numbers_tutor) == 1 else 'os números '
            text_count_tutor = ', '.join([f'{str(x)}' for x in temp_numbers_tutor[:-1]])
            if len(temp_numbers_tutor) > 1:
                text_count_tutor += ' e '
            text_count_tutor += f'{temp_numbers_tutor[-1]}. '
            message += text_count_tutor
        message += f'Por gentileza, retire o número {number_informed} do tabuleiro. '
        message += '\n\nPressione o botão VERMELHO para continuar'
        
        self.teacher.set_message(
            message,
            emotions[random.randrange(0,len(emotions))]
        )
        
        message = 'Você ainda pode escolher '
        message += 'o número ' if len(blocks_available) == 1 else 'os números '
        text_count_available = ', '.join([f'{str(x)}' for x in blocks_available[:-1]])
        if len(blocks_available) > 1:
            text_count_available += ' e '
        text_count_available += f'{blocks_available[-1]}. '
        message += text_count_available
        message += '\n\nPressione o botão VERMELHO para continuar'
        
        self.teacher.set_message(
            message,
            emotions[random.randrange(0,len(emotions))]
        )
        
        
    def message_teacher_domain_deficiency(self):
        logging.info(f'Executando função: message_teacher_domain_deficiency')
        numbers_student = self.memory.get_fact('numbers_student')
        
        number_informed = self.number_informed()
        
        text_err = ['Legal', 'Interessante', 'Muito bom', 'Bacana']
        
        emotions = ['neutral0', 'neutral1', 'neutral2']
        checks = Phase03Checks()
        
        message = f'{text_err[random.randrange(0,len(text_err))]} {self.game.student.nickname}. '
        message += f'Você colocou sobre a plataforma o número {number_informed}. '
        
        if checks.do_not_make_sum_fifteen(self.memory):
            message += 'Nesta jogada, você deixou de realizar uma soma 15. '
            message += 'Observe os números que você já possui e os números que estão disponíveis.'
        else:
            message += 'Uma das estratégias deste jogo é evitar que seu oponente '
            message += 'consiga fazer uma soma 15. Pense nisso na próxima rodada.'
        
        message += '\n\nPressione o botão VERMELHO para continuar'
        
        self.teacher.set_message(
            message, 
            emotions[random.randrange(0,len(emotions))]
        )
        
        self.update_blocks_student(numbers_student)
        
        number_tutor = self.next_tutor_number()
        
        message = ''
        if number_tutor:
            message += f'Nesta rodada, eu vou escolher o número {number_tutor}.'
        else:
            message += f'Este foi o último número disponível.'
        message += '\n\nPressione o botão VERMELHO para continuar'
        
        emotions = ['happy0', 'happy1', 'happy2', 'happy3', 'happy4', 'heart0']
        self.teacher.set_message(
            message, 
            emotions[random.randrange(0,len(emotions))]
        )
        
        self.show_error_domain_deficiency = True
        
    def message_teacher_rule_deficiency(self):
        logging.info(f'Executando função: message_teacher_rule_deficiency')
    
    def message_teacher_operator_use(self):
        logging.info(f'Executando função: message_teacher_operator_use')
    
    def message_teacher_indirectly_identifiable(self):
        logging.info(f'Executando função: message_teacher_indirectly_identifiable')
        
        numbers_student = self.memory.get_fact('numbers_student')
        number_informed = self.number_informed()
        self.update_blocks_student(numbers_student)
        emotions = ['neutral0', 'neutral1', 'neutral2']

        message = f'Você colocou sobre a plataforma o número {number_informed}. '
        message += 'Este não é o número que aparece mais vezes nas possíveis somas. '
        message += '\n\nPressione o botão VERMELHO para continuar'
        
        self.teacher.set_message(
            message, 
            emotions[random.randrange(0,len(emotions))]
        )
        
        message = 'Uma estratégia interessante é selecionar o número '
        message += '5 primeiro, pois ele aparece em quatro possíveis somas. '
        
        number_tutor = self.next_tutor_number()
        if number_tutor:
            message += f'Nesta rodada, eu vou escolher o número {number_tutor}.'
        else:
            message += f'Este foi o último número disponível.'
        message += '\n\nPressione o botão VERMELHO para continuar'
        
        self.teacher.set_message(
            message, 
            emotions[random.randrange(0,len(emotions))]
        )
        
        self.show_error_indirectly_identifiable = True
    
    def message_teacher_uncategorized_solution(self):
        logging.info(f'Executando função: message_teacher_uncategorized_solution')
        numbers_student = self.memory.get_fact('numbers_student')
        number_informed = self.number_informed()
        
        message = f'Atenção {self.game.student.nickname}! '
        if len(numbers_student) == 0:
            message += 'Você deve escolher um bloco numerado e '
            message += 'colocá-lo sobre a plataforma, '
        else:
            message += 'Você precisa escolher um número que esteja contido '
            message += 'quadro "Blocos disponíveis", pegar o bloco numerado '
            message += 'correspondente e colocá-lo sobre a plataforma, '
        
        message += 'só então você deve apertar o botão VERDE.'
        message += '\n\nPressione o botão VERMELHO para continuar'
        
        emotions = ['neutral0', 'neutral1', 'neutral2']
        self.teacher.set_message(
            message, 
            emotions[random.randrange(0,len(emotions))]
        )
        
        self.show_error_uncategorized_solution = True
    
    def feedback(self):
        errors = self.memory.get_fact('errors')
        correct = self.memory.get_fact('correct')
        quantity_corrects = self.memory.get_fact('quantity_corrects')
        numbers_student = self.memory.get_fact('numbers_student')
        blocks_student = self.memory.get_fact('blocks_student')
        blocks_tutor = self.memory.get_fact('blocks_tutor')
        blocks_available = self.memory.get_fact('blocks_available')
        
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
        
        response['other_numbers'] = ','.join([f'{str(x)}' for x in blocks_student.keys()])
        
        if len(errors) == 0:
            response['is_correct'] = True
            self.memory.add_fact('is_correct', True)
            
            number_informed = self.number_informed()
            response['number'] = number_informed
            
            
            self.update_blocks_student(numbers_student)
            
            
            text = f'{self.text_good_play[random.randrange(0,len(self.text_good_play))]} {self.game.student.nickname}! '
            text += f'Você colocou sobre a plataforma o número {number_informed}. '
            
            if self.verify_sums_student():
                text += 'Com esse bloco, você conseguiu realizar uma soma 15. Parabéns.\n\n '
            
            number_tutor = self.next_tutor_number()
            if number_tutor:
                text += f'Eu vou escolher nesta rodada o número {number_tutor}.'
            else:
                text += f'Este foi o último número disponível.'
            text += '\n\nPressione o botão VERMELHO para continuar'
            
            emotions = ['happy0', 'happy1', 'happy2', 'happy3', 'happy4', 'heart0']
            self.teacher.set_message(
                text, 
                emotions[random.randrange(0,len(emotions))]
            )
            
        
        else:
            response['is_correct'] = False
            self.memory.add_fact('is_correct', False)
            quantity_corrects = 0
            errors = sorted(errors, key=lambda error: error.weight, reverse=True)
            
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
                response['number'] = -1
                self.message_teacher_misinterpretation_language()
            elif error.type == TypeError.TYPE_DIRECTLY_IDENTIFIABLE:
                response['number'] = self.number_informed()
                if error.subtype == TypeError.SUBTYPE_DOMAIN_DEFICIENCY:
                    self.message_teacher_domain_deficiency()
                elif error.subtype == TypeError.SUBTYPE_RULE_DEFICIECY:
                    self.message_teacher_rule_deficiency()
                elif error.subtype == TypeError.SUBTYPE_OPERATOR_USAGE:
                    self.message_teacher_operator_use()
            elif error.type == TypeError.TYPE_INDIRECTLY_IDENTIFIABLE:
                response['number'] = self.number_informed()
                self.message_teacher_indirectly_identifiable()
            elif error.type == TypeError.TYPE_UNCATEGORIZED_SOLUTION:
                response['number'] = -2
                self.message_teacher_uncategorized_solution()
                
            self.memory.reset()
            
        self.memory.get_fact('responses').append(response)
        self.save_challenge(response)
        self.memory.add_fact('quantity_corrects', quantity_corrects)
        
        if len(blocks_available) == 0 and not self.memory.get_fact('end_phase'):
            message = f'Muito bom {self.game.student.nickname}! \n\n'
            message += 'Acabaram os blocos disponíveis para esta rodada. '
            
            count_sums_student = self.count_possible_sums_student()
            count_sums_tutor = self.count_possible_sums_tutor()
            
            if count_sums_student != 0:
                message += f'Você conseguiu realizar {count_sums_student} soma(s) 15. '
            else:
                message += 'Você não realizou nenhuma soma 15 nesta rodada. '
            
            if count_sums_tutor != 0:
                message += f'Enquanto isso, eu consegui realizar {count_sums_tutor} soma(s) 15.'
            else:
                message += 'Eu não consegui realizar nenhuma soma 15 .'
                
            if self.memory.get_fact('step') < self.memory.get_fact('max_steps'):
                message += '\nVamos jogar mais uma rodada.'
            
            emotions = ['happy0', 'neutral1', 'neutral2']
            self.teacher.set_message(
                message, 
                emotions[random.randrange(0,len(emotions))],
                modal=False,
                position=(500, 400)
            )
            self.show_possible_sums = True
            
            if self.memory.get_fact('lives') > 0 and self.memory.get_fact('step') <= self.memory.get_fact('max_steps'):
                step = self.memory.get_fact('step')
                step += 1
                self.memory.add_fact('step', step)
                
                self.memory.add_fact('reload', True)
                
        
        self.rules.execute_rules()
        self.adjust_game_levels()
        
        self.teacher.next_message()
        self.show_teacher = True
        
    def count_possible_sums_student(self):
        blocks_student = self.memory.get_fact('blocks_student')
        numbers = list(blocks_student.keys())
        combs = combinations(numbers, 3)
        count = 0
        for c in combs:
            result = sum(c)
            if result == 15:
                count += 1
        return count
        
    
    def count_possible_sums_tutor(self):
        numbers = self.memory.get_fact('blocks_tutor')
        combs = combinations(numbers, 3)
        count = 0
        for c in combs:
            result = sum(c)
            if result == 15:
                count += 1
        return count
    
    def draw_possible_sums_student(self):
        display = self.game.game_canvas
        font = pygame.font.SysFont(FONT_NAME, 16, False, False)
        blocks_student = self.memory.get_fact('blocks_student')

        possibile_sums = []
        if len(blocks_student) == 0:
            return
        
        numbers = list(blocks_student.keys())

        if len(blocks_student) == 1:
            s = {
                'sum': f'{numbers[0]}+?+? = ?', 
                'result': 0, 
                'color': (0,0,0)
            }
            possibile_sums.append(s)

        elif len(blocks_student) == 2:
            s = {
                'sum': f'{numbers[0]}+{numbers[1]}+? = ?', 
                'result': 0, 
                'color': (0,0,0)
            }
            possibile_sums.append(s)

        elif len(blocks_student) == 3:
            result = sum(numbers)
            s = {
                'sum': f'{numbers[0]}+{numbers[1]}+{numbers[2]} = {result}', 
                'result': result, 
                'color': DARKGREEN if result == 15 else RED
            }
            possibile_sums.append(s)
        
        else:
            combs = combinations(numbers, 3)
            for c in combs:
                result = sum(c)
                s = {
                    'sum': f'{c[0]}+{c[1]}+{c[2]} = {result}', 
                    'result': result, 
                    'color': DARKGREEN if result == 15 else RED
                }
                possibile_sums.append(s)

        x = 395
        y = 160
        width = 130
        height = 25
        for i in range(len(possibile_sums)):
            text = font.render(possibile_sums[i]['sum'], True, possibile_sums[i]['color'])
            text_rect = text.get_rect(topleft=(x, y))
            display.blit(text, text_rect)
            if (i+1) % 2 == 0:
                x = 395
                y += height + self.offset
            else:
                x += width + self.offset
    
    def verify_sums_student(self):
        blocks_student = self.memory.get_fact('blocks_student')
        
        numbers = list(blocks_student.keys())
        if len(blocks_student) >= 3:
            combs = combinations(numbers, 3)
            for c in combs:
                l = list(c)
                l.sort()
                result = sum(l)
                if result == 15:
                    key = "".join(map(str, l))
                    if not key in self.memory.get_fact('sums_founds_student'):
                        self.memory.get_fact('sums_founds_student').append(key)
                        self.frame_confetti = 1
                        self.confetti.visible = True
                        return True
        return False


    def draw_possible_sums_tutor(self):
        display = self.game.game_canvas
        font = pygame.font.SysFont(FONT_NAME, 16, False, False)
        blocks_tutor = self.memory.get_fact('blocks_tutor')

        possibile_sums = []
        if len(blocks_tutor) == 0:
            return
        
        numbers = blocks_tutor

        if len(blocks_tutor) == 1:
            s = {
                'sum': f'{numbers[0]}+?+? = ?', 
                'result': 0, 
                'color': (0,0,0)
            }
            possibile_sums.append(s)

        elif len(blocks_tutor) == 2:
            s = {
                'sum': f'{numbers[0]}+{numbers[1]}+? = ?', 
                'result': 0, 
                'color': (0,0,0)
            }
            possibile_sums.append(s)

        elif len(blocks_tutor) == 3:
            result = sum(numbers)
            s = {
                'sum': f'{numbers[0]}+{numbers[1]}+{numbers[2]} = {result}', 
                'result': result, 
                'color': DARKGREEN if result == 15 else RED
            }
            possibile_sums.append(s)
        
        else:
            combs = combinations(numbers, 3)
            for c in combs:
                result = sum(c)
                s = {
                    'sum': f'{c[0]}+{c[1]}+{c[2]} = {result}', 
                    'result': result, 
                    'color': DARKGREEN if result == 15 else RED
                }
                possibile_sums.append(s)

        x = 685
        y = 160
        width = 130
        height = 25
        for i in range(len(possibile_sums)):
            text = font.render(possibile_sums[i]['sum'], True, possibile_sums[i]['color'])
            text_rect = text.get_rect(topleft=(x, y))
            display.blit(text, text_rect)
            if (i+1) % 2 == 0:
                x = 685
                y += height + self.offset
            else:
                x += width + self.offset
    
    def verify_sums_student(self):
        blocks_student = self.memory.get_fact('blocks_student')
        
        numbers = list(blocks_student.keys())
        if len(blocks_student) >= 3:
            combs = combinations(numbers, 3)
            for c in combs:
                l = list(c)
                l.sort()
                result = sum(l)
                if result == 15:
                    key = "".join(map(str, l))
                    if not key in self.memory.get_fact('sums_founds_student'):
                        self.memory.get_fact('sums_founds_student').append(key)
                        self.frame_confetti = 1
                        self.confetti.visible = True
                        return True
        return False
    
    def number_informed(self):
        numbers_student = self.memory.get_fact('numbers_student')
        blocks_student = self.memory.get_fact('blocks_student')

        diff = [x for x in numbers_student if x not in blocks_student]
        
        if len(diff) == 0:
            return False
        
        return diff[0]
    
    def new_tutor_number(self, number_informed):
        ntutor = self.next_tutor_number()
        
        if ntutor:
            self.teacher.set_message(
                "Muito bem! Você adicionou o "+
                f"número {number_informed}. O tutor escolheu "+
                f"o número {ntutor}."+
                '\n\nPressione o botão VERMELHO para continuar', 
                "happy0"
            )
        else:
            self.teacher.set_message(
                "Muito bem! Você adicionou o "+
                f"número {number_informed}. Esse foi o último "+
                "número disponível."+
                '\n\nPressione o botão VERMELHO para continuar', 
                "happy0"
            )
        
        
    def next_tutor_number(self):
        if len(self.memory.get_fact('blocks_available')) > 0:
            index = random.randrange(0, len(self.memory.get_fact('blocks_available')))
            removed = self.memory.get_fact('blocks_available').pop(index)
            self.memory.get_fact('blocks_tutor').append(removed)
            return removed
        return False
        
    def update_blocks_student(self, numbers_student):
        blocks_student = self.memory.get_fact('blocks_student')
        blocks_available = self.memory.get_fact('blocks_available')
        
        blocks_student.update(numbers_student)
        for key in blocks_student.keys():
            if key in blocks_available:
                blocks_available.remove(key)
            
        self.memory.add_fact('blocks_student', blocks_student)
        self.memory.add_fact('blocks_available', blocks_available)
    
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

        pos_x = self.offset
        pos_y = 100

        pos_x_rect = total_shape_x+pos_x+self.offset
        width_rect = (screen_width-pos_x_rect-self.offset)/2-self.offset/2
        height_rect = (screen_height-pos_y-50)/2+self.offset*2

        color = (220,220,220,255)

        #Bloco das possíveis somas do estudante
        rect_shape = (pos_x_rect, pos_y, width_rect, height_rect)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect(), border_radius= 15)
        display.blit(shape, rect_shape)

        font = pygame.font.SysFont(FONT_NAME, 18, False, False)
        text = font.render('Possíveis somas estudante', True, (0,0,0))
        text_rect = text.get_rect(topleft=(pos_x_rect+self.offset, pos_y+self.offset))
        display.blit(text, text_rect)

        #Bloco das possíveis somas do tutor
        rect_shape = (pos_x_rect+width_rect+self.offset, pos_y, width_rect, height_rect)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect(), border_radius= 15)
        display.blit(shape, rect_shape)

        font = pygame.font.SysFont(FONT_NAME, 18, False, False)
        text = font.render('Possíveis somas tutor', True, (0,0,0))
        text_rect = text.get_rect(topleft=(pos_x_rect+width_rect+self.offset+self.offset, pos_y+self.offset))
        display.blit(text, text_rect)

        height_rect = (screen_height-pos_y-50)/2-self.offset*4
        color = (130,115,0,255)
        
        #Bloco das peças disponíveis
        rect_shape = (pos_x_rect, pos_y+height_rect+self.offset*7, width_rect, height_rect+self.offset)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect(), border_radius= 15)
        display.blit(shape, rect_shape)

        blocks_available = self.memory.get_fact('blocks_available')
        text = font.render(f'Blocos disponíveis: {len(blocks_available)}', True, (255,255,255))
        text_rect = text.get_rect(topleft=(pos_x_rect+self.offset, pos_y+height_rect+self.offset+self.offset*8))
        display.blit(text, text_rect)

        #Bloco das peças tutor
        rect_shape = (pos_x_rect+width_rect+self.offset, pos_y+height_rect+self.offset*7, width_rect, height_rect+self.offset)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, color, shape.get_rect(), border_radius= 15)
        display.blit(shape, rect_shape)

        text = font.render('Blocos do tutor', True, (255,255,255))
        text_rect = text.get_rect(topleft=(pos_x_rect+width_rect+self.offset+self.offset, pos_y+height_rect+self.offset+self.offset*8))
        display.blit(text, text_rect)


        font = pygame.font.SysFont(FONT_NAME, 24, False, False)
        text = font.render(self.game.student.name, True, (255,255,255))
        text_rect = text.get_rect(bottomleft=(pos_x, pos_y))
        display.blit(text, text_rect)


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
    
    def render(self, display):        
        display.fill((255,255,255))
        
        self.draw_board()
        
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