from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

# Подключение к базе данных
conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB", "polls"),
    user=os.getenv("POSTGRES_USER", "user"),
    password=os.getenv("POSTGRES_PASSWORD", "password"),
    host=os.getenv("DB_HOST", "db")
)
cur = conn.cursor()

# Создание таблицы, если не существует
cur.execute('''
    CREATE TABLE IF NOT EXISTS votes (
        id SERIAL PRIMARY KEY,
        option TEXT NOT NULL
    )
''')
conn.commit()

class Vote(BaseModel):
    option: str

@app.get("/")
def read_root():
    return {"message": "Polling API is up"}

@app.post("/vote/")
def vote(v: Vote):
    cur.execute("INSERT INTO votes (option) VALUES (%s)", (v.option,))
    conn.commit()
    return {"message": f"Vote for {v.option} recorded"}

@app.get("/results/")
def results():
    cur.execute("SELECT option, COUNT(*) FROM votes GROUP BY option")
    data = cur.fetchall()
    return {"results": dict(data)}
