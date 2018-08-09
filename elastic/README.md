**If you run RESTful api and elasticsearch** separately on the local machine,<br>
then use the following settings:
[rest_api]<br>
host = 127.0.0.1<br>
port = 5000

[elasticsearch]<br>
host = 127.0.0.1<br>
port = 9200<br>


**If you run the docker containers** then use the following settings:<br>
[rest_api]<br>
host = 0.0.0.0<br>
port = 5000<br>

[elasticsearch]<br>
host = elasticsearch<br>
port = 9200<br>

