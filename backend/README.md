# Book recommender backend

The backend is a Flask application created by `create_app()`. It initializes
SQLAlchemy, migrations, and CORS, and currently exposes one endpoint:

- `GET /api/health` returns `{"status":"ok"}`.

The repository root `.env` file must contain `SUPABASE_DATABASE_URL` with the
connection string from Supabase. The Flask config also reads `APP_ENV`,
`FLASK_ENV`, `FLASK_DEBUG`, `CORS_ORIGINS`, `GOOGLE_API_KEY`, and
`GEMINI_EMBEDDING_MODEL`. The `Book` model is defined; embedding provider
selection and recommendation services are not implemented yet.

Use Python 3.11 or newer. The project's current virtual environment uses
Python 3.11.9.

## Start the server

From the repository root, activate the virtual environment and start Flask:

```bash
source .venv/bin/activate
python -m backend.run
```

The server runs at `http://127.0.0.1:5000`.

## Database migrations

Run these commands from the repository root with the virtual environment
activated and the database connection available:

```bash
# Generate a migration from model changes
flask --app backend.run db migrate -d backend/migrations -m "describe the change"

# Apply pending migrations
flask --app backend.run db upgrade -d backend/migrations

# Undo the latest migration
flask --app backend.run db downgrade -d backend/migrations -1
```

`migrate` creates a migration revision, `upgrade` applies pending revisions,
and `downgrade -1` reverses the latest applied revision.

## Check the health endpoint

In a second terminal, check the health endpoint:

```bash
curl -i http://127.0.0.1:5000/api/health
```

An HTTP `200` response with `{"status":"ok"}` confirms the app started and
the health route is responding.
