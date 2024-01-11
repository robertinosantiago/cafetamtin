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

from pathlib import Path
from imutils import face_utils
import datetime
import imutils
import time
import dlib
import cv2, math
import numpy as np
from imutils import face_utils, rotate_bound

#Import biblioteca torch
import torch
from torch import nn
from torch.utils.data import DataLoader
from torch.utils.data.sampler import WeightedRandomSampler
from torchvision import transforms

from threading import Thread


#importa biblioteca Rede Neural Profunda
from emonet.models import EmoNet

class FacialThread(Thread):
    
    def __init__ (self, app, id = None, action = None):
        Thread.__init__(self)
        self.app = app
        self.id = id
        self.action = action
        self.expression = ''
        self.valence = None
        self.arousal = None
        self.quad = ''
        
    
    def run(self):
        expression, valence, arousal = self.app.facial.evaluate()
        self.expression = expression
        self.valence = valence
        self.arousal = arousal
        self.calculateQuad()
        self.action(self.id, self.expression, self.quad)
        
    def calculateQuad(self):
        if self.expression == 'fear' or self.expression == 'anger' or self.expression == 'disgust' or self.expression == 'contempt':
            self.quad = 'Q2'
        elif self.expression == 'sad':
            self.quad = 'Q3'
        elif self.expression == 'surprise':
            if self.valence > 0:
                self.quad = 'Q1'
            else:
                self.quad = 'Q2'
        elif self.expression == 'happy':
            if self.arousal > 0:
                self.quad = 'Q1'
            else:
                self.quad = 'Q4'
        else:
            self.quad = 'QN'
            
        if self.quad == '':
            self.quad = 'QN'
        

class Facial:
    
    def __init__(self, app):
        self.app = app
        self.camera = self.app.camera_student
        self.net = EmoNet(n_expression=8).to()
        self.state_dict = torch.load(
            str(self.__get_data_path().joinpath('affectnet', 'emonet_8.pth')),
            map_location='cpu'
        )
        self.state_dict = {k.replace('module.',''):v for k,v in self.state_dict.items()}
        self.net.load_state_dict(self.state_dict, strict=False)
        self.net.eval()
        self.transform_image = transforms.Compose([transforms.ToTensor()])
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(
            str(self.__get_data_path().joinpath('affectnet', 'shape_predictor_68_face_landmarks.dat'))
        )
        self.__expressions = {0: 'neutral', 1:'happy', 2:'sad', 3:'surprise', 4:'fear', 5:'disgust', 6:'anger', 7:'contempt', 8:'none'}
        print('init facial')

        
        
    def __get_data_path(self):
        path = Path(__file__).absolute()
        path = path.parent.parent.parent
        return path.joinpath('data')
    
    def evaluate(self):
        st = time.time()
        expression = ''
        valence = None
        arousal = None
        
        image = self.camera.take_picture(delay = 6, width=412, process=False)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rects = self.detector(gray, 0)

        # loop sobre detecção de faces
        for rect in rects:
            shape = self.predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            x,y, w, h = rect.left(), rect.top(), rect.width(), rect.height()
            if y>0 and x>0:
                crop_img = image[y:y+h, x:x+w]
                dim = (256, 256)
                
                resized = cv2.resize(crop_img, dim)
                
                image_cropada = self.transform_image(resized)
                image_cropada = image_cropada.unsqueeze(0)
                
                with torch.no_grad():
                    out = self.net(image_cropada)

                expr = out['expression']
                expr = np.argmax(np.squeeze(expr.cpu().numpy()), axis=0)
                
                val = out['valence']
                ar = out['arousal']

                val = np.squeeze(val.cpu().numpy())
                ar = np.squeeze(ar.cpu().numpy())

                expression = self.__expressions.get(int(expr))
                valence = val
                arousal = ar
                
                print("expression = ", expression)
                print("valencia = ", valence)
                print("arousal = ", arousal)
        
        et = time.time()
        elapsed_time = et - st
        print('Execution time:', elapsed_time, 'seconds')
        
        return expression, valence, arousal
                