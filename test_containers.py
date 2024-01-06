import unittest
from containers import Note, Accidental, WhiteNote


class TestNote(unittest.TestCase):
    def test_from_str(self):
        equals = [
            (Note.from_str("A"), Note(WhiteNote.A, [], 4)),
            (Note.from_str("  B      b- 2"), Note(WhiteNote.B, [Accidental.FLAT], 2)),
            (Note.from_str("C\nb-3"), Note(WhiteNote.C, [Accidental.FLAT], 3)),
            (Note.from_str("G#"), Note(WhiteNote.G, [Accidental.SHARP], 4)),
        ]

        raisers = [lambda: Note.from_str("bB"), lambda: Note.from_str("A#4")]

        for a, b in equals:
            self.assertEqual(a, b)

        for f in raisers:
            self.assertRaises(ValueError, f)
