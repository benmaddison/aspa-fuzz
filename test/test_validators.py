# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
"""aspa validation tests."""

from aspa import (IPV4, IPV6,
                  AsPath, AsPathSegment, AS_SEQUENCE, AS_SET,
                  Aspa, AspaSet,
                  Draft6Validator, HeitzValidator,
                  Customer, IxpRouteServer, IxpRouteServerClient,
                  Peer, Provider,
                  Invalid, Valid, Unknown, Unverifiable)

import pytest


class TestValidators(object):

    @pytest.mark.parametrize("afi", (IPV4, IPV6))
    @pytest.mark.parametrize("validator_cls",
                             (Draft6Validator, HeitzValidator))
    @pytest.mark.parametrize("neighbor_type",
                             (Customer, Provider))
    def test_unverifible(self, afi, validator_cls, neighbor_type):
        validator = validator_cls(AspaSet(), local_as=10)
        as_path = AsPath(AsPathSegment(segment_type=AS_SEQUENCE,
                                       values=(1, 2)),
                         AsPathSegment(segment_type=AS_SET,
                                       values=(3, 4)),
                         AsPathSegment(segment_type=AS_SEQUENCE,
                                       values=(5, 6)))
        state = validator.validate(as_path=as_path,
                                   neighbor_as=6,
                                   afi=afi,
                                   neighbor_type=neighbor_type)
        assert state is Unverifiable

    @pytest.mark.parametrize("afi", (IPV4, IPV6))
    @pytest.mark.parametrize("validator_cls",
                             (Draft6Validator, HeitzValidator))
    @pytest.mark.parametrize("path,neighbor,neighbor_type,expected_state",
                             (((1, 2, 3, 4), 4, Provider, Unknown),
                              ((1, 2, 2), 2, Peer, Valid),
                              ((1, 3), 3, Customer, Invalid),
                              ((1, 1, 2), 5, IxpRouteServer, Valid),
                              ((), 0, IxpRouteServerClient, Invalid),
                              ((), 0, IxpRouteServer, Invalid),
                              ((1, 3), 5, IxpRouteServer, Invalid)))
    def test_validator(self, afi, validator_cls, path,
                       neighbor, neighbor_type, expected_state):
        aspa_set = AspaSet(Aspa(1, (2,), afi),
                           Aspa(4, (3,), afi),
                           Aspa(10, (4,), afi))
        as_path = AsPath(AsPathSegment(segment_type=AS_SEQUENCE,
                                       values=path))
        validator = validator_cls(aspa_set, local_as=10)
        state = validator.validate(as_path=as_path,
                                   neighbor_as=neighbor,
                                   afi=afi,
                                   neighbor_type=neighbor_type)
        assert state is expected_state
