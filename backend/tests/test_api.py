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
            "reviewer_name": "Test Reviewer",
            "reviewer_role": "Security Reviewer",
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
        "reviewer_name": "Test Reviewer",
        "reviewer_role": "Security Reviewer",
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

def test_assessment_history_contains_risk_and_pipeline(client):
    create_response = client.post(
        "/api/v1/assessments",
        json={"vendor_id": "cloudnova-001"},
    )
    assert create_response.status_code == 201

    response = client.get("/api/v1/assessments")
    assert response.status_code == 200
    items = response.json()
    created_id = create_response.json()["assessment_id"]
    summary = next(item for item in items if item["assessment_id"] == created_id)

    assert summary["risk_score"] == 10
    assert summary["pipeline_mode"] in {"ADK", "FALLBACK", "DETERMINISTIC", "UNKNOWN"}
    assert summary["status"] == "AWAITING_HUMAN_REVIEW"


def test_review_records_identity_and_backend_timestamp(client):
    create_response = client.post(
        "/api/v1/assessments",
        json={"vendor_id": "cloudnova-001"},
    )
    assessment_id = create_response.json()["assessment_id"]

    response = client.post(
        f"/api/v1/assessments/{assessment_id}/review",
        json={
            "reviewer_name": "Agrima Saxena",
            "reviewer_role": "Security Reviewer",
            "decision": "APPROVED",
            "reason": "The available evidence supports approval.",
            "conditions": [],
        },
    )

    assert response.status_code == 200
    decision = response.json()["human_decision"]
    assert decision["reviewer_name"] == "Agrima Saxena"
    assert decision["reviewer_role"] == "Security Reviewer"
    assert decision["decision_timestamp"]
