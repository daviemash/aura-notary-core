# Use a slim, professional Python base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies first (leverages Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Aura logic
COPY . .

# Start the Oxygen Flow, binding to the environment PORT automatically
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]