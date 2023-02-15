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

from board.recognizer import Recognizer

class Board:

    def __init__(self, app, lines = 7, columns = 7):
        self.app = app
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
        
        self.camera = self.app.camera_board
        self.recognizer = Recognizer(self)
        
        self.matrix_centers_board = []

        self.matrix_board = []
        self.define_matrix_board()

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
        print('Alinhamento\n=============\n')
        print('Posicione o bloco 1 no canto superior ESQUERDO e o bloco 2 no canto inferior ESQUERDO')
        input('Tecle enter')
        image = self.camera.take_picture()
        positions = self.recognizer.get_positions(image, True)

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

    def define_right_limits(self):
        print('Posicione o bloco 1 no canto superior DIREITO e o bloco 2 no canto inferior DIREITO')
        input('Tecle enter')
        image = self.camera.take_picture()
        positions = self.recognizer.get_positions(image, True)

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
        image = self.camera.take_picture()
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