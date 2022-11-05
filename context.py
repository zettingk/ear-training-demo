import asyncio
import pygame
from typing import Type, TypeVar, Callable
from events import Event

prev_id = 0

async def foo():
    return 1

def generate_id():
    global prev_id
    prev_id += 1

    return prev_id

pygame.font.init()
FONT = pygame.font.SysFont("Arial", 64)

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

    def draw_text(self, text: str, position: tuple[int, int], color=(0, 0, 0)):
        rendered_text = FONT.render(text, True, color)
        self.draw_surface(rendered_text, position)

    def draw_surface(self, surf: pygame.surface.Surface, position: tuple[int, int]):
        self.surface.blit(surf, position)

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
                

    T = TypeVar("T")
    async def await_events(self, eventType: Type[T], amount: int, event_filter: Callable[[T], bool] = lambda _: True) -> list[T]:
        queue = asyncio.Queue(amount)

        self.await_queues.append((eventType, event_filter, queue))

        results = []

        for _ in range(amount):
            results.append(await queue.get())

        self.await_queues.remove((eventType, event_filter, queue))
        
        return results
