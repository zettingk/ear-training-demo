import sys
import pygame
import pygame.midi
from mingus.containers import Note

import audio


pygame.init()
pygame.display.init()
pygame.midi.init()


INSTRUMENT = 1
BG_COLOR = (255, 255, 255)


def main():
    midi_port = pygame.midi.get_default_output_id()
    midi_output = pygame.midi.Output(midi_port)
    midi_output.set_instrument(INSTRUMENT)
    window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_c:
                    audio.note_on(midi_output, Note("C"))

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_c:
                    audio.note_off(midi_output, Note("C"))

        window.fill(BG_COLOR)
        pygame.display.update()


if __name__ == "__main__":
    main()
