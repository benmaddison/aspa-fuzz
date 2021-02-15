# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
"""aspa Package."""

import logging

from .afi import IPV4, IPV6
from .as_path import AsPath, AsPathSegment, AS_SEQUENCE, AS_SET
from .aspa import Aspa, AspaSet
from .draft_06 import Validator as Draft6Validator
from .heitz import Validator as HeitzValidator
from .neighbors import (Any, Customer,
                        IxpRouteServer, IxpRouteServerClient,
                        Peer, Provider)
from .state import Invalid, Unknown, Unverifiable, Valid

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    # AFIs
    IPV4, IPV6,
    # AS_PATH
    AsPath, AsPathSegment, AS_SEQUENCE, AS_SET,
    # ASPA objects
    Aspa, AspaSet,
    # Neighbor types
    Any, Customer, IxpRouteServer, IxpRouteServerClient, Peer, Provider,
    # Validator implementations
    Draft6Validator,
    HeitzValidator,
    # Validation States
    Unverifiable, Unknown, Valid, Invalid
]
