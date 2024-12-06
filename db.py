import sqlite3

def initialize_database():
    conn = sqlite3.connect("theater.db")
    cursor = conn.cursor()

    # Create the roles table first
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name varchar(100) NOT NULL,
            gender varchar(25),
            play varchar(50)
        )
    """)

    # Create the actors table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name varchar(100) NOT NULL,
            role_type varchar(100),
            age INTEGER,
            gender varchar(25),
            rank varchar(50)
        )
    """)

    # Create the performances table that references roles and actors
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_ DATE,
            director varchar(100),
            cast_number INTEGER,
            actor_id INTEGER,
            roles_id INTEGER,
            FOREIGN KEY (actor_id) REFERENCES actors(id),
            FOREIGN KEY (roles_id) REFERENCES roles(id)
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
