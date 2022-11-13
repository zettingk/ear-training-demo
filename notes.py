from typing import Any, Generator
from random import randint

NOTE_OFFSET = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5, 
    "G": 7,
    "A": 9,
    "B": 10
}

DIATONIC_NOTE_OFFSET = {
    "C": 0,
    "D": 1,
    "E": 2,
    "F": 3, 
    "G": 4,
    "A": 5,
    "B": 6
}

def _get_key_from_value(d: dict[Any, Any], val: Any) -> Any:
    return [k for k, v in d.items() if v == val][0]

def generate_notes(*, variability: int, base: int) -> Generator[int, None, None]:
    current_base = base

    while True:
        yield current_base

        increment_by = randint(-variability, variability)
        current_base = max(0, min(127, current_base + increment_by)) # make sure value is between 0-127

def chromatic_to_diatonic(note: int) -> tuple[int, bool]:
    sharp = False

    if is_black(note):
        sharp = True
        note -= 1

    octaves = note // 12

    [key] = _get_key_from_value(NOTE_OFFSET, note % 12)

    result = octaves * 7 + DIATONIC_NOTE_OFFSET[key]
    

    return result, sharp


def is_white(note: int) -> bool:
    return note % 12 in NOTE_OFFSET.values()

def is_black(note: int) -> bool:
    return note % 12 not in NOTE_OFFSET.values()

def note_from_str(s: str) -> int:
    filtered = filter(lambda ch: not ch.isspace(), s)

    try:
        first_char = next(filtered)
        white_note_offset = NOTE_OFFSET[first_char]
    except (StopIteration, KeyError) as exc:
        raise ValueError from exc

    accidental_offset = 0

    split = "".join(filtered).split("-", 1)

    if len(split) == 1:
        accidental_str = split[0]
        octave = 4
    else:
        accidental_str, octave_str = split
        octave = int(octave_str)

    for ch in accidental_str:
        if ch == "b" or ch == "♭":
            accidental_offset -= 1
        elif ch == "#" or ch == "♯":
            accidental_offset += 1;
        else:
            raise ValueError(f"unrecognized accidental '{ch}'")

    return octave * 12 + white_note_offset + accidental_offset

def format_note_as_str(note: int, ascii=False) -> str:
    octave = note // 12
    accidental = ""
    if is_black(note):
        accidental = "#" if ascii else "♯"
        note -= 1

    white_note = _get_key_from_value(NOTE_OFFSET, note % 12)

    return f"{white_note}{accidental}-{octave}"

