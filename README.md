# Students API

Учебный REST API на FastAPI для управления списком студентов.
Данные хранятся в локальном JSON-файле. Валидация — через Pydantic.
Документация — Swagger UI (`/docs`).

## Стек

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic v2

## Структура проекта

```
.
├── main.py            # приложение FastAPI
├── requirements.txt   # зависимости
├── Dockerfile         # сборка образа
├── db.json            # создаётся автоматически при первом POST/DELETE
└── README.md
```

## Эндпоинты

| Метод  | Путь       | Параметр              | Описание                | Коды ответа |
|--------|------------|-----------------------|-------------------------|-------------|
| GET    | `/students`| —                     | Список всех студентов   | 200         |
| GET    | `/student` | `student_id` (query)  | Один студент по id      | 200, 404    |
| POST   | `/students`| тело: `Student`       | Создать студента        | 200, 422    |
| DELETE | `/students`| `student_id` (query)  | Удалить студента по id  | 200, 404    |

**Важно про параметры:**
- `GET /student` и `DELETE /students` принимают `student_id` как **query-параметр** — то есть в URL: `/student?student_id=1`, а не `/student/1`.
- `POST /students` принимает JSON в теле запроса.

### Модель студента

**Входная (`Student`)** — то, что отправляет клиент в POST:

```json
{
  "name": "Eugeni",
  "group": "507",
  "age": 22,
  "average_score": 4
}
```

**Выходная (`StudentOut`)** — то, что хранится и возвращается (с `id`):

```json
{
  "id": 1,
  "name": "Eugeni",
  "group": "507",
  "age": 22,
  "average_score": 4
}
```

**Поля:**
- `id` — присваивается сервером, уникален, не переиспользуется после удаления (вычисляется как `max(id) + 1`)
- `name` — строка
- `group` — строка
- `age` — целое
- `average_score` — целое или `null` (опционально, по умолчанию `null`)

⚠️ **Валидация сейчас минимальная:** Pydantic проверяет только **типы** (что `name` — строка, `age` — целое). Ограничения на диапазон (`age` от 16 до 100 и т.п.) не заданы, поэтому `age: 5` или `age: -100` пройдут.

### Примеры запросов

**Создать студента:**
```bash
curl -X POST http://localhost:8000/students \
  -H "Content-Type: application/json" \
  -d '{"name": "Eugeni", "group": "507", "age": 22, "average_score": 4}'
```

Ответ `200` — **входной объект без `id`** (так реализовано в коде: `return student`):
```json
{"name": "Eugeni", "group": "507", "age": 22, "average_score": 4}
```

⚠️ Сервер **не возвращает `id`** созданного студента. Чтобы узнать id — сделайте `GET /students` и посмотрите последний элемент.

**Получить всех:**
```bash
curl http://localhost:8000/students
```

**Получить одного (query-параметр):**
```bash
curl "http://localhost:8000/student?student_id=1"
```

**Удалить (query-параметр):**
```bash
curl -X DELETE "http://localhost:8000/students?student_id=1"
```

Ответ `200` — **обновлённый список** студентов (так реализовано в коде: `return students`):
```json
[]
```

Если `student_id` не найден — `404` с `{"detail": "Student not found"}`.

**Ошибка валидации** (например, `age: "abc"` вместо числа) — `422` от Pydantic.

## Установка и запуск (локально)

### 1. Клонировать репозиторий

```bash
git clone <url-репозитория>
cd <папка-проекта>
```

### 2. Создать виртуальное окружение (рекомендуется)

```bash
python -m venv .venv
```

Активировать:

- Linux / macOS:
  ```bash
  source .venv/bin/activate
  ```
- Windows (cmd):
  ```cmd
  .venv\Scripts\activate.bat
  ```
- Windows (PowerShell):
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

`requirements.txt` должен содержать:
```
fastapi
uvicorn[standard]
pydantic
```

### 4. Запустить сервер

```bash
uvicorn main:app --reload
```

- `main` — имя файла `main.py` без расширения
- `app` — переменная `FastAPI()` внутри файла
- `--reload` — авто-перезагрузка при изменении кода (только для разработки)

Сервер поднимется на `http://127.0.0.1:8000`.

### 5. Открыть документацию

- Swagger UI: **http://127.0.0.1:8000/docs**
- ReDoc: http://127.0.0.1:8000/redoc
- OpenAPI-спецификация: http://127.0.0.1:8000/openapi.json

В Swagger UI можно нажать «Try it out» на любом эндпоинте и отправить реальный запрос.

## Запуск в Docker

### 1. Собрать образ

```bash
docker build -t students-api .
```

### 2. Запустить контейнер

```bash
docker run -d -p 8000:80 --name students-app students-api
```

⚠️ **Обрати внимание на порты:** в контейнере uvicorn слушает **порт 80** (так указано в `CMD`), поэтому проброс — `-p 8000:80` (хост `8000` → контейнер `80`), а не `8000:8000`.

- `-d` — в фоне
- `-p 8000:80` — порт `8000` хоста → порт `80` контейнера
- `--name students-app` — имя контейнера

### 3. Проверить

Открыть **http://localhost:8000/docs** в браузере.

Или:
```bash
curl http://localhost:8000/students
```
Ожидается `[]` (пустой список — `db.json` в контейнере создаётся при первом POST/DELETE).

### 4. Логи, остановка, удаление

```bash
docker logs students-app        # логи uvicorn
docker stop students-app        # остановить
docker rm students-app          # удалить контейнер
```

Одной командой — остановить и удалить:
```bash
docker rm -f students-app
```

### ⚠️ Про сохранение данных в Docker

В текущем `Dockerfile` **нет `WORKDIR`**, поэтому файлы копируются в **корень контейнера** (`/main.py`, `/requirements.txt`), и `db.json` создаётся в **`/db.json`** внутри контейнера. При `docker rm` контейнера данные **теряются**.

Если нужно сохранять между перезапусками — используйте volume:

```bash
docker run -d -p 8000:80 -v $(pwd)/data:/data --name students-app students-api
```

Но тогда в коде путь к файлу должен быть `"/data/db.json"`, а не `"db.json"`. Сейчас код использует относительный путь, поэтому для сохранения данных потребуется правка кода. Для учебного проекта можно пропустить.

## Хранение данных

- При старте приложение читает `db.json` (если файла нет — начинает с пустого списка).
- Данные хранятся **в памяти** (список `students`).
- При POST и DELETE — синхронизируются в `db.json`.
- GET — только читает из памяти, файл не трогает.

**Ограничения:**
- Нет транзакционности: если запись в файл упадёт, память и файл разойдутся.
- Нет потокобезопасности: при одновременных запросах возможны гонки.
- Для учебного проекта этого достаточно; для продакшена нужна БД (PostgreSQL, SQLite).

## Тестирование через Swagger (чек-лист)

1. **POST `/students`** → тело `{"name": "Eugeni", "group": "507", "age": 22}` → ожидается `200` и объект **без `id`**.
2. **GET `/students`** → ожидается `[{"id": 1, "name": "Eugeni", ...}]` (тут `id` уже есть).
3. **GET `/student?student_id=1`** → ожидается один объект.
4. **GET `/student?student_id=999`** → ожидается `404`.
5. **POST `/students`** с `"age": "abc"` → ожидается `422` (валидация типа Pydantic).
6. **DELETE `/students?student_id=1`** → ожидается `200` и **обновлённый список**.
7. **DELETE `/students?student_id=999`** → ожидается `404`.

## Возможные проблемы

**`ModuleNotFoundError: No module named 'fastapi'`**
→ Не активировано виртуальное окружение или не выполнен `pip install -r requirements.txt`.

**`Address already in use` при запуске uvicorn**
→ Порт 8000 занят. Запустите на другом: `uvicorn main:app --port 8001`.

**В Docker: `localhost:8000/docs` не открывается**
→ Проверьте проброс портов: должно быть `-p 8000:80` (в контейнере uvicorn на порту 80). Если написать `-p 8000:8000` — не заработает, потому что в контейнере слушается 80.

**В Docker: `permission denied` при записи `db.json`**
→ В текущем `Dockerfile` нет `WORKDIR`, файлы в `/`. Запись в `/` обычно разрешена (контейнер запускается от `root`), но если вы добавите `USER` — упадёт. Решение: добавить `WORKDIR /app` в Dockerfile.

**Кириллица в `db.json` выглядит как `\u0415\u0432...`**
→ В `json.dump` не указан `ensure_ascii=False`. Сейчас в коде — `indent=4`, без `ensure_ascii=False`, поэтому кириллица будет экранирована. Это не ошибка, но файл менее читаем.

**`UnicodeDecodeError` при чтении `db.json` на Windows**
→ В `open(...)` не указан `encoding="utf-8"`. Сейчас в коде — без `encoding`, поэтому на Windows возможна проблема с кириллицей. Решение: добавить `encoding="utf-8"` в обе `open` (чтение и запись).

## Лицензия

Учебный проект. Используйте свободно.
