from context import Context
import asyncio
from events import KeyEvent
from notes import note_from_str

TRILL_NOTES = (note_from_str("C"), note_from_str("D"))

async def on_start(ctx: Context) -> None:
    while True:
        print(f'Press as many trill keys as possible in 10 seconds!')
        queue_id = ctx.begin_gather(KeyEvent, 0, lambda e: e.velocity != 0 and e.key in TRILL_NOTES)

        await asyncio.sleep(10)

        evts = ctx.end_gather(queue_id)

        print(f'You hit {len(evts)} keys')



