FROM python:3

ADD requirements.txt /config/
RUN pip install -r /config/requirements.txt

WORKDIR /elastic_indexer
ADD . /elastic_indexer

EXPOSE 5000
EXPOSE 9200
CMD ["python", "app.py"]