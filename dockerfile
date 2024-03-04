FROM python:3.8-slim
WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt


ENTRYPOINT ["/app/run.sh"]