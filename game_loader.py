import importlib
import asyncio


class Game:
    def __init__(self, name: str):
        self.game_module = importlib.import_module("." + name, "game")

    async def begin(self):
        print(dir(self.game_module))
        await asyncio.create_task(self.game_module.starter())
