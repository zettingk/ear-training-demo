import asyncio
from random import randint
from typing import Generator
from mingus.containers import Note
import pygame.midi

from audio import note_on, note_off

BASE_NOTE = Note("C")
SEQUENCE_LENGTH = 3


def generate_notes(*, variability: int, base: Note) -> Generator[Note, None, None]:
    current_base = base

    while True:
        increment_by = randint(-variability, variability)
        new_note = Note().from_int(int(current_base) + increment_by)

        current_base = new_note
        yield new_note


async def on_start(midi_output: pygame.midi.Output) -> None:
    note_gen = generate_notes(variability=12, base=BASE_NOTE)
    notes = [next(note_gen) for _ in range(SEQUENCE_LENGTH)]

    for note in notes:
        note_on(midi_output, note)
        await asyncio.sleep(1)
        note_off(midi_output, note)
