# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variable to make Python output unbuffered
ENV PYTHONUNBUFFERED=1

# Create a non-root user and group
RUN groupadd -r fintel && useradd -r -m -g fintel fintel

# Set the working directory in the container
WORKDIR /home/fintel

# Copy everything into the container 
COPY . .
# Change ownership of the /home/fintel directory to fintel
RUN chown -R fintel:fintel /home/fintel
# Allow run script to execute.
RUN chmod +x /home/fintel/run

# Switch to non-root user.
USER fintel

# Create a Python virtual environment
RUN python -m venv /home/fintel/venv
# Permanently add the virtual environment’s bin directory to PATH
ENV PATH="/home/fintel/venv/bin:$PATH"

# Upgrade pip.
RUN pip install --upgrade pip
# Install the required Python packages
RUN pip install -r requirements.txt

EXPOSE 61000

# Set the entrypoint to the script
ENTRYPOINT ["/home/fintel/run"]