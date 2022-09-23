# Dockerfile
FROM python:3.9-alpine3.14
# Set Python output is sent straight to terminal to see the output in realtime.
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
