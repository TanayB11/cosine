# Use Python 3.8.11 base image
FROM python:3.9.0

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy app code
COPY main.py .
COPY Makefile .

EXPOSE 9000

# Command to run the app
CMD [ "make", "prod" ]
