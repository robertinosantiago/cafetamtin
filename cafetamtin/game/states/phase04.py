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
from itertools import combinations
from datetime import datetime, timedelta

from base.board import Board
from utils.timer import Timer
from game.states.state import State
from utils.confetti import Confetti
from base.facial import FacialThread
from game.actors.teacher import Teacher
from game.actors.student import Student
from base.leds import Leds, RainbowThread
from database.models import DBSession, DBUser, DBSteps, DBChallengeP4

from production.error import Error
from production.memory import Memory
from production.type_error import TypeError
from production.level_rules import LevelRules
from production.phase04_rules import Phase04Rules
from game.states.phase04_feedback import Phase04Feedback


from game import BACKGROUND_COLOR
from game import TEXT_COLOR
from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN, DARKGREEN


class Phase04(State):

    def __init__(self, game):
        super().__init__(game)
        self.log('Executando Phase03')
        
        self.load_tips()

        self.memory = Memory()
        self.rules = Phase04Rules(self.memory)
        self.rules_level = LevelRules(self.memory)
        self.init_working_memory()
        
        self.board = Board(self.game.app)
        self.teacher = Teacher(self.game.game_canvas)
        self.show_teacher = False
        self.confetti = Confetti()
        self.frame_confetti = 1

        self.lives = 3
        self.score = 0
        self.max_steps = 5
        self.step = 1
        self.incremental_points = 5

        self.images = self.load_images()
        self.challenges = self.load_challenges()

        self.offset = 15
        self.box_width, self.box_height = 50, 50

        self.position_no_modal = (730, 350)

        self.enable_timer = False
        self.is_paused = False
        self.started = False
        self.end_phase = False
        self.new_challenge = True
        self.tutor_starting = False
        self.reload = False

        self.tips_times = 0
        self.leds = Leds()
        self.rainbow = RainbowThread()

        self.initial_blocks = []
        self.student_blocks = {}
        self.challenge_blocks = []
        self.matrix = []
        self.challenges_found = []
        self.generate_blocks()

        self.adjust_game_levels()
        self.first_gaming()
        self.teacher.next_message()

    def load_images(self):
        return {
            'heart': pygame.image.load(os.path.join('images', 'heart.png')),
        }
        
    @db_session
    def init_working_memory(self):
        user  = DBUser[self.game.student.id]

        score = 0
        if len(user.steps) > 0:
            step = select(s for s in user.steps if s.phase == 4).order_by(desc(DBSteps.id)).first()
            score = step.score

        session = DBSession(
            start_time = datetime.now()
        )
        session.flush()
        self.memory.add_fact('student', self.game.student)
        self.memory.add_fact('session_id', session.id)
        self.memory.add_fact('game', self.game)
        
        self.memory.add_fact('initial_blocks', [])
        self.memory.add_fact('student_blocks', {})
        self.memory.add_fact('challenge_blocks', [])
        self.memory.add_fact('matrix', [])
        self.memory.add_fact('challenges_found', [])
        self.memory.add_fact('challenges', self.load_challenges())
        
        self.memory.add_fact('tutor_starting', False)
        self.memory.add_fact('quantity_corrects', 0)
        self.memory.add_fact('quantity_errors', 0)
        self.memory.add_fact('quantity_same_error', 0)
        self.memory.add_fact('limit_errors', 2)
        self.memory.add_fact('history_errors', [])
        self.memory.add_fact('tips_times', 0)
        self.memory.add_fact('step', 1)
        self.memory.add_fact('max_steps', 5)
        self.memory.add_fact('average_time', 120)
        self.memory.add_fact('minimum_time', 10)
        self.memory.add_fact('time_per_step', [])
        self.memory.add_fact('accumulated_time', 0)
        self.memory.add_fact('errors', [])
        self.memory.add_fact('responses', [])
        self.memory.add_fact('reset_timer', True)
        self.memory.add_fact('reload', False)
        self.memory.add_fact('max_lives', 5)
        self.memory.add_fact('lives', 5)
        self.memory.add_fact('score', score)
        self.memory.add_fact('correct_points', 10)
        self.memory.add_fact('incorrect_points', 5)
        self.memory.add_fact('bonus_points', 5)
        self.memory.add_fact('valid_initial', False)
        self.memory.add_fact('reset_blocks', False)
        
        #self.memory.add_fact('enable_timer', True)
        #self.memory.add_fact('amount_time', 60)
        self.memory.add_fact('phase', 4)
        
        self.memory.add_fact('timer_response', Timer())
    
    def load_tips(self):
        error1 = Error(type=TypeError.TYPE_MISINTERPRETATION_LANGUAGE, subtype=TypeError.SUBTYPE_NONE)
        self.tips.add_tip(error=error1, message='Tente relembrar as possíveis somas quinze já encontradas por você. Você pode consultar suas anotações.')
        
        error2 = Error(type=TypeError.TYPE_DIRECTLY_IDENTIFIABLE, subtype=TypeError.SUBTYPE_DOMAIN_DEFICIENCY)
        self.tips.add_tip(error=error2, message='Analise a diferença entre cada eixo (horizontal, vertical e diagonal) e o valor 15 para planejar suas jogadas.')
        self.tips.add_tip(error=error2, message='Observe o quadro "Possíveis somas do estudante" para calcular o valor da diferença entre os números informados e o número 15.')
        
        error3 = Error(type=TypeError.TYPE_DIRECTLY_IDENTIFIABLE, subtype=TypeError.SUBTYPE_RULE_DEFICIECY)
        self.tips.add_tip(error=error3, message='O resultado da soma de três números pares sempre será um número par.')
        self.tips.add_tip(error=error3, message='O resultado da soma de dois números ímpares e um número par será sempre um número par.')
        self.tips.add_tip(error=error3, message='O resultado da soma de três números ímpares sempre será um número ímpar.')
        self.tips.add_tip(error=error3, message='O resultado da soma de dois números par e um número ímpar será sempre um número ímpar.')
        
        error4 = Error(type=TypeError.TYPE_INDIRECTLY_IDENTIFIABLE, subtype=TypeError.SUBTYPE_NONE)
        self.tips.add_tip(error=error4, message='Avalie em quantas somas 15 a posição central do quadrado mágico está envolvida. Para isso, olhe para a horizontal, vertical e diagonais.')
        self.tips.add_tip(error=error4, message='Você percebeu que existe apenas uma possibilidade de número para a posição central do quadrado mágico?')
        self.tips.add_tip(error=error4, message='Observe as extremidades (pontas) do quadrado mágico e verifique em quantas possíveis somas cada uma está envolvida.')
        self.tips.add_tip(error=error4, message='Você percebeu que as extremidades (pontas) do quadrado mágico aparecem em três somas possíveis, cada extremidade, assim como os números pares?')
        self.tips.add_tip(error=error4, message='Observe os números centrais de cada coluna e cada linha e verifique em quantas somas possíveis eles estão envolvidos.')
        self.tips.add_tip(error=error4, message='Você percebeu que os números centrais de cada coluna e cada linha aparecem em duas somas possíveis, cada um, assim como os números ímpares?')
        
        error5 = Error(type=TypeError.TYPE_UNCATEGORIZED_SOLUTION, subtype=TypeError.SUBTYPE_NONE)
        self.tips.add_tip(error=error5, message='Você pode tentar resolver as linhas, colunas ou diagonais parcialmente, informando os números e pressionando o botão VERDE.')
        self.tips.add_tip(error=error5, message='Ao somar os números presentes em uma linha horizontal, o resultado deve ser 15.')
        self.tips.add_tip(error=error5, message='Ao somar os números de uma coluna vertical, o resultado deve ser 15.')
        self.tips.add_tip(error=error5, message='Ao somar os números que estão na diagonal, o resultado deve ser 15.')
        
        self.tips_errors.append({'error': error1, 'count': 0})
        self.tips_errors.append({'error': error2, 'count': 0})
        self.tips_errors.append({'error': error3, 'count': 0})
        self.tips_errors.append({'error': error4, 'count': 0})
        self.tips_errors.append({'error': error5, 'count': 0})
        
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

                if event.key == pygame.K_RETURN or event.key == 1073741912:
                    pass

    def button_white_changed(self, data):
        if self.show_teacher:
            return
        
        if self.is_paused:
            if self.memory.get_fact('valid_initial'):
                self.log('[TIMER] Resume')
                self.memory.get_fact('timer_response').resume()
                interval = self.memory.get_fact('timer_response').get_time_resumed() - self.memory.get_fact('timer_response').get_time_paused()
                self.memory.add_fact('end_time', self.memory.get_fact('end_time') + timedelta(seconds=interval.seconds))
            self.is_paused = False
        else:
            if self.memory.get_fact('valid_initial'):
                self.log('[TIMER] Pause')
                self.memory.get_fact('timer_response').pause()
            self.is_paused = True

    def button_black_changed(self, data):
        pass

    def button_green_changed(self, data):
        if self.show_teacher:
            return

        if self.is_paused:
            return
        
        if self.memory.get_fact('valid_initial'):
            self.log('Responder desafio')
            self.memory.get_fact('timer_response').stop()

            if self.teacher.has_next_message():
                self.teacher.clear_messages()

            self.teacher.set_message(
                'Verificando...\n'+
                'Aguarde.', 
                'neutral0'
            )
            self.teacher.next_message()
            self.show_teacher = True

            self.board.avaliable_board()
            self.board.draw_matrix_board()
            self.check_challenge()
        else:
            self.teacher.set_message(
                'Verificando...\n'+
                'Aguarde.', 
                'neutral0'
            )
            self.teacher.next_message()
            self.show_teacher = True
            
            self.board.avaliable_board()
            self.board.draw_matrix_board()
            
            numbers_student = self.board.values_positions()
            self.memory.add_fact('numbers_student', numbers_student)
            
            if self.check_initial_blocks(numbers_student):
                self.teacher.set_message(
                    'Muito bem. Você organizou os blocos conforme foi exibido. '+
                    'Agora, tente resolver o quadrado mágico. '+
                    '\n\nPressione o botão VERMELHO para continuar',
                    'neutral1'
                )
                
                self.calculate_challenge_blocks(numbers_student)
                self.memory.add_fact('valid_initial', True)
                self.memory.add_fact('reset_timer', True)
                
            else:
                self.teacher.set_message(
                    f'Atenção {self.game.student.nickname}!.\n'+
                    'Você deve organizar os blocos numerados no tabuleiro '+
                    'conforme estão exibidos aqui. Observe, inclusive, a '+
                    'posição de cada bloco. '+
                    '\n\nPressione o botão VERMELHO para continuar',
                    'neutral1'
                )
            
            self.teacher.next_message()
            self.show_teacher = True

    def button_red_changed(self, data):
        if self.is_paused:
            return
        
        if not self.show_teacher:
            self.memory.get_fact('timer_response').pause()
            
            tips_times = self.memory.get_fact('tips_times')
            self.memory.add_fact('tips_times', tips_times + 1)
            
            self.log('Acesso a dicas')
            emotions = ['neutral0', 'neutral1', 'neutral2']
            message, image = self.get_message_tips()
            self.teacher.set_message(
                message= f'Dica\n\n {message}\n\nPressione o botão VERMELHO para continuar',
                image_key= emotions[random.randrange(0,len(emotions))],
                image_explication= image
            )
        
        if self.teacher.has_next_message():
            self.teacher.next_message()
            self.show_teacher = True

        else:
            self.show_teacher = False

            if self.new_challenge:
                self.memory.get_fact('timer_response').start()
                self.memory.add_fact('end_time', datetime.now() + timedelta(seconds=self.memory.get_fact('amount_time')))
                self.new_challenge = False
                self.generate_blocks()
            else:
                if self.memory.get_fact('timer_response').is_paused():
                    self.memory.get_fact('timer_response').resume()
                    interval = self.memory.get_fact('timer_response').get_time_resumed() - self.memory.get_fact('timer_response').get_time_paused()
                    self.memory.add_fact('end_time', self.memory.get_fact('end_time') + timedelta(seconds=interval.seconds))

            if self.memory.get_fact('step') > self.memory.get_fact('max_steps'):
                step = self.memory.get_fact('step')
                step += 1
                step = self.memory.add_fact('step', step)
                self.save_steps(4, 'completed')
                    
            if self.memory.get_fact('lives') <= 0:
                self.memory.add_fact('lives', -1)
                self.save_steps(4, 'not-completed')

            if self.end_phase and not self.show_teacher:
                self.exit_state()


    def update(self, delta_time):
        if self.memory.get_fact('reset_blocks'):
            self.generate_blocks()
            self.memory.add_fact('reset_blocks', False)

    def exit_state(self):
        super().exit_state()
        #self.leds.turnOff()

    def load_challenges(self):
        challenges = {
            '159': {'equation': '1 + 5 + 9','found': False},
            '168': {'equation': '1 + 6 + 8','found': False},
            '249': {'equation': '2 + 4 + 9','found': False},
            '258': {'equation': '2 + 5 + 8','found': False},
            '267': {'equation': '2 + 6 + 7','found': False},
            '348': {'equation': '3 + 4 + 8','found': False},
            '357': {'equation': '3 + 5 + 7','found': False},
            '456': {'equation': '4 + 5 + 6','found': False},
        }
        return challenges

    def first_gaming(self):
        self.teacher.set_message(
                'Prepare-se para começar!\n\n '+
                'Remova todos os blocos que '+
                'possam estar sobre o tabuleiro.'+
                '\n\nPressione o botão VERMELHO para continuar',
                'neutral1'
        )

        self.teacher.set_message(
                'Organize os blocos no tabuleiro conforme apresentado.'+
                '\n\n'+
                'Lembre-se de utilizar a região central do tabuleiro.\n' +
                'Após organizar, pressione o botão VERDE para \n'+
                'confirmar o posicionamento.'+
                '\n\nPressione o botão VERMELHO para continuar',
                'neutral2',
                modal=False,
                position=(730, 300)
        )
        self.show_teacher = True

    def generate_blocks(self):
        self.reset_blocks()
        if self.memory.get_fact('step') == 1:
            self.memory.add_fact('initial_blocks' , [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 2, 0, 4, 0, 0],
                [0, 0, 0, 5, 0, 0, 0],
                [0, 0, 6, 0, 8, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0]
            ])
        
        elif self.memory.get_fact('step') == 2:
            self.memory.add_fact('initial_blocks' , [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 4, 0, 2, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 8, 0, 6, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0]
            ])
        
        elif self.memory.get_fact('step') == 3:
            self.memory.add_fact('initial_blocks' , [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 7, 0, 0, 0],
                [0, 0, 1, 0, 9, 0, 0],
                [0, 0, 0, 3, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0]
            ])

        elif self.memory.get_fact('step') == 4:
            self.memory.add_fact('initial_blocks' , [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 5, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0]
            ])

        else:
            self.memory.add_fact('initial_blocks' , [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0]
            ])
        
        #self.leds_initial_blocks()    
        
    def leds_initial_blocks(self):
        count = 0
        leds = []
        for i in range(0, self.board.lines):
            for j in range(0, self.board.columns):
                if self.initial_blocks[i][j] != 0:
                    leds.append(count)
                count += 1
        
        self.leds.turnOn(RED, leds)

    def reset_blocks(self):       
        self.memory.add_fact('initial_blocks', [])
        self.memory.add_fact('student_blocks', {})
        self.memory.add_fact('challenge_blocks', [])
        self.memory.add_fact('matrix', [])
        self.memory.add_fact('challenges', self.load_challenges())

    def calculate_challenge_blocks(self, numbers):
        initial_blocks = self.memory.get_fact('initial_blocks')
        
        matrix = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        for l in range(2, len(initial_blocks) - 2):
            for c in range(2, len(initial_blocks[l]) - 2):
                matrix[l-1][c-1] = initial_blocks[c][l]
        
        for key in numbers.keys():
            l,c = numbers[key]
            if matrix[l-2][c-2] == 0:
                matrix[l-2][c-2] = key
        
        
        for l in range(1, len(matrix)-1):
            total = 0
            numbers_found = []
            for c in range(1, len(matrix[l]) - 1):
                total += matrix[l][c]
                if matrix[l][c] != 0:
                    numbers_found.append(matrix[l][c])
            matrix[l][0] = total - 15
            matrix[l][len(matrix[l])-1] = total - 15
            self.verify_key_in_challenges(numbers_found)
        
        for c in range(1, len(matrix) -1):
            total = 0
            numbers_found = []
            for l in range(1, len(matrix[c]) -1):
                total += matrix[l][c]
                if matrix[l][c] != 0:
                    numbers_found.append(matrix[l][c])
            matrix[0][c] = total - 15
            matrix[len(matrix[l])-1][c] = total - 15
            self.verify_key_in_challenges(numbers_found)

        total = 0
        numbers_found = []
        for l in range(1, len(matrix) - 1):
            total += matrix[l][l]
            if matrix[l][l] != 0:
                numbers_found.append(matrix[l][l])
        matrix[0][0] = total - 15
        matrix[len(matrix)-1][len(matrix)-1] = total - 15
        self.verify_key_in_challenges(numbers_found)

        total = 0
        numbers_found = []
        for l in range(len(matrix)-2, 0, -1):
            total += matrix[l][len(matrix) - 1 - l]
            if matrix[l][len(matrix) - 1 - l] != 0:
                numbers_found.append(matrix[l][len(matrix) - 1 - l])
        matrix[len(matrix) - 1][0] = total - 15
        matrix[0][len(matrix) -1] = total - 15
        self.verify_key_in_challenges(numbers_found)

        #self.matrix = matrix
        self.memory.add_fact('matrix', matrix)
        

    def verify_key_in_challenges(self, numbers):
        if len(numbers) > 0:
            numbers.sort()
            key = ''.join(map(str, numbers))
            if self.memory.get_fact('challenges').get(key) is not None:
                self.memory.get_fact('challenges')[key]['found'] = True

    def count_challenges_found(self):
        total = 0
        for key in self.memory.get_fact('challenges').keys():
            if self.memory.get_fact('challenges')[key]['found']:
                total += 1
        return total

    def blocks_in_board(self):
        total = 0
        for l in range(0, self.board.lines):
            for c in range(0, self.board.columns):
                if self.memory.get_fact('initial_blocks')[l][c] != 0:
                    total += 1
        return total

    def check_initial_blocks(self, numbers):
        initial_blocks = self.memory.get_fact('initial_blocks')
        
        initial_numbers = self.__initial_numbers__()
        student_numbers = self.__student_numbers__()
        
        print('initial: ', initial_numbers)
        print('student: ', student_numbers)
        
        if len(initial_numbers) != len(student_numbers):
            return False
        
        for c in range(0, len(initial_blocks)):
            for l in range(0, len(initial_blocks[c])):
                if initial_blocks[l][c] != 0:
                    n = numbers.get(initial_blocks[l][c])
                    if n is not None:
                        if n[1] != l+1 or n[0] != c+1:
                            return False
                    else:
                        return False
        return True

    def check_challenge(self):
        numbers_student = self.board.values_positions()
        self.memory.add_fact('numbers_student', numbers_student)
        self.memory.add_fact('numbers_initial_response', str(self.__initial_numbers__()))
        self.memory.add_fact('numbers_student_response', str(self.__student_numbers__()))
        
        self.log(f'numbers_student [{numbers_student}]')
        self.log(f'numbers_initial_response [{str(self.__initial_numbers__())}]')
        self.log(f'numbers_student_response [{str(self.__student_numbers__())}]')

        self.rules.execute_rules()
        
        feedback = Phase04Feedback(self.game, self.memory)
        feedback.enter_state()
        
        self.calculate_challenge_blocks(numbers_student)
        
        self.teacher.clear_messages()
        self.show_teacher = False
        
        if self.memory.get_fact('lives') == 0:
            self.log('Acabaram as vidas')
            self.teacher.set_message(
                'Puxa, você não conseguiu '+
                'encontrar as melhores estratégias para jogar comigo.\n\n'+
                'Tente novamente!'
                '\n\nPressione o botão VERMELHO para continuar', 
                'neutral1'
            )
            self.end_phase = True
            self.teacher.next_message()
            self.show_teacher = True
            

        if self.memory.get_fact('step') > self.memory.get_fact('max_steps') and not self.end_phase:
            self.log('Acabaram os desafios')
            self.teacher.set_message(
                'Ual, parabéns!!! Você conseguiu resolver todos os ' +
                'os desafios e completar todas as fases do jogo. \n\n'+
                'Obrigado por jogar :D '+
                '\n\nPressione o botão VERMELHO para continuar',
                'heart0'
            )
            self.started = False
            self.end_phase = True
            self.teacher.next_message()
            self.show_teacher = True
    
    def draw_lifes(self):
        display = self.game.game_canvas
        for i in range(0, self.memory.get_fact('lives')):
            heart = self.images['heart']
            heart_rect = heart.get_rect()
            heart_rect.x = 10 + 50 * i
            heart_rect.y = 5
            display.blit(heart, heart_rect)

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
        text = 'Dicas'
        if self.show_teacher:
            if self.teacher.has_next_message():
                text = 'Continuar'
            else:
                text = 'Fechar'
        red_text = font.render(text, True, (0,0,0))
        display.blit(red_text, (145, baseline_text))

        if not self.show_teacher:
            pygame.draw.circle(display,WHITE,(20,baseline_circle),10)
            white_text = font.render('Pausar' if not self.is_paused else 'Continuar', True, (0,0,0))
            display.blit(white_text, (35, baseline_text))

            pygame.draw.circle(display,GREEN,(220,baseline_circle),10)
            green_text = font.render('Responder' if self.memory.get_fact('valid_initial') else 'Validar posições', True, (0,0,0))
            display.blit(green_text, (235, baseline_text))

    
    def draw_challenge(self):
        initial_blocks = self.memory.get_fact('initial_blocks')
        student_blocks = self.memory.get_fact('student_blocks')
        matrix = self.memory.get_fact('matrix')
        
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        font = pygame.font.SysFont(FONT_NAME, 30, False, False)

        total_shape_x = self.box_width * self.board.columns + self.offset * (self.board.columns + 1)
        total_shape_y = self.box_height * self.board.lines + self.offset * (self.board.lines + 1)

        pos_x = self.offset * 2
        pos_y = screen_height/2 - total_shape_y / 2

        pos_x += self.offset
        pos_y += self.offset
        x = pos_x
        
        for col in range(0, self.board.columns):
            y = pos_y
            for lin in range(0, self.board.lines):
                if initial_blocks[col][lin] != 0:
                    color = (220, 3, 3)
                    rect = (x,y,self.box_width,self.box_height)
                    shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                    pygame.draw.rect(shape, color, shape.get_rect())
                    display.blit(shape, rect)
                    color = (255,255,255,255)
                    text = font.render(str(initial_blocks[col][lin]), True, color)
                    text_rect = text.get_rect(center=(x+self.box_width/2, y+self.box_height/2))
                    display.blit(text, text_rect)
                y += self.box_height + self.offset
            x += self.box_width + self.offset

        pos_x = self.offset * 2
        pos_y = screen_height/2 - total_shape_y / 2

        for key in student_blocks.keys():
            pos = student_blocks[key]
            x = pos_x + self.offset * pos[1] + self.box_width * (pos[1] - 1)
            y = pos_y + self.offset * pos[0] + self.box_height * (pos[0] - 1)
            rect = (x,y,self.box_width,self.box_height)
            shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
            pygame.draw.rect(shape, (220, 3, 3), shape.get_rect())
            display.blit(shape, rect)
            text = font.render(str(key), True, (255,255,255))
            text_rect = text.get_rect(center=(x+self.box_width/2, y+self.box_height/2))
            display.blit(text, text_rect)

        if self.memory.get_fact('valid_initial'):
            font = pygame.font.SysFont(FONT_NAME, 20, False, False)
            box_width = 30
            box_height = 30
            offset = 10
            pos_x = (total_shape_x + self.offset * 3) + ((screen_width - (total_shape_x + self.offset * 3))/2) - (box_width*len(matrix))/2 - (offset * (len(matrix)-1))/2
            pos_y = 100
            x = pos_x
            
            for c in range(0, len(matrix)):
                y = pos_y
                for l in range(0, len(matrix[c])):
                    if self.is_calculate_value(l, c):
                        color = DARKGREEN
                        if matrix[l][c] > 0:
                            color = RED
                        elif matrix[l][c] < 0:
                            color = BLACK
                        text = font.render(str(matrix[l][c]), True, color)
                        text_rect = text.get_rect(center=(x+box_width/2, y+box_height/2))
                        display.blit(text, text_rect)
                    else:
                        color = (220, 3, 3)
                        rect = (x,y,box_width,box_height)
                        shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                        pygame.draw.rect(shape, color, shape.get_rect())
                        display.blit(shape, rect)
                        color = (255,255,255,255)
                        text = font.render(str(matrix[l][c]), True, color)
                        text_rect = text.get_rect(center=(x+box_width/2, y+box_height/2))
                        if matrix[l][c] != 0:
                            display.blit(text, text_rect)
                    y += box_height + offset
                x += box_width + offset

    def is_calculate_value(self, l, c):
        matrix = self.memory.get_fact('matrix')
        if (l > 0 and l < len(matrix) - 1) and (c > 0 and c < len(matrix[0]) - 1):
            return False
        return True


    def draw_timer(self):
        display = self.game.game_canvas
        timer_font = pygame.font.Font(os.path.join('fonts', 'digital-7.ttf'), 40)
        screen_width = self.game.GAME_WIDTH
        reset_timer = self.memory.get_fact('reset_timer')
        end_time = self.memory.get_fact('end_time')
        
        if reset_timer and not self.show_teacher:
            self.log('[TIMER] - Reset')
            self.memory.add_fact('reset_timer', False)
            self.memory.get_fact('timer_response').stop()
            self.memory.get_fact('timer_response').start()
            self.memory.add_fact('end_time', datetime.now() + timedelta(seconds=self.memory.get_fact('amount_time')))

        if not self.memory.get_fact('timer_response').is_paused() and self.memory.get_fact('timer_response').is_started() and self.memory.get_fact('valid_initial'):
            time_left = max(end_time - datetime.now(), timedelta(0))

            if time_left.seconds > 0:
                self.time_hms = self.convert_time(time_left.seconds)
            else:
                self.end_timer()

            timer_text = timer_font.render(f'{self.time_hms[1]:02d}:{self.time_hms[2]:02d}', True, (255, 0, 0))
            timer_text_rect = timer_text.get_rect(center=(screen_width/2, 20))
            display.blit(timer_text, timer_text_rect)
        
    
    def end_timer(self):
        student: Student = self.memory.get_fact('student')
        if student.inhibitory_capacity_online != Student.INHIBITORY_CAPACITY_LOW:
            self.log('[TIMER] - Acabou o tempo')

            self.memory.add_fact('reset_timer', True)
            
            self.memory.get_fact('timer_response').stop()
            self.memory.add_fact('is_correct', False)
            
            response = {}
            response['is_correct'] = False
            response['numbers'] = str([-1])
            response['numbers_base'] = str(self.__initial_numbers__())
            
            response['reaction_time'] = self.memory.get_fact('timer_response').total_time_seconds()
            response['reaction_time_without_pauses'] = self.memory.get_fact('timer_response').total_time_without_paused_seconds()
            response['paused_counter'] = self.memory.get_fact('timer_response').total_times_paused() - self.memory.get_fact('tips_times')
            response['tips_counter'] = self.memory.get_fact('tips_times')
            response['max_time'] = self.memory.get_fact('average_time')

            response['start_time'] = self.memory.get_fact('timer_response').get_time_started()
            response['end_time'] = self.memory.get_fact('timer_response').get_time_finished()

            response['affective_state'] = ''
            response['affective_quad'] = ''
            response['icc'] = student.inhibitory_capacity_online
            
            response['type_error'] = TypeError.ERROR_TIMEOUT
            response['subtype_error'] = TypeError.SUBTYPE_NONE
            
            self.memory.get_fact('responses').append(response)
            
            self.log(f'[RESPONSE]\n{response}')
            self.save_challenge(response)
            
            history_errors = self.memory.get_fact('history_errors')
            history_errors.append(Error(type=TypeError.ERROR_TIMEOUT, subtype=TypeError.SUBTYPE_NONE))
            self.memory.add_fact('history_errors', history_errors)
            
            quantity_errors = self.memory.get_fact('quantity_errors')
            quantity_errors += 1
            self.memory.add_fact('quantity_errors', quantity_errors)
            
            self.rules_level.execute_rules()
            self.adjust_game_levels()
            
            if self.memory.get_fact('lives') == 0:
                self.teacher.set_message(
                    f"Puxa {student.nickname}!!! Infelizmente suas "+
                    "vidas acabaram. Tente resolver novamente este desafio "+
                    "para que você possa avançar de fase."+
                    "\n\nPressione o botão VERMELHO para continuar",  
                    "neutral1"
                )
            else:
                self.teacher.set_message(
                    f"Preste atenção {student.nickname}!!! Tente resolver o "+
                    "exercício antes que o tempo acabe. Mantenha o foco "+
                    "na resolução dos exercícios."+
                    "\n\nPressione o botão VERMELHO para continuar",  
                    "neutral1"
                )

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
    
    @db_session
    def save_challenge(self, response) -> None:
        user = DBUser[self.game.student.id]
        session = DBSession[int(self.memory.get_fact('session_id'))]
        challenge = DBChallengeP4(
            numbers = response['numbers'],
            numbers_base = response['numbers_base'],
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
            icc = response['icc'],
            user = user,
            session = session
        )
        challenge.flush()
        facialThread = FacialThread(self.game.app, challenge.id, self.update_challenge)
        facialThread.start()
    
    @db_session
    def update_challenge(self, id, expression, quad):
        challenge = DBChallengeP4[id]
        challenge.set(affective_state = expression, affective_quad = quad)
        challenge.flush()

    @db_session
    def save_steps(self, phase, status):
        user = DBUser[self.game.student.id]
        step = DBSteps(
            phase = phase,
            score = self.memory.get_fact('score'),
            lifes = self.memory.get_fact('lives'),
            status = status,
            user = user
        )
        commit()

    def adjust_game_levels(self):
        student: Student = self.memory.get_fact('student')
        
        average_time = self.memory.get_fact('average_time')
        
        if student.inhibitory_capacity_online == Student.INHIBITORY_CAPACITY_LOW:
            self.memory.add_fact('amount_time', average_time)
            self.memory.add_fact('enable_timer', False)
        elif student.inhibitory_capacity_online == Student.INHIBITORY_CAPACITY_MEDIUM:
            self.memory.add_fact('amount_time', average_time)
            self.memory.add_fact('enable_timer', True)
        else:
            self.memory.add_fact('amount_time', math.ceil(average_time * 0.5))
            self.memory.add_fact('enable_timer', True)

    def __initial_sums__(self) -> list[str]:
        challenges = self.memory.get_fact('challenges')
        numbers = self.__initial_numbers__()
        
        keys = []
        for n in numbers:
            key = ''.join(map(str, n))
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
    
    def __student_sums__(self) -> list[str]:
        challenges = self.memory.get_fact('challenges')
        numbers = self.__student_numbers__()
        
        keys = []
        for n in numbers:
            key = ''.join(map(str, n))
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
            if len(t) > 0 and elements.count(t) == 0:
                elements.append(t)
                
        for c in range(1, len(matrix) -1):
            t = []
            for l in range(1, len(matrix[c]) -1):
                if matrix[l][c] != 0:
                    t.append(matrix[l][c])
            if len(t) > 0 and elements.count(t) == 0:
                elements.append(t)
        
        t = []
        for l in range(1, len(matrix) - 1):
            if matrix[l][l] != 0:
                t.append(matrix[l][l])
        if len(t) > 0 and elements.count(t) == 0:
                elements.append(t)
                
        t = []
        for l in range(len(matrix)-2, 0, -1):
            if matrix[l][len(matrix) - 1 - l] != 0:
                t.append(matrix[l][len(matrix) - 1 - l])
        if len(t) > 0 and elements.count(t) == 0:
                elements.append(t)
        
        for n in elements:
            n.sort()
            keys.append(n)
        
        return keys

    def render(self, display):
        display.fill((255,255,255))
        
        self.draw_board()
        self.draw_lifes()
        self.draw_score()
        self.draw_physical_buttons()
        self.draw_student_name()

        if self.show_teacher:
            self.teacher.draw()

        if self.is_paused:
            self.draw_pause()

        if self.confetti.visible:
            self.draw_confetti()
        
        if (not self.show_teacher and not self.is_paused) or (self.show_teacher and not self.teacher.modal):
            self.draw_challenge()
            
        if self.memory.get_fact('lives') > 0 and self.memory.get_fact('step') <= self.memory.get_fact('max_steps'):
            if self.memory.get_fact('enable_timer') and not self.show_teacher:
                self.draw_timer()