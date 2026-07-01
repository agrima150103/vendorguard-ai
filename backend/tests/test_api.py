"""
API integration tests for VendorGuard AI.
"""


def test_health(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_vendor_list(client):
    response = client.get("/api/v1/vendors")

    assert response.status_code == 200

    vendors = response.json()

    assert len(vendors) == 3
    assert {vendor["vendor_id"] for vendor in vendors} == {
        "cloudnova-001",
        "paysphere-002",
        "dataquick-003",
    }


def test_dataquick_injection_and_human_gate(client):
    create_response = client.post(
        "/api/v1/assessments",
        json={
            "vendor_id": "dataquick-003",
        },
    )

    assert create_response.status_code == 201

    assessment = create_response.json()

    assert assessment["status"] == "AWAITING_HUMAN_REVIEW"
    assert (
        assessment["recommendation"]["decision"]
        == "ESCALATE_TO_HUMAN"
    )
    assert (
        assessment["risk_assessment"]["prompt_injection_detected"]
        is True
    )

    assessment_id = assessment["assessment_id"]

    review_response = client.post(
        f"/api/v1/assessments/{assessment_id}/review",
        json={
            "reviewer_id": "test-reviewer",
            "decision": "INFORMATION_REQUESTED",
            "reason": (
                "Resolve contradictory retention statements and provide "
                "the mandatory security evidence."
            ),
            "conditions": [],
        },
    )

    assert review_response.status_code == 200

    completed_assessment = review_response.json()

    assert completed_assessment["status"] == "COMPLETE"
    assert (
        completed_assessment["human_decision"]["decision"]
        == "INFORMATION_REQUESTED"
    )


def test_cannot_review_twice(client):
    create_response = client.post(
        "/api/v1/assessments",
        json={
            "vendor_id": "cloudnova-001",
        },
    )

    assert create_response.status_code == 201

    assessment_id = create_response.json()["assessment_id"]

    review_payload = {
        "reviewer_id": "test-reviewer",
        "decision": "APPROVED",
        "reason": (
            "The fictional low-risk vendor supplied sufficient evidence."
        ),
        "conditions": [],
    }

    first_review = client.post(
        f"/api/v1/assessments/{assessment_id}/review",
        json=review_payload,
    )

    assert first_review.status_code == 200
    assert first_review.json()["status"] == "COMPLETE"

    second_review = client.post(
        f"/api/v1/assessments/{assessment_id}/review",
        json=review_payload,
    )

    assert second_review.status_code == 409
    assert (
        second_review.json()["detail"]
        == "Assessment is not awaiting human review."
    )