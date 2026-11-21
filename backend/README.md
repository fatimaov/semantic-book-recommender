# Flask API

The Flask backend exposes a health check and semantic book recommendations.
See the root README for the project overview and data preparation workflow.

## Deployed API

The backend app is deployed on Render. Visit the [interactive API documentation](https://semantic-book-recommender-4tbl.onrender.com/api/docs/). The backend runs on Render's free tier, so its first request may take 30–60 seconds.

## Configuration

Create a root `.env` file from `.env.example` and set `APP_ENV`:

| `APP_ENV` | Embeddings and retrieval | Search logging |
| --- | --- | --- |
| `local` | Hugging Face + ChromaDB | Disabled |
| `production` | Gemini + Supabase pgvector | Enabled |

`APP_ENV=production` can also be used when running locally; searches will then
be logged to Supabase. If `APP_ENV` is omitted, the backend defaults to
`production`.

The Flask app initializes SQLAlchemy in both modes, so `SUPABASE_DATABASE_URL`
must be set. Local recommendations use Chroma and do not connect to Supabase.
Production also requires `GOOGLE_API_KEY` and `GEMINI_EMBEDDING_MODEL`.

Local retrieval requires the Chroma collection and
`data/books_with_emotions.csv`. The root README explains how to prepare these
data files.

## Start the server

From the repository root, activate the virtual environment, install the
dependencies, and start Flask:

```bash
source .venv/Scripts/activate
pip install -r requirements.txt
python -m backend.run
```

The API runs at `http://127.0.0.1:5000`.

## API documentation

The interactive Swagger UI is available at
`http://127.0.0.1:5000/api/docs/`. The OpenAPI 3.0.3 document is served at
`http://127.0.0.1:5000/api/openapi.json` and describes the health and
recommendations endpoints, request fields, response schemas, and error codes.

## Endpoints

### Health

```bash
curl -i http://127.0.0.1:5000/api/health
```

Returns `{"status":"ok"}` when the server is responding.

### Recommendations

`POST /api/recommendations`

| Field | Validation | Default |
| --- | --- | --- |
| `query` | Required, non-empty string | — |
| `top_k` | Integer from 1 to 250 | `250` |
| `category` | `All`, `Fiction`, `Nonfiction`, `Children's Fiction`, or `Children's Nonfiction` | `All` |
| `emotion` | `All`, one of the seven emotion labels, or a Gradio tone label | `All` |

Emotion labels: `Anger`, `Disgust`, `Fear`, `Joy`, `Sadness`, `Surprise`,
`Neutral`. Gradio tone labels: `Happy`, `Surprising`, `Angry`, `Suspenseful`,
`Sad`.

Example request:

```bash
curl -X POST http://127.0.0.1:5000/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{"query":"A story about friendship and adventure","top_k":50,"category":"Fiction","emotion":"Happy"}'
```

The response has the form `{"recommendations": [...], "total": 1}` and contains
up to 240 recommendations from the retrieved candidates. Each recommendation
includes `isbn13`, `title_and_subtitle`, `authors`, `thumbnail`,
`description`, `simple_categories`, `published_year`, `average_rating`, the
seven emotion scores, and `similarity_score`. A search with no matches returns
HTTP 200 with an empty recommendation list.

Invalid requests return HTTP 400. Provider or database availability failures
return HTTP 503; unexpected failures return HTTP 500. Internal exception
details are not included in responses. Search events are logged only in
production; a logging failure does not block recommendations.

## Database migrations

Run these commands from the repository root with the database connection
configured:

```bash
# Generate a migration from model changes
flask --app backend.run db migrate -d backend/migrations -m "describe the change"

# Apply pending migrations
flask --app backend.run db upgrade -d backend/migrations

# Undo the latest migration
flask --app backend.run db downgrade -d backend/migrations -1
```

## Tests

From the repository root, run the backend tests with the project interpreter:

```bash
./.venv/Scripts/python.exe -m pytest backend/tests/
```
