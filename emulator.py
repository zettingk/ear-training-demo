import pygame
from math import ceil, floor
from pygame import Rect

class KeyboardEmulator:
    def __init__(self, surf):
        self.surface = surf
        self.keys_pressed = set([0, 2, 4, 5, 6, 9, 10])
        self.width_factor = 0.75

    def get_rect(self):
        surf_width, surf_height = self.surface.get_size()

        keyboard_width = surf_width * self.width_factor
        keyboard_height = surf_height * self.width_factor / 7.5
        keyboard_x = surf_width * 0.5 - keyboard_width * 0.5
        keyboard_y = surf_height - keyboard_height

        return Rect(keyboard_x, keyboard_y, keyboard_width, keyboard_height)

    def draw_outline(self, keyboard_rect: Rect):
        keyboard_x, keyboard_y, keyboard_width, keyboard_height = keyboard_rect
        pygame.draw.line(self.surface, (0, 0, 0), (keyboard_x, keyboard_y), (keyboard_x + keyboard_width, keyboard_y))
        pygame.draw.line(self.surface, (0, 0, 0), (keyboard_x + keyboard_width, keyboard_y), (keyboard_x + keyboard_width, keyboard_y + keyboard_height))
        pygame.draw.line(self.surface, (0, 0, 0), (keyboard_x + keyboard_width, keyboard_y + keyboard_height), (keyboard_x, keyboard_y + keyboard_height))
        pygame.draw.line(self.surface, (0, 0, 0), (keyboard_x, keyboard_y + keyboard_height), (keyboard_x, keyboard_y))
    
    def white_to_midi(self, white_n: int) -> int:
        octave = white_n // 7
        midi = 12 * octave

        rest = white_n % 7

        midi += ({
            0: 0,
            1: 2,
            2: 4,
            3: 5,
            4: 7,
            5: 9,
            6: 11,
        })[rest]


        return midi

    def draw_keys(self, keyboard_rect: Rect):
        keyboard_x, keyboard_y, keyboard_width, keyboard_height = keyboard_rect

        n_keys = 52
        key_width = keyboard_width / n_keys

        for i in range(n_keys):
            key_pos = keyboard_x + key_width * i

            if self.white_to_midi(i) in self.keys_pressed:
                next_key_pos = keyboard_x + key_width * (i + 1)
                current_key_width = ceil(next_key_pos - key_pos)
                
                pygame.draw.rect(self.surface, (180, 180, 180), Rect(key_pos, keyboard_y, current_key_width, keyboard_height))

            if i % 7 not in [0, 3]:
                color = (0, 0, 0)

                if self.white_to_midi(i) - 1 in self.keys_pressed:
                    color = (70, 70, 70)

                black_key_pos = key_pos - key_width * 0.75 / 2
                pygame.draw.rect(self.surface, color, Rect(black_key_pos, keyboard_y, key_width * 0.75, keyboard_height / 2))
    
    def draw_key_outlines(self, keyboard_rect: Rect):
        keyboard_x, keyboard_y, keyboard_width, keyboard_height = keyboard_rect

        n_keys = 52

        key_width = keyboard_width / n_keys

        for i in range(n_keys + 1):
            outline_x = keyboard_x + key_width * i
            outline_y = keyboard_y

            if i % 7  not in [0, 3]:
                outline_y += keyboard_height / 2

            pygame.draw.line(self.surface, (0, 0, 0), (outline_x, outline_y), (outline_x, keyboard_y + keyboard_height))


    def draw(self):
        keyboard_rect = self.get_rect()

        pygame.draw.rect(self.surface, (240, 240, 240), keyboard_rect)
        self.draw_keys(keyboard_rect)
        self.draw_outline(keyboard_rect)
        self.draw_key_outlines(keyboard_rect)
    
    def key_at_pos(self, pos) -> int | None:
        keyboard_rect = self.get_rect()
        keyboard_x, keyboard_y, keyboard_width, keyboard_height = keyboard_rect

        n_keys = 52

        pos_x, pos_y = pos
        relative_x = pos_x - keyboard_x
        relative_y = pos_y - keyboard_y

        key_width = keyboard_width / n_keys

        key_num = floor(relative_x / key_width)

        if key_num > 52 or key_num < 0 or relative_y > keyboard_height or relative_y < 0:
            return None
        
        if key_num % 7 not in [2, 6]:
            if relative_x / key_width % 1 >= 0.625 and relative_y <= keyboard_height / 2:
                return self.white_to_midi(key_num) + 1
        if key_num % 7 not in [0, 3]:
            if relative_x / key_width % 1 <= 0.375 and relative_y <= keyboard_height / 2:
                return self.white_to_midi(key_num) - 1

        return self.white_to_midi(key_num)



