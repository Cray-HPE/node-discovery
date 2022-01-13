## Copyright 2019-2022 Hewlett Packard Enterprise Development LP

FROM docker.io/library/alpine:3.14 as testing_base

WORKDIR /usr/src/app

RUN apk add --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

COPY requirements.txt requirements_test.txt constraints.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt && \
 pip3 install --no-cache-dir -r requirements_test.txt

COPY . .


FROM testing_base as testing

CMD [ "./docker_test_entry.sh" ]


FROM testing_base as codestyle

CMD [ "./docker_codestyle_entry.sh" ]


FROM docker.io/library/alpine:3.14

WORKDIR /usr/src/app

RUN apk add --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

COPY requirements.txt constraints.txt ./

# Force the stdout and stderr streams to be unbuffered.
# Needed for kubectl logs cray-node-discovery; otherwise logs are empty.
ENV PYTHONUNBUFFERED=1

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "src/nd/service.py" ]
