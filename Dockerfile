# Use a slim, professional 2026 Python base
FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Aura logic
COPY . .

# Expose the Matrix Gate
EXPOSE 8000

# Start the Oxygen Flow
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]