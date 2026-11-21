from pathlib import Path

from flask import Blueprint, current_app


openapi = Blueprint("openapi", __name__, url_prefix="/api")
OPENAPI_SPEC_PATH = Path(__file__).resolve().parents[1] / "openapi.json"


@openapi.get("/openapi.json")
def get_openapi_spec():
    with OPENAPI_SPEC_PATH.open(encoding="utf-8") as spec_file:
        return current_app.response_class(
            spec_file.read(), mimetype="application/json"
        )
