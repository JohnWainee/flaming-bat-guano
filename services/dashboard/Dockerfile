FROM python:3.12-slim
WORKDIR /app
COPY services/orchestrator/requirements.txt ./orch_req.txt
COPY services/dashboard/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r orch_req.txt -r requirements.txt
COPY shared/ ./shared/
COPY services/orchestrator/ ./services/orchestrator/
COPY services/dashboard/ ./services/dashboard/
ENV PYTHONPATH=/app
CMD ["streamlit", "run", "services/dashboard/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
