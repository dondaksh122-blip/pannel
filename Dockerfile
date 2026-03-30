FROM python:3.10-slim
RUN apt-get update && apt-get install -y g++ make && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
RUN pip install flask flask-sqlalchemy
RUN g++ -O3 prime.cpp -o PRIME -pthread
RUN chmod +x PRIME
CMD ["python", "app.py"]