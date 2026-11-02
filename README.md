# Students API

Учебный REST API на FastAPI для управления студентами. 
Данные хранятся в локальном JSON-файле (`db.json`). Валидация — через Pydantic.

## Установка и запуск

1. Установите зависимости:
   pip install fastapi uvicorn[standard] pydantic

2. Запустите сервер:
   uvicorn main:app --reload

3. Откройте Swagger UI: http://127.0.0.1:8000/docs

## Запуск в Docker

В контейнере сервер слушает 8000 порт.

docker build -t students-api .
docker run -d -p 8000:8000 --name students-app students-api

Документация в Docker будет доступна на: http://localhost:8000/docs

## Эндпоинты

| Метод | Путь | Параметр | Описание |
|---|---|---|---|
| POST | /students | JSON в теле | Создать студента. Возвращает созданный объект (без id). |
| GET | /students | — | Получить всех студентов (с id). |
| GET | /student | student_id=1 | Получить одного студента по id. |
| DELETE | /students | student_id=1 | Удалить студента. Возвращает обновлённый список. |

## Валидация (Pydantic)

- name, group — непустые строки.
- age — целое число больше или равно 0.
- average_score — опциональное дробное число от 0 до 5 (или null).
При ошибке возвращается код 422 Validation Error.

## Хранение

Все изменения сохраняются в файл db.json (создаётся автоматически). При старте данные загружаются из файла в память.
