PYTHON_VERSION := 3.12
CODE_PATH      ?= src

ENV            ?= dev
ENV_FILE       ?= .env.$(ENV)
PROJECT        ?= float-$(ENV)
APP_SERVICE    ?= backend
COMPOSE        ?= docker compose
COMPOSE_FILE   ?= docker-compose.yml
DC             := $(COMPOSE) -f $(COMPOSE_FILE) --env-file $(ENV_FILE) -p $(PROJECT)

ifeq ($(OS),Windows_NT)
  POETRY := poetry
else
  POETRY := $(shell command -v poetry 2> /dev/null || echo poetry)
endif

INSTALL_STAMP := .install.stamp

app-dev:
	ENV=dev $(DC) --profile core up -d

app-prod:
	ENV=prod $(DC) --profile core up -d

mon-dev:
	ENV=dev $(DC) --profile monitoring up -d

mon-prod:
	ENV=prod $(DC) --profile monitoring up -d

auth-dev:
	ENV=dev $(DC) --profile auth up -d

auth-prod:
	ENV=prod $(DC) --profile auth up -d

down:
	$(DC) down


.PHONY: docker-upgrade docker-downgrade docker-migrate
docker-upgrade:
	$(DC) run --rm $(APP_SERVICE) bash -c "poetry run alembic upgrade head"


docker-downgrade:
	$(DC) run --rm $(APP_SERVICE) bash -c "poetry run alembic downgrade -1"


docker-migrate:
	@if [ -z "$(m)" ]; then echo "Specify migration name via m=..."; exit 1; fi
	$(DC) run --rm $(APP_SERVICE) bash -c "poetry run alembic revision --autogenerate -m '$(m)'"


.PHONY: activate-env uvicorn install format check
activate-env:
	@$(POETRY) env activate || true


uvicorn: install
	$(POETRY) run python -m $(CODE_PATH).main


install: $(INSTALL_STAMP)
$(INSTALL_STAMP): pyproject.toml
	$(POETRY) run pip install --upgrade pip setuptools
	$(POETRY) install
	touch $(INSTALL_STAMP)


format: activate-env install
	$(POETRY) run ruff check --select I --fix $(CODE_PATH)
	$(POETRY) run ruff format $(CODE_PATH)
	$(POETRY) run ruff check --fix $(CODE_PATH)


check: activate-env install
	-$(POETRY) run ruff check --select I --output-format=full --show-fixes -n $(CODE_PATH)
	$(POETRY) run ruff format --check $(CODE_PATH)
