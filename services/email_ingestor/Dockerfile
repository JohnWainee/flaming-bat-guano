FROM python:3.12-slim
WORKDIR /app
COPY services/email_ingestor/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ ./shared/
COPY services/email_ingestor/ ./services/email_ingestor/
ENV PYTHONPATH=/app
CMD ["python", "-m", "services.email_ingestor.main"]
