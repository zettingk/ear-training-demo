import asyncio
import pygame

from main import Context
from notes import note_from_str, generate_notes

import audio

BASE_NOTE = note_from_str("C")
SEQUENCE_LENGTH = 3

async def foo_event():
    print('key c pressed')

async def on_start(ctx: Context) -> None:
    ctx.on_keystroke(pygame.K_c, foo_event)

    tone_gen = generate_notes(variability=12, base=BASE_NOTE)
    tones = [next(tone_gen) for _ in range(SEQUENCE_LENGTH)]

    for tone in tones:
        audio.note_on(tone, 127)
        await asyncio.sleep(1)
        audio.note_off(tone)

