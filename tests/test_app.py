import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client():
    """Fixture to provide a TestClient instance for testing."""
    return TestClient(app)

def test_get_activities_initial(client):
    """Test GET /activities returns initial activities."""
    # Arrange: No specific setup needed as activities are initialized in app

    # Act: Make the GET request
    response = client.get("/activities")

    # Assert: Check response status and content
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Check initial activities are present
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    # Check structure
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]

def test_get_activities_lazy_load(client):
    """Test GET /activities lazy loads additional activities on first call."""
    # Arrange: First call to trigger lazy loading

    # Act: Make the GET request (first time)
    response = client.get("/activities")

    # Assert: Check that lazy-loaded activities are now present
    assert response.status_code == 200
    data = response.json()
    # Lazy-loaded activities
    assert "Soccer Club" in data
    assert "Swimming Team" in data
    assert "Drama Club" in data
    assert "Art Studio" in data
    assert "Science Olympiad" in data
    assert "Mathletes" in data

def test_signup_success(client):
    """Test POST /activities/{activity_name}/signup successful signup."""
    # Arrange: Choose an activity and email
    activity = "Chess Club"
    email = "student@example.com"

    # Act: Make the POST request
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert: Check response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity}"
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity]["participants"]

def test_signup_duplicate(client):
    """Test POST /activities/{activity_name}/signup rejects duplicate signup."""
    # Arrange: Sign up first
    activity = "Programming Class"
    email = "duplicate@example.com"
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act: Try to sign up again
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert: Should return 400
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already registered" in data["detail"].lower()

def test_signup_nonexistent_activity(client):
    """Test POST /activities/{activity_name}/signup for nonexistent activity."""
    # Arrange: Use a non-existent activity
    activity = "Nonexistent Activity"
    email = "test@example.com"

    # Act: Make the POST request
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert: Should return 404
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

def test_remove_participant_success(client):
    """Test DELETE /activities/{activity_name}/participants/{email} successful removal."""
    # Arrange: Sign up first
    activity = "Gym Class"
    email = "remove@example.com"
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act: Remove the participant
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert: Check response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from {activity}"
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity]["participants"]

def test_remove_participant_not_signed_up(client):
    """Test DELETE /activities/{activity_name}/participants/{email} for not signed up."""
    # Arrange: Activity and email not signed up
    activity = "Chess Club"
    email = "notsigned@example.com"

    # Act: Try to remove
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert: Should return 404
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

def test_remove_participant_nonexistent_activity(client):
    """Test DELETE /activities/{activity_name}/participants/{email} for nonexistent activity."""
    # Arrange: Non-existent activity
    activity = "Fake Activity"
    email = "test@example.com"

    # Act: Try to remove
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert: Should return 404
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

def test_get_root_redirect(client):
    """Test GET / redirects to static file."""
    # Arrange: No setup needed

    # Act: Make the GET request
    response = client.get("/")

    # Assert: Should redirect
    assert response.status_code == 200  # FastAPI TestClient follows redirects by default
    # Since it's serving static file, check if it's HTML content
    assert "text/html" in response.headers.get("content-type", "")