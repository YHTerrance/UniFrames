from fastapi import APIRouter
import sqlite3
import os

dbrouter = APIRouter()

def get_conn():
    db_path = os.getenv("UNIV_DB_PATH", "univ.db")  
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@dbrouter.post("/add/{val}")
def add_item(val: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, value TEXT)")
    cur.execute("INSERT INTO items (value) VALUES (?)", (val,))
    conn.commit()
    conn.close()
    return {"message": f"{val} ADD"}

@dbrouter.get("/list")
def list_items():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items")
    rows = cur.fetchall()
    conn.close()
    return {"items": rows}

@dbrouter.delete("/delete/{item_id}")
def delete_item(item_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return {"message": f"id={item_id} DEL"}

