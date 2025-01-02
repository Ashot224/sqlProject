from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel
from typing import List, Union

app = FastAPI()

DATABASE = "theater.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def reset_ids(table_name: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create a temporary table to preserve data
        cursor.execute(f"""
            CREATE TEMPORARY TABLE temp_{table_name} AS SELECT * FROM {table_name};
        """)
        cursor.execute(f"DELETE FROM {table_name};")

        # Insert data back with sequential IDs
        columns_query = cursor.execute(f"PRAGMA table_info({table_name});").fetchall()
        columns = [col[1] for col in columns_query if col[1] != "id"]  # Skip the "id" column
        columns_str = ", ".join(columns)
        cursor.execute(f"""
            INSERT INTO {table_name} (id, {columns_str})
            SELECT ROW_NUMBER() OVER (ORDER BY id), {columns_str}
            FROM temp_{table_name};
        """)

        # Drop the temporary table
        cursor.execute(f"DROP TABLE temp_{table_name};")
        conn.commit()
        conn.close()
        return {"message": f"IDs for {table_name} table have been reset sequentially."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting IDs for {table_name}: {e}")

### ACTORS ###

class Actor(BaseModel):
    id: Union[int, None] = None
    name: str
    role_type: Union[str, None] = None
    age: int
    gender: str
    rank: Union[str, None] = None

@app.get("/actors/reset-ids/")
def reset_actor_ids():
    return reset_ids("actors")

@app.get("/actors/", response_model=List[Actor])
def get_actors():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM actors")
    actors = cursor.fetchall()
    conn.close()
    return [dict(actor) for actor in actors]

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

@app.get("/actors/filter/")
def get_filtered_actors(gender: str = "Male", min_age: int = 30, role_type: str = "Lead"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM actors 
        WHERE gender = ? AND age > ? AND role_type = ?
    """, (gender, min_age, role_type))
    actors = cursor.fetchall()
    conn.close()
    return [dict(actor) for actor in actors]


@app.get("/actors-with-roles/")
def get_actors_with_roles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            actors.id AS actor_id, 
            actors.name AS actor_name, 
            roles.name AS role_name, 
            roles.play AS play_name
        FROM actors
        JOIN performances ON actors.id = performances.actor_id
        JOIN roles ON performances.roles_id = roles.id
    """)
    results = cursor.fetchall()
    conn.close()
    return [dict(result) for result in results]

@app.put("/actors/update-rank/")
def update_actor_rank():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE actors
        SET rank = "Rank-1"
        WHERE role_type = "Villain" AND age < 40
    """)
    affected_rows = cursor.rowcount
    conn.commit()
    conn.close()
    return {"message": f"Updated rank for {affected_rows} actors"}

@app.get("/actors/group-by-age/")
def group_actors_by_age():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            CASE 
                WHEN age BETWEEN 18 AND 30 THEN '18-30'
                WHEN age BETWEEN 31 AND 50 THEN '31-50'
                ELSE '51+' 
            END AS age_group,
            COUNT(*) AS total_actors
        FROM actors
        GROUP BY age_group
    """)
    results = cursor.fetchall()
    conn.close()
    return [dict(result) for result in results]


@app.get("/actors/sorted/")
def get_sorted_actors(sort_by: str = "age", order: str = "asc"):
    if sort_by not in ["age", "rank"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT * FROM actors
        ORDER BY {sort_by} {order.upper()}
    """)
    actors = cursor.fetchall()
    conn.close()
    return [dict(actor) for actor in actors]


### ROLES ###

class Role(BaseModel):
    id: Union[int, None] = None
    name: str
    gender: Union[str, None] = None
    play: Union[str, None] = None

@app.get("/roles/reset-ids/")
def reset_role_ids():
    return reset_ids("roles")

@app.get("/roles/", response_model=List[Role])
def get_roles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    conn.close()
    return [dict(role) for role in roles]

@app.post("/roles/", response_model=Role)
def create_role(role: Role):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO roles (name, gender, play)
        VALUES (?, ?, ?)
    """, (role.name, role.gender, role.play))
    conn.commit()
    role_id = cursor.lastrowid
    conn.close()
    return {**role.dict(), "id": role_id}

@app.get("/roles/{role_id}", response_model=Role)
def get_role(role_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM roles WHERE id = ?", (role_id,))
    role = cursor.fetchone()
    conn.close()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return dict(role)

@app.delete("/roles/{role_id}")
def delete_role(role_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"detail": "Role deleted"}

### PERFORMANCES ###

class Performance(BaseModel):
    id: Union[int, None] = None
    date_: Union[str, None] = None
    director: Union[str, None] = None
    cast_number: int
    actor_id: int
    roles_id: int

@app.get("/performances/reset-ids/")
def reset_performance_ids():
    return reset_ids("performances")

@app.get("/performances/", response_model=List[Performance])
def get_performances():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM performances")
    performances = cursor.fetchall()
    conn.close()
    return [dict(performance) for performance in performances]

@app.post("/performances/", response_model=Performance)
def create_performance(performance: Performance):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO performances (date_, director, cast_number, actor_id, roles_id)
        VALUES (?, ?, ?, ?, ?)
    """, (performance.date_, performance.director, performance.cast_number, performance.actor_id, performance.roles_id))
    conn.commit()
    performance_id = cursor.lastrowid
    conn.close()
    return {**performance.dict(), "id": performance_id}

@app.get("/performances/{performance_id}", response_model=Performance)
def get_performance(performance_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM performances WHERE id = ?", (performance_id,))
    performance = cursor.fetchone()
    conn.close()
    if not performance:
        raise HTTPException(status_code=404, detail="Performance not found")
    return dict(performance)

@app.delete("/performances/{performance_id}")
def delete_performance(performance_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM performances WHERE id = ?", (performance_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Performance not found")
    return {"detail": "Performance deleted"}
