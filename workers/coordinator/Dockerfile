FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir pyyaml==6.0.2
COPY workers/common /app/workers/common
COPY workers/coordinator /app/workers/coordinator
ENV PYTHONPATH=/app
EXPOSE 8080
CMD ["python", "-m", "workers.coordinator.coordinator"]
