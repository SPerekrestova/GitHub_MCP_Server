# Optimized for fast builds using Debian slim with pre-compiled wheels
# Build time: ~30 seconds (cached) vs 5-10 minutes (Alpine compilation)
# Image size: ~150MB (acceptable trade-off for 10-20x faster builds)

FROM python:3.10-slim AS builder

WORKDIR /app

# Copy requirements first (better layer caching)
COPY requirements.txt .

# Use BuildKit cache mount for pip - dramatically speeds up rebuilds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user -r requirements.txt

# Runtime stage - minimal final image
FROM python:3.10-slim

# Create non-root user
RUN useradd -m -u 1000 app

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder --chown=app:app /root/.local /home/app/.local

# Copy application code (changes frequently, so last)
COPY --chown=app:app main.py .

USER app

ENV PATH="/home/app/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "main.py"]
