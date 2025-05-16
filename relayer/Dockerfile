FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make health check script executable
RUN chmod +x /app/scripts/healthcheck.py

# Set up healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python /app/scripts/healthcheck.py

# Expose the port
EXPOSE 8000

# Run the application
CMD ["python", "run.py"] 