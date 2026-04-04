import pytest
from datetime import datetime, timedelta

def test_get_statistics_overall(client, auth_headers, db_session):
    # Создаем несколько инцидентов для статистики
    for i in range(3):
        client.post("/api/news", json={
            "type": f"Test Type {i}",
            "description": f"Test description {i}",
            "location": f"Location {i}",
            "severity": "medium",
            "involvedPersons": []
        }, headers=auth_headers)
    
    response = client.get("/api/statistics", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "totalnews" in data
    assert "byType" in data
    assert "bySeverity" in data
    assert data["totalnews"] == 3

def test_get_statistics_with_date_range(client, auth_headers, db_session):
    # Создаем тестовые данные
    client.post("/api/news", json={
        "type": "Recent new",
        "description": "Recent test",
        "location": "Test location",
        "severity": "high",
        "involvedPersons": []
    }, headers=auth_headers)
    
    # Тестируем с диапазоном дат
    end_date = (datetime.now() + timedelta(days=30)).date().isoformat()
    start_date = (datetime.now() - timedelta(days=30)).date().isoformat()
    
    response = client.get(
        f"/api/statistics?start_date={start_date}&end_date={end_date}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["totalnews"] >= 1