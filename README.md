# templateproject

## Requirements

For development:

- Docker & docker-compose


## How to prepare

- Create .env files inside the dir
- Use `docker compose up` or `docker compose build` to rebuild images
- Run migrations via `docker-migrate`


### Fast start

You may start in docker only dependencies such as postgres, redis etc.
with command `make docker-run-deps`

> Note: You have to stop previous started containers with `docker compose down`

To run main application use `make run-dev` or just `make`.
In this case base application is not related to docker and you may use hot reload.


### Migrations

You may use `docker-migrate` to run migrations or `make docker-bash` and run `alembic ...` commands manually.


## All Available Commands (short list)

### Development
- `make format` - Format code with ruff
- `make alembic-migrate m="migration_name"` - Create migration locally

### Docker
- `make docker-run` - Start all services (app + dependencies)
- `make docker-run-deps` - Start only dependencies (postgres, etc.)
- `make docker-bash` - Open bash in app container
- `make docker-upgrade` - Run database migrations
- `make docker-downgrade` - Rollback last migration
- `make docker-migrate m="migration_name"` - Create new migration
