import copy

from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
initial_activities = copy.deepcopy(app_module.activities)


def setup_function():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(initial_activities))


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Yoga Club"]["schedule"] == "Wednesdays, 5:00 PM - 6:00 PM"


def test_signup_for_activity():
    email = "test@example.com"
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate_fails():
    email = "michael@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant():
    email = "michael@mergington.edu"
    response = client.delete("/activities/Chess%20Club/participants", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404():
    response = client.delete("/activities/Chess%20Club/participants", params={"email": "ghost@example.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_activity_not_found():
    response = client.post("/activities/Nonexistent/signup", params={"email": "test@example.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
