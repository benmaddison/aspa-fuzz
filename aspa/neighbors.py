# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
"""aspa.neighbors Module."""


class _BaseNeighborType(object):
    pass


class _Customer(_BaseNeighborType):
    pass


class _Provider(_BaseNeighborType):
    pass


class _Peer(_BaseNeighborType):
    pass


class _IxpRouteServer(_BaseNeighborType):
    pass


class _IxpRouteServerClient(_BaseNeighborType):
    pass


Any = _BaseNeighborType()
Customer = _Customer()
Provider = _Provider()
Peer = _Peer()
IxpRouteServer = _IxpRouteServer()
IxpRouteServerClient = _IxpRouteServerClient()
