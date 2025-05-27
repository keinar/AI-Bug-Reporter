# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Streamlit environment variables
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8502
ENV STREAMLIT_BROWSER_SERVER_ADDRESS=0.0.0.0

# disable the file watcher globally
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none

# Run the app
CMD ["streamlit", "run", "ai_bug_reporter.py", "--server.port", "8502", "--server.address", "0.0.0.0"]

# To build and run:
# 1. docker build -t ai_bug_reporter:latest .
# 2. docker run -p 8502:8502 --env-file .env ai_bug_reporter:latest
