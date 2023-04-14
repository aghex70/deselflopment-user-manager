# Use the official Python base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the requirements file to the container
COPY ./requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the FastAPI app code to the container
COPY . /app

# Expose the port that the FastAPI app will run on
EXPOSE 18010

# Start the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "18010"]
