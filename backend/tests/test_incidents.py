import pytest

def test_create_new(client, auth_headers, db_session):
    # Сначала создаем персону для involvement
    person_response = client.post("/api/persons", json={
        "name": "Involved Person",
        "address": "456 Side St",
        "role": "witness",
        "phone": "+1234567890",  # Исправлено на валидный формат
        "email": "witness@example.com"
    }, headers=auth_headers)
    
    person_id = person_response.json()["id"]
    
    new_data = {
        "type": "Theft",
        "description": "Stolen laptop from office",
        "location": "Office building, 123 Main St",
        "severity": "medium",
        "involvedPersons": [person_id]
    }
    
    response = client.post("/api/news", json=new_data, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == new_data["type"]
    assert data["severity"] == new_data["severity"]
    assert person_id in data["involvedPersons"]
    assert "registration_number" in data
    
def test_get_news(client, auth_headers, db_session):
    # Сначала создаем инцидент
    test_create_new(client, auth_headers, db_session)
    
    response = client.get("/api/news", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["type"] == "Theft"

def test_get_public_news(client, auth_headers, db_session):
    # Создаем инцидент (требует авторизации)
    test_create_new(client, auth_headers, db_session)
    
    # Публичный эндпоинт должен работать без авторизации
    response = client.get("/api/news/public")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
def test_get_news_by_person(client, auth_headers, db_session):
    # Создаем персону и инцидент
    person_response = client.post("/api/persons", json={
        "name": "Test Person",
        "address": "123 Test St",
        "role": "suspect",
        "phone": "+1234567890",  # Исправлено на валидный формат
        "email": "test@example.com"
    }, headers=auth_headers)
    
    person_id = person_response.json()["id"]
    
    new_response = client.post("/api/news", json={
        "type": "Assault",
        "description": "Physical assault case",
        "location": "Park area",
        "severity": "high",
        "involvedPersons": [person_id]
    }, headers=auth_headers)
    
    # Получаем инциденты по персоне
    response = client.get(f"/api/news/by-person/{person_id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["type"] == "Assault"