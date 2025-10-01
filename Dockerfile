# Stage 1: Frontend build
FROM node:20-alpine as frontend

WORKDIR /app/frontend

# Add project files to install dependencies
COPY frontend/package*.json ./
RUN npm install

# Add project files to install dependencies
COPY frontend ./
RUN npm run build

# --------------------------------------------
# --------------------------------------------

# Stage 1: Build stage
FROM python:3.12-alpine as backend

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
ADD backend ./backend
ADD scripts ./scripts

COPY --from=frontend /app/frontend/dist ./backend/static

EXPOSE 8000/tcp

# Add entrypoint.sh and grant execution permissions
ADD entrypoint.sh .
RUN chmod +x entrypoint.sh

# Run the application
CMD ["./entrypoint.sh"]
