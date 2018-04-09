FROM python:3.6-alpine3.7

RUN apk add --no-cache make \
    && addgroup -S gconfigs && adduser -S -G gconfigs gconfigs

WORKDIR /gconfigs

RUN pip install pipenv

USER gconfigs

COPY Pipfile ./
COPY Pipfile.lock ./

RUN pipenv install --dev

COPY . ./
