#!/usr/bin/env python3

import asyncio
from fastapi import FastAPI
from faker import Faker
import aiosqlite, random
from hashlib import md5
from os import path, remove

DB_FILENAME = 'vfapi.db'
app = FastAPI()
fake = Faker()

async def get_db():
    db = await aiosqlite.connect(database=DB_FILENAME)
    return db

async def init_db():
    if path.isfile(DB_FILENAME):
        remove(DB_FILENAME)
    db = await get_db()
    await db.execute('''
CREATE TABLE users ( id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     username TEXT NOT NULL,
                     password TEXT NOT NULL,
                     address TEXT NOT NULL,
                     email TEXT NOT NULL,
                     contact TEXT NOT NULL
                     );'''[1:])
    await db.commit()
    for _ in range(random.randint(7, 84)):
        query = f'''
INSERT INTO users ( name,
                    username,
                    password,
                    address,
                    email,
                    contact
                    )
       VALUES (
                "{fake.name()}",
                "{fake.user_name()}",
                "{md5(fake.password().encode()).hexdigest()}",
                "{fake.address()}",
                "{fake.email()}",
                "{fake.phone_number()}"
            );
'''[1:-1]
        await db.execute(query)
        await db.commit()
    await db.close()
    return True

async def run_query(query):
    try:
        db = await get_db()
        cursor = await db.execute(query)
        _data, data = await cursor.fetchall(), {}
        await cursor.close()
        await db.close()
        if len(_data) == 1:
            _data = _data[0]
            data['id'] = _data[0]
            data['name'] = _data[1]
            data['username'] = _data[2]
            data['address'] = _data[4]
            data['email'] = _data[5]
            data['phone'] = _data[6]
            return data
        return {'users': _data}
    except Exception as e:
        # print(repr(e))
        await init_db()
        return run_query(query)

@app.get('/')
def root():
    return {'goto': '/docs'}

@app.get('/get')
async def return_user(username: str):
    resp = await run_query(f'SELECT * FROM users WHERE username = "{username}"')
    return resp

if __name__ == '__main__':
    asyncio.run(init_db()); __import__('uvicorn').run('main:app', port=8888, reload=False)
