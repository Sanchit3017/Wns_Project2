FROM python:3.11-slim

WORKDIR /app

# Copy the web interface and required dependencies
COPY web_interface/ ./web_interface/
COPY enhanced_features.py .

# Install dependencies
RUN pip install fastapi uvicorn jinja2 httpx python-multipart

# Set working directory to web_interface
WORKDIR /app/web_interface

# Set Python path to include parent directory for imports
ENV PYTHONPATH=/app

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"] 