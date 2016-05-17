FROM python:2-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app
RUN python setup.py install

CMD ["leadrouter", "subscriber"]
