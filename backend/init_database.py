"""
Проверка подключения к базе данных
"""
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import SessionLocal
from sqlalchemy import text  # Добавьте этот импорт

def check_database_connection():
    max_retries = 15
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Используем text() для SQL выражений
            db.execute(text("SELECT 1"))
            db.close()
            print("✅ Подключение к базе данных успешно установлено")
            return True
        except Exception as e:
            print(f"⚠️ Попытка {attempt + 1}/{max_retries}: Не удалось подключиться к БД: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Повторная попытка через {retry_delay} секунд...")
                time.sleep(retry_delay)
    
    print("❌ Не удалось установить подключение к базе данных после всех попыток")
    return False


if __name__ == "__main__":
    check_database_connection()