## FastAPI Quiz App Backend

Простий бекенд на FastAPI з endpoint для перевірки справності.

### Встановлення та налаштування

1. **Клонування репозиторію**
   \`\`\`bash
   git clone <URL_твого_репозиторію>
   cd Quiz-App-BE
   \`\`\`

2. **Встановлення Poetry** (якщо ще не встановлено)
   \`\`\`bash
   curl -sSL https://install.python-poetry.org | python3 -
   \`\`\`

3. **Встановлення залежностей**
   \`\`\`bash
   poetry install
   \`\`\`

4. **Активація віртуального середовища**
   \`\`\`bash
   poetry shell
   \`\`\`

5. **Налаштування .env**

   Створи файл .env у корені проєкту:

   PORT=8000

   POSTGRES_USER=admin
   POSTGRES_PASSWORD=admin
   POSTGRES_DB=quiz_app

   DATABASE_URL=postgresql+asyncpg://admin:admin@db:5432/quiz_app
   REDIS_URL=redis://redis:6379/0

   ALLOWED_ORIGINS=http://localhost:3000

### Запуск додатку

Запуск через Docker Compose
docker compose up --build

Сервіси, які будуть запущені:
   backend – FastAPI застосунок
   db – PostgreSQL
   redis – Redis

Після запуску бекенд буде доступний за адресою:
👉 http://localhost:8000

### Перевірка роботи

**Тестування endpoint \`/\`:**
\`\`\`bash
curl http://127.0.0.1:8000/
\`\`\`

**Очікуваний результат:**
\`\`\`json
{"status_code": 200, "detail": "ok", "result": "working"}
\`\`\`

🧰 Інструменти розробки
   Poetry – менеджер залежностей
   Ruff – linting
   Black – автоформатування
   Pytest – тестування
   Uvicorn – сервер