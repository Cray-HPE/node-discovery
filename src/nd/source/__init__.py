"""
Copyright 2019, Cray Inc. All Rights Reserved.
This package implements the routines which gather information about the system;
there is a general 1-1 mapping between the name of the module and the label it
provides information for; e.g. a networks module will provide labels that follow
the form:
node-discovery.cray.com/networks as a prefix.

Each module that is part of this package should implement a discovery function;
the function should return a dictionary of key/values that can be used to
send back to the kubernetes service as labels to patch or set.
"""

from os.path import dirname, basename, isfile
import glob

modules = glob.glob(dirname(__file__) + "/*.py")
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
