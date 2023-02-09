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

import cv2
import imutils
import pygame


class Webcam:

    def __init__(self, cam_number, angle_rotation):
        self.cam_number = cam_number
        self.camera = cv2.VideoCapture(cam_number)
        self.angle_rotation = angle_rotation

    
    def get_image(self, width = 320, height = 240):
        if not self.camera.isOpened():
            self.camera.open(self.cam_number)
            
        success, image = self.camera.read()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = imutils.rotate(image, self.angle_rotation)
        #image = cv2.rotate(image, cv2.ROTATE_180)
        image = imutils.resize(image, width=width)
        buffer = None
        
        if success:
            buffer = pygame.image.frombuffer(image.tostring(), image.shape[1::-1], "RGB")

        return buffer
    
    def release(self):
        self.camera.grab()
        self.camera.release()