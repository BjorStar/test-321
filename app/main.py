from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.db import get_conn, create_schema

app = FastAPI()

✅ ADD THIS (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],  # allow all for now
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=["*"],
)

Create tables
create_schema()


Get user from API key
def get_user_id(api_key):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM users WHERE api_key = %s",
            (api_key,)
        )
        user = cur.fetchone()
        return user["id"] if user else None


ROOT
@app.get("/")
def root():
    return {"message": "API is running"}


GET /todos
@app.get("/todos")
def get_todos(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    user_id = get_user_id(x_api_key)
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid API key")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT t.id, t.text, t.done, c.name AS category
            FROM todos t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = %s
        """, (user_id,))
        rows = cur.fetchall()

    return rows


POST /todos
@app.post("/todos")
def create_todo(todo: dict, x_api_key: str = Header(None)):
    user_id = get_user_id(x_api_key)
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid API key")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO todos (text, done, user_id, category_id)
            VALUES (%s, %s, %s, %s)
        """, (todo["text"], False, user_id, todo["category_id"]))

    return {"message": "Todo created"}
PUT /todos/{id}
@app.put("/todos/{id}")
def update_todo(id: int, todo: dict, x_api_key: str = Header(None)):
    user_id = get_user_id(x_api_key)
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid API key")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE todos
            SET text = %s, done = %s
            WHERE id = %s AND user_id = %s
        """, (todo["text"], todo["done"], id, user_id))

    return {"message": "Updated"}


DELETE /todos/{id}
@app.delete("/todos/{id}")
def delete_todo(id: int, x_api_key: str = Header(None)):
    user_id = get_user_id(x_api_key)
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid API key")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM todos WHERE id = %s AND user_id = %s",
            (id, user_id)
        )

    return {"message": "Deleted"}
