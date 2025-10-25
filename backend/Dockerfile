FROM python:3.10

WORKDIR /app

# ffmpeg and git are already available in the non-slim image

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Create necessary directories
RUN mkdir -p /audio /transcripts /models

# Expose port
EXPOSE 5501

# Run the application
CMD ["python", "app.py"]

