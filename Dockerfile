# Use the official Python 3.12 image as the base
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy all files from the Crawl4AI-Unified-Scraper folder
COPY Crawl4AI-Unified-Scraper/ ./

# Install packages from requirements.txt and awscli
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir awscli

# Run the crawl4ai-setup command
RUN crawl4ai-setup

# Expose port 8000 to let the container listen on this port
EXPOSE 8000