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
#from gpiozero import Button

import sys
import time
from telemetrix import telemetrix

class Button:
    
    def __init__(self, board, pin, callback = None):
        self.board = board
        self.pin = pin
        self.callback = callback
        self.board.set_pin_mode_digital_input_pullup(pin, self.when_pressed)
        self.__time_start = 0
        
    def __execute_callback(self, data):
        self.callback(data)
        
    
    def when_pressed(self, data):
        if data[2] == 1:
            self.__time_start = data[3]
        if data[2] == 0:
            time_total = data[3] - self.__time_start
            if time_total > 0.01:
                self.__execute_callback(data)
                
            
    def set_callback(self, callback):
        self.callback = callback

class PhysicalButtons:

    def __init__(self):
        self.arduino_board = telemetrix.Telemetrix()
        self.green_button = Button(self.arduino_board, int(os.getenv('PIN_BUTTON_GREEN')))
        self.red_button = Button(self.arduino_board, int(os.getenv('PIN_BUTTON_RED')))
        self.black_button = Button(self.arduino_board, int(os.getenv('PIN_BUTTON_BLACK')))
        self.white_button = Button(self.arduino_board, int(os.getenv('PIN_BUTTON_WHITE')))