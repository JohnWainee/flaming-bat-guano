FROM python:3.12-slim
WORKDIR /app
RUN mkdir -p /data
COPY services/orchestrator/requirements.txt ./orch_req.txt
COPY services/ingestion_pipeline/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r orch_req.txt -r requirements.txt
COPY shared/ ./shared/
COPY services/orchestrator/ ./services/orchestrator/
COPY services/ingestion_pipeline/ ./services/ingestion_pipeline/
ENV PYTHONPATH=/app
CMD ["python", "-m", "services.ingestion_pipeline.main"]
