# Stage 1: Build stage
FROM python:3.12-alpine

# Install build dependencies
RUN apk add --no-cache gcc libffi-dev musl-dev curl bash

# Add project files to install dependencies
WORKDIR /float-mode
ADD pyproject.toml poetry.lock ./

# Install Poetry and project dependencies
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main

# Copy application code and required files
ADD alembic.ini .
ADD alembic ./alembic
ADD logs ./logs
ADD src ./src

EXPOSE 8000/tcp

# Add entrypoint.sh and grant execution permissions
ADD entrypoint.sh .
RUN chmod +x entrypoint.sh

# Run the application
CMD ["./entrypoint.sh"]
