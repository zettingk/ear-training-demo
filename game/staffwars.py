import asyncio
import random
import pygame
from context import VisualNote, Context, TREBLE_CLEFF
from events import KeyEvent

NOTE_TRAVEL_TIME = 8
NOTE_SPAWN_RATE = 4

to_draw: list[tuple[int, float]] = []
clock = pygame.time.Clock()

async def on_key_press(evt: KeyEvent):
    if evt.velocity == 0: return
    if len(to_draw) == 0: return

    if to_draw[0][0] == evt.key:
        to_draw.pop(0)



def on_update(ctx: Context) -> None:
    global to_draw

    surf_width, surf_height = ctx.brush.surface.get_size()
    staff_rect = pygame.rect.Rect(surf_width * 0.1, surf_height / 2 - surf_width * 0.05, surf_width * 0.8, surf_width * 0.1)

    dt = clock.tick()

    visual_notes = []

    new_to_draw = []
    for note, offset in to_draw:
        if offset < 0:
            continue
        
        new_to_draw.append((note, offset - dt / 1000 / NOTE_TRAVEL_TIME))
        visual_notes.append(VisualNote(note, pygame.color.Color(0, 0, 0), offset=offset))

    to_draw = new_to_draw

    ctx.brush.draw_staff(TREBLE_CLEFF, 30, staff_rect, visual_notes)

async def on_start(ctx: Context) -> None:
    ctx.register_event_handler(KeyEvent, on_key_press)

    while True:
        to_draw.append((random.randint(48, 69), 1))
        await asyncio.sleep(NOTE_SPAWN_RATE)

