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
import random
from pony.orm import *

from game.states.state import State
from base.board import Board
from game.actors.teacher import Teacher
from utils.timer import Timer
from utils.confetti import Confetti
from database.models import DBUser, DBSteps, DBChallengeP2

from game import BACKGROUND_COLOR
from game import TEXT_COLOR
from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN

class Phase02(State):

    def __init__(self, game):
        super().__init__(game)
        self.board = Board(self.game.app)
        self.teacher = Teacher(self.game.game_canvas)
        self.show_teacher = False

        self.images = self.load_images()
        self.challenges = self.load_challenges()
        self.responses = []

        self.lives = 3
        self.score = 0
        self.max_steps = 8
        self.step = 0
        self.incremental_points = 5

        self.start_time = pygame.time.get_ticks()
        self.total_seconds = 10
        self.time_hms = 0, 0, 0
        self.total_time = self.start_time + self.total_seconds*1000

        self.enable_timer = False
        self.is_paused = False
        self.started = False
        self.new_challenge = True
        self.new_response = True
        self.end_phase = False

        self.timer_challenge = Timer()
        self.timer_teacher = Timer()
        self.timer_teacher.start()
        self.timer_response = Timer()

        self.tips_times = 0

        self.confetti = Confetti()
        self.frame_confetti = 1
        self.starting_game()


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
                    self.exit_state()

                if event.key == pygame.K_UP:
                    pass

                if event.key == pygame.K_DOWN:
                    pass

                if event.key == pygame.K_RETURN or event.key == 1073741912:
                    pass

    def button_black_changed(self, data):
        pass

    def button_white_changed(self, data):
        if self.show_teacher:
            return
        
        if self.is_paused:
            self.timer_challenge.resume()
            self.timer_response.resume()
            self.is_paused = False
        else:
            self.timer_challenge.pause()
            self.timer_response.pause()
            self.is_paused = True

    def button_green_changed(self, data):
        """
        Executed when the green button of the base is pressed
        """
        if self.show_teacher:
            return

        if self.is_paused:
            return
        
        self.timer_teacher.resume()
        self.timer_response.stop()
        self.timer_challenge.pause()
        #irá contar o tempo enquanto verifica a resposta?


        if self.teacher.has_next_message():
            self.teacher.clear_messages()


        self.teacher.set_message(
            "Verificando...\n"+
            "Aguarde.", 
            "neutral0"
        )
        self.teacher.next_message()
        self.show_teacher = True

        self.board.avaliable_board()
        self.board.draw_matrix_board()
        self.check_challenge()
    
    def button_red_changed(self, data):
        if self.is_paused:
            return

        if not self.show_teacher:
            self.timer_challenge.pause()
            self.timer_response.pause()
            self.timer_teacher.resume()
            self.tips_times += 1
            self.teacher.set_message(
                "Dicas", 
                "neutral0"
            )

        if self.teacher.has_next_message():
            self.teacher.next_message()
            self.show_teacher = True

            if not self.started:
                self.started = True
        else:
            self.show_teacher = False
            self.timer_teacher.pause()

            if self.step == self.max_steps:
                self.step += 1
                self.save_steps(2, 'completed')
                self.save_steps(3, 'not-started')
            if self.lives == 0 and self.end_phase:
                self.lives -= 1
                self.save_challenge()
                self.save_steps(2, 'not-completed')
            
            if self.new_challenge:
                self.timer_challenge.start()
                self.timer_response.start()
                self.new_challenge = False
                self.tips_times = 0
            else:
                self.timer_challenge.resume()
                if self.new_response:
                    self.timer_response.start()
                    self.new_response = False
                else:
                    self.timer_response.resume()
            

            if self.end_phase and not self.show_teacher:
                self.exit_state()

    def button_red_changed2(self):
        if self.is_paused:
            return 
        
        if self.show_teacher:
            if not self.started:
                self.started = True
            
            if self.step == self.max_steps:
                self.step += 1
                self.save_steps(2, 'completed')
                self.save_steps(3, 'not-started')
            if self.lives == 0 and self.end_phase:
                self.lives -= 1
                self.save_challenge()
                self.save_steps(2, 'not-completed')
            
            if self.new_challenge:
                self.timer_challenge.start()
                self.timer_response.start()
                self.new_challenge = False
                self.tips_times = 0
            else:
                self.timer_challenge.resume()
                if self.new_response:
                    self.timer_response.start()
                    self.new_response = False
                else:
                    self.timer_response.resume()
                
            self.timer_teacher.pause()
            self.show_teacher = False
        else:
            self.timer_challenge.pause()
            self.timer_response.pause()
            self.teacher.set_message("Lorem ipsum dolor sit amet, consectetur adipiscing elit. \nFusce ultricies massa elit, nec lacinia mauris ultricies vitae.\nLorem ipsum dolor sit amet, consectetur adipiscing elit. \nFusce ultricies massa elit, nec lacinia mauris ultricies vitae.")
            self.timer_teacher.resume()
            self.show_teacher = True
            self.tips_times += 1

    def load_challenges(self):
        challenges = {
            '159': {'equations': ['1 + 5 + 9', '1 + 9 + 5', '5 + 1 + 9', '5 + 9 + 1', '9 + 1 + 5', '9 + 5 + 1'], 'visible': False, 'index': random.randrange(0, 6)},
            '168': {'equations': ['1 + 6 + 8', '1 + 8 + 6', '6 + 1 + 8', '6 + 8 + 1', '8 + 1 + 6', '8 + 6 + 1'], 'visible': False, 'index': random.randrange(0, 6)},
            '249': {'equations': ['2 + 4 + 9', '2 + 9 + 4', '4 + 2 + 9', '4 + 9 + 2', '9 + 2 + 4', '9 + 4 + 2'], 'visible': False, 'index': random.randrange(0, 6)},
            '258': {'equations': ['2 + 5 + 8', '2 + 8 + 5', '5 + 2 + 8', '5 + 8 + 2', '8 + 2 + 5', '8 + 5 + 2'], 'visible': False, 'index': random.randrange(0, 6)},
            '267': {'equations': ['2 + 6 + 7', '2 + 7 + 6', '6 + 2 + 7', '6 + 7 + 2', '7 + 2 + 6', '7 + 6 + 2'], 'visible': False, 'index': random.randrange(0, 6)},
            '348': {'equations': ['3 + 4 + 8', '3 + 8 + 4', '4 + 3 + 8', '4 + 8 + 3', '8 + 3 + 4', '8 + 4 + 3'], 'visible': False, 'index': random.randrange(0, 6)},
            '357': {'equations': ['3 + 5 + 7', '3 + 7 + 5', '5 + 3 + 7', '5 + 7 + 3', '7 + 3 + 5', '7 + 5 + 3'], 'visible': False, 'index': random.randrange(0, 6)},
            '456': {'equations': ['4 + 5 + 6', '4 + 6 + 5', '5 + 4 + 6', '5 + 6 + 4', '6 + 4 + 5', '6 + 5 + 4'], 'visible': False, 'index': random.randrange(0, 6)},
        }
        return challenges
        
    def starting_game(self):
        if not self.started:
            self.teacher.set_message(
                "Atenção!\n"+
                "Prepare-se para começar", 
                "neutral1"
            )
            self.teacher.next_message()
            self.show_teacher = True

    def update(self, delta_time):
        pass

    def draw_physical_buttons(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        baseline_text = screen_height - 35
        baseline_circle = screen_height - 23
        
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        
        pygame.draw.circle(display,RED,(130,baseline_circle),10)
        red_text = font.render("Dicas" if not self.show_teacher else "Fechar", True, (0,0,0))
        display.blit(red_text, (145, baseline_text))

        if not self.show_teacher:
            pygame.draw.circle(display,WHITE,(20,baseline_circle),10)
            white_text = font.render("Pausar", True, (0,0,0))
            display.blit(white_text, (35, baseline_text))

            pygame.draw.circle(display,GREEN,(220,baseline_circle),10)
            green_text = font.render("Responder", True, (0,0,0))
            display.blit(green_text, (235, baseline_text))
    
    def draw_lifes(self):
        display = self.game.game_canvas
        for i in range(0, self.lives):
            heart = self.images['heart']
            heart_rect = heart.get_rect()
            heart_rect.x = 10 + 50 * i
            heart_rect.y = 5
            display.blit(heart, heart_rect)

    def draw_score(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        font = pygame.font.SysFont(FONT_NAME, 30, False, False)
        score_text = font.render(f'Pontos: {self.score:>4}', True, (0,0,0))
        score_text_rect = score_text.get_rect(midright=(screen_width-5, 30))
        display.blit(score_text, score_text_rect)
    
    def draw_student_name(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        baseline_text = screen_height - 23

        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        name_text = font.render(self.game.student.nickname, True, (0,0,0))
        name_text_rect = name_text.get_rect(midright=(screen_width-5, baseline_text))
        display.blit(name_text, name_text_rect)

    def draw_table(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT

        table = self.images['table']
        table_rect = table.get_rect(center=(screen_width/2, 410))
        display.blit(table, table_rect)

    def draw_student_desk(self, quantity = 4):
        display = self.game.game_canvas
        student_desk = self.images['student-desk']

        x_coordenate = []
        if (quantity == 1):
            x_coordenate = [160]
        elif (quantity == 2):
            x_coordenate = [160, 580]
        else:
            x_coordenate = [-80, 160, 590, 830]

        for x in x_coordenate:
            student_desk_rect = student_desk.get_rect(topleft=(x,380))
            display.blit(student_desk, student_desk_rect)
    
    def draw_pause(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
                
        rect_background = (0,0,screen_width,screen_height)
        shape_surf = pygame.Surface(pygame.Rect(rect_background).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (0,0,0,230), shape_surf.get_rect())
        display.blit(shape_surf, rect_background)

        font = pygame.font.SysFont(FONT_NAME, 72, False, False)
        instruction_text = font.render('Pause', True, (220,220,220))
        instruction_text_rect = instruction_text.get_rect(center=(screen_width/2, screen_height/2))
        display.blit(instruction_text, instruction_text_rect)
    
    def draw_challenge(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        color = (213, 255, 213)

        font = pygame.font.SysFont(FONT_NAME, 22, False, False)
        instruction_text = font.render('Encontre as somas com 3 números que resultam 15', True, (220,220,220))
        instruction_text_rect = instruction_text.get_rect(center=(screen_width/2, 90))

        if not self.show_teacher and not self.is_paused:
            display.blit(instruction_text, instruction_text_rect)

            i = 1
            width = 140
            height = 60
            offset = 20
            x = 160
            y = 150
            for key in self.challenges.keys():
                rect = (x,y,width,height)
                shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                pygame.draw.rect(shape, color, shape.get_rect(), border_radius= 15)
                display.blit(shape, rect)
                inner_text = '? + ? + ?' if not self.challenges[key]['visible'] else self.challenges[key]['equations'][self.challenges[key]['index']]
                text = font.render(inner_text, True, BLACK if not self.challenges[key]['visible'] else GREEN)
                text_rect = text.get_rect(center=(x + width/2, y + height/2))
                display.blit(text, text_rect)
                if i % 4 == 0:
                    x = 160
                    y += height + offset
                else:
                    x += width + offset
                i += 1
    
    def add_response(self, response):
        self.responses.append(response)
        self.timer_response.stop()
        self.tips_times = 0
        self.new_response = True

    def check_challenge(self):
        numbers = self.board.result_matrix_board()
        response = {}
        response['total_time'] = self.timer_response.total_time_seconds()
        response['time_without_pauses'] = (self.timer_response.total_time_seconds() - self.timer_response.total_time_paused_seconds())
        #@TODO: corrigir quantidade de pausas
        response['paused_counter'] = self.timer_response.total_times_paused() - self.tips_times
        response['tips_counter'] = self.tips_times

        if len(numbers) == 0:
            response['number01'] = -1
            response['number02'] = -1
            response['number03'] = -1
            response['is_correct'] = False
            self.add_response(response)

            self.teacher.set_message(
                "Atenção. Você deve colocar\n"+
                "os bloco numérico correspondente\n"+
                "à respostas sobre o tabuleiro.", 
                "neutral0"
            )
            self.lives -= 1
        elif len(numbers) == 1:
            response['number01'] = numbers[0]
            response['number02'] = -1
            response['number03'] = -1
            response['is_correct'] = False
            self.add_response(response)

            self.teacher.set_message(
                "Atenção! Você deve usar 3 números\n"+
                "para tentar encontrar a soma 15.", 
                "neutral0"
            )
            self.lives -= 1

        elif len(numbers) == 2:
            response['number01'] = numbers[0]
            response['number02'] = numbers[1]
            response['number03'] = -1
            response['is_correct'] = False
            self.add_response(response)
            
            result = sum(numbers)
            if result == 15:
                self.teacher.set_message(
                    "Apesar do resultado da operação\n"+
                    "resultar em 15, é necessário\n"+
                    "utilizar 3 números distintos na soma.", 
                    "neutral0"
                )
            else:
                self.teacher.set_message(
                    "Atenção! Você deve usar 3 números\n"+
                    "para tentar encontrar a soma 15.", 
                    "neutral0"
                )
            self.lives -= 1

        elif len(numbers) == 3:
            response['number01'] = numbers[0]
            response['number02'] = numbers[1]
            response['number03'] = numbers[2]

            numbers.sort()
            key = "".join(map(str, numbers))
            if self.challenges.get(key) is not None:
                if self.challenges[key]['visible']:
                    response['is_correct'] = False
                    self.add_response(response)
                    
                    self.teacher.set_message(
                        "Atenção. Você já informou\n"+
                        f"essa operação: {numbers[0]}+{numbers[1]}+{numbers[2]}.\n"+
                        "Tente resolver outras.",
                        "happy0"
                    )
                    self.lives -= 1

                else:
                    response['is_correct'] = True
                    self.add_response(response)

                    emotions = ['happy0', 'happy1', 'happy2', 'heart0']
                    self.teacher.set_message(
                        "Parabéns!!!\n"+
                        "Está correto. Quando somados,\n"+
                        f" os valores {numbers[0]}, {numbers[1]} e {numbers[2]}, produzem\n"+
                        "resultado 15.", 
                        emotions[random.randrange(0,len(emotions))]
                    )

                    self.challenges[key]['visible'] = True
                    self.frame_confetti = 1
                    self.confetti.visible = True
                    self.score += self.incremental_points
                    self.step += 1
                    #self.save_challenge(numbers)
            else:
                response['is_correct'] = False
                self.add_response(response)

                result = sum(numbers)
                fault = abs(15 - result)
                self.teacher.set_message(
                    f"Atenção. Essa operação resulta {result}.\n"+
                    f"Há uma diferença de {fault} para o\n"+
                    "resultado esperado 15. Tente novamente.", 
                    "neutral1"
                )
                self.lives -= 1
        
        else:
            result = sum(numbers)

            response['number01'] = -result
            response['number02'] = -result
            response['number03'] = -result
            response['is_correct'] = False
            self.add_response(response)

            if result == 15:
                self.teacher.set_message(
                    "Apesar do resultado da operação\n"+
                    "resultar em 15, é necessário\n"+
                    "utilizar 3 números distintos na soma.", 
                    "neutral0"
                )
            else:
                self.teacher.set_message(
                    "Atenção! Você deve usar 3 números\n"+
                    "para tentar encontrar a soma 15.", 
                    "neutral0"
                )
            self.lives -= 1
        
        if self.lives == 0:
            self.teacher.set_message(
                "Infelizmente, você não conseguiu\n"+
                "encontrar todas as possibilidades.\n"+
                "Tente novamente!", 
                "neutral1"
            )
            self.end_phase = True

        if self.step >= self.max_steps and not self.end_phase:
            self.teacher.set_message(
                "Parabéns!!! Você encontrou todas\n"+
                "as somas  possíveis com 3 números\n"+
                "que resultam em 15. Nos vemos na\n"+
                "próxima fase.", 
                "heart0"
            )
            self.end_phase = True

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
    
    @db_session
    def save_challenge(self, numbers = None):
        user = DBUser[self.game.student.id]
        responses = []
        if not numbers:
            numbers = [-99, -99, -99]

        challenge = DBChallengeP2(
            number01 = numbers[0],
            number02 = numbers[1],
            number03 = numbers[2],
            total_time = self.timer_challenge.total_time_seconds(),
            user = user
        )

        for r in self.responses:
            data = DBResponseP2(
                number01 = r['number01'],
                number02 = r['number02'],
                number03 = r['number03'],
                is_correct = r['is_correct'],
                total_time = r['total_time'],
                time_without_pauses = r['time_without_pauses'],
                paused_counter = r['paused_counter'],
                tips_counter = r['tips_counter'],
                challengep2 = challenge
            )
            commit()
        self.timer_challenge.stop()
        self.timer_response.stop()
        self.new_challenge = True
        self.responses = []

    @db_session
    def save_steps(self, phase, status):
        user = DBUser[self.game.student.id]
        step = DBSteps(
            phase = phase,
            score = self.score,
            lifes = self.lives,
            status = status,
            user = user
        )
        commit()

    def render(self, display):
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        offset_height = 0

        display.fill((255,255,255))

        background = self.images['background']
        display.blit(background, (0,0))
        self.draw_table()
        self.draw_student_desk()
        self.draw_lifes()
        self.draw_score()
        self.draw_student_name()
        self.draw_physical_buttons()
        
        if self.show_teacher:
            self.teacher.draw()

        if self.is_paused:
            self.draw_pause()
        
        if self.confetti.visible:
            self.draw_confetti()
        
        if self.lives > 0 and self.step < self.max_steps:
            self.draw_challenge()

