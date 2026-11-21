# Gradio Frontend

The frontend is being refactored into a lightweight Gradio client for the Flask
API. Recommendation retrieval, filtering, and ranking stay in Flask; Gradio
will handle user input and presentation.

## Structure

| Path | Purpose |
| --- | --- |
| `app.py` | Gradio application and Flask API event handlers |
| `config.py` | Gallery page size, category and tone choices, and asset paths |
| `services/recommendation_api.py` | Calls the Flask recommendations endpoint |
| `utils/gallery_formatter.py` | Gallery captions, descriptions, and missing-cover fallback |
| `assets/cover_not_found.png` | Placeholder cover image |
| `tests/test_recommendation_api.py` | Unit tests for the API client |

## Configuration

Set `FLASK_API_URL` to the Flask API base URL. For local development, copy the
root `.env.example` to `.env`; it includes the local default:

```dotenv
FLASK_API_URL=http://127.0.0.1:5000
```

The client loads the root `.env` file and appends `/api/recommendations` to the
configured base URL. For a deployed frontend, set `FLASK_API_URL` in the hosting
environment to the deployed Flask API base URL. Flask's `APP_ENV` controls the
backend retrieval configuration; the frontend does not use it to choose a data
source.

## API client

`fetch_recommendations` sends `query`, `top_k`, `category`, and `emotion` as JSON
to `POST /api/recommendations`. It returns the validated list of book records
and raises `RecommendationAPIError` for network failures, HTTP errors, and
invalid responses. The request uses a 5-second connection timeout and a
60-second response timeout.

See the [backend README](../backend/README.md) for the full API contract and
instructions for starting Flask locally.

## Start the frontend

Start the Flask backend in a separate terminal as described in the
[backend README](../backend/README.md), then run Gradio from the repository
root:

```bash
./.venv/Scripts/python.exe -m frontend.app
```

The frontend listens on Gradio's default local address. Its recommendation
requests go to the URL configured in `FLASK_API_URL`.

## Tests

From the repository root, run the frontend unit tests with the project
interpreter:

```bash
./.venv/Scripts/python.exe -m pytest frontend/tests/
```
