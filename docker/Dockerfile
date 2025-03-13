FROM quay.io/ccsportal/ubuntu:jammy-python3-latest-ma AS auto-sm-test-image
ARG JFROG_USERNAME
ARG JFROG_PASSWORD
ARG K8S_VERSION=v1.18.6

RUN adduser -u 1000 ubuntu --disabled-password --gecos ",,,"

ENV JFROG_USERNAME=$JFROG_USERNAME
ENV JFROG_PASSWORD=$JFROG_PASSWORD

ENV APP_ROOT_DIR_1=/opt/ccs/automation

ENV POETRY_VERSION=1.3.0
ENV POETRY_HOME="/opt/poetry"
    # no interaction during poetry installs
ENV POETRY_NO_INTERACTION=1
     # python deps root
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PIP_VENV_VERSION=23.0
ENV PLAYWRIGHT_VERSION=1.30.0

ENV PATH="$POETRY_HOME/bin:${APP_ROOT_DIR_1}/.venv/bin:$PATH"

RUN mkdir -p $APP_ROOT_DIR_1
WORKDIR $APP_ROOT_DIR_1


COPY ./automation/pyproject.toml ./
COPY ./scripts ./scripts
COPY ./automation ./
COPY ./run-st.sh ./
COPY ./generate_spec.sh $APP_ROOT_DIR_1
# Due to an open poetry issue: https://github.com/python-poetry/poetry/issues/534
COPY ./dependency.py /opt/poetry/lib/poetry/packages/dependency.py


RUN apt-get update && apt-get install --no-install-recommends -y curl jq
RUN pip install lockfile

RUN pip install poetry==$POETRY_VERSION
RUN apt-get -y install gcc python3-dev libssl-dev swig
RUN apt-get install vim -y
RUN curl -s -L -o /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/${K8S_VERSION}/bin/linux/amd64/kubectl && \
    chmod +x /usr/local/bin/kubectl
RUN poetry config http-basic.jfrog $JFROG_USERNAME $JFROG_PASSWORD && \
  poetry install

RUN poetry run pip install --upgrade M2Crypto

RUN poetry run pip install playwright==$PLAYWRIGHT_VERSION pytest-playwright
RUN playwright install-deps
RUN playwright install chromium

####################### automation svc ui #####################

ENV JFROG_PASSWORD=$JFROG_PASSWORD

ENV APP_ROOT_DIR_2=/opt/ccs/automation_svc_ui

ENV POETRY_VERSION=1.3.0
ENV POETRY_HOME="/opt/poetry"
    # no interaction during poetry installs
ENV POETRY_NO_INTERACTION=1
     # python deps root
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PIP_VENV_VERSION=23.0
ENV PLAYWRIGHT_VERSION=1.30.0

ENV PATH="$POETRY_HOME/bin:${APP_ROOT_DIR_2}/.venv/bin:$PATH"

RUN mkdir -p $APP_ROOT_DIR_2
WORKDIR $APP_ROOT_DIR_2


COPY ./automation_svc_ui/pyproject.toml ./
COPY ./scripts ./scripts
COPY ./automation_svc_ui ./
COPY ./generate_spec.sh $APP_ROOT_DIR_2
COPY ./run-st.sh ./../
# Due to an open poetry issue: https://github.com/python-poetry/poetry/issues/534
COPY ./dependency.py /opt/poetry/lib/poetry/packages/dependency.py


RUN apt-get update && apt-get install --no-install-recommends -y curl jq
RUN pip install lockfile

RUN pip install poetry==$POETRY_VERSION
RUN apt-get -y install gcc python3-dev libssl-dev swig
RUN apt-get install vim -y
RUN curl -s -L -o /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/${K8S_VERSION}/bin/linux/amd64/kubectl && \
    chmod +x /usr/local/bin/kubectl
RUN poetry config http-basic.jfrog $JFROG_USERNAME $JFROG_PASSWORD && \
  poetry install

RUN poetry run pip install --upgrade M2Crypto

RUN poetry run pip install playwright==$PLAYWRIGHT_VERSION pytest-playwright
RUN playwright install-deps
RUN playwright install chromium

####################### CI Stage ##################################
FROM auto-sm-test-image AS ci-stage

USER root
