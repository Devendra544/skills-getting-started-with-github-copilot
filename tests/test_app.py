"""
Comprehensive test suite for Mergington High School API

Tests cover all endpoints, validation logic, edge cases, and proper error handling.
"""

import pytest
from fastapi import status


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_index(self, client):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_follow(self, client):
        """Test that root endpoint can be followed to static files"""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == status.HTTP_200_OK


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert isinstance(data, dict)
        assert len(data) == 9

        # Verify each activity has required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that all expected activities are returned"""
        response = client.get("/activities")
        data = response.json()

        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Swimming Club",
            "Art Studio",
            "Drama Club",
            "Science Olympiad",
            "Debate Team"
        ]

        for activity in expected_activities:
            assert activity in data

    def test_get_activities_has_participants(self, client):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        data = response.json()

        # Check that some activities have participants
        total_participants = sum(len(activity["participants"]) for activity in data.values())
        assert total_participants > 0


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client, reset_activities, sample_email):
        """Test successful signup for an activity"""
        response = client.post("/activities/Chess%20Club/signup", params={"email": sample_email})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_activity_not_found(self, client, sample_email):
        """Test signup with non-existent activity"""
        response = client.post("/activities/NonExistent/signup", params={"email": sample_email})
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_participant(self, client, reset_activities, existing_participant):
        """Test that duplicate signup is currently allowed (known bug)"""
        # This test documents the current behavior - duplicate signups are allowed
        # but should be fixed to prevent duplicates
        response = client.post("/activities/Chess%20Club/signup", params={"email": existing_participant})
        assert response.status_code == status.HTTP_200_OK  # This should be 400 in the future

    def test_signup_empty_email(self, client, reset_activities):
        """Test signup with empty email"""
        response = client.post("/activities/Chess%20Club/signup", params={"email": ""})
        assert response.status_code == status.HTTP_200_OK  # Currently allows empty email

    def test_signup_invalid_email_format(self, client, reset_activities):
        """Test signup with invalid email format"""
        response = client.post("/activities/Chess%20Club/signup", params={"email": "invalid-email"})
        assert response.status_code == status.HTTP_200_OK  # Currently no email validation


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client, reset_activities, existing_participant):
        """Test successful unregister from an activity"""
        response = client.post("/activities/Chess%20Club/unregister", params={"email": existing_participant})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert existing_participant in data["message"]
        assert "Chess Club" in data["message"]

    def test_unregister_activity_not_found(self, client, existing_participant):
        """Test unregister with non-existent activity"""
        response = client.post("/activities/NonExistent/unregister", params={"email": existing_participant})
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_student_not_registered(self, client, reset_activities, sample_email):
        """Test unregister when student is not registered"""
        response = client.post("/activities/Chess%20Club/unregister", params={"email": sample_email})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "Student is not registered" in data["detail"]


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""

    def test_signup_then_unregister_workflow(self, client, reset_activities, sample_email):
        """Test complete signup and unregister workflow"""
        # First signup
        signup_response = client.post("/activities/Chess%20Club/signup", params={"email": sample_email})
        assert signup_response.status_code == status.HTTP_200_OK

        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert sample_email in activities_data["Chess Club"]["participants"]

        # Then unregister
        unregister_response = client.post("/activities/Chess%20Club/unregister", params={"email": sample_email})
        assert unregister_response.status_code == status.HTTP_200_OK

        # Verify student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert sample_email not in activities_data["Chess Club"]["participants"]

    def test_multiple_signups_same_activity(self, client, reset_activities):
        """Test multiple students signing up for the same activity"""
        emails = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]

        # All signups should succeed
        for email in emails:
            response = client.post("/activities/Programming%20Class/signup", params={"email": email})
            assert response.status_code == status.HTTP_200_OK

        # Verify all students are registered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data["Programming Class"]["participants"]
        for email in emails:
            assert email in participants


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_special_characters_in_email(self, client, reset_activities):
        """Test signup with special characters in email"""
        special_email = "test+tag@example.com"
        response = client.post("/activities/Chess%20Club/signup", params={"email": special_email})
        assert response.status_code == status.HTTP_200_OK

    def test_long_email(self, client, reset_activities):
        """Test signup with very long email"""
        long_email = "a" * 200 + "@example.com"
        response = client.post("/activities/Chess%20Club/signup", params={"email": long_email})
        assert response.status_code == status.HTTP_200_OK

    def test_unicode_in_email(self, client, reset_activities):
        """Test signup with unicode characters in email"""
        unicode_email = "tëst@example.com"
        response = client.post("/activities/Chess%20Club/signup", params={"email": unicode_email})
        assert response.status_code == status.HTTP_200_OK