#!/usr/bin/env python3

from fastapi import FastAPI
import mysql.connector

app = FastAPI()

def init_db():
    global db
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="toor",
        database="testdb"
    )

def run_query(query):
    try:
        cursor = db.cursor()
        cursor.execute(query)
        resp = cursor.fetchall()
        return dict(resp)
    except Exception as e:
        # print(repr(e))
        init_db()
        return run_query(query)

@app.get('/')
def root():
    return {'goto': '/docs'}

@app.get('/user')
def return_user(username: str):
    return run_query(f'SELECT * FROM users WHERE name = "{username}"')

if __name__ == '__main__':
    init_db(); __import__('uvicorn').run('main:app', port=8888, reload=False)
