# Hardware Storage System

A DBMS-driven information system for managing a hardware storage / inventory
business. Built with **Python + Flask + MySQL** to demonstrate:

- Normalized relational database design (3NF, 10 tables)
- CRUD operations for every entity
- SQL queries with selection (AND/OR/NOT), projection, Cartesian product,
  UNION and DIFFERENCE
- A full relational-algebra translation for each query (stepwise + compact)
- Staff login system with role-based access (admin, manager, staff)
- Reports built from UNION, DIFFERENCE, and complex conditions
- A clean, professional-but-friendly Bootstrap 5 user interface

The website is the **only** way data is entered or modified — every CRUD
action writes straight to MySQL and is immediately reflected in the database.

---

## Project structure

```
hardware-storage-system/
├── app/                       # Flask application
│   ├── __init__.py            # app factory
│   ├── auth.py                # login / logout / role decorators
│   ├── config.py              # env-driven config
│   ├── db.py                  # PyMySQL connection helpers
│   ├── queries.py             # SQL + relational-algebra catalog
│   ├── static/css/app.css     # custom styling
│   ├── templates/             # Jinja2 templates (Bootstrap 5)
│   └── views/                 # one blueprint per resource
├── sql/
│   ├── schema.sql             # CREATE DATABASE + tables + constraints
│   └── seed.sql               # sample rows for every table
├── scripts/init_db.py         # one-shot installer (reads .env)
├── docs/
│   ├── ER_DIAGRAM.md          # ER diagram (Mermaid)
│   ├── SCHEMA.md              # column-by-column description + 3NF notes
│   ├── QUERIES.md             # all SQL queries + relational algebra
│   ├── USER_MANUAL.md         # how to use the website
│   └── TECHNICAL.md           # architecture, security, deployment
├── requirements.txt
├── run.py                     # `python run.py` to launch
└── README.md
```

---

## Quick start

1. **Install MySQL / MariaDB** and create a `root` user with a password.
2. **Clone the repo and create a virtualenv:**

   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Copy the env file and adjust credentials:**

   ```bash
   cp .env.example .env
   ```

4. **Create the database and seed sample data:**

   ```bash
   python scripts/init_db.py
   ```

5. **Run the server:**

   ```bash
   python run.py
   ```

   Open <http://localhost:5000>.

6. **Sign in** with one of the seeded accounts (password `password123`):

   | Username  | Role     | Notes                                 |
   |-----------|----------|---------------------------------------|
   | `admin`   | admin    | Full access including staff management |
   | `mlopez`  | manager  | Can manage products / stock / reports |
   | `jdcruz`  | staff    | Day-to-day operations                 |
   | `asantos` | staff    | Day-to-day operations                 |

---

## Features map

| Requirement                                  | Where                              |
|----------------------------------------------|-------------------------------------|
| Database design (3NF, ≥6 tables, PK/FK, constraints) | `sql/schema.sql`, `docs/SCHEMA.md` |
| ER diagram                                   | `docs/ER_DIAGRAM.md`                |
| SQL queries (AND/OR/NOT, projection, ×, ∪, −)| `app/queries.py`, `docs/QUERIES.md` |
| Relational algebra translation               | `app/queries.py`, `docs/QUERIES.md` |
| CRUD UI                                      | every `/app/views/*.py` blueprint   |
| Query execution module                       | `/queries` page                     |
| Reports (UNION, DIFFERENCE, complex)         | `/reports` page                     |
| Staff login + roles                          | `app/auth.py`                       |
| User manual                                  | `docs/USER_MANUAL.md`               |
| Technical documentation                      | `docs/TECHNICAL.md`                 |

---

## License

For academic / classroom use.
