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

import pygame
import os
import random
from itertools import combinations

from game.states.state import State
from base.board import Board
from game.actors.teacher import Teacher
from utils.timer import Timer
from utils.confetti import Confetti
from base.leds import Leds, RainbowThread

from game import BACKGROUND_COLOR
from game import TEXT_COLOR
from game import FONT_NAME
from game import WHITE, BLACK, RED, GREEN, DARKGREEN


class Phase04(State):

    def __init__(self, game):
        super().__init__(game)
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

        self.timer_challenge = Timer()
        self.timer_teacher = Timer()
        self.timer_teacher.start()
        self.timer_response = Timer()
        

        self.first_gaming()
        self.teacher.next_message()

    def load_images(self):
        return {
            'heart': pygame.image.load(os.path.join("images", "heart.png")),
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

                if event.key == pygame.K_RETURN or event.key == 1073741912:
                    pass
    def button_white_changed(self, data):
        pass

    def button_black_changed(self, data):
        pass

    def button_green_changed(self, data):
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
        
        if self.teacher.has_next_message():
            self.teacher.next_message()
            self.show_teacher = True

        else:
            if self.new_challenge:
                self.new_challenge = False
                self.generate_blocks()

            self.show_teacher = False

            if self.end_phase and not self.show_teacher:
                self.exit_state()


    def update(self, delta_time):
        pass

    def exit_state(self):
        super().exit_state()
        self.leds.turnOff()

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
                "Atenção!\n"+
                "Prepare-se para começar.\n"+
                "Remova todos os blocos que\n"+
                "possam estar sobre o tabuleiro.", 
                "neutral1"
        )

        self.teacher.set_message(
                "Organize os blocos no tabuleiro\n"+
                "conforme apresentado pelo tutor.", 
                "neutral1",
                modal=False,
                position=self.position_no_modal
        )
        self.show_teacher = True

    def generate_blocks(self):
        self.reset_blocks()
        if self.step == 1:
            self.initial_blocks = [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 2, 0, 4, 0, 0],
                [0, 0, 0, 5, 0, 0, 0],
                [0, 0, 6, 0, 8, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0]
            ]            
        
        elif self.step == 2:
            self.initial_blocks = [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 4, 0, 2, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 8, 0, 6, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0]
            ]
        
        elif self.step == 3:
            self.initial_blocks = [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 7, 0, 0, 0],
                [0, 0, 1, 0, 9, 0, 0],
                [0, 0, 0, 3, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0]
            ]

        elif self.step == 4:
            self.initial_blocks = [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 5, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0]
            ]

        else:
            self.initial_blocks = [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0]
            ]
        
        self.leds_initial_blocks()    
        
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
        self.initial_blocks = []
        self.student_blocks = {}
        self.challenge_blocks = []
        self.matrix = []
        self.challenges = self.load_challenges()

    def calculate_challenge_blocks(self, numbers):
        matrix = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        for l in range(2, len(self.initial_blocks) - 2):
            for c in range(2, len(self.initial_blocks[l]) - 2):
                matrix[l-1][c-1] = self.initial_blocks[c][l]
        
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

        self.matrix = matrix
        print(self.challenges)

    def verify_key_in_challenges(self, numbers):
        if len(numbers) > 0:
            numbers.sort()
            key = "".join(map(str, numbers))
            if self.challenges.get(key) is not None:
                self.challenges[key]['found'] = True

    def count_challenges_found(self):
        total = 0
        for key in self.challenges.keys():
            if self.challenges[key]['found']:
                total += 1
        return total
    
    def draw_challenges_found(self):
        display = self.game.game_canvas
        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        
        if not self.show_teacher and not self.is_paused:
            
            i = 1
            width = 140
            height = 60
            offset = 20
            x = 160
            y = 150
            color = (0,0,0)
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

    def blocks_in_board(self):
        total = 0
        for l in range(0, self.board.lines):
            for c in range(0, self.board.columns):
                if self.initial_blocks[l][c] != 0:
                    total += 1
        return total

    def check_initial_blocks(self, numbers):
        for c in range(0, len(self.initial_blocks)):
            for l in range(0, len(self.initial_blocks[c])):
                if self.initial_blocks[l][c] != 0:
                    n = numbers.get(self.initial_blocks[l][c])
                    print("n: ", n, l, c)
                    if n is not None:
                        if n[1] != l+1 or n[0] != c+1:
                            return False
                    else:
                        return False
        return True

    def check_challenge(self):
        numbers_students = self.board.values_positions()

        if not self.check_initial_blocks(numbers_students):
            if self.new_challenge:
                self.teacher.set_message(
                        "Atenção. Você deve colocar\n"+
                        "sobre o tabuleiro os blocos\n"+
                        "na ordem e posição solicitado\n"+
                        "pelo tutor.", 
                        "neutral0"
                    )
                self.new_challenge = False
            else:
                self.teacher.set_message(
                    "Atenção. Você não deve alterar\n"+
                    "a ordem inicial dos blocos que\n"+
                    "estavam dispostos sobre o tabuleiro.\n"+
                    "Por gentileza, organize-os novamente.", 
                    "neutral0"
                )
            self.lives -= 1
        else:

            self.calculate_challenge_blocks(numbers_students)

            if self.new_challenge:
                if (self.blocks_in_board() != len(numbers_students)):
                    self.teacher.set_message(
                        "Atenção. Você deve colocar\n"+
                        "sobre o tabuleiro os blocos\n"+
                        "solicitados pelo tutor.", 
                        "neutral0"
                    )
                    self.lives -= 1
                
                else:
                    self.teacher.set_message(
                        "Muito bom!\n"+
                        "Você deve completar o quadrado\n"+
                        "mágico colocando sobre o tabuleiro\n"+
                        "os blocos restantes.", 
                        "happy0",
                        modal=False,
                        position=self.position_no_modal
                    )
                    self.new_challenge = False
            else:
                found = self.count_challenges_found()

                if len(numbers_students) < 9:
                    if found == 0:
                        self.teacher.set_message(
                            "Atenção. Você deve colocar\n"+
                            "sobre o tabuleiro os blocos\n"+
                            "que faltam para completar o\n"+
                            "quadrado mágico 3x3.", 
                            "neutral0"
                        )
                        self.lives -= 1
                    else:
                        self.teacher.set_message(
                            "Parabéns! Você conseguir encontrar\n"+
                            f"{found} soma(s) que resultam 15 no\n"+ 
                            "quadrado mágico. Tente encontrar as\n"+
                            "demais somas.", 
                            "happy1"
                        )
                else:
                    self.student_blocks.update(numbers_students)
                    if found == len(self.challenges):
                        self.teacher.set_message(
                            "Muito bem! Você conseguiu encontrar\n"+
                            "todas as somas possíveis que resultam\n"+
                            "15 neste quadrado mágico.", 
                            "heart0"
                        )
                        self.frame_confetti = 1
                        self.confetti.visible = True
                        self.rainbow.run()

                        if self.step < self.max_steps:
                            self.teacher.set_message(
                                "Tente resolver o próximo desafio!\n", 
                                "happy0"
                            )
                            self.step += 1
                            self.new_challenge = True

                    else:
                        self.teacher.set_message(
                            "Parabéns! Você conseguir encontrar\n"+
                            f"{found} soma(s) que resultam 15 no\n"+ 
                            "quadrado mágico. Tente encontrar as\n"+
                            "demais somas.", 
                            "happy1"
                        )


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
    
    def draw_lifes(self):
        display = self.game.game_canvas
        for i in range(0, self.lives):
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
        red_text = font.render("Dicas" if not self.show_teacher else "Fechar", True, (0,0,0))
        display.blit(red_text, (145, baseline_text))

        if not self.show_teacher:
            pygame.draw.circle(display,WHITE,(20,baseline_circle),10)
            white_text = font.render("Pausar" if not self.is_paused else "Continuar", True, (0,0,0))
            display.blit(white_text, (35, baseline_text))

            pygame.draw.circle(display,GREEN,(220,baseline_circle),10)
            green_text = font.render("Responder", True, (0,0,0))
            display.blit(green_text, (235, baseline_text))

    def lose_life(self):
        if self.lives > 0:
            self.lives -= 1
            self.start_time = pygame.time.get_ticks()
            self.total_time = self.start_time + self.total_seconds*1000
            #self.new_challenge = True

    
    
    def draw_challenge(self):
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
                if self.initial_blocks[col][lin] != 0:
                    color = (220, 3, 3)
                    rect = (x,y,self.box_width,self.box_height)
                    shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                    pygame.draw.rect(shape, color, shape.get_rect())
                    display.blit(shape, rect)
                    color = (255,255,255,255)
                    text = font.render(str(self.initial_blocks[col][lin]), True, color)
                    text_rect = text.get_rect(center=(x+self.box_width/2, y+self.box_height/2))
                    display.blit(text, text_rect)
                y += self.box_height + self.offset
            x += self.box_width + self.offset

        pos_x = self.offset * 2
        pos_y = screen_height/2 - total_shape_y / 2

        for key in self.student_blocks.keys():
            pos = self.student_blocks[key]
            x = pos_x + self.offset * pos[1] + self.box_width * (pos[1] - 1)
            y = pos_y + self.offset * pos[0] + self.box_height * (pos[0] - 1)
            rect = (x,y,self.box_width,self.box_height)
            shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
            pygame.draw.rect(shape, (220, 3, 3), shape.get_rect())
            display.blit(shape, rect)
            text = font.render(str(key), True, (255,255,255))
            text_rect = text.get_rect(center=(x+self.box_width/2, y+self.box_height/2))
            display.blit(text, text_rect)

        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        box_width = 30
        box_height = 30
        offset = 10
        pos_x = (total_shape_x + self.offset * 3) + ((screen_width - (total_shape_x + self.offset * 3))/2) - (box_width*len(self.matrix))/2 - (offset * (len(self.matrix)-1))/2
        pos_y = 100
        x = pos_x
        
        for c in range(0, len(self.matrix)):
            y = pos_y
            for l in range(0, len(self.matrix[c])):
                if self.is_calculate_value(l, c):
                    color = DARKGREEN
                    if self.matrix[l][c] > 0:
                        color = RED
                    elif self.matrix[l][c] < 0:
                        color = BLACK
                    text = font.render(str(self.matrix[l][c]), True, color)
                    text_rect = text.get_rect(center=(x+box_width/2, y+box_height/2))
                    display.blit(text, text_rect)
                else:
                    color = (220, 3, 3)
                    rect = (x,y,box_width,box_height)
                    shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                    pygame.draw.rect(shape, color, shape.get_rect())
                    display.blit(shape, rect)
                    color = (255,255,255,255)
                    text = font.render(str(self.matrix[l][c]), True, color)
                    text_rect = text.get_rect(center=(x+box_width/2, y+box_height/2))
                    if self.matrix[l][c] != 0:
                        display.blit(text, text_rect)
                y += box_height + offset
            x += box_width + offset

    def is_calculate_value(self, l, c):
        if (l > 0 and l < len(self.matrix) - 1) and (c > 0 and c < len(self.matrix[0]) - 1):
            return False
        return True

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

    def draw_pause(self):
        display = self.game.game_canvas
        screen_width, screen_height = self.game.GAME_WIDTH, self.game.GAME_HEIGHT
        baseline_text = screen_height - 35
        baseline_circle = screen_height - 23
                
        rect_background = (0,0,screen_width,screen_height)
        shape_surf = pygame.Surface(pygame.Rect(rect_background).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (0,0,0,230), shape_surf.get_rect())
        display.blit(shape_surf, rect_background)

        font = pygame.font.SysFont(FONT_NAME, 72, False, False)
        instruction_text = font.render('Pause', True, (220,220,220))
        instruction_text_rect = instruction_text.get_rect(center=(screen_width/2, screen_height/2))
        display.blit(instruction_text, instruction_text_rect)

        font = pygame.font.SysFont(FONT_NAME, 20, False, False)
        pygame.draw.circle(display,WHITE,(20,baseline_circle),10)
        white_text = font.render("Continuar", True, WHITE)
        display.blit(white_text, (35, baseline_text))

    def draw_timer(self):
        display = self.game.game_canvas
        timer_font = pygame.font.Font(os.path.join("fonts", "digital-7.ttf"), 40)
        screen_width = self.game.GAME_WIDTH
        time_ms = self.total_time - pygame.time.get_ticks()

        if time_ms >= 0:
            self.time_hms = ((time_ms//(1000*60*60))%24, (time_ms//(1000*60))%60, (time_ms//1000)%60)
        else:
            self.lose_life()

        timer_text = timer_font.render(f'{self.time_hms[1]:02d}:{self.time_hms[2]:02d}', True, (255, 0, 0))
        timer_text_rect = timer_text.get_rect(center=(screen_width/2, 20))
        display.blit(timer_text, timer_text_rect)
    
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
        text = font.render('Possíveis somas estudante', True, (0,0,0))
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

    def render(self, display):
        display.fill((255,255,255))
        
        self.draw_board()
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
        
        if (not self.show_teacher and not self.is_paused) or (self.show_teacher and not self.teacher.modal):
            self.draw_challenge()