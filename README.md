This is the Node Discovery service. The purpose of this service is to provide a means by which a node can discover information about its hardware or network state. The service periodically updates a set of labels it maintains, and feeds these back into kubernetes. Services can rely on the existence of these labels for purposes of allocation.

The Node Discovery service is implemented as a daemonset, and is expected to run on every node in the cluster. It periodically updates the information about a node as it changes. One particular use for this is for when a network comes online or offline; this service will allow for kubernetes to dynamically reallocate pods to different hardware should a network become disconnected.

The first specific usecase for this service will be for the identification of attached networks that a node has. The immediate use of this information will be in determining if a pod or service can run as part of the attached High Speed Network, the Site Network, the Hardware Network, or the Node Management Network -- or any other network that is attached to a node.

It is up to individual services to rely on the information provided by this service through Node Label Selection.

This project is implemented in the spirit of the node-feature-discovery project (https://github.com/kubernetes-incubator/node-feature-discovery). Currently, the node-feature-discovery project is largely involved in hardware identification. Information provided by the upstream node-feature-service should be preferred over implementation of labels provied by Cray's own Node Discovery service. It is intended that Cray's maintained version of this software deprecate features when parity is reached in the upstream version in order to decrease the cost of ownership. This project includes a copy of the Node Discovery Service when run so that both sets of data are provided to all nodes.

Running tests:

```
docker build . -t node-discovery-testing --target testing &&
 docker run --rm -v $PWD/results:/results node-discovery-testing &&
 docker build . -t node-discovery-codestyle --target codestyle &&
 docker run --rm -v $PWD/results:/results node-discovery-codestyle
```
