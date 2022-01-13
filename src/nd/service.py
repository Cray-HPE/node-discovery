#!/usr/bin/env python
#
# MIT License
#
# (C) Copyright 2019-2020, 2022 Hewlett Packard Enterprise Development LP
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
"""
This is the main entrypoint for the Cray node discovery service; the node
discovery service is responsible for reading information from a given node
and applying a set of labels to that node periodically.

The intent is that this pod runs on all available manager and worker nodes
in a cluster as a daemonset. Other pods can detect the presence of the variables
that the node discovery service maintains and can schedule themselves
on nodes that match the requirements that they decide upon.

This service refreshes labels and labelnamespaces it owns once every 30
seconds; any labels that are part of this namespace that no longer
accurate as to the state of the node are removed. It is up to Kubernetes
and the service leveraging these labels to be configured appropriately should
these labels change.
"""

import os
import time
import sys
import signal
from kubernetes import client, config

# Inject reference to this package into the interpreter resolution list;
# this allows other modules to perform relative imports
sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../..')))

from nd.source.discovery import all_labels
from nd import KEY


class GracefulExit(object):
    """
    Registers graceful behavior in the event of termination signals.
    """
    kill_now = False

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True
        print("Job is quitting, cleaning up.")
        self.func(*self.args, **self.kwargs)
        print("Cleaned up!")


def clean_up_labels(api_instance, key):
    """
    This is invoked as a clean up action; it should delete all
    labels in the kubernetes instance for this node that match the
    service <key>.
    """
    labels = {}
    for to_remove in get_existing_labels(api_instance, key):
        labels[to_remove] = None
    body = {"metadata": {"labels": labels}}
    api_instance.patch_node(os.environ['NODE_NAME'], body)


def get_existing_labels(api_instance, key):
    """
    This service is designed to maintain its' keyed namesapce; so any
    keys that are currently set that match that are no longer honored
    need to be cleaned from the node. This function queries the
    <api_instance> for existing labels that have been set.
    Returns:
    - a set object which represents the label keys that match the
    KEY for this service.
    """
    resp = api_instance.read_node(os.environ['NODE_NAME']).to_dict()
    all_labels = list(resp['metadata']['labels'].keys())
    matched_labels = [label for label in all_labels if label.startswith(key)]
    return set(matched_labels)


if __name__ == '__main__':
    # Load Configuration and indicate initial health
    try:
        config.load_incluster_config()
    except Exception:
        sys.exit("This application must be run within the k8s cluster.")
        raise
    api_instance = client.CoreV1Api()
    gc = GracefulExit(clean_up_labels, api_instance, KEY)
    print("Managing label namespace '%s' for node '%s'" % (KEY, os.environ['NODE_NAME']))
    while not gc.kill_now:
        labels = all_labels(api_instance)
        # Add that we're running
        labels['%s/%s' % (KEY, "running")] = 'true'
        # Remove namespaced labels that are no longer set
        existing_labels = get_existing_labels(api_instance, KEY)
        for to_remove in existing_labels - set(labels.keys()):
            labels[to_remove] = None
        body = {"metadata": {"labels": labels}}
        api_instance.patch_node(os.environ['NODE_NAME'], body)
        for _ in range(30):
            if not gc.kill_now:
                time.sleep(1)
