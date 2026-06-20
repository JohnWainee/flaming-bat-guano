FROM python:3.12-slim
WORKDIR /app
COPY services/teams_bot/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ ./shared/
COPY services/teams_bot/ ./services/teams_bot/
ENV PYTHONPATH=/app
CMD ["python", "-m", "services.teams_bot.main"]
