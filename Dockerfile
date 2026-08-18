# Use an official lightweight Python runtime as a base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (needed for compiling certain packages if required)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies without storing the pip cache to save space
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project source code into the container
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run your application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]