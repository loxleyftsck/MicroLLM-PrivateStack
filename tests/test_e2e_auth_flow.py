# -*- coding: utf-8 -*-
"""
E2E Auth Flow Test — MicroLLM-PrivateStack
P2-1: Critical user journey coverage

Tests the full sequence:
  register → login → GET /me → POST /chat (authenticated) → logout → verify 401

Requires a running server at http://localhost:8000 with a valid JWT_SECRET_KEY.
Run with: pytest tests/test_e2e_auth_flow.py -v
"""

import pytest
import requests
import uuid

BASE = "http://localhost:8000"
HEADERS_JSON = {"Content-Type": "application/json"}


@pytest.fixture(scope="module")
def test_credentials():
    """Unique credentials per test run to avoid DB conflicts."""
    suffix = uuid.uuid4().hex[:8]
    return {
        "email": f"e2e_{suffix}@test.local",
        "password": "E2eTestPass!99",
        "display_name": f"E2E User {suffix}"
    }


@pytest.fixture(scope="module")
def registered_token(test_credentials):
    """Register a user and return the JWT token."""
    resp = requests.post(
        f"{BASE}/api/auth/register",
        json=test_credentials,
        headers=HEADERS_JSON,
        timeout=10
    )
    assert resp.status_code == 201, f"Registration failed: {resp.text}"
    data = resp.json()
    assert "token" in data, "No token in register response"
    return data["token"]


class TestAuthFlow:
    """Full end-to-end authentication journey."""

    def test_register_returns_token(self, registered_token):
        """Registration produces a valid JWT."""
        assert registered_token
        assert len(registered_token) > 20

    def test_login_returns_token(self, test_credentials):
        """Login with correct credentials returns 200 + token."""
        resp = requests.post(
            f"{BASE}/api/auth/login",
            json={"email": test_credentials["email"], "password": test_credentials["password"]},
            headers=HEADERS_JSON,
            timeout=10
        )
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        data = resp.json()
        assert "token" in data

    def test_login_wrong_password_returns_401(self, test_credentials):
        """Wrong password must return 401, not 500."""
        resp = requests.post(
            f"{BASE}/api/auth/login",
            json={"email": test_credentials["email"], "password": "WrongPass!000"},
            headers=HEADERS_JSON,
            timeout=10
        )
        assert resp.status_code == 401

    def test_get_me_with_valid_token(self, registered_token):
        """Authenticated GET /api/auth/me returns user info."""
        resp = requests.get(
            f"{BASE}/api/auth/me",
            headers={**HEADERS_JSON, "Authorization": f"Bearer {registered_token}"},
            timeout=10
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "user" in data
        assert "password_hash" not in data["user"], "password_hash must be stripped"
        assert "role" in data["user"], "role field missing"

    def test_get_me_without_token_returns_401(self):
        """Unauthenticated request to protected endpoint must return 401."""
        resp = requests.get(f"{BASE}/api/auth/me", timeout=10)
        assert resp.status_code == 401

    def test_chat_with_valid_token(self, registered_token):
        """Authenticated chat request must return 200 with response field."""
        resp = requests.post(
            f"{BASE}/api/chat",
            json={"message": "Hello, this is an E2E test.", "max_tokens": 32},
            headers={**HEADERS_JSON, "Authorization": f"Bearer {registered_token}"},
            timeout=60  # Model inference can be slow
        )
        assert resp.status_code == 200, f"Chat failed: {resp.text}"
        data = resp.json()
        assert "response" in data
        assert data["status"] == "success"
        # TTFT header must be present
        assert "X-TTFT-Ms" in resp.headers, "TTFT header missing"

    def test_chat_without_token_returns_401(self):
        """Unauthenticated chat must be blocked."""
        resp = requests.post(
            f"{BASE}/api/chat",
            json={"message": "test"},
            headers=HEADERS_JSON,
            timeout=10
        )
        assert resp.status_code == 401

    def test_logout_invalidates_session(self, registered_token):
        """Logout must return 200 and token should stop working."""
        # Logout
        resp = requests.post(
            f"{BASE}/api/auth/logout",
            headers={**HEADERS_JSON, "Authorization": f"Bearer {registered_token}"},
            timeout=10
        )
        assert resp.status_code == 200

        # Post-logout: /me should return 401
        me_resp = requests.get(
            f"{BASE}/api/auth/me",
            headers={**HEADERS_JSON, "Authorization": f"Bearer {registered_token}"},
            timeout=10
        )
        assert me_resp.status_code == 401, "Token still valid after logout"


class TestRateLimiting:
    """Verify Flask-Limiter blocks brute-force on auth endpoints."""

    def test_login_brute_force_blocked(self):
        """Sending 10 rapid login attempts must trigger 429 before 10th attempt."""
        blocked = False
        for i in range(10):
            resp = requests.post(
                f"{BASE}/api/auth/login",
                json={"email": "attacker@evil.com", "password": f"wrong{i}"},
                headers=HEADERS_JSON,
                timeout=5
            )
            if resp.status_code == 429:
                blocked = True
                break
        assert blocked, "Rate limiter did not block after 10 rapid login attempts"


class TestRBACRole:
    """Verify role field exists in user objects."""

    def test_user_has_role_field(self, registered_token):
        """Newly registered user should have role='user'."""
        resp = requests.get(
            f"{BASE}/api/auth/me",
            headers={**HEADERS_JSON, "Authorization": f"Bearer {registered_token}"},
            timeout=10
        )
        assert resp.status_code == 200
        user = resp.json()["user"]
        assert user.get("role") == "user", f"Expected role=user, got {user.get('role')}"
