import os, sqlite3, time
from flask import Flask, jsonify, render_template, request

DB_PATH = os.environ.get("DB_PATH", "tasks.db")
app = Flask(__name__)


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            est_minutes INTEGER DEFAULT 25,
            spent_seconds INTEGER DEFAULT 0,
            started_at REAL,
            done INTEGER DEFAULT 0)""")


def to_dict(r):
    d = dict(r)
    live = int(time.time() - d["started_at"]) if d["started_at"] else 0
    d["total_seconds"] = d["spent_seconds"] + live
    d["running"] = d["started_at"] is not None
    return d


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/api/tasks", methods=["GET", "POST"])
def tasks():
    with db() as c:
        if request.method == "POST":
            j = request.get_json(force=True)
            title = (j.get("title") or "").strip()
            if not title:
                return jsonify(error="title required"), 400
            c.execute("INSERT INTO tasks (title, category, est_minutes) VALUES (?,?,?)",
                      (title, j.get("category") or "General", int(j.get("est_minutes") or 25)))
        rows = c.execute("SELECT * FROM tasks ORDER BY done, id DESC").fetchall()
    return jsonify([to_dict(r) for r in rows])


def _stop_running(c, task_id=None):
    q = "SELECT * FROM tasks WHERE started_at IS NOT NULL"
    for r in c.execute(q).fetchall():
        if task_id is None or r["id"] == task_id:
            spent = r["spent_seconds"] + int(time.time() - r["started_at"])
            c.execute("UPDATE tasks SET spent_seconds=?, started_at=NULL WHERE id=?", (spent, r["id"]))


@app.route("/api/tasks/<int:tid>/start", methods=["POST"])
def start(tid):
    with db() as c:
        _stop_running(c)  # only one timer at a time
        c.execute("UPDATE tasks SET started_at=? WHERE id=? AND done=0", (time.time(), tid))
    return jsonify(ok=True)


@app.route("/api/tasks/<int:tid>/stop", methods=["POST"])
def stop(tid):
    with db() as c:
        _stop_running(c, tid)
    return jsonify(ok=True)


@app.route("/api/tasks/<int:tid>/done", methods=["POST"])
def done(tid):
    with db() as c:
        _stop_running(c, tid)
        c.execute("UPDATE tasks SET done=1 WHERE id=?", (tid,))
    return jsonify(ok=True)


@app.route("/api/tasks/<int:tid>", methods=["DELETE"])
def delete(tid):
    with db() as c:
        c.execute("DELETE FROM tasks WHERE id=?", (tid,))
    return jsonify(ok=True)


@app.route("/api/summary")
def summary():
    with db() as c:
        rows = [to_dict(r) for r in c.execute("SELECT * FROM tasks").fetchall()]
    by_cat = {}
    for r in rows:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + r["total_seconds"]
    return jsonify(total_seconds=sum(r["total_seconds"] for r in rows),
                   done=sum(r["done"] for r in rows), tasks=len(rows), by_category=by_cat)


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
