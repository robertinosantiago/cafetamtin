import pygame
from game import FONT_NAME

def draw_speech_bubble(display, text, text_colour, bg_colour, pos, size):
        screen_width, screen_height = display.get_size()
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
                    x = pos[0]
                    y += word_height
                words_blits.append(word_surface)
                pos_blits.append((x,y))
                
                x += word_width + space
                bw += word_width + space
            
            
            box_height += word_height
            if bw > box_width:
                
                box_width = bw
            x = pos[0]
            y += word_height

        bg_rect = pygame.Rect(pos[0], pos[1], box_width, box_height)
        bg_rect.inflate_ip(10, 10)

        frame_rect = bg_rect.copy()
        frame_rect.inflate_ip(4, 4)

        pygame.draw.rect(display, text_colour, frame_rect)
        pygame.draw.rect(display, bg_colour, bg_rect)
        
        for word, p in zip(words_blits, pos_blits):
            x, y = p
            display.blit(word, (x, y))