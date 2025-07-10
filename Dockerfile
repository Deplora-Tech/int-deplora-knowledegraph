FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .
EXPOSE 8002

# Command to run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port 8002