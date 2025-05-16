import unittest
from app.crypto.note import Note

class TestNote(unittest.TestCase):
    def test_note_creation(self):
        """Test that a note can be created with an amount."""
        amount = 100
        note = Note(amount=amount)
        
        self.assertEqual(note.amount, amount)
        self.assertIsNotNone(note.secret)
        self.assertIsNotNone(note.nullifier_secret)
        self.assertIsNotNone(note.commitment)
        self.assertIsNotNone(note.nullifier_hash)

    def test_note_with_custom_secrets(self):
        """Test that a note can be created with custom secrets."""
        amount = 200
        secret = "custom_secret_for_test"
        nullifier_secret = "custom_nullifier_secret_for_test"
        
        note = Note(amount=amount, secret=secret, nullifier_secret=nullifier_secret)
        
        self.assertEqual(note.amount, amount)
        self.assertEqual(note.secret, secret)
        self.assertEqual(note.nullifier_secret, nullifier_secret)
        self.assertIsNotNone(note.commitment)
        self.assertIsNotNone(note.nullifier_hash)

if __name__ == "__main__":
    unittest.main() 