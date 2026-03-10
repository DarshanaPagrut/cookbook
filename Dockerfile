# Use an official lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's cache
# This prevents re-installing dependencies if only the app code changes
COPY app/requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code from the local app/ directory to the container
COPY app/ .

# Expose the port Flask is running on (as defined in app.py)
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Command to run the application
# We use 'python app.py' because your app.py contains the app.run() block
CMD ["python", "app.py"]