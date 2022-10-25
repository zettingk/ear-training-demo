from dataclasses import dataclass

@dataclass
class Event:
    pass

@dataclass
class MidiEvent(Event):
    pass

@dataclass
class KeyEvent(MidiEvent):
    key: int
    velocity: int

@dataclass
class KeystrokeEvent(Event):
    key: int
    pressed_down: bool
