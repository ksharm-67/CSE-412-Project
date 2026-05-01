# RepairMatrix

Backend API for a device repair shop management system.

## Prerequisites

- PostgreSQL (running locally on `localhost:5432`)
- Python 3.10+
- `make`

Make sure your local PostgreSQL accepts password auth on `localhost` (the
default `pg_hba.conf` on most installs already does — `host ... 127.0.0.1/32 md5`).

## 1. Database setup

From the project root, run:

```bash
make setup_postgres
```

This will:

1. Create a `repairmatrix` PostgreSQL role with password `password123`.
2. Create a `repairmatrix` database owned by that role.
3. Create all tables (`customer`, `device`, `technician`, `part`, `repairorder`, `orderparts`).
4. Add primary keys and foreign-key relationships.

Other useful targets:

```bash
make clean_postgres   # drop all tables (keeps the database/user)
make drop_postgres    # drop the repairmatrix database AND role
```

## 2. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Not necessary to use a python virtual environment but I use WSL so I have to otherwise I cant install python packages for some reason.

The default DB URL is hard-coded in `backend/config.py`:

```
postgresql://repairmatrix:password123@localhost:5432/repairmatrix
```

You can override it by setting the `DATABASE_URL` environment variable.

## 3. Running the app

From the `backend/` folder with the venv activated:

```bash
python app.py
```

The Flask dev server will start on `http://127.0.0.1:5000`.

you can test the API with health endpoint:

```bash
curl http://127.0.0.1:5000/api/health
# {"status": "ok"}
```



### API endpoints

All endpoints are prefixed with `/api`:

- `/api/customers` — CRUD; `/customers/<id>/orders`, `/customers/<id>/devices`
- `/api/devices` — CRUD
- `/api/technicians` — CRUD; `/technicians/<id>/orders`, `/technicians/busiest`
- `/api/parts` — CRUD; `/parts/<id>/restock`
- `/api/orders` — CRUD; `/orders/<id>/status` (PATCH); `/orders/<id>/parts` (GET/POST/DELETE)

## 4. Running tests

The test suite uses an in-memory SQLite database, so no Postgres is needed
to run it.

```bash
cd backend
source venv/bin/activate
pytest tests/ -q
```

## Project layout

```
412project/
├── makefile                    # setup_postgres / clean_postgres / drop_postgres
├── setup_repairmatrix/         # SQL files for DB + schema setup
│   ├── create_db.sql           # creates repairmatrix role + database
│   ├── create_tables.sql
│   ├── add_relationships.sql
│   ├── drop_tables.sql
│   └── drop_db.sql
└── backend/
    ├── app.py                  # Flask entry point
    ├── config.py               # DATABASE_URL config
    ├── models.py               # SQLAlchemy models
    ├── routes/                 # API blueprints
    ├── tests/                  # pytest suite
    └── requirements.txt
```
