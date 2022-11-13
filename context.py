import asyncio
from dataclasses import dataclass
from functools import cache
from math import ceil
import pygame
from typing import Type, TypeVar, Callable
from events import Event
from notes import chromatic_to_diatonic

prev_id = 0

async def foo():
    return 1

def generate_id():
    global prev_id
    prev_id += 1

    return prev_id


T = TypeVar('T')
def _queue_to_list(q: asyncio.Queue[T]) -> list[T]:
    result = []

    try:
        while True:
            result.append(q.get_nowait())
    except asyncio.QueueEmpty:
        return result

pygame.font.init()

@cache
def get_font(fontname: str, size: int, bold: bool, italic: bool):
    return pygame.font.SysFont(fontname, size, bold, italic)


treble_cleff = pygame.image.load("images/treble_cleff.png")
sharp_img = pygame.image.load("images/sharp.png")

@dataclass
class VisualNote:
    note: int
    color: pygame.color.Color

class Context:
    '''
    Instances of Context are passed down to the start function of game modules.
    A Context instance can register event handlers and callbacks that the engine then
    invokes.

    The difference between an event handler and a callback is that callbacks are
    only invoked once when a given event occurs, while event_handlers can be invoked
    many times.
    '''

    def __init__(self, surface: pygame.surface.Surface):
        self.surface = surface
        self.callbacks = []
        self.event_handlers = []
        self.await_queues = []
        self.gather_queues = []

    def get_surf_size(self) -> tuple[int, int]:
        return self.surface.get_size()

    def draw_text(self, fontname: str, size: int, text: str, position: tuple[int, int], color, bold: bool = False, italic: bool = False, antialias: bool = True):
        rendered_text = get_font(fontname, size, bold, italic).render(text, antialias, color)
        self.draw_surface(rendered_text, position)

    def draw_surface(self, surf: pygame.surface.Surface, position: tuple[int, int]):
        self.surface.blit(surf, position)

    def draw_staff(self, rect: pygame.rect.Rect, notes: list[list[VisualNote]], fit_notes: int):
        x, y, width, height = rect
        line_thickness = ceil(height / 40)

        y_offset = height / 4

        for i in range(5):
            pygame.draw.line(self.surface, (0, 0, 0), (x, y + y_offset * i), (x + width, y + y_offset * i), line_thickness)

        clef_width = height * 0.5
        clef_height = height * 1.3
        self.surface.blit(pygame.transform.scale(treble_cleff, (clef_width, clef_height)), (x, y))

        x_start = x + clef_width * 1.5
        x_end = x + width

        x_offset = (x_end - x_start) / (fit_notes)
        
        for i, chord in enumerate(notes):
            for note in chord:
                diatonic, sharp = chromatic_to_diatonic(note.note)
                note_y = y + int(y_offset / 2 * -(diatonic - 37))
                note_x = int(x_start + x_offset * i)
                note_width = int(height * 0.35)
                note_height = int(height * 0.25)

                if sharp:
                    self.surface.blit(pygame.transform.scale(sharp_img, (int(note_height * 0.75), note_height * 1.5)), (note_x + note_width, note_y - note_height * 0.25))
            
                if diatonic < 29:
                    n_lines = (30 - diatonic) // 2

                    initial_line = y + int(y_offset / 2 * 9) + note_height / 2

                    for i in range(n_lines):
                        pygame.draw.line(self.surface, (0, 0, 0), (note_x - note_width * 0.2, initial_line + y_offset * i), (note_x + note_width * 1.2, initial_line + y_offset * i), line_thickness)

                elif diatonic > 39:
                    n_lines = (diatonic - 38) // 2

                    initial_line = y - int(y_offset / 2 * 3) + note_height / 2

                    for i in range(n_lines):
                        pygame.draw.line(self.surface, (0, 0, 0), (note_x - note_width * 0.2, initial_line - y_offset * i), (note_x + note_width * 1.2, initial_line - y_offset * i), line_thickness)

                pygame.draw.ellipse(self.surface, note.color, (note_x, note_y, note_width, note_height))

    def cancel(self, handler_id: int) -> None:
        '''
        cancel removes an event handler with the given id from the event handler list,
        effectively preventing future invokations of the event handler.
        '''
        self.event_handlers = list(filter(lambda h: h[0] != handler_id, self.event_handlers))

    def register_event_handler(self, eventType: Type[Event], coro) -> None:
        '''
        register_event_handler registers an event handler coroutine function into the
        event handler list. This coroutine will be invoked when the given event or
        a subclass thereof occurs.
        '''
        handler_id = generate_id()
        
        self.event_handlers.append((handler_id, eventType, coro))

    def register_callback(self, eventType: Type[Event], coro) -> None:
        '''
        register_callback registers a callback coroutine function into the
        callback list. This coroutine will be invoked once when the given event or
        a subclass thereof occurs.
        '''
        self.callbacks.append((eventType, coro))

    def fire_events(self, event: Event) -> None:
        '''
        fire_events invokes event handlers and callbacks taking the given event
        type or a superclass thereof. It also removes invoked callbacks from the
        callback list. Additionally, fire_events adds awaited events to their
        rightful queues.

        Note that this function is meant to be called from the engine only.
        '''
        remaining_callbacks = []
        for eventType, coro in self.callbacks:
            if isinstance(event, eventType):
                asyncio.create_task(coro(event))
            else:
                remaining_callbacks.append((eventType, coro))

        self.callbacks = remaining_callbacks

        for _, eventType, coro in self.event_handlers:
            if isinstance(event, eventType):
                asyncio.create_task(coro(event))

        for eventType, event_filter, queue in self.await_queues:
            if isinstance(event, eventType) and event_filter(event):
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    pass

        for _, eventType, event_filter, queue in self.gather_queues:
            if isinstance(event, eventType) and event_filter(event):
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    pass
                
    Y = TypeVar("Y")
    def begin_gather(self, eventType: Type[Y], max_amount: int = 0, event_filter: Callable[[Y], bool] = lambda _: True) -> int:
        queue = asyncio.Queue(max_amount)
        queue_id = generate_id()
        self.gather_queues.append((queue_id, eventType, event_filter, queue))
        
        return queue_id

    def end_gather(self, queue_id: int) -> list[Event]: # type: ignore
        result_tup = None
        result = None

        for tup in self.gather_queues:
            current_id, _, _, queue = tup
            if current_id == queue_id:
                result = _queue_to_list(queue)
                result_tup = tup

        if result_tup is None or result is None:
            raise ValueError
        
        self.gather_queues.remove(result_tup)

        return result


    T = TypeVar("T")
    async def await_events(self, eventType: Type[T], amount: int, event_filter: Callable[[T], bool] = lambda _: True) -> list[T]:
        queue = asyncio.Queue(amount)

        self.await_queues.append((eventType, event_filter, queue))

        results = []

        for _ in range(amount):
            results.append(await queue.get())

        self.await_queues.remove((eventType, event_filter, queue))
        
        return results
