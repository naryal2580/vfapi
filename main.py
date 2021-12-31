#!/usr/bin/env python3

from typing import Optional, Any
import asyncio
from fastapi import FastAPI, Request
from faker import Faker
import aiosqlite, random
from hashlib import md5
from os import path, remove
from shutil import rmtree
from montydb import set_storage, MontyClient
from pydantic import BaseModel

class User(BaseModel):
    name: str
    username: str
    address: str
    email: str
    password: str
    contact: str

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
            ) ;
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
            'contact': user[6]
            })

async def init_db():
    await init_sql_db()
    await init_nosql_db()

async def run_sql_query(query, commit=False):
    try:
        db = await get_sql_db()
        cursor = await db.execute(query)
        _data, data = await cursor.fetchall(), {}
        if commit: await db.commit()
        await cursor.close()
        await db.close()
        if len(_data) == 1:
            if len(_data[0]) == 1 and type(_data[0][0]) == int:
                return _data[0][0]
            _data = _data[0]
            data['id'] = _data[0]
            data['name'] = _data[1]
            data['username'] = _data[2]
            data['address'] = _data[4]
            data['email'] = _data[5]
            data['contact'] = _data[6]
            return data
        return {'users': _data}
    except KeyboardInterrupt as e:
    # except Exception as e:
        print(e)
        await init_db()
        return await run_sql_query(query)

def get_nosql_users(query):
    users = db_client.vfapi.users
    user_data = tuple(users.find(query))
    for data in user_data: data.pop('_id'); data.pop('password')
    if len(user_data) == 1: return user_data[0]
    return tuple(user_data)

@app.get('/')
def root():
    return {'goto': '/docs'}

@app.get('/select')
async def sql_return_users_from_username(username: str):
    resp = await run_sql_query(f'SELECT * FROM users WHERE username = "{username}";')
    return resp

@app.put('/user')
async def put_user(user: User):
    user.password = md5(user.password.encode()).hexdigest()
    query = f'''
INSERT INTO users (
                    name,
                    username,
                    password,
                    address,
                    email,
                    contact
                ) VALUES ( 
                            "{user.name}",
                            "{user.username}",
                            "{user.password}",
                            "{user.address}",
                            "{user.email}",
                            "{user.contact}"
                            );
'''[1:-1]
    await run_sql_query(query, commit=True)
    _id = await run_sql_query('SELECT id from users ORDER BY ROWID DESC limit 1;')
    db_client.vfapi.users.insert_one({
        'id': _id,
        'name': user.name,
        'username': user.username,
        'password': user.password,
        'address': user.address,
        'email': user.email,
        'contact': user.contact
        })
    return {'resp': 'done'}

@app.get('/find')
async def nosql_return_users_from_username(username: str):
    return get_nosql_users({'username': username})

@app.post('/find')
async def nosql_return_users(request: Request):
    query = await request.json()
    return get_nosql_users(query)

@app.delete('/user')
async def delete_user(username: Optional[str] = '', user: Optional[User] = None):
    if username:
        db_client.vfapi.users.delete_one({'username': username})
        await run_sql_query(f'DELETE FROM users WHERE username = "{username}";', commit=True)
        return {'resp': 'done'}
    elif user:
        db_client.vfapi.users.delete_one({'id': user.id})
        await run_sql_query(f'DELETE FROM users WHERE id = {user.id};', commit=True)
    return {'resp': '!done'}

if __name__ == '__main__':
    asyncio.run(init_db()); __import__('uvicorn').run('main:app', port=8888, reload=False)
