import sys
import asyncio
from typing import Callable
from collections.abc import Awaitable
import pygame
import pygame.midi

from game import game1

pygame.init()
pygame.display.init()
pygame.midi.init()


BG_COLOR = (255, 255, 255)

class Context:
    def __init__(self):
        self.key_events = {}

    def on_keystroke(self, key: int, coro: Callable[[], Awaitable[None]]):
        self.key_events[key] = coro
        

async def main() -> None:
    window = pygame.display.set_mode((800, 600))

    ctx = Context()
    asyncio.create_task(game1.on_start(ctx))

    while True:
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if coro := ctx.key_events.get(event.key):
                    asyncio.create_task(coro())

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        window.fill(BG_COLOR)
        pygame.display.update()

        await asyncio.sleep(0) # allow game coroutines to run


if __name__ == "__main__":
    asyncio.run(main())

