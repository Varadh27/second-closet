# Small official Python image
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Install dependencies first so Docker can cache this layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# The pipeline passes the commit SHA so the footer shows it
ARG GIT_SHA=local
ENV GIT_SHA=$GIT_SHA PORT=5000

# Do not run as root
RUN useradd --create-home appuser
USER appuser

EXPOSE 5000
CMD gunicorn --bind 0.0.0.0:$PORT app:app
