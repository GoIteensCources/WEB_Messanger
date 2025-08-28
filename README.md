# Online Messenger

Це реальний месенджер, де користувачі можуть додавати друзів і спілкуватися.

## create .env

    DB_USER = <postgres_user>
    DB_PASSWORD = <postgres_passw>
    DATABASE_NAME = <database_name>

    SECRET_KEY = <your_secret_key>

## create database

1) **Postgres**: 
```
python3 pg_create_database.py
```
2)  **sqlite**
```
python3 sqlite_create_database.py
```

## Необхідні бібліотеки:
 - Flask
 - Flask-SQLAlchemy
 - Flask-Login
 - Flask-WTF

`pip install -r requirements.txt`
