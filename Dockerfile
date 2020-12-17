## Copyright 2019-2020 Hewlett Packard Enterprise Development LP

FROM python:3.9.0-slim as testing_base

WORKDIR /usr/src/app

COPY requirements.txt requirements_test.txt constraints.txt ./

RUN pip install --no-cache-dir -r requirements.txt && \
 pip install --no-cache-dir -r requirements_test.txt

COPY . .


FROM testing_base as testing

CMD [ "./docker_test_entry.sh" ]


FROM testing_base as codestyle

CMD [ "./docker_codestyle_entry.sh" ]


FROM python:3.9.0-slim

WORKDIR /usr/src/app

COPY requirements.txt constraints.txt ./

# Force the stdout and stderr streams to be unbuffered.
# Needed for kubectl logs cray-node-discovery; otherwise logs are empty.
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "src/nd/service.py" ]
