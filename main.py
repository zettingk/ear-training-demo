import sys
import audio
from context import Context
import asyncio
import pygame
import pygame.midi
from events import KeyEvent, KeystrokeEvent
from emulator import KeyboardEmulator
from game_loader import Game

pygame.init()
pygame.display.init()
pygame.midi.init()


BACKGROUND_COLOR = (255, 255, 255)


def is_mouse_pressed() -> bool:
    return pygame.mouse.get_pressed()[0]


async def main() -> None:
    game = Game('game1')

    window = pygame.display.set_mode((800, 600))

    ctx = Context(window)
    game.begin(ctx)

    midi_input_id = pygame.midi.get_default_input_id()
    midi_input = None    
    keyboard_emulator = None

    if midi_input_id == -1:
        keyboard_emulator = KeyboardEmulator(window)
    else: 
        midi_input = pygame.midi.Input(midi_input_id)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                ctx.fire_events(KeystrokeEvent(event.key, True))

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            elif event.type == pygame.KEYUP:
                ctx.fire_events(KeystrokeEvent(event.key, False))

        window.fill(BACKGROUND_COLOR)
        game.update(ctx)
    
        if midi_input is not None:
            while midi_input.poll():
                events = midi_input.read(10)

                for evt in events:
                    [[_, note_num, velocity, _], _] = evt # type: ignore
                    
                    ctx.fire_events(KeyEvent(note_num, velocity))
        elif keyboard_emulator is not None:
            if is_mouse_pressed():
                hovering_over = keyboard_emulator.key_at_pos(pygame.mouse.get_pos())

                if hovering_over is not None and hovering_over not in keyboard_emulator.keys_pressed:
                    ctx.fire_events(KeyEvent(hovering_over, 127))
                    audio.note_on(hovering_over, 127)

                    keyboard_emulator.keys_pressed.add(hovering_over)
            else:
                for k in keyboard_emulator.keys_pressed:
                    ctx.fire_events(KeyEvent(k, 0))
                    audio.note_off(k)
                
                keyboard_emulator.keys_pressed = set()
            keyboard_emulator.draw()


        pygame.display.update()
        await asyncio.sleep(0) # allow game coroutines to run


if __name__ == "__main__":
    asyncio.run(main())

