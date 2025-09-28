# Отчёт по лабораторной работе №2

## Тема

Взаимодействие с Web API с помощью Python-скрипта.

---

## Цель работы

Освоить основы работы с внешними API, научиться отправлять HTTP-запросы, обрабатывать ответы и сохранять данные в удобном формате.

---

## Задание

Реализовать Python-скрипт `currency_exchange_rate.py`, который:

1. Получает курс одной валюты к другой на указанную дату.
2. Принимает параметры из командной строки: `from_currency`, `to_currency`, `date`.
3. Сохраняет полученные данные в формате JSON (файл в папке `data/`, имя формируется из валют и даты).
4. Логирует ошибки в файл `error.log`.
5. Проверяет корректность введённой даты.

---

## Код программы (`currency_exchange_rate.py`)

*находится в lab02*

---

## Примеры запуска

Запрос курса **USD → EUR** на `2025-01-01`:

```bash
python lab02/currency_exchange_rate.py USD EUR 2025-01-01
```

Вывод:

```
Данные сохранены в ...\data\USD_EUR_2025-01-01.json
```

Запрос курса **EUR → MDL** на `2025-03-15`:

```bash
python lab02/currency_exchange_rate.py EUR MDL 2025-03-15
```

Запрос курса **RON → UAH** на `2025-06-01`:

```bash
python lab02/currency_exchange_rate.py RON UAH 2025-06-01
```

Запрос курса **MDL → EUR** для нескольких дат:

```bash
python lab02/currency_exchange_rate.py MDL EUR 2025-01-15
python lab02/currency_exchange_rate.py MDL EUR 2025-03-15
python lab02/currency_exchange_rate.py MDL EUR 2025-05-15
python lab02/currency_exchange_rate.py MDL EUR 2025-07-15
python lab02/currency_exchange_rate.py MDL EUR 2025-09-15
```

---

## Результаты (файлы JSON)

Примеры содержимого файлов:

**USD_EUR_2025-01-01.json**

```json
{
    "from": "USD",
    "to": "EUR",
    "rate": 1.0449967801462194,
    "date": "2025-01-01"
}
```

**EUR_MDL_2025-03-15.json**

```json
{
    "from": "EUR",
    "to": "MDL",
    "rate": 0.051556224640782,
    "date": "2025-03-15"
}
```

**MDL_EUR_2025-07-15.json**

```json
{
    "from": "MDL",
    "to": "EUR",
    "rate": 19.8027,
    "date": "2025-07-15"
}
```

**RON_UAH_2025-06-01.json**

```json
{
    "from": "RON",
    "to": "UAH",
    "rate": 0.1079430789133247,
    "date": "2025-06-01"
}
```

---

## Вывод

В ходе работы:

* Был реализован Python-скрипт для обращения к API валютного сервиса.
* Скрипт корректно принимает параметры и сохраняет результат в JSON.
* Реализована обработка ошибок и ведение лога `error.log`.
* Проведено тестирование на разных датах (от `2025-01-01` до `2025-09-15`) — результаты сохранены в `data/`.
