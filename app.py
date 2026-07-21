import json
import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request

from analysis import find_food_symptom_rules

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "entries.json")


def load_entries():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_entries(entries):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/entries", methods=["GET"])
def get_entries():
    entries = load_entries()
    entries.sort(key=lambda e: e["date"], reverse=True)
    return jsonify(entries)


@app.route("/api/entries", methods=["POST"])
def add_entry():
    data = request.get_json()
    entries = load_entries()

    next_id = max((e["id"] for e in entries), default=0) + 1
    entry = {
        "id": next_id,
        "date": data.get("date") or datetime.now().isoformat(timespec="minutes"),
        "foods": [f.strip().lower() for f in data.get("foods", []) if f.strip()],
        "symptoms": [s.strip().lower() for s in data.get("symptoms", []) if s.strip()],
    }
    entries.append(entry)
    save_entries(entries)
    return jsonify(entry), 201


@app.route("/api/entries/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    entries = load_entries()
    entries = [e for e in entries if e["id"] != entry_id]
    save_entries(entries)
    return "", 204


@app.route("/api/analysis", methods=["GET"])
def get_analysis():
    entries = load_entries()
    return jsonify(find_food_symptom_rules(entries))


if __name__ == "__main__":
    app.run(debug=True)
