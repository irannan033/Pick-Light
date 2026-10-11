import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("pick_to_light.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS orders (
            mo TEXT PRIMARY KEY,
            style TEXT NOT NULL,
            description TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS trolleys (
            trolley_id TEXT PRIMARY KEY,
            mo TEXT NOT NULL,
            FOREIGN KEY(mo) REFERENCES orders(mo)
        );
        CREATE TABLE IF NOT EXISTS bins (
            bin_id TEXT PRIMARY KEY,
            material_code TEXT NOT NULL UNIQUE,
            material_name TEXT NOT NULL,
            current_stock INTEGER NOT NULL DEFAULT 0 CHECK(current_stock >= 0),
            low_stock_threshold INTEGER NOT NULL DEFAULT 5 CHECK(low_stock_threshold >= 0),
            controller_address TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS order_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mo TEXT NOT NULL,
            material_code TEXT NOT NULL,
            required_qty INTEGER NOT NULL CHECK(required_qty > 0),
            FOREIGN KEY(mo) REFERENCES orders(mo),
            FOREIGN KEY(material_code) REFERENCES bins(material_code),
            UNIQUE(mo, material_code)
        );
        CREATE TABLE IF NOT EXISTS pick_tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            trolley_id TEXT NOT NULL,
            mo TEXT NOT NULL,
            style TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            FOREIGN KEY(trolley_id) REFERENCES trolleys(trolley_id)
        );
        CREATE TABLE IF NOT EXISTS pick_task_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            bin_id TEXT NOT NULL,
            material_code TEXT NOT NULL,
            material_name TEXT NOT NULL,
            required_qty INTEGER NOT NULL,
            picked_qty INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'WAITING',
            FOREIGN KEY(task_id) REFERENCES pick_tasks(task_id),
            FOREIGN KEY(bin_id) REFERENCES bins(bin_id)
        );
        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bin_id TEXT NOT NULL,
            qty INTEGER NOT NULL CHECK(qty > 0),
            movement_type TEXT NOT NULL,
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(bin_id) REFERENCES bins(bin_id)
        );
        """)
        if db.execute("SELECT COUNT(*) FROM bins").fetchone()[0] == 0:
            db.executemany("INSERT INTO orders(mo,style,description) VALUES(?,?,?)", [
                ("MO-26001", "STY-ALPHA", "Demo shirt order"),
                ("MO-26002", "STY-BRAVO", "Demo trouser order")
            ])
            db.executemany("INSERT INTO bins(bin_id,material_code,material_name,current_stock,low_stock_threshold,controller_address) VALUES(?,?,?,?,?,?)", [
                ("BIN-A01", "MAT-BUTTON-WHT", "White button", 120, 20, "controller-1/output-1"),
                ("BIN-A02", "MAT-LABEL-CARE", "Care label", 8, 10, "controller-1/output-2"),
                ("BIN-B01", "STK-SIZE-M", "Size M sticker", 50, 10, "controller-1/output-3"),
                ("BIN-B02", "MAT-ZIP-BLK", "Black zipper", 80, 15, "controller-1/output-4")
            ])
            db.executemany("INSERT INTO trolleys(trolley_id,mo) VALUES(?,?)", [
                ("TRL-001", "MO-26001"), ("TRL-002", "MO-26002")
            ])
            db.executemany("INSERT INTO order_requirements(mo,material_code,required_qty) VALUES(?,?,?)", [
                ("MO-26001", "MAT-BUTTON-WHT", 12),
                ("MO-26001", "MAT-LABEL-CARE", 1),
                ("MO-26001", "STK-SIZE-M", 1),
                ("MO-26002", "MAT-ZIP-BLK", 1),
                ("MO-26002", "MAT-LABEL-CARE", 1)
            ])
