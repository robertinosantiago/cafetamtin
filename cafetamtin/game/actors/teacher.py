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

# Images from https://getavataaars.com/?accessoriesType=Prescription02&avatarStyle=Circle&clotheType=BlazerSweater&eyeType=Hearts&eyebrowType=DefaultNatural&facialHairType=Blank&hairColor=BrownDark&mouthType=Smile&ref=medevel-com&skinColor=Light&topType=LongHairBob

import pygame
import os

from game import FONT_NAME

class Teacher:

    def __init__(self, display):
        self.display = display
        self.images = self.load_images()
        self.image_key = 'happy0'
        self.image = self.images[self.image_key]
        self.rect = self.image.get_rect(center = (0,0))
        self.message = None


    def load_images(self):
        return {
            'happy0': pygame.image.load(os.path.join("images", "teacher-happy0.png")),
            'happy1': pygame.image.load(os.path.join("images", "teacher-happy1.png")),
            'happy2': pygame.image.load(os.path.join("images", "teacher-happy2.png")),
            'neutral0': pygame.image.load(os.path.join("images", "teacher-neutral0.png")),
            'neutral1': pygame.image.load(os.path.join("images", "teacher-neutral1.png")),
            'heart0': pygame.image.load(os.path.join("images", "teacher-heart0.png")),
        }
    
    def set_message(self, message):
        self.message = message

    def draw_speech_bubble(self, text, text_colour, bg_colour, pos, size):
        screen_width, screen_height = self.display.get_size()
        font = pygame.font.SysFont(FONT_NAME, size, False, False)

        collection = [word.split(' ') for word in text.splitlines()]
        space = font.size(' ')[0]
        x,y = pos
        box_width, box_height = 0, 0
        words_blits = []
        pos_blits = []
        
        for lines in collection:
            bw = 0
            for words in lines:
                word_surface = font.render(words, True, text_colour)
                word_width , word_height = word_surface.get_size()
                
                
                
                if x + word_width >= screen_width:
                    x = pos[0]#self.rect[0]#pos[0]
                    y += word_height
                words_blits.append(word_surface)
                pos_blits.append((x,y))
                #self.display.blit(word_surface, (x,y))
                x += word_width + space
                bw += word_width + space
            
            
            box_height += word_height
            if bw > box_width:
                
                box_width = bw
            x = pos[0]#self.rect[0]#pos[0]
            y += word_height



        #text_surface = font.render(text, True, text_colour)
        #text_rect = text_surface.get_rect(center=pos)

        # background
        bg_rect = pygame.Rect(screen_width/2-box_width/2, pos[1], box_width, box_height)
        bg_rect.inflate_ip(10, 10)

        # Frame
        frame_rect = bg_rect.copy()
        frame_rect.inflate_ip(4, 4)

        pygame.draw.rect(self.display, text_colour, frame_rect)
        pygame.draw.rect(self.display, bg_colour, bg_rect)
        for word, p in zip(words_blits, pos_blits):
            x, y = p
            self.display.blit(word, (frame_rect[0] + 10 + x, y))
        #self.display.blit(text_surface, text_rect)

    def draw(self):
        screen_width, screen_height = self.display.get_size()
        self.rect.center = (screen_width / 2, screen_height / 2)
        
        rect_background = (0,0,screen_width,screen_height)
        shape_surf = pygame.Surface(pygame.Rect(rect_background).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (0,0,0,105), shape_surf.get_rect())
        self.display.blit(shape_surf, rect_background)

        self.display.blit(self.image, self.rect)
        self.draw_speech_bubble(self.message, (255, 255, 255), (0, 0, 0), (0, self.rect.midbottom[1]), 16)