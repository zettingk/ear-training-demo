import importlib
import asyncio

from context import Context

class Game:
    def __init__(self, name: str):
        self.game_module = importlib.import_module("." + name, "game")
        self.task = None

    def begin(self, ctx: Context) -> None:
        self.task = asyncio.create_task(self.game_module.on_start(ctx))

    def update(self, ctx: Context) -> None:
        if hasattr(self.game_module, 'on_update'):
            self.game_module.on_update(ctx)
    
