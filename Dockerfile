# Multi-stage build for GitHub MCP Server
# Stage 1: Builder - Install dependencies
FROM python:3.10-alpine AS builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime - Minimal image
FROM python:3.10-alpine

# Create a non-root user 'app'
RUN adduser -D -h /home/app -s /bin/sh app

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder --chown=app:app /root/.local /home/app/.local

# Copy application code
COPY --chown=app:app main.py .

# Switch to non-root user
USER app

# Add local packages to PATH
ENV PATH="/home/app/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Run the MCP server
ENTRYPOINT ["python", "main.py"]
