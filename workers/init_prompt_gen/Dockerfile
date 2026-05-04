FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir pyyaml==6.0.2
COPY workers/common /app/workers/common
COPY workers/init_prompt_gen /app/workers/init_prompt_gen
COPY briefs /app/briefs
ENV PYTHONPATH=/app
CMD ["python", "-m", "workers.init_prompt_gen.init_prompt_gen"]
