import pygame.midi

pygame.midi.init()

INSTRUMENT: int = 1

midi_port = pygame.midi.get_default_output_id()
midi_output = pygame.midi.Output(midi_port)
midi_output.set_instrument(INSTRUMENT)


def note_on(note: int, velocity: int = 127) -> None:
    midi_output.note_on(note, velocity)


def note_off(note: int) -> None:
    midi_output.note_off(note, 0)
