import pytest
from main import get_password_hash

def test_login_success(client, test_user, db_session):
    # Обновляем пользователя с хешированным паролем
    test_user.hashed_password = get_password_hash("testpass123")
    db_session.commit()
    
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "user" in data
    assert data["user"]["username"] == "testuser"
    assert "token" in data

def test_login_invalid_credentials(client, test_user):
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 400
    data = response.json()
    assert data["success"] == False
    assert "Incorrect username or password" in data["message"]

def test_verify_token_valid(client, auth_headers):
    response = client.get("/api/auth/verify", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True
    assert "user" in data

def test_verify_token_invalid(client):
    response = client.get("/api/auth/verify", headers={
        "Authorization": "Bearer invalid_token"
    })
    
    assert response.status_code == 401

def test_logout(client, auth_headers):
    response = client.post("/api/auth/logout", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True