FROM python:3.12-slim

WORKDIR /app

# Install deps from pyproject.toml before copying the full source
# (keeps this layer cached as long as pyproject.toml doesn't change)
COPY pyproject.toml .
RUN touch README.md \
    && pip install --no-cache-dir .

# Copy application source
COPY . .

# Render injects PORT at runtime; default to 8000 for local/other providers
ENV PORT=8000

EXPOSE $PORT

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')"

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
