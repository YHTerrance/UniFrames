from fastapi import APIRouter
import sqlite3

db_router = APIRouter()

def get_conn():
    return sqlite3.connect("univ.db")

@db_router.post("/add/{val}")
def add_item(val: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, value TEXT)")
    cur.execute("INSERT INTO items (value) VALUES (?)", (val,))
    conn.commit()
    conn.close()
    return {"message": f"{val} ADD"}

@db_router.get("/list")
def list_items():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items")
    rows = cur.fetchall()
    conn.close()
    return {"items": rows}

@db_router.delete("/delete/{item_id}")
def delete_item(item_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return {"message": f"id={item_id} DEL"}
