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

import time
import board
import neopixel
from threading import Thread

class RainbowThread(Thread):
    
    def __init__ (self):
        Thread.__init__(self)
        self.leds = Leds()
    
    def run(self):
        self.leds.rainbow_cycle()

class Leds:
    
    def __init__(self):
        self.__data_pin = board.D10
        self.__num_pixels = 49
        self.__pixel_order = neopixel.GRB
        self.__turned_on = False
        self.__first_execute = True

        self.strip = neopixel.NeoPixel(
            self.__data_pin, 
            self.__num_pixels, 
            brightness=0.5, 
            auto_write=False,
            pixel_order=self.__pixel_order
        )

    def turnOff(self):
        color = (0, 0, 0)
        self.strip.fill(color)
        self.strip.show()

    def turnOn(self, color, leds):
        self.strip.fill((0,0,0))
        for i in leds:
            self.strip[i] = color
        self.strip.show()
        
            
    def matrix3x3(self):
        leds = [16,17,18,23,24,25,30,31,32]
        color = (0,255,0)
        self.turnOn(color, leds)
        
    def central_led(self):
        leds = [24]
        color = (0,255,0)
        self.turnOn(color, leds)
        
    def configureLeftSide(self):
        leds = [0, 42]
        color = (0,255,0)
        self.turnOn(color, leds)
    
    def configureRightSide(self):
        leds = [6, 48]
        color = (0,255,0)
        self.turnOn(color, leds)
    
    def rainbow_cycle(self, wait = 0.001):
        for j in range(255):
            for i in range(self.__num_pixels):
                pixel_index = (i * 256 // self.__num_pixels) + j
                self.strip[i] = self.wheel(pixel_index & 255)
            self.strip.show()
        self.turnOff()
            
    def wheel(self, pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return (r, g, b) if self.__pixel_order in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)
