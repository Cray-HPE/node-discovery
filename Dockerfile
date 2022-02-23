#
# MIT License
#
# (C) Copyright 2019-2022 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#

FROM artifactory.algol60.net/csm-docker/stable/docker.io/library/alpine:3.14 as testing_base

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


FROM artifactory.algol60.net/csm-docker/stable/docker.io/library/alpine:3.14

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
