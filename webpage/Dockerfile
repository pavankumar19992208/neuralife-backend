# filepath: /webpage/Dockerfile
FROM python:3.10-slim

WORKDIR /webpage

RUN apt-get update && apt-get install -y \
    unixodbc-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ../shared/db.py ./db.py
COPY . .

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]