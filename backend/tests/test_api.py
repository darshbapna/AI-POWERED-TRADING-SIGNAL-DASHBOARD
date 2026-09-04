import unittest
from fastapi.testclient import TestClient
from backend.app.main import app

class TestAPIEndpoints(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_check(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")

    def test_assets_list(self):
        res = self.client.get("/api/assets")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("assets", data)
        self.assertTrue(len(data["assets"]) > 0)

    def test_price_endpoint(self):
        res = self.client.get("/api/price/%5ENSEI?days=30")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["ticker"], "^NSEI")
        self.assertTrue(len(data["bars"]) > 0)

    def test_predict_endpoint(self):
        res = self.client.get("/api/predict/%5ENSEI")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("signal", data)
        self.assertIn("shap_drivers", data)

    def test_backtest_endpoint(self):
        res = self.client.get("/api/backtest/%5ENSEI")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("metrics", data)
        self.assertIn("equity_curves", data)

    def test_accuracy_endpoint(self):
        res = self.client.get("/api/accuracy/%5ENSEI")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("summary", data)
        self.assertIn("outcomes", data)

    def test_news_endpoint(self):
        res = self.client.get("/api/news/%5ENSEI")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(isinstance(data, list))

if __name__ == "__main__":
    unittest.main()
