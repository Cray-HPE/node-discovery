"""
Copyright 2019-2020 Hewlett Packard Enterprise Development LP
This routine is used in discovering which networks are attached
to the kubernets cluster.

When a known network is attached to this node, we populate the
name of the network explicitly, e.g. if a node has an HSN attached,
this key will be set:
node-discovery.cray.com/networks.hsn = true

All existing labels as part of the node-discovery.cray.com/networks/
namespace that disappear as a function of attach/disconnect will
be removed when no longer detected.

The value for these labels will always be 'true'.
"""

import ifaddr
import netaddr
import sys
from json import loads

from nd import KEY

NETKEY = '%s/%s' % (KEY, __name__.split('.')[-1])
# This is a list of interface names that aren't useful
# to expose; mainly because they represent information about
# internal kubernetes networking. When these are present, skip
# reporting information about these NICs.
INTERFACE_BLACKLIST = frozenset(['kube-ipvs0', 'docker0', 'lo', 'weave'])

# Initially, we aren't interested in these. We might change that in the
# future.
FILTER_IPV6 = True


def discovery(api_instance):
    """
    Given our api_instance, ask it for a set of known
    endpoints that correspond with known named networks.
    Then, queries the host environment for the ipv4 addresses
    currently use. Host interfaces that belong to a known
    named network are added to the return value dictionary;
    unknown networks are appended to the return of values
    to set.
    """
    labels = {}
    # Obtain a set of named networks from the configmap
    try:
        raw_response = api_instance.read_namespaced_config_map('cray-node-discovery', 'services')
        # k8s encapsulates changes single and double quotes, and adds unsigned flags,
        # which need to be replaced.
        raw_networks = loads(raw_response.data['networks'].strip().replace("'", '"').replace('u"', '"'))
        networks = {}
        for network_name, nv in raw_networks.items():
            try:
                if 'blocks' in nv:
                    blocks = nv['blocks']
                    if 'ipv4' in blocks:
                        for bl in blocks['ipv4']:
                            if 'network' in bl:
                                # We are only applying labels to NCNs and they will only have "river" IPs
                                if 'label' in bl and bl['label'] == "river":
                                    networks[network_name] = netaddr.IPNetwork('%s' % (bl['network']))
                            else:
                                print("No networks found for {0}".format(network_name))
            except KeyError as err:
                print("Key Error: {0} for network {1}".format(err, network_name))
    except Exception:
        print("Unexpected error:", sys.exc_info()[0])
        return labels

    # Obtain a set of ip address currently assigned to this node
    ips = []
    for adapter in ifaddr.get_adapters():
        if adapter.name in INTERFACE_BLACKLIST:
            continue
        for ipinfo in adapter.ips:
            try:
                ip = ipinfo.ip
                # To be used for unnamed networks later... maybe.
                # prefix = ipinfo.network_prefix
                if FILTER_IPV6 and netaddr.IPAddress(ip).version == 6:
                    continue
                ips.append(netaddr.IPAddress(ip))
            except (KeyError, TypeError):
                continue
    for network_name, network in networks.items():
        if any([this_ip in network for this_ip in ips]):
            labels['%s.%s' % (NETKEY, network_name)] = 'true'
    return labels
