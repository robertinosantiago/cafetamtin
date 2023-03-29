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
import pygame

class Confetti:

    def __init__(self):
        self.visible = False
        self.width = 512
        self.height = 512
        self.sheet = pygame.image.load(os.path.join("images", "confetti.png")).convert_alpha()
        self.total_frames = 64

    def get_image(self, frame, scale = 1, colour = (0, 0, 0)):
        n = frame - 1
        line = n // 8
        column = n % 8
        image = pygame.Surface((self.width, self.height)).convert_alpha()
        image.blit(self.sheet, (0,0), (column*self.width, line*self.height,self.width,self.height))
        image = pygame.transform.scale(image, (self.width * scale, self.height * scale))
        image.set_colorkey(colour)
        return image


    

