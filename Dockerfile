FROM python:3.8-slim-buster

RUN mkdir -p /home/flaskapp
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y


# Copy the requirements file into the container and install dependencies
COPY requirements.txt /home/flaskapp

# Copy the rest of the application code into the container
COPY ./flaskapp /home/flaskapp

# Set the working directory to /app
WORKDIR /home/flaskapp
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the Flask app will listen on
EXPOSE 5000

# Start the Flask app when the container starts
CMD ["python", "peopleDist.py"]