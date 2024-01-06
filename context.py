import asyncio
from dataclasses import dataclass
from functools import cache
from math import ceil
import pygame
from typing import Type, TypeVar, Callable, Iterable
from events import Event
from notes import chromatic_to_diatonic



prev_id = 0
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


@dataclass
class VisualNote:
    note: int
    color: pygame.color.Color
    offset: float | None = None


@dataclass
class Clef:
    g_position: int
    lines: int
    symbol: pygame.surface.Surface
    poke_out_point: int
    dip_point: int


TREBLE_CLEFF = Clef(
    g_position=2,
    lines=5,
    symbol=pygame.image.load('images/treble_cleff.png'),
    poke_out_point=110,
    dip_point=432
)


sharp_img = pygame.image.load("images/sharp.png")


def _interpolate(val: float, from_low: float, from_high: float, to_low: float, to_high: float):
    return (val - from_low) / (from_high - from_low) * (to_high - to_low) + to_low


@dataclass
class Brush:
    surface: pygame.surface.Surface

    def draw_text(self, fontname: str, size: int, text: str, position: tuple[int, int], color, bold: bool = False, italic: bool = False, antialias: bool = True):
        rendered_text = get_font(fontname, size, bold, italic).render(text, antialias, color)
        self.surface.blit(rendered_text, position)

    def _draw_horizontal_lines(self, y_start: int, line_offset: int, n_lines: int, x_start: int, x_end: int, thickness: int):
        for i in range(n_lines):
            y = y_start + line_offset * i
            pygame.draw.line(self.surface, (0, 0, 0), (x_start, y), (x_end, y), thickness)

    def draw_staff(self, clef: Clef, line_offset: int, rect: pygame.rect.Rect, notes: Iterable[VisualNote]):
        x, y, width, height = rect
        line_thickness = ceil(line_offset * 0.05)

        y_start = int(y + 0.5 * (height - (clef.lines - 1) * line_offset)) # (n - 1) spaces for n lines

        self._draw_horizontal_lines(y_start, line_offset, clef.lines, x, x + width, line_thickness)

        y_end = y_start + line_offset * (clef.lines - 1)

        clef_width, clef_height = clef.symbol.get_size()

        clef_start = _interpolate(0, clef.poke_out_point, clef.dip_point, y_start, y_end)
        clef_end = _interpolate(clef_height, clef.poke_out_point, clef.dip_point, y_start, y_end)

        new_height = clef_end - clef_start
        new_width = new_height * (clef_width / clef_height)

        scaled_clef = pygame.transform.scale(clef.symbol, (new_width, new_height))

        note_width = line_offset * 1.25

        extra_line_jut_out = 0.2

        remaining_x_start = x + new_width
        remaining_width = x + width - remaining_x_start - note_width * (1 + extra_line_jut_out) - note_width * extra_line_jut_out

        sharp_symbol = pygame.transform.scale(sharp_img, (int(line_offset * 0.75), line_offset * 1.5))

        for n in notes:
            if n.offset is not None:
                diatonic, sharp = chromatic_to_diatonic(n.note)
                where_32 = clef.g_position
                where_note = where_32 + (diatonic - 32)

                note_x = extra_line_jut_out * note_width + remaining_x_start + int(n.offset * remaining_width)
                note_y = y_end - (line_offset / 2) * (where_note + 1)

                note_rect = pygame.rect.Rect(note_x, note_y, note_width, line_offset)

                line_start_x = int(note_x - note_width * extra_line_jut_out)
                line_end_x = int(note_x + note_width * (1 + extra_line_jut_out))

                if where_note <= -2:
                    # draw extra lines under staff
                    n_extra_lines = -where_note // 2
                    first_line = y_end + line_offset
                    self._draw_horizontal_lines(first_line, line_offset, n_extra_lines, line_start_x, line_end_x, line_thickness)
                elif where_note >= clef.lines * 2:
                    # draw extra lines over staff
                    n_extra_lines = (where_note - (clef.lines - 1) * 2) // 2
                    first_line = y_start - line_offset
                    self._draw_horizontal_lines(first_line, -line_offset, n_extra_lines, line_start_x, line_end_x, line_thickness)

                if sharp == True:
                    self.surface.blit(sharp_symbol, (note_x + note_width, note_y - line_offset * 0.25))

                pygame.draw.ellipse(self.surface, n.color, note_rect)

        self.surface.blit(scaled_clef, (x, clef_start))


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
        self.callbacks = []
        self.event_handlers = []
        self.await_queues = []
        self.gather_queues = []
        self.brush = Brush(surface)

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

