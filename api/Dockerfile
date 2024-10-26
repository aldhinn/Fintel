# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy everything into the container 
COPY . .

# Install the required Python packages
RUN pip install --no-cache-dir --root-user-action ignore -r requirements.txt

# Set the entrypoint to the script
ENTRYPOINT ["/app/run"]