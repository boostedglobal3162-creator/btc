# V5 High-Confidence Bot Deployment
FROM python:3.10-slim

WORKDIR /app

# System dependencies for technical indicators
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the BTC Agent directly
CMD ["python", "main.py"]
