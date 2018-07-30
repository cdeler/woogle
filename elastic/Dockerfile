FROM python:3
 
ENV PYTHONUNBUFFERED 1

ADD /config/requirements.txt /config/
RUN pip install -r /config/requirements.txt

COPY cmd.sh /
WORKDIR /rest_api
COPY rest_api /rest_api

EXPOSE 5000 5000
