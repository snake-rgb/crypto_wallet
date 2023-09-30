FROM python:3.10-alpine

USER root

RUN apk add --no-cache gcc libffi-dev musl-dev postgresql-dev
RUN apk add g++ && apk add make
ENV APP_HOME=/home/app/crypto_wallet
WORKDIR $APP_HOME

# install poetry
RUN pip install poetry
#ENV PATH "/root/.local/bin:$PATH"
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

# install python dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false --local
RUN poetry install --no-dev --no-root
COPY ./ $APP_HOME