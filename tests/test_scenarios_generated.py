import requests
import unittest
import time

# Configuration
ANOMALY_SERVICE_URL = "http://localhost:5053"

class TestScenarios(unittest.TestCase):

    def test_fire_scenario(self):
        """test_fire_scenario: Smoke Sensor = 1 => FIRE Anomaly"""
        payload = {
            "temp": 25.0,
            "devices": [
                {"id": "smoke_sensor_01", "type": "smoke_sensor", "value": 1, "status": "active"}
            ]
        }
        res = requests.post(f"{ANOMALY_SERVICE_URL}/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["has_anomaly"])
        # Check for FIRE type
        types = [a["type"] for a in data["anomalies"]]
        self.assertIn("FIRE", types)
        print("\n✅ Fire Scenario (Smoke) Passed")

    def test_waste_scenario_ac(self):
        """test_waste_scenario_ac: Window OPEN + AC ON => WASTE Anomaly"""
        payload = {
            "temp": 25.0,
            "devices": [
                {"id": "living_room_window", "type": "window", "value": 1, "status": "OPEN"},
                {"id": "air_conditioner", "type": "ac", "value": 1, "status": "ON"}
            ]
        }
        res = requests.post(f"{ANOMALY_SERVICE_URL}/analyze", json=payload)
        data = res.json()
        self.assertTrue(data["has_anomaly"])
        types = [a["type"] for a in data["anomalies"]]
        self.assertIn("WASTE", types)
        print("\n✅ Waste Scenario (Window + AC) Passed")

    def test_waste_scenario_heater(self):
        """test_waste_scenario_heater: Window OPEN + Heater ON => WASTE Anomaly"""
        payload = {
            "temp": 25.0,
            "devices": [
                {"id": "living_room_window", "type": "window", "value": 1, "status": "OPEN"},
                {"id": "smart_heater_1", "type": "heater", "value": 1, "status": "ON"}
            ]
        }
        res = requests.post(f"{ANOMALY_SERVICE_URL}/analyze", json=payload)
        data = res.json()
        self.assertTrue(data["has_anomaly"])
        types = [a["type"] for a in data["anomalies"]]
        self.assertIn("WASTE", types)
        print("\n✅ Waste Scenario (Window + Heater) Passed")

    def test_conflict_scenario(self):
        """test_conflict_scenario: Heater ON + AC ON => CONFLICT Anomaly"""
        payload = {
            "temp": 25.0,
            "devices": [
                {"id": "smart_heater_1", "type": "heater", "value": 1, "status": "ON"},
                {"id": "air_conditioner", "type": "ac", "value": 1, "status": "ON"}
            ]
        }
        res = requests.post(f"{ANOMALY_SERVICE_URL}/analyze", json=payload)
        data = res.json()
        self.assertTrue(data["has_anomaly"])
        types = [a["type"] for a in data["anomalies"]]
        self.assertIn("CONFLICT", types)
        print("\n✅ Conflict Scenario (Heater + AC) Passed")

    def test_high_temp_warning(self):
        """test_high_temp_warning: Temp > 28 => HIGH_TEMP Warning (Not Fire)"""
        payload = {
            "temp": 35.0,
            "devices": []
        }
        res = requests.post(f"{ANOMALY_SERVICE_URL}/analyze", json=payload)
        data = res.json()
        self.assertTrue(data["has_anomaly"])
        types = [a["type"] for a in data["anomalies"]]
        self.assertIn("HIGH_TEMP", types)
        self.assertNotIn("FIRE", types) # Should NOT be FIRE
        print("\n✅ High Temp Warning Passed")

if __name__ == '__main__':
    unittest.main()
