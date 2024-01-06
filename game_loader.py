import importlib
import os
import asyncio

from context import Context

cached_games = None

def reload_games() -> None:
    global cached_games
    cached_games = list(map(lambda g: g.removesuffix(".py"), filter(lambda g: g != '__pycache__', os.listdir('game/'))))

def get_games() -> list[str]:
    if cached_games is None:
        reload_games()

    return cached_games # type: ignore

class Game:
    def __init__(self, name: str):
        self.game_module = importlib.import_module("." + name, "game")
        self.task = None

    def begin(self, ctx: Context) -> None:
        self.task = asyncio.create_task(self.game_module.on_start(ctx))

    def update(self, ctx: Context) -> None:
        if hasattr(self.game_module, 'on_update'):
            self.game_module.on_update(ctx)
    
