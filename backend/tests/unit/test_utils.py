# tests/unit/test_utils.py
import pytest
from datetime import datetime, timezone, timedelta
from jose import jwt

def test_password_hashing():
    """Тестируем функцию хеширования паролей"""
    # Данные: пароль "test123"
    # Ожидаемый результат: хеш не равен оригиналу, длина > 0
    from main import get_password_hash, verify_password
    
    password = "test123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert len(hashed) > 0
    assert verify_password(password, hashed) == True
    assert verify_password("wrong_password", hashed) == False

def test_token_creation_and_validation():
    """Тестируем создание и валидацию JWT токенов"""
    from main import create_access_token, SECRET_KEY, ALGORITHM
    
    # Тестовые данные
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    # Проверяем что токен создан
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Проверяем что токен можно декодировать
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "testuser"
    assert "exp" in payload

def test_email_validation():
    """Тестируем валидацию email адресов"""
    from main import validate_email
    
    valid_emails = [
        "test@example.com",
        "user.name@domain.co.uk",
        "user+tag@example.org"
    ]
    
    invalid_emails = [
        "invalid-email",
        "missing@domain",
        "@nodomain.com",
        "spaces in@email.com"
    ]
    
    for email in valid_emails:
        assert validate_email(email) == True, f"Email {email} should be valid"
    
    for email in invalid_emails:
        assert validate_email(email) == False, f"Email {email} should be invalid"

def test_phone_validation():
    """Тестируем валидацию телефонных номеров"""
    from main import validate_phone
    
    valid_phones = [
        "+1234567890",
        "+1-234-567-8900",
        "+44 7911 123456"
    ]
    
    invalid_phones = [
        "123456",  # слишком короткий
        "abcdefghij",  # не цифры
        "+1234567890123456"  # слишком длинный
    ]
    
    for phone in valid_phones:
        assert validate_phone(phone) == True, f"Phone {phone} should be valid"
    
    for phone in invalid_phones:
        assert validate_phone(phone) == False, f"Phone {phone} should be invalid"
