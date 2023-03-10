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

import os, sys
import getopt
from game.game import Game
from pony.orm import *
from dotenv import load_dotenv
from database.connection import db
from database.models.user import User
from utils.webcam import Webcam
from board.board import Board
from board.physical_buttons import PhysicalButtons

class Application:
    
    def __init__(self):
        self.camera_student = Webcam(int(os.getenv('INDEX_CAMERA_STUDENT')), angle_rotation=180)
        self.camera_board = Webcam(int(os.getenv('INDEX_CAMERA_BOARD')), angle_rotation=270)
        
        self.game = Game(self, False)
        self.board = Board(self)
        self.physical_buttons = PhysicalButtons()

def main(argv):
    fullpath = os.path.abspath(argv[0])
    dir = os.path.dirname(fullpath)
    os.chdir(dir)

    load_dotenv(dotenv_path=os.path.join(dir, '.env'))

    db.bind(
        provider = 'mysql',
        user = os.getenv('DATABASE_USER'),
        password = os.getenv('DATABASE_PASS'),
        host = os.getenv('DATABASE_HOST'),
        database = os.getenv('DATABASE_SCHEMA')
        )

    db.generate_mapping(create_tables=True)

    create_user()

    app = Application()
    
    '''
    app.board.define_left_limits()
    app.board.define_right_limits()
    app.board.calculate_limits()
    app.board.define_centers()
    app.board.draw_matrix_board()
    
    while True:
        print('Posicione as pe??as no tabuleiro e pressione ENTER')
        input()


        app.board.avaliable_board()
        app.board.draw_matrix_board()

        print("Continuar? (S/N): ", end='')
        entrada = input()
        if (entrada.upper() == 'N'): break
    '''
    app.game.loop()

@db_session
def create_user():
    user = User(name='Robertino', nickname='Tino', age=41, gender='M')

if __name__ == '__main__':
    main(sys.argv)