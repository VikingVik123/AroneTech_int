# Basic Flask App

This is a basic web app built with Flask, it handles user registeration and login

## Setup

1. clone the repo
2. cd into the directory with 'cd <repo name>'
3. install postgresql and psycopg2-binary
4. open the psql shell with "psql -h localhost -U postgres"
5. create a database, use the command "CREATE DATABASE your_db_name;"
6. exit the shell
7. generate a secret key with
    import secrets
    secrets.token_urlsafe(32)
8. create a .env file and populate it with
    DATABASE_URL=postgresql://postgres:password@localhost:port/your_db_name
    SECRET_KEY="your secret key"
9. on the project root dir run "gunicorn --workers 4 --bind 0.0.0.0:5000 main:app"

## Routes
1. /register
2. /login
3. /dashboard