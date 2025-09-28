#!/usr/bin/env python3
import argparse
import os
import sys
import requests
import json
from datetime import datetime

# Константы
API_URL = "http://localhost:8080/"
API_KEY = os.getenv("API_KEY", "EXAMPLE_API_KEY")  # Берём ключ из переменной окружения или дефолт

# Директории и файлы
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "error.log")


def save_error(message: str):
    """Сохраняет сообщение об ошибке в error.log"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")


def get_exchange_rate(from_currency: str, to_currency: str, date: str):
    """Делает запрос к API для получения курса валют"""
    try:
        response = requests.post(
            API_URL,
            params={"from": from_currency, "to": to_currency, "date": date},
            data={"key": API_KEY},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()

        if result.get("error"):
            raise ValueError(result["error"])

        return result["data"]

    except Exception as e:
        error_msg = f"Ошибка при получении курса валют ({from_currency}->{to_currency}, {date}): {e}"
        print(error_msg, file=sys.stderr)
        save_error(error_msg)
        return None


def save_to_file(data: dict, from_currency: str, to_currency: str, date: str):
    """Сохраняет результат в JSON файл"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    filename = f"{from_currency}_{to_currency}_{date}.json"
    filepath = os.path.join(DATA_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Данные сохранены в {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Currency exchange rate fetcher")
    parser.add_argument("from_currency", help="Валюта-источник (например, USD)")
    parser.add_argument("to_currency", help="Валюта-назначение (например, EUR)")
    parser.add_argument("date", help="Дата в формате YYYY-MM-DD")

    args = parser.parse_args()

    # Проверка формата даты
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        msg = f"Некорректный формат даты: {args.date}. Используйте YYYY-MM-DD."
        print(msg, file=sys.stderr)
        save_error(msg)
        sys.exit(1)

    # Получение курса
    data = get_exchange_rate(args.from_currency, args.to_currency, args.date)
    if data:
        save_to_file(data, args.from_currency, args.to_currency, args.date)


if __name__ == "__main__":
    main()
