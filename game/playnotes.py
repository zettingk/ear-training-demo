import asyncio
import pygame
from context import VisualNote, Context

from events import KeyEvent
from notes import note_from_str, generate_notes

import audio


BASE_NOTE = note_from_str("C")
SEQUENCE_LENGTH = 4

to_draw: list[list[VisualNote]] = []

def on_update(ctx: Context) -> None:
    surf_width, surf_height = ctx.get_surf_size()
    ctx.draw_staff(pygame.rect.Rect(surf_width * 0.1, surf_height / 2 - surf_width * 0.05, surf_width * 0.8, surf_width * 0.1), to_draw, SEQUENCE_LENGTH)

async def on_start(ctx: Context) -> None:
    global to_draw

    while True:
        to_draw = []

        note_gen = generate_notes(variability=12, base=BASE_NOTE)
        notes = [next(note_gen) for _ in range(SEQUENCE_LENGTH)]

        for note in notes:
            audio.note_on(note, 127)
            await asyncio.sleep(1)
            audio.note_off(note)

        for note in notes:
            [key_event] = await ctx.await_events(KeyEvent, 1, lambda e: e.velocity != 0)

            if key_event.key == note:
                to_draw.append([VisualNote(note, pygame.color.Color(0, 255, 0))])
            else:
                to_draw.append([
                    VisualNote(note, pygame.color.Color(255, 0, 0))
                ])
                

        await asyncio.sleep(3)

