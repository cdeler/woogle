FROM python:3
 
ENV PYTHONUNBUFFERED 1
 
RUN pip3 install uwsgi
RUN groupadd -r uwsgi && useradd -r -g uwsgi uwsgi

ADD /config/requirements.txt /config/
RUN pip install -r /config/requirements.txt

WORKDIR /app
COPY app /app
COPY cmd.sh /
COPY wait-postgres.sh /


EXPOSE 8080 8080
EXPOSE 8000 8000
EXPOSE 5000 5000
USER uwsgi