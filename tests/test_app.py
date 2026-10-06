import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def activity_data():
    return {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 2,
            "participants": ["current@mergington.edu"],
        }
    }


@pytest.fixture
def client(monkeypatch, activity_data):
    monkeypatch.setattr(app_module, "activities", activity_data)
    return TestClient(app_module.app)


def test_get_activities_returns_activity_and_participants(client):
    # Arrange
    expected_activity = {
        "description": "Play chess",
        "schedule": "Fridays",
        "max_participants": 2,
        "participants": ["current@mergington.edu"],
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"Chess Club": expected_activity}


def test_signup_adds_participant(client, activity_data):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert activity_data["Chess Club"]["participants"] == [
        "current@mergington.edu",
        email,
    ]


def test_signup_for_unknown_activity_returns_not_found(client):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post("/activities/Unknown Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_duplicate_signup_returns_bad_request_without_changing_participants(
    client, activity_data
):
    # Arrange
    email = "current@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    assert activity_data["Chess Club"]["participants"] == [email]


def test_remove_participant_unregisters_student(client, activity_data):
    # Arrange
    email = "current@mergington.edu"

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert activity_data["Chess Club"]["participants"] == []


def test_remove_participant_from_unknown_activity_returns_not_found(client):
    # Arrange
    email = "current@mergington.edu"

    # Act
    response = client.delete("/activities/Unknown Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_nonparticipant_returns_not_found_without_changing_participants(
    client, activity_data
):
    # Arrange
    email = "not-signed-up@mergington.edu"

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert activity_data["Chess Club"]["participants"] == ["current@mergington.edu"]
