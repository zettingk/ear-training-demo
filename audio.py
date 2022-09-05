from mingus.containers import Note
import pygame

DEFAULT_VELOCITY = 127


def note_to_midi(note: Note) -> int:
    return int(note) + 12


def note_on(midi_output: pygame.midi.Output, note: Note) -> None:
    velocity = note.velocity if note.velocity is not None else DEFAULT_VELOCITY

    midi_output.note_on(note_to_midi(note), velocity)


def note_off(midi_output: pygame.midi.Output, note: Note) -> None:
    velocity = note.velocity if note.velocity is not None else DEFAULT_VELOCITY
    
    midi_output.note_off(note_to_midi(note), velocity)
