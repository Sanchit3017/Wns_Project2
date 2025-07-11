FROM python:3.11-slim

WORKDIR /app

# Copy shared dependencies
COPY shared/ /app/shared/
COPY user-service/ /app/user-service/

# Copy requirements from main project
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies
RUN pip install -U pip && pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart pydantic[email] pydantic-settings httpx

# Set Python path to include shared modules
ENV PYTHONPATH=/app

WORKDIR /app/user-service

EXPOSE 8002

CMD ["python", "main.py"]