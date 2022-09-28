# Dockerfile
FROM python:3.11.0rc2-bullseye
# Set Python output is sent straight to terminal to see the output in realtime.
ENV PYTHONUNBUFFERED=1
COPY . /code
WORKDIR /code
RUN python -m pip install -r requirements.txt 
RUN  python manage.py makemigrations 
CMD ["python", "manage.py runserver"]
