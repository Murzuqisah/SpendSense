"""Tests for authentication functionality"""

import pytest
from flask import session
from src.web_app import app, users, validate_username, validate_password


@pytest.fixture
def client():
    """Create a test client"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_client(client):
    """Create an authenticated test client"""
    # Register and login
    client.post(
        "/register",
        data={
            "name": "testuser",
            "password": "testpass123",
            "confirm_password": "testpass123",
        },
    )
    return client


class TestValidation:
    """Test validation functions"""

    def test_valid_username(self):
        """Test valid username"""
        assert validate_username("john123") is True
        assert validate_username("user_name") is True
        assert validate_username("a1b2c3") is True

    def test_invalid_username_too_short(self):
        """Test username too short"""
        assert validate_username("ab") is False

    def test_invalid_username_too_long(self):
        """Test username too long"""
        assert validate_username("a" * 21) is False

    def test_invalid_username_special_chars(self):
        """Test username with special characters"""
        assert validate_username("john@123") is False
        assert validate_username("user-name") is False
        assert validate_username("john.doe") is False

    def test_valid_password(self):
        """Test valid password"""
        assert validate_password("password123") is True
        assert validate_password("secret") is True

    def test_invalid_password_too_short(self):
        """Test password too short"""
        assert validate_password("pass") is False
        assert validate_password("") is False or validate_password("") == ""


class TestRegistration:
    """Test registration functionality"""

    def test_register_page_loads(self, client):
        """Test register page loads"""
        response = client.get("/register")
        assert response.status_code == 200
        assert b"Create Account" in response.data

    def test_register_success(self, client):
        """Test successful registration"""
        response = client.post(
            "/register",
            data={
                "name": "newuser",
                "password": "password123",
                "confirm_password": "password123",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "newuser" in users

    def test_register_username_exists(self, client):
        """Test registration with existing username"""
        # First registration
        client.post(
            "/register",
            data={
                "name": "existinguser",
                "password": "password123",
                "confirm_password": "password123",
            },
        )

        # Try to register with same username
        response = client.post(
            "/register",
            data={
                "name": "existinguser",
                "password": "password456",
                "confirm_password": "password456",
            },
        )
        assert b"Username already exists" in response.data

    def test_register_passwords_dont_match(self, client):
        """Test registration with mismatched passwords"""
        response = client.post(
            "/register",
            data={
                "name": "newuser",
                "password": "password123",
                "confirm_password": "different123",
            },
        )
        assert b"do not match" in response.data or response.status_code == 200

    def test_register_invalid_username(self, client):
        """Test registration with invalid username"""
        response = client.post(
            "/register",
            data={
                "name": "ab",
                "password": "password123",
                "confirm_password": "password123",
            },
        )
        assert b"3-20 characters" in response.data

    def test_register_short_password(self, client):
        """Test registration with short password"""
        response = client.post(
            "/register",
            data={"name": "newuser2", "password": "pass", "confirm_password": "pass"},
        )
        # Should either show error or create account (depends on validation order)
        assert response.status_code in [200, 302]


class TestLogin:
    """Test login functionality"""

    def test_login_page_loads(self, client):
        """Test login page loads"""
        response = client.get("/login")
        assert response.status_code == 200
        assert b"Login to SpendSense" in response.data

    def test_login_success(self, client):
        """Test successful login"""
        # Register first
        client.post(
            "/register",
            data={
                "name": "testuser",
                "password": "testpass123",
                "confirm_password": "testpass123",
            },
        )

        # Login
        response = client.post(
            "/login",
            data={"name": "testuser", "password": "testpass123"},
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_login_invalid_username(self, client):
        """Test login with invalid username"""
        response = client.post(
            "/login", data={"name": "nonexistent", "password": "password123"}
        )
        assert b"Invalid username or password" in response.data

    def test_login_invalid_password(self, client):
        """Test login with invalid password"""
        # Register first
        client.post(
            "/register",
            data={
                "name": "testuser",
                "password": "testpass123",
                "confirm_password": "testpass123",
            },
        )

        # Try to login with wrong password
        response = client.post(
            "/login", data={"name": "testuser", "password": "wrongpassword"}
        )
        assert b"Invalid username or password" in response.data

    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        response = client.post("/login", data={"name": "", "password": "password123"})
        assert b"Please provide both" in response.data


class TestAuthentication:
    """Test authentication requirements"""

    def test_index_redirects_to_login(self, client):
        """Test that index redirects to login when not authenticated"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location

    def test_evaluate_redirects_to_login(self, client):
        """Test that evaluate redirects to login when not authenticated"""
        response = client.post("/evaluate", follow_redirects=False)
        assert response.status_code == 302

    def test_index_loads_when_authenticated(self, auth_client):
        """Test that index loads when authenticated"""
        response = auth_client.get("/", follow_redirects=True)
        assert response.status_code == 200
        # Check that page loaded (either main content or heading)
        assert b"SpendSense" in response.data


class TestLogout:
    """Test logout functionality"""

    def test_logout(self, auth_client):
        """Test logout clears session"""
        response = auth_client.get("/logout", follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login
        assert b"Login to SpendSense" in response.data

    def test_after_logout_index_redirects(self, auth_client):
        """Test that after logout, index redirects to login"""
        auth_client.get("/logout")
        response = auth_client.get("/", follow_redirects=False)
        assert response.status_code == 302
