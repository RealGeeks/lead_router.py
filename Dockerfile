FROM alpine:edge

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apk add --no-cache python supervisor ca-certificates && rm -rf /root/.cache

COPY supervisord.ini /etc/supervisor.d/leadrouter.ini

COPY . /usr/src/app
RUN python setup.py install

CMD ["supervisord","-n", "-c", "/etc/supervisord.conf"]
