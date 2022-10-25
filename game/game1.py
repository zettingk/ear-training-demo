import asyncio

from main import Context
from events import KeyEvent
from notes import note_from_str, generate_notes, format_note_as_str

import audio

BASE_NOTE = note_from_str("C")
SEQUENCE_LENGTH = 3

async def play_note(evt: KeyEvent):
    if evt.velocity != 0:
        audio.note_on(evt.key, evt.velocity)
    else:
        audio.note_off(evt.key)

async def on_start(ctx: Context) -> None:
    ctx.register_event_handler(KeyEvent, play_note)
    print(f"Play the keys you hear!")

    while True:
        note_gen = generate_notes(variability=12, base=BASE_NOTE)
        notes = [next(note_gen) for _ in range(SEQUENCE_LENGTH)]

        for note in notes:
            audio.note_on(note, 127)
            await asyncio.sleep(1)
            audio.note_off(note)

        correct = 0
        for note in notes:
            [key_event] = await ctx.await_events(KeyEvent, 1, lambda e: e.velocity != 0)
            if key_event.key == note:
                print(f"\tCorrect! ({format_note_as_str(note, ascii=True)})")
                correct += 1
            else:
                print(f"\tWrong. Correct answer: {format_note_as_str(note, ascii=True)}. Played: {format_note_as_str(key_event.key, ascii=True)}")
        
        print(f"{correct}/{SEQUENCE_LENGTH}. Next round...")

        await asyncio.sleep(1)


