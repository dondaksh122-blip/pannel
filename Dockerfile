FROM python:3.10-slim

RUN apt-get update && apt-get install -y g++ make && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

# 👇 IMPORTANT LINE
RUN pip install --no-cache-dir flask flask-sqlalchemy gunicorn

RUN g++ -O3 prime.cpp -o PRIME -pthread
RUN chmod +x PRIME

CMD gunicorn --bind 0.0.0.0:$PORT app:app
