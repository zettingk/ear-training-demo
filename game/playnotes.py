import asyncio
import pygame
from context import VisualNote, Context

from events import KeyEvent
from notes import note_from_str, generate_notes
from context import TREBLE_CLEFF

import audio


BASE_NOTE = note_from_str("C")
SEQUENCE_LENGTH = 4

to_draw: list[VisualNote] = []

def on_update(ctx: Context) -> None:
    surf_width, surf_height = ctx.brush.surface.get_size()
    staff_rect = pygame.rect.Rect(surf_width * 0.1, surf_height / 2 - surf_width * 0.05, surf_width * 0.8, surf_width * 0.1)

    ctx.brush.draw_staff(TREBLE_CLEFF, 30, staff_rect, to_draw)

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

        for i, note in enumerate(notes):
            [key_event] = await ctx.await_events(KeyEvent, 1, lambda e: e.pressing)
            offset = i * (1 / (len(notes) - 1))

            if key_event.key == note:
                to_draw.append(VisualNote(note, pygame.color.Color(0, 255, 0), offset))
            else:
                to_draw.append(VisualNote(note, pygame.color.Color(255, 0, 0), offset))

        await asyncio.sleep(3)

