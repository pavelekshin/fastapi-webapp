# FastAPI WebApp Example Project

- well-structured easy to understand and scale-up project structure
```bash
.
├── Dockerfile
├── README.md
├── alembic
├── alembic.ini
├── docker-compose.yml
├── logging.ini
├── requirements.txt
├── ruff.toml
├── env
├── data                            - json data for db init
├── scripts                         - scripts for container
│   ├── downgrade
│   ├── init_db
│   ├── makemigrations
│   ├── migrate
│   └── start-dev.sh
└── src                             - global configuration
    ├── __init__.py
    ├── config
    ├── constants.py                - global constants
    ├── database.py                 - global database configuration
    ├── db                          - db folder for local deployment
    │   ├── db_folder.py      
    │   └── pypi.sqlite           
    ├── dependencies.py             - dependencies
    ├── exception_handlers.py       - global exception handlers
    ├── exceptions.py               - global exceptions
    ├── main.py
    ├── models                      - global models
    │   ├── __init__.py
    │   ├── model.py                - db model
    │   └── schema.py               - pydantic schema
    ├── redis.py                    - global redis configuration
    ├── services                    - service logic
    │   ├── __init__.py
    │   ├── aggr_service.py
    │   ├── package_service.py
    │   └── user_service.py
    ├── settings.py                 - global settings
    ├── static                      - static web content
    │   ├── css
    │   ├── external
    │   └── img
    ├── templates                   - web templates
    │   ├── account
    │   ├── auth
    │   ├── default.html
    │   ├── error
    │   ├── home
    │   ├── packages
    │   └── search
    ├── tools                       - json loader tool
    │   └── data_loader.py
    ├── utils                       - utils 
    │   ├── __init__.py
    │   ├── cookie_auth.py
    │   └── security.py
    └── views                       - views
        ├── __init__.py
        ├── account.py
        ├── auth.py
        ├── home.py
        ├── package.py
        └── search.py

```
- async IO operations
- easy local development
    - Dockerfile optimized for small size and fast builds with a non-root user
    - Docker-compose for easy deployment
    - environment with configured Postgres and Redis
- SQLAlchemy with slightly configured `alembic`
    - async SQLAlchemy engine
    - migrations set in easy to understand format (`YYYY-MM-DD_HHmm_rev_slug`)
- SQLAlchemy Core query
- Jinja2 templates
- login / register form with validations
- cookies based auth (http-only)
- salted password storage with `bcrypt`
- cookie signed with `blake2b`
- redis cache for `search` and `package` article
- pydantic model
- linters / format with ruff
- FastAPI dependencies and background task
- and some other extras, like global custom exceptions, index naming convention, shortcut scripts for alembic,
  json data parsing and load into db, etc...

## Local Development

### First Build Only

1. `cp .env.example .env`
2. `docker network create app_main`
3. `docker-compose up -d --build`


### Migrations

- Create an automatic migration from changes in `src/models/models.py`

```shell
docker compose exec app makemigrations *migration_name*
```

- Run migrations

```shell
docker compose exec app migrate
```

- Downgrade migrations

```shell
docker compose exec app downgrade -1  # or -2 or base or hash of the migration
```

### Load data into DB

- Run script for load data into DB `src/tools/data_loader.py`

```shell
docker compose exec app init_db
```