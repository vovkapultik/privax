from fastapi.testclient import TestClient
import unittest
from app.main import app

client = TestClient(app)

class TestAPI(unittest.TestCase):
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})
    
    def test_create_note(self):
        """Test creating a note through the API."""
        test_amount = 500
        response = client.post(
            "/api/v1/notes",
            json={"amount": test_amount}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["amount"], test_amount)
        self.assertIn("secret", data)
        self.assertIn("nullifier_secret", data)
        self.assertIn("commitment", data)
        self.assertIn("nullifier_hash", data)
    
    def test_create_note_custom_secrets(self):
        """Test creating a note with custom secrets."""
        test_amount = 300
        test_secret = "test_secret_via_api"
        test_nullifier = "test_nullifier_via_api"
        
        response = client.post(
            "/api/v1/notes",
            json={
                "amount": test_amount,
                "secret": test_secret,
                "nullifier_secret": test_nullifier
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["amount"], test_amount)
        self.assertEqual(data["secret"], test_secret)
        self.assertEqual(data["nullifier_secret"], test_nullifier)

if __name__ == "__main__":
    unittest.main() 