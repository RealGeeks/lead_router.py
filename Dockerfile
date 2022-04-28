FROM python:2.7-stretch

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y supervisor

COPY supervisord.ini /etc/supervisor.d/leadrouter.ini

COPY . /usr/src/app

RUN pip install raven click beanstalkc3 pyyaml tox && python setup.py install

CMD ["supervisord","-n", "-c", "/etc/supervisord.conf"]
