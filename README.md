# FastAPI WebApp Example Project

- well-structured easy to understand and scale-up project structure
- async IO operations
- easy local development
    - Dockerfile optimized for small size and fast builds with a non-root user
    - Docker-compose for easy deployment
    - environment with configured postgres and redis
    - script to lint code with `ruff` and `ruff format`
- SQLAlchemy with slightly configured `alembic`
    - async SQLAlchemy engine
    - migrations set in easy to sort format (`YYYY-MM-DD_HHmm_rev_slug`)
- SQLAlchemy Core
- Jinja2 template
- login / register form with validations
- cookie based auth (http-only)
- salted password storage with `bcrypt`
- cookie signed with `blake2b`
- redis cache for `search` and `package` article
- global pydantic model
- FastAPI dependencies and background task
- and some other extras, like global custom exceptions, index naming convention, shortcut scripts for alembic,
  json data parsing and load into db, etc.

## Local Development

### First Build Only

1. `cp .env.example .env`
2. `docker network create app_main`
3. `docker-compose up -d --build`

### Linters

Format the code with `ruff --fix` and `ruff format`

```shell
docker compose exec app format
```

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