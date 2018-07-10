FROM python:3
 
ENV PYTHONUNBUFFERED 1
 
RUN pip3 install uwsgi
RUN groupadd -r uwsgi && useradd -r -g uwsgi uwsgi

ADD /config/requirements.txt /config/
RUN pip install -r /config/requirements.txt

WORKDIR /app
COPY app /app
COPY cmd.sh /

EXPOSE 9090 9191
USER uwsgi

CMD ["/cmd.sh"]