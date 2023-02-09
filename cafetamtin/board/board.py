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