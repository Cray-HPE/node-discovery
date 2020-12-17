'''
Copyright 2019, Cray Inc. All Rights Reserved.
Created on Oct 29, 2018

A package used to implement aggregation of all sources defined in
node-discovery.source.

@author: jsl
'''
# Import and collect all discovery routines on first import
routines = []
from .networks import discovery as net_disc
routines.append(net_disc)


def all_labels(api_instance):
    """
    Executes all discovery routines in this package and returns a
    unified dictionary of key/values to set for the node.

    The api_instance is a client instance of the k8s library; disovery
    routines can query kubernetes for any information deemed necessary
    for generating k/v information.
    """
    labels = {}
    for routine in routines:
        labels.update(routine(api_instance))
    return labels
