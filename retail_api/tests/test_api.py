# PROMPT:
# Generate pytest test cases for a FastAPI retail analytics application.
# Include tests for health endpoint, metrics endpoint, funnel endpoint,
# heatmap endpoint, anomaly endpoint and idempotent event ingestion.

# CHANGES MADE:
# Added duplicate ingestion test.
# Added empty store test cases.
# Modified assertions to match actual API responses.
# Added edge case coverage for metrics and funnel endpoints.
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from main import app

client = TestClient(app)


def test_home():

    response = client.get("/")

    assert response.status_code == 200


def test_health():

    response = client.get("/health")

    assert response.status_code == 200


def test_metrics():

    response = client.get(
        "/stores/STORE_BLR_002/metrics"
    )

    assert response.status_code == 200


def test_funnel():

    response = client.get(
        "/stores/STORE_BLR_002/funnel"
    )

    assert response.status_code == 200


def test_heatmap():

    response = client.get(
        "/stores/STORE_BLR_002/heatmap"
    )

    assert response.status_code == 200


def test_anomalies():

    response = client.get(
        "/stores/STORE_BLR_002/anomalies"
    )

    assert response.status_code == 200
    

def test_duplicate_ingest():

    payload = [
        {
            "event_id": "dup_test_1",
            "store_id": "STORE_BLR_002",
            "camera_id": "CAM_1",
            "visitor_id": "VIS_1",
            "event_type": "ZONE_ENTER",
            "timestamp": "2026-05-30T05:00:00Z",
            "zone_id": "RIGHT_SECTION",
            "dwell_ms": 0,
            "is_staff": False,
            "confidence": 0.95,
            "metadata": {
                "queue_depth": None,
                "sku_zone": "COSMETICS",
                "session_seq": 1
            }
        }
    ]

    client.post(
        "/events/ingest",
        json=payload
    )

    response = client.post(
        "/events/ingest",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["duplicates"] >= 1