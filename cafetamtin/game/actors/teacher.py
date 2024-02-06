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
import queue

from game import FONT_NAME

class Teacher:

    def __init__(self, display):
        self.display = display
        self.images = self.load_images()
        self.image_key = 'happy0'
        self.image = self.images[self.image_key]
        self.rect = self.image.get_rect(center = (0,0))
        self.message = None
        self.modal = True
        self.position = None
        self.image_explication = False
        self.max_words = 10
        self.messages = queue.Queue()


    def load_images(self):
        return {
            'happy0': pygame.image.load(os.path.join("images", "teacher-happy0.png")),
            'happy1': pygame.image.load(os.path.join("images", "teacher-happy1.png")),
            'happy2': pygame.image.load(os.path.join("images", "teacher-happy2.png")),
            'happy3': pygame.image.load(os.path.join("images", "teacher-happy3.png")),
            'happy4': pygame.image.load(os.path.join("images", "teacher-happy4.png")),
            'neutral0': pygame.image.load(os.path.join("images", "teacher-neutral0.png")),
            'neutral1': pygame.image.load(os.path.join("images", "teacher-neutral1.png")),
            'neutral2': pygame.image.load(os.path.join("images", "teacher-neutral2.png")),
            'heart0': pygame.image.load(os.path.join("images", "teacher-heart0.png")),
        }
    
    def set_message(self, message, image_key = 'happy0', image_explication = False, modal = True, position = None, max_words = 10):
        data = {
            'image_key': image_key,
            'message': message,
            'modal': modal,
            'position': position,
            'image_explication': image_explication,
            'max_words': max_words
        }
        self.messages.put(data)

    def next_message(self):
        data = self.messages.get()
        self.image_key = data['image_key']
        self.message = data['message']
        self.modal = data['modal']
        self.position = data['position']
        self.image_explication = data['image_explication']
        self.max_words = data['max_words']

    def has_next_message(self):
        return not self.messages.empty()
    
    def clear_messages(self):
        self.messages = queue.Queue()

    def draw_speech_bubble(self, text, text_colour, bg_colour, pos, size, max_words = 10):
        font = pygame.font.SysFont(FONT_NAME, size, False, False)
        collection = [word.split(' ') for word in text.splitlines()]
        lines = []
        
        for words in collection:
            t = ''
            words_count = 0    
            for i in range(len(words)):
                t += words[i]
                words_count += 1
                if i < len(words)-1 and words_count < max_words:
                    t += ' '
                if i >= len(words)-1 or words_count >= max_words:
                    words_count = 0
                    lines.append(t)
                    t = ''
        
        max_width = 0
        max_height = 0
        max_word_height = 0
        for line in lines:
            word_surface = font.render(line, True, text_colour)
            word_width , word_height = word_surface.get_size()
            max_word_height = max(word_height, max_word_height)
            max_width = max(word_width, max_width)
        max_height = len(lines) * max_word_height
        
        
        bg_rect = pygame.Rect(pos[0]+pos[2]//2-max_width//2, pos[1]+pos[3], max_width, max_height)
        bg_rect.inflate_ip(10, 10)

        frame_rect = bg_rect.copy()
        frame_rect.inflate_ip(4, 4)

        pygame.draw.rect(self.display, text_colour, frame_rect)
        pygame.draw.rect(self.display, bg_colour, bg_rect)
        
        for i in range(0, len(lines)):
            word_surface = font.render(lines[i], True, text_colour)
            word_width , word_height = word_surface.get_size()
            self.display.blit(word_surface, (pos[0]+pos[2]//2-word_width//2, pos[1] + pos[3] + i * max_word_height))

    def draw(self):
        screen_width, screen_height = self.display.get_size()
        
        pos = (screen_width / 2, screen_height / 2)
        if self.position:
            pos = self.position
        
        self.rect = pygame.Surface.get_rect(self.images[self.image_key], center=pos)
        
        rect_background = (0,0,screen_width,screen_height-46)
        shape_surf = pygame.Surface(pygame.Rect(rect_background).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (0,0,0,105), shape_surf.get_rect())
        if self.modal:
            self.display.blit(shape_surf, rect_background)

        self.display.blit(self.images[self.image_key], self.rect)
        self.draw_speech_bubble(
            text = self.message, 
            text_colour = (255, 255, 255), 
            bg_colour = (0, 0, 0), 
            pos = self.rect, 
            size = 16,
            max_words=self.max_words
            )
        
        if (self.image_explication != False):
            image_explication = pygame.image.load(os.path.join("images", self.image_explication))
            image_explication_rect = image_explication.get_rect(center=(screen_width/2, screen_height/2 - 170))
            self.display.blit(image_explication, image_explication_rect)