from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import init_db, get_db
import hardware

app = Flask(__name__)
app.secret_key = "change-this-before-production"
init_db()

def low_stock(current, threshold):
    return current <= threshold

@app.get("/")
def dashboard():
    with get_db() as db:
        bins = db.execute("SELECT * FROM bins ORDER BY bin_id").fetchall()
        tasks = db.execute("SELECT * FROM pick_tasks ORDER BY task_id DESC LIMIT 10").fetchall()
        active = db.execute("SELECT * FROM pick_tasks WHERE status='ACTIVE' ORDER BY task_id DESC LIMIT 1").fetchone()
        lines = []
        if active:
            lines = db.execute("""
                SELECT ptl.*, b.current_stock, b.low_stock_threshold, b.bin_id
                FROM pick_task_lines ptl JOIN bins b ON b.bin_id=ptl.bin_id
                WHERE ptl.task_id=? ORDER BY ptl.id
            """, (active["task_id"],)).fetchall()
    return render_template("index.html", bins=bins, tasks=tasks, active=active, lines=lines,
                           low_stock=low_stock, light_state=hardware.get_light_state)

@app.post("/start")
def start_task():
    trolley_id = request.form.get("trolley_id", "").strip().upper()
    if not trolley_id:
        flash("Enter a trolley ID.", "error")
        return redirect(url_for("dashboard"))
    with get_db() as db:
        trolley = db.execute("""
            SELECT t.trolley_id, o.mo, o.style
            FROM trolleys t JOIN orders o ON o.mo=t.mo WHERE t.trolley_id=?
        """, (trolley_id,)).fetchone()
        if not trolley:
            flash(f"Trolley {trolley_id} was not found in the database.", "error")
            return redirect(url_for("dashboard"))
        existing = db.execute("SELECT task_id FROM pick_tasks WHERE trolley_id=? AND status='ACTIVE'", (trolley_id,)).fetchone()
        if existing:
            flash(f"Trolley already has active task #{existing['task_id']}.", "error")
            return redirect(url_for("dashboard"))
        cur = db.execute("INSERT INTO pick_tasks(trolley_id,mo,style,status) VALUES(?,?,?,'ACTIVE')",
                         (trolley["trolley_id"], trolley["mo"], trolley["style"]))
        task_id = cur.lastrowid
        reqs = db.execute("""
            SELECT r.required_qty, b.bin_id, b.material_code, b.material_name,
                   b.current_stock, b.low_stock_threshold
            FROM order_requirements r JOIN bins b ON b.material_code=r.material_code
            WHERE r.mo=? ORDER BY b.bin_id
        """, (trolley["mo"],)).fetchall()
        if not reqs:
            db.execute("UPDATE pick_tasks SET status='ERROR' WHERE task_id=?", (task_id,))
            flash("No material requirements are configured for this MO.", "error")
            return redirect(url_for("dashboard"))
        for item in reqs:
            status = "WAITING"
            db.execute("""INSERT INTO pick_task_lines
                (task_id,bin_id,material_code,material_name,required_qty,status)
                VALUES(?,?,?,?,?,?)""",
                (task_id, item["bin_id"], item["material_code"], item["material_name"], item["required_qty"], status))
            hardware.activate_light(item["bin_id"], low_stock(item["current_stock"], item["low_stock_threshold"]))
    flash(f"Task #{task_id} started for {trolley_id}. Required pick lights are active.", "success")
    return redirect(url_for("dashboard"))

@app.post("/confirm/<int:line_id>")
def confirm_pick(line_id):
    with get_db() as db:
        line = db.execute("""
            SELECT ptl.*, pt.status AS task_status, b.current_stock
            FROM pick_task_lines ptl JOIN pick_tasks pt ON pt.task_id=ptl.task_id
            JOIN bins b ON b.bin_id=ptl.bin_id WHERE ptl.id=?
        """, (line_id,)).fetchone()
        if not line or line["task_status"] != "ACTIVE":
            flash("Pick line not found or task is not active.", "error")
            return redirect(url_for("dashboard"))
        if line["status"] == "CONFIRMED":
            flash("This pick has already been confirmed.", "error")
            return redirect(url_for("dashboard"))
        if line["current_stock"] < line["required_qty"]:
            flash("Insufficient stock. Restock this bin before confirming the pick.", "error")
            return redirect(url_for("dashboard"))
        db.execute("UPDATE bins SET current_stock=current_stock-? WHERE bin_id=?",
                   (line["required_qty"], line["bin_id"]))
        db.execute("INSERT INTO stock_movements(bin_id,qty,movement_type,note) VALUES(?,?,?,?)",
                   (line["bin_id"], line["required_qty"], "PICK", f"Task line {line_id}"))
        db.execute("UPDATE pick_task_lines SET picked_qty=required_qty,status='CONFIRMED' WHERE id=?", (line_id,))
        remaining = db.execute("SELECT COUNT(*) FROM pick_task_lines WHERE task_id=? AND status!='CONFIRMED'",
                               (line["task_id"],)).fetchone()[0]
        if remaining == 0:
            db.execute("UPDATE pick_tasks SET status='COMPLETED', completed_at=CURRENT_TIMESTAMP WHERE task_id=?",
                       (line["task_id"],))
            flash("All picks confirmed. Trolley task completed; hub is ready for the next trolley.", "success")
        else:
            flash("Pick confirmed.", "success")
        stock = db.execute("SELECT current_stock,low_stock_threshold FROM bins WHERE bin_id=?", (line["bin_id"],)).fetchone()
        if low_stock(stock["current_stock"], stock["low_stock_threshold"]):
            hardware.activate_light(line["bin_id"], True)
        else:
            hardware.turn_off_light(line["bin_id"])
    return redirect(url_for("dashboard"))

@app.post("/restock")
def restock():
    bin_id = request.form.get("bin_id", "")
    try:
        qty = int(request.form.get("qty", "0"))
    except ValueError:
        qty = 0
    if qty <= 0:
        flash("Restock quantity must be a positive whole number.", "error")
        return redirect(url_for("dashboard"))
    with get_db() as db:
        row = db.execute("SELECT bin_id FROM bins WHERE bin_id=?", (bin_id,)).fetchone()
        if not row:
            flash("Bin not found.", "error")
            return redirect(url_for("dashboard"))
        db.execute("UPDATE bins SET current_stock=current_stock+? WHERE bin_id=?", (qty, bin_id))
        db.execute("INSERT INTO stock_movements(bin_id,qty,movement_type,note) VALUES(?,?,?,?)",
                   (bin_id, qty, "RESTOCK", request.form.get("note", "").strip()))
        stock = db.execute("SELECT current_stock,low_stock_threshold FROM bins WHERE bin_id=?", (bin_id,)).fetchone()
        if not low_stock(stock["current_stock"], stock["low_stock_threshold"]):
            hardware.turn_off_light(bin_id)
        flash(f"Restocked {bin_id} by {qty} units.", "success")
    return redirect(url_for("dashboard"))

@app.get("/api/bins")
def api_bins():
    with get_db() as db:
        rows = db.execute("SELECT * FROM bins ORDER BY bin_id").fetchall()
    return jsonify([dict(r) | {"low_stock": low_stock(r["current_stock"], r["low_stock_threshold"]),
                               "light_state": hardware.get_light_state(r["bin_id"])} for r in rows])

@app.get("/health")
def health():
    return {"status": "ok", "service": "pick-to-light"}, 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
