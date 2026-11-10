# Ollama + PostgreSQL (local SQL assistant)

Windows PowerShell:

```powershell
cd path\to\ollama-postgres-assistant
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
python app.py
```

Edit `.env` for the actual PostgreSQL host, port, database, schema, username and password.
Use a PostgreSQL account with `SELECT` only. A Python DB connection does **not** start or install PostgreSQL. If PostgreSQL is in Docker, publish port 5432 to the host and set `PGHOST=localhost`. Ollama runs on Windows using `localhost:11434`.

The app reads schema metadata from `information_schema`, requests SQL from local Ollama, validates for a single SELECT statement, displays the generated SQL and asks for approval before executing. PostgreSQL transactions are read-only. This is a learning lab, not a security-approved production database gateway. Test on synthetic/non-sensitive data only.
