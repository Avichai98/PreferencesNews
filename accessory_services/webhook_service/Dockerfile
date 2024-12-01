# Base Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

# Run the service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
