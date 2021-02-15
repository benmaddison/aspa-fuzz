# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
"""aspa.neighbors Module."""


class _BaseNeighborType(object):
    def __repr__(self):
        try:
            return self.name
        except AttributeError:
            return super().__repr__()


class _Customer(_BaseNeighborType):
    name = "Customer"


class _Provider(_BaseNeighborType):
    name = "Provider"


class _Peer(_BaseNeighborType):
    name = "Peer"


class _IxpRouteServer(_BaseNeighborType):
    name = "IXP Route Server"


class _IxpRouteServerClient(_BaseNeighborType):
    name = "IXP Route Server Client"


Any = _BaseNeighborType()
Customer = _Customer()
Provider = _Provider()
Peer = _Peer()
IxpRouteServer = _IxpRouteServer()
IxpRouteServerClient = _IxpRouteServerClient()
