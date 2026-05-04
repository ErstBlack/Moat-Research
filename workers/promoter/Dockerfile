FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir pyyaml==6.0.2
COPY workers/common /app/workers/common
COPY workers/promoter /app/workers/promoter
COPY briefs /app/briefs
ENV PYTHONPATH=/app
CMD ["python", "-m", "workers.promoter.promoter"]
