PYTHON_VERSION := 3.12
CODE_PATH = src

ifeq ($(OS),Windows_NT)
    POETRY := poetry
else
    POETRY := $(shell command -v poetry 2> /dev/null || echo poetry)
endif
INSTALL_STAMP := .install.stamp


activate-env:
	@$(POETRY) env activate || true


.PHONY: run
uvicorn: install
	poetry run python -m src.main


install: $(INSTALL_STAMP)
$(INSTALL_STAMP): pyproject.toml
	$(POETRY) run pip install --upgrade pip setuptools
	$(POETRY) install
	touch $(INSTALL_STAMP)


.PHONY: format
format: activate-env install
	$(POETRY) run ruff check --select I --fix $(CODE_PATH)
	$(POETRY) run ruff format $(CODE_PATH)
	$(POETRY) run ruff check --fix $(CODE_PATH)


.PHONY: check
check: activate-env install
	$(POETRY) run ruff check --select I --output-format=full --show-fixes -n $(CODE_PATH) || true
	$(POETRY) run ruff format --check $(CODE_PATH)


.PHONY: docker-run
docker-run:
	docker-compose up -d


.PHONY: docker-run-deps
docker-run-deps:
	docker-compose up --scale app=0 --scale kudago_worker=0 -d


.PHONY: tg-worker
tg-worker:
	docker-compose run telegram_worker


.PHONY: docker-upgrade
docker-upgrade:
	docker compose run app bash -c "poetry run alembic upgrade head"


.PHONY: docker-downgrade
docker-downgrade:
	docker compose run app bash -c "poetry run alembic downgrade -1"


.PHONY: docker-migrate
docker-migrate:
	@if [ -z "$(m)" ]; then \
		echo "Specify name of migration"; \
		exit 1; \
	fi
	docker compose run --rm app bash -c "poetry run alembic revision --autogenerate -m '$(m)'"


.PHONY: docker-bash
docker-bash:
	docker compose run --rm app bash


.PHONY: alembic-migrate
alembic-migrate:
	poetry run alembic revision --autogenerate -m '$(m)'
