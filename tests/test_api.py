from fastapi.testclient import TestClient

from src.api.app import app


client = TestClient(app)

UETR = "550e8400-e29b-41d4-a716-446655440001"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_uetr_validation():
    response = client.post(
        "/api/v1/uetr/validate",
        json={
            "uetr": UETR,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["valid"] is True


def test_create_payment():
    response = client.post(
        "/api/v1/payments",
        json={
            "uetr": UETR,
            "amount": 10000.00,
            "currency": "USD",
            "origin": "SYSTEM_A",
            "destination": "SYSTEM_B",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["uetr"] == UETR
    assert data["status"] == "CREATED"


def test_get_payment():
    response = client.get(
        f"/api/v1/payments/{UETR}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["uetr"] == UETR


def test_update_payment_status():
    response = client.post(
        f"/api/v1/payments/{UETR}/status",
        json={
            "status": "VALIDATED",
            "reason": "Validation successful",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["payment"]["status"] == "VALIDATED"


def test_payment_events():
    response = client.get(
        f"/api/v1/payments/{UETR}/events"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["uetr"] == UETR
    assert len(data["workflow_events"]) == 1
    assert len(data["audit_events"]) >= 1
