# Use an official Python runtime as a parent image
FROM python:3.9-slim

RUN apt-get update && apt-get install -y dnsutils

RUN apt-get -y update && apt-get -y install telnet

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY app/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY app .

# Run the application with uvicorn listening on port 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"] 