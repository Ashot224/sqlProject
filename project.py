from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel
from typing import List, Union

app = FastAPI()

# Модель для данных об актерах
class Actor(BaseModel):
    id: Union[int, None] = None
    name: str
    role_type: Union[str, None] = None
    age: int
    gender: str
    rank: Union[str, None] = None

DATABASE = "theater.db"

# Функция для подключения к базе
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Получение всех актеров
@app.get("/actors/", response_model=List[Actor])
def get_actors():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM actors")
    actors = cursor.fetchall()
    conn.close()
    return [dict(actor) for actor in actors]

# Добавление нового актера
@app.post("/actors/", response_model=Actor)
def create_actor(actor: Actor):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO actors (name, role_type, age, gender, rank) 
        VALUES (?, ?, ?, ?, ?)
    """, (actor.name, actor.role_type, actor.age, actor.gender, actor.rank))
    conn.commit()
    actor_id = cursor.lastrowid
    conn.close()
    return {**actor.dict(), "id": actor_id}

# Получение актера по ID
@app.get("/actors/{actor_id}", response_model=Actor)
def get_actor(actor_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM actors WHERE id = ?", (actor_id,))
    actor = cursor.fetchone()
    conn.close()
    if not actor:
        raise HTTPException(status_code=404, detail="Actor not found")
    return dict(actor)

# Удаление актера
@app.delete("/actors/{actor_id}")
def delete_actor(actor_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM actors WHERE id = ?", (actor_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Actor not found")
    return {"detail": "Actor deleted"}
