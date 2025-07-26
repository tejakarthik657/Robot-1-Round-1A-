FROM python:3.11

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Set up logging directory
RUN mkdir -p /app/logs

# The main.py script is now the entrypoint, ready for CLI arguments
ENTRYPOINT ["python", "main.py"]

# Default command if none is provided via docker-compose
CMD ["--help"]