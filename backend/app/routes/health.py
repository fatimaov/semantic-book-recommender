from flask import Blueprint, jsonify


health = Blueprint("health", __name__, url_prefix="/api")


@health.get("/health")
def get_health():
    return jsonify(status="ok"), 200
