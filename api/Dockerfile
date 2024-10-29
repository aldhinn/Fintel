# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy everything into the container 
COPY . .

# Upgrade pip.
RUN pip install --root-user-action ignore --upgrade pip
# Install the required Python packages
RUN pip install --no-cache-dir --root-user-action ignore -r requirements.txt

EXPOSE 5000

# Set the entrypoint to the script
ENTRYPOINT ["/app/run"]