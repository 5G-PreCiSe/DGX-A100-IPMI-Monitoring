#The base image for the container 
FROM python:3.9-slim-buster 
 
# Keeps Python from generating .pyc files in the container 
ENV PYTHONDONTWRITEBYTECODE=1 
 
# Turns off buffering for easier container logging 
ENV PYTHONUNBUFFERED=1 
 
# Copy python requirements to the docker container and install
COPY requirements.txt . 
RUN python -m pip install -r requirements.txt

RUN apt update -y
RUN apt install ipmitool -y
 
#create a non root user to access the container 
#RUN adduser -u 5678 --disabled-password --gecos “” vscode

ADD app.py .
ADD mqtt.py .
ADD config.ini .
CMD python app.py