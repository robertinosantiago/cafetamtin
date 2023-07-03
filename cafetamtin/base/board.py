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
from pony.orm import *

from database.models import DBBoard
from base.recognizer import Recognizer
from base.leds import Leds
from utils import message_box

from game import FONT_NAME


class Board:

    def __init__(self, app, lines = 7, columns = 7):
        self.app = app
        self.id = None
        self.top_left = ()
        self.top_right = ()
        self.bottom_left = ()
        self.bottom_right = ()
        self.lines = lines
        self.columns = columns
        self.width = 0
        self.height = 0
        self.span_cols = 0
        self.span_rows = 0
        self.block_width = 0
        self.block_height = 0
        self.configuration_mode = False
        
        self.camera = self.app.camera_board
        self.recognizer = Recognizer(self)
        self.leds = Leds()
        
        self.matrix_centers_board = []

        self.matrix_board = []
        self.load_dbboard()
        self.configure()
        self.define_matrix_board()

    @db_session
    def load_dbboard(self):
        board = DBBoard.select().order_by(desc(DBBoard.id)).first()
        if board:
            self.id = board.id
            self.columns = board.columns
            self.lines = board.lines
            self.top_left = (board.top_left_x, board.top_left_y)
            self.top_right = (board.top_right_x, board.top_right_y)
            self.bottom_left = (board.bottom_left_x, board.bottom_left_y)
            self.bottom_right = (board.bottom_right_x, board.bottom_right_y)
            self.block_width = board.block_width
            self.block_height = board.block_height
            self.width = board.width
            self.height = board.height
            self.span_cols = board.span_cols
            self.span_rows = board.span_rows
    
    @db_session
    def update_dbboard(self):
        try:
            DBBoard[self.id].set(
                top_left_x = self.top_left[0],
                top_left_y = self.top_left[1],
                top_right_x = self.top_right[0],
                top_right_y = self.top_right[1],
                bottom_left_x = self.bottom_left[0],
                bottom_left_y = self.bottom_left[1],
                bottom_right_x = self.bottom_right[0],
                bottom_right_y = self.bottom_right[1],
                block_width = self.block_width,
                block_height = self.block_height,
                width = self.width,
                height = self.height,
                span_cols = self.span_cols,
                span_rows = self.span_rows

            )
        except ObjectNotFound:
            board = DBBoard(
                top_left_x = self.top_left[0],
                top_left_y = self.top_left[1],
                top_right_x = self.top_right[0],
                top_right_y = self.top_right[1],
                bottom_left_x = self.bottom_left[0],
                bottom_left_y = self.bottom_left[1],
                bottom_right_x = self.bottom_right[0],
                bottom_right_y = self.bottom_right[1],
                block_width = self.block_width,
                block_height = self.block_height,
                width = self.width,
                height = self.height,
                span_cols = self.span_cols,
                span_rows = self.span_rows,
                lines = 7,
                columns = 7
            )
            self.load_dbboard()

    def define_matrix_board(self):
        self.matrix_board.clear()
        for i in range(self.lines):
            line = []
            for j in range(self.columns):
                line.append(0)
            self.matrix_board.append(line)

    def draw_matrix_board(self):
        print('===='*(self.columns-1))
        for i in range(self.lines):
            print('|', end='')
            for j in range(self.columns):
                print('{0:2}|'.format(self.matrix_board[i][j]),end='')
            print('')
            print('----'*(self.columns-1), end='')
            print('')

    def define_left_limits(self):
        self.configuration_mode = True
        image = self.camera.take_picture(delay=10)
        positions = self.recognizer.get_positions(image, True)

        if 'block-01' in positions and 'block-02' in positions:
            self.block_width = 0
            self.block_height = 0

            self.block_width += positions['block-01']['w'] + positions['block-02']['w']
            self.block_height += positions['block-01']['h'] + positions['block-02']['h']
            
            self.top_left = (
                positions['block-01']['x'],
                positions['block-01']['y']
            )
            self.bottom_left = (
                positions['block-02']['x'],
                positions['block-02']['y'] + positions['block-02']['h']
            )
            self.update_dbboard()
            return True
        return False

    def define_right_limits(self):
        self.configuration_mode = True
        image = self.camera.take_picture()
        positions = self.recognizer.get_positions(image, True)

        if 'block-01' in positions and 'block-02' in positions:
            self.block_width += positions['block-01']['w'] + positions['block-02']['w']
            self.block_height += positions['block-01']['h'] + positions['block-02']['h']

            self.top_right = (
                positions['block-01']['x'] + positions['block-01']['w'],
                positions['block-01']['y']
            )
            self.bottom_right = (
                positions['block-02']['x'] + positions['block-02']['w'],
                positions['block-02']['y'] + positions['block-02']['h']
            )
            self.update_dbboard()
            return True
        return False

    def is_validate_positions(self):
        #print(self.top_left)
        if not self.top_left:
            #if (not self.top_left[0]) or (not self.top_right):
            return False
        if self.top_right:
            if (not self.top_right[0]) or (not self.top_right):
                return False
        if self.bottom_left:
            if (not self.bottom_left[0]) or (not self.bottom_right):
                return False
        if self.bottom_right:
            if (not self.bottom_right[0]) or (not self.bottom_right):
                return False
        return True
    
    def configure(self, new_configuration = False):
        if self.is_validate_positions():
            if new_configuration:
                self.calculate_limits()

            self.define_centers()
            
            if new_configuration:
                self.update_dbboard()

    def calculate_limits(self):
        self.width = self.top_right[0] - self.top_left[0]
        self.height = self.bottom_left[1] - self.top_left[1]

        self.block_width = round(self.block_width/4)
        self.block_height = round(self.block_height/4)

        self.span_cols = round((self.width - (self.block_width * self.columns))/(self.columns - 1))
        self.span_rows = round((self.height - (self.block_height * self.lines))/(self.lines - 1))

    def define_centers(self):
        x = 0
        y = 0
        
        for i in range(self.lines):
            line = []
            y = round(self.top_left[1] + self.block_height/2) if i == 0 else round(y + self.span_rows + self.block_height)
            for j in range(self.columns):
                x = round(self.top_left[0] + self.block_width/2) if j == 0 else round(x + self.span_cols + self.block_width)
                line.append((x,y))
            self.matrix_centers_board.append(line)

    def block_in_board(self, block):
        line = -1
        column = -1
        for i in range(self.lines):
            for j in range(self.columns):
                center_x = self.matrix_centers_board[i][j][0]
                center_y = self.matrix_centers_board[i][j][1]

                if block[1][0] >= (center_x - self.block_width) and block[1][0] <= (center_x + self.block_width):
                    column = j
                if block[1][1] >= (center_y - self.block_height) and block[1][1] <= (center_y + self.block_height):
                    line = i

        return (line, column)

    def avaliable_board(self):
        self.define_matrix_board()
        image = self.camera.take_picture(delay = 1)
        positions = self.recognizer.get_positions(image, True)

        for key, value in positions.items():
            if key != 'board':
                block = []
                if key == 'block-01': block.append(1)
                if key == 'block-02': block.append(2)
                if key == 'block-03': block.append(3)
                if key == 'block-04': block.append(4)
                if key == 'block-05': block.append(5)
                if key == 'block-06': block.append(6)
                if key == 'block-07': block.append(7)
                if key == 'block-08': block.append(8)
                if key == 'block-09': block.append(9)

                center_x = value.get('center_x')
                center_y = value.get('center_y')
                block.append((center_x, center_y))
                pos = self.block_in_board(block)
                self.matrix_board[pos[0]][pos[1]] = block[0]

    def result_matrix_board(self):
        numbers = []
        for i in range(self.lines):
            for j in range(self.columns):
                if self.matrix_board[i][j] != 0:
                    numbers.append(self.matrix_board[i][j])
        return numbers
    
    def values_positions(self):
        result = {}
        for i in range(self.lines):
            for j in range(self.columns):
                if self.matrix_board[i][j] != 0:
                    result[self.matrix_board[i][j]] = (i+1, j+1)
        return result

        

    def draw_configure(self, display, side = 'left'):
        screen_width, screen_height = display.get_size()
        font = pygame.font.SysFont(FONT_NAME, 35, False, False)
        offset = 15
        box_width, box_height = 50, 50

        total_shape_x = box_width * self.columns + offset * (self.columns + 1)
        total_shape_y = box_height * self.lines + offset * (self.lines + 1)

        pos_x = screen_width/2 - total_shape_x / 2
        pos_y = screen_height/2 - total_shape_y / 2

        rect_shape = (pos_x,pos_y,total_shape_x,total_shape_y)
        shape = pygame.Surface(pygame.Rect(rect_shape).size, pygame.SRCALPHA)
        pygame.draw.rect(shape, (130,115,0,255), shape.get_rect())
        display.blit(shape, rect_shape)

        pos_x += offset
        pos_y += offset
        x = pos_x

        for col in range(0, self.columns):
            y = pos_y
            for lin in range(0, self.lines):
                if side == 'left' and col == 0 and (lin == 0 or lin == self.lines -1):
                    color = (180,0,0,255)
                elif side == 'right' and col == self.columns - 1 and (lin == 0 or lin == self.lines -1):
                    color = (180,0,0,255)
                else:
                    color = (255,255,255,255)
                rect = (x,y,box_width,box_height)
                shape = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                pygame.draw.rect(shape, color, shape.get_rect())
                display.blit(shape, rect)


                if (side == 'left' and col == 0 and lin == 0) or (side == 'right' and col == self.columns - 1 and lin == 0):
                    text_1 = font.render("1", True, (255,255,255))
                    text_1_rect = text_1.get_rect(center=(x+box_width/2, y+box_height/2))
                    display.blit(text_1, text_1_rect)
                
                if (col == 0 and lin == self.lines - 1) or (side == 'right' and col == self.columns - 1 and lin == self.lines - 1):
                    text_2 = font.render("2", True, (255,255,255))
                    text_2_rect = text_2.get_rect(center=(x+box_width/2, y+box_height/2))
                    display.blit(text_2, text_2_rect)

                y += box_height + offset
            x += box_width + offset

        pos_text = (20, 100)
        if side == 'right':
            pos_text = (screen_width-200, 100)

        message_box.draw_speech_bubble(display, "Posicione os blocos\n1 e 2 conforme\nexibido na imagem\n\nApós, pressionar\no botão verde", (255, 255, 255), (0, 0, 0), pos_text, 14)
