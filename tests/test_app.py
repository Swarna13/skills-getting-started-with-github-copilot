"""
Test suite for Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_has_expected_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_contains_chess_club(self):
        """Test that Chess Club activity exists"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data

    def test_activities_have_participants(self):
        """Test that some activities have participants"""
        response = client.get("/activities")
        data = response.json()
        has_participants = any(len(activity["participants"]) > 0 for activity in data.values())
        assert has_participants


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_success(self):
        """Test successful signup of a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_duplicate_participant_fails(self):
        """Test that duplicate signup fails"""
        email = "duplicate@mergington.edu"
        # First signup should succeed
        client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email}
        )
        # Second signup with same email should fail
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self):
        """Test that signup for non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_adds_participant_to_list(self):
        """Test that signup adds participant to activity's participant list"""
        email = "participant@mergington.edu"
        client.post(
            "/activities/Programming%20Class/signup",
            params={"email": email}
        )
        response = client.get("/activities")
        data = response.json()
        assert email in data["Programming Class"]["participants"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant_success(self):
        """Test successful unregistration of an existing participant"""
        # First, sign up a participant
        email = "unregister_test@mergington.edu"
        client.post(
            "/activities/Soccer%20Team/signup",
            params={"email": email}
        )
        # Then unregister them
        response = client.post(
            "/activities/Soccer%20Team/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_nonexistent_participant_fails(self):
        """Test that unregistering a non-existent participant fails"""
        response = client.post(
            "/activities/Basketball%20Club/unregister",
            params={"email": "nothere@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()

    def test_unregister_nonexistent_activity_fails(self):
        """Test that unregistering from non-existent activity fails"""
        response = client.post(
            "/activities/Fake%20Club/unregister",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_removes_participant_from_list(self):
        """Test that unregister removes participant from activity's participant list"""
        email = "remove_me@mergington.edu"
        # Sign up
        client.post(
            "/activities/Art%20Club/signup",
            params={"email": email}
        )
        # Verify they were added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Art Club"]["participants"]
        
        # Unregister
        client.post(
            "/activities/Art%20Club/unregister",
            params={"email": email}
        )
        # Verify they were removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Art Club"]["participants"]


class TestIntegration:
    """Integration tests for full signup/unregister workflows"""

    def test_full_signup_and_unregister_flow(self):
        """Test complete flow: signup, verify, unregister, verify removal"""
        activity = "Debate%20Team"
        email = "integration_test@mergington.edu"

        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()["Debate Team"]["participants"])

        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200

        # Verify participant count increased
        response = client.get("/activities")
        after_signup_count = len(response.json()["Debate Team"]["participants"])
        assert after_signup_count == initial_count + 1

        # Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200

        # Verify participant count decreased back to initial
        response = client.get("/activities")
        final_count = len(response.json()["Debate Team"]["participants"])
        assert final_count == initial_count
