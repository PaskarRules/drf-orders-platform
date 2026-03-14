import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from conftest import USER_PASSWORD

User = get_user_model()

REGISTER_URL = reverse("accounts:register")
LOGIN_URL = reverse("accounts:login")
REFRESH_URL = reverse("accounts:token-refresh")
LOGOUT_URL = reverse("accounts:logout")
PROFILE_URL = reverse("accounts:profile")
CHANGE_PASSWORD_URL = reverse("accounts:change-password")

VALID_REGISTER_DATA = {
    "email": "new@example.com",
    "username": "newuser",
    "password": "strongpass123!",
    "password_confirm": "strongpass123!",
}


@pytest.mark.django_db
class TestRegister:
    def test_success(self, api_client):
        response = api_client.post(REGISTER_URL, VALID_REGISTER_DATA)
        assert response.status_code == 201
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]
        assert "user" in response.data
        assert response.data["user"]["email"] == "new@example.com"
        assert User.objects.filter(email="new@example.com").exists()

    def test_password_mismatch(self, api_client):
        data = {**VALID_REGISTER_DATA, "password_confirm": "wrongpass123!"}
        response = api_client.post(REGISTER_URL, data)
        assert response.status_code == 400
        assert "password_confirm" in response.data

    def test_duplicate_email(self, api_client, user):
        data = {**VALID_REGISTER_DATA, "email": user.email}
        response = api_client.post(REGISTER_URL, data)
        assert response.status_code == 400
        assert "email" in response.data

    def test_weak_password(self, api_client):
        data = {**VALID_REGISTER_DATA, "password": "123", "password_confirm": "123"}
        response = api_client.post(REGISTER_URL, data)
        assert response.status_code == 400
        assert "password" in response.data

    def test_missing_email(self, api_client):
        data = {**VALID_REGISTER_DATA}
        del data["email"]
        response = api_client.post(REGISTER_URL, data)
        assert response.status_code == 400
        assert "email" in response.data

    def test_missing_username(self, api_client):
        data = {**VALID_REGISTER_DATA}
        del data["username"]
        response = api_client.post(REGISTER_URL, data)
        assert response.status_code == 400
        assert "username" in response.data

    def test_duplicate_username(self, api_client, user):
        data = {**VALID_REGISTER_DATA, "username": user.username}
        response = api_client.post(REGISTER_URL, data)
        assert response.status_code == 400
        assert "username" in response.data


@pytest.mark.django_db
class TestLogin:
    def test_success(self, api_client, user):
        response = api_client.post(LOGIN_URL, {
            "email": user.email,
            "password": USER_PASSWORD,
        })
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_wrong_password(self, api_client, user):
        response = api_client.post(LOGIN_URL, {
            "email": user.email,
            "password": "wrongpass",
        })
        assert response.status_code == 401

    def test_nonexistent_email(self, api_client):
        response = api_client.post(LOGIN_URL, {
            "email": "nobody@example.com",
            "password": "whatever123",
        })
        assert response.status_code == 401

    def test_token_refresh(self, api_client, user):
        login = api_client.post(LOGIN_URL, {
            "email": user.email,
            "password": USER_PASSWORD,
        })
        response = api_client.post(REFRESH_URL, {
            "refresh": login.data["refresh"],
        })
        assert response.status_code == 200
        assert "access" in response.data


@pytest.mark.django_db
class TestLogout:
    def test_success(self, auth_client, user):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        response = auth_client.post(LOGOUT_URL, {"refresh": str(refresh)})
        assert response.status_code == 205

    def test_unauthenticated(self, api_client):
        response = api_client.post(LOGOUT_URL, {"refresh": "fake-token"})
        assert response.status_code == 401

    def test_missing_refresh_token(self, auth_client):
        response = auth_client.post(LOGOUT_URL, {})
        assert response.status_code == 400
        assert "refresh" in response.data


@pytest.mark.django_db
class TestProfile:
    def test_get_profile(self, auth_client, user):
        response = auth_client.get(PROFILE_URL)
        assert response.status_code == 200
        assert response.data["email"] == user.email
        assert response.data["username"] == user.username
        assert "id" in response.data
        assert "date_joined" in response.data

    def test_update_phone(self, auth_client, user):
        response = auth_client.patch(PROFILE_URL, {"phone": "1234567890"})
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.phone == "1234567890"

    def test_update_username(self, auth_client, user):
        response = auth_client.patch(PROFILE_URL, {"username": "newname"})
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.username == "newname"

    def test_cannot_change_email(self, auth_client, user):
        original_email = user.email
        auth_client.patch(PROFILE_URL, {"email": "hacked@example.com"})
        user.refresh_from_db()
        assert user.email == original_email

    def test_cannot_change_date_joined(self, auth_client, user):
        original = user.date_joined
        auth_client.patch(PROFILE_URL, {"date_joined": "2000-01-01T00:00:00Z"})
        user.refresh_from_db()
        assert user.date_joined == original

    def test_unauthenticated(self, api_client):
        response = api_client.get(PROFILE_URL)
        assert response.status_code == 401


@pytest.mark.django_db
class TestChangePassword:
    def test_success(self, auth_client, user):
        response = auth_client.post(CHANGE_PASSWORD_URL, {
            "old_password": USER_PASSWORD,
            "new_password": "newsecurepass456!",
        })
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.check_password("newsecurepass456!")

    def test_wrong_old_password(self, auth_client):
        response = auth_client.post(CHANGE_PASSWORD_URL, {
            "old_password": "totallyWrong",
            "new_password": "newsecurepass456!",
        })
        assert response.status_code == 400
        assert "old_password" in response.data

    def test_weak_new_password(self, auth_client):
        response = auth_client.post(CHANGE_PASSWORD_URL, {
            "old_password": USER_PASSWORD,
            "new_password": "123",
        })
        assert response.status_code == 400
        assert "new_password" in response.data

    def test_unauthenticated(self, api_client):
        response = api_client.post(CHANGE_PASSWORD_URL, {
            "old_password": USER_PASSWORD,
            "new_password": "newsecurepass456!",
        })
        assert response.status_code == 401


@pytest.mark.django_db
class TestUserModel:
    def test_str(self, user):
        assert str(user) == user.email

    def test_email_is_username_field(self):
        assert User.USERNAME_FIELD == "email"
