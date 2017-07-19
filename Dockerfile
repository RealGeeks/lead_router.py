FROM alpine:3.4

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apk add --no-cache python py-pip supervisor ca-certificates && rm -rf /root/.cache

COPY supervisord.ini /etc/supervisor.d/leadrouter.ini

COPY . /usr/src/app
RUN pip install beanstalkc pyyaml && python setup.py install

CMD ["supervisord","-n", "-c", "/etc/supervisord.conf"]
