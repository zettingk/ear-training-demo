import asyncio

from main import Context
from events import KeyEvent
from notes import note_from_str, generate_notes, format_note_as_str

import audio


BASE_NOTE = note_from_str("C")
SEQUENCE_LENGTH = 2

notes: list[int] = []
notes_played: list[int] = []

def on_update(ctx: Context) -> None:
    height, width = ctx.surface.get_size()
    height_to_draw = height // 2 - 200
    margin = 50

    n_notes = len(notes)

    note_x_offset = (width - margin * 2) // (n_notes - 1)

    for i, (note, note_played) in enumerate(zip(notes, notes_played)):
        if note == note_played:
            color = (0, 255, 0)
        else:
            color = (0, 0, 0)
            ctx.draw_text(format_note_as_str(note_played, ascii=True), (margin + note_x_offset * i, height_to_draw - 100), (255, 0, 0))

        ctx.draw_text(format_note_as_str(note, ascii=True), (margin + note_x_offset * i, height_to_draw), color)

async def on_start(ctx: Context) -> None:
    global notes
    global notes_played

    print(f"Play the keys you hear!")

    while True:
        notes_played = []

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

            notes_played.append(key_event.key)
        
        print(f"{correct}/{SEQUENCE_LENGTH}. Next round...")

        await asyncio.sleep(1)

