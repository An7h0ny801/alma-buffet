from flask import Blueprint, jsonify


salud_bp = Blueprint("salud", __name__)


@salud_bp.route("/salud")
def estado():
    return jsonify(estado="ok")
