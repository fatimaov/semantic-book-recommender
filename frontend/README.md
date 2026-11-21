# Gradio Frontend

The frontend is being refactored into a lightweight Gradio client for the Flask
API. Recommendation retrieval, filtering, and ranking stay in Flask; Gradio
will handle user input and presentation.

## Structure

| Path | Purpose |
| --- | --- |
| `app.py` | Gradio application entry point (not wired up yet) |
| `config.py` | Frontend configuration (to be filled in as integration continues) |
| `services/recommendation_api.py` | Calls the Flask recommendations endpoint |
| `utils/gallery_formatter.py` | Gallery presentation helpers (to be implemented) |
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

## Tests

From the repository root, run the frontend unit tests with the project
interpreter:

```bash
./.venv/Scripts/python.exe -m pytest frontend/tests/
```

The Gradio UI is not connected to the API client yet, so the frontend app is not
ready to launch. The API client can be developed and tested independently.
