#!/usr/bin/env python3

import asyncio
from fastapi import FastAPI, Request
from faker import Faker
import aiosqlite, random
from hashlib import md5
from os import path, remove
from shutil import rmtree
from montydb import set_storage, MontyClient

DB_FILENAME = 'vfapi'
app, fake = FastAPI(), Faker()
set_storage(
        repository=f'{DB_FILENAME}.nosql.db',
        storage='sqlite',
        use_bson=False
        )
db_client = MontyClient(
        f"{DB_FILENAME}.nosql.db",
        synchronous=1,
        automatic_index=False,
        busy_timeout=5000
        )

async def get_sql_db():
    db = await aiosqlite.connect(database=f'{DB_FILENAME}.sql.db')
    return db

async def init_sql_db():
    if path.isfile(f'{DB_FILENAME}.sql.db'):
        remove(f'{DB_FILENAME}.sql.db')
    db = await get_sql_db()
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

async def init_nosql_db():
    if path.isdir(f'{DB_FILENAME}.nosql.db'):
        rmtree(f'{DB_FILENAME}.nosql.db')
    users = db_client.vfapi.users
    data = await run_sql_query('SELECT * FROM USERS;')
    for user in data['users']:
        users.insert_one({
            'id': user[0],
            'name': user[1],
            'username': user[2],
            'address': user[4],
            'email': user[5],
            'phone': user[6]
            })

async def init_db():
    await init_sql_db()
    await init_nosql_db()

async def run_sql_query(query):
    try:
        db = await get_sql_db()
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
        await init_db()
        return run_sql_query(query)

def get_nosql_users(query):
    users = db_client.vfapi.users
    user_data = tuple(users.find(query))
    for data in user_data: data.pop('_id')
    return {'users': tuple(user_data)}

@app.get('/')
def root():
    return {'goto': '/docs'}

@app.get('/select')
async def sql_return_users(username: str):
    resp = await run_sql_query(f'SELECT * FROM users WHERE username = "{username}"')
    return resp

@app.post('/find')
async def nosql_return_users(request: Request):
    query = await request.json()
    return get_nosql_users(query)

if __name__ == '__main__':
    asyncio.run(init_db()); __import__('uvicorn').run('main:app', port=8888, reload=False)
