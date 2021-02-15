# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
"""aspa validation tests."""

from aspa import (AsPath, AsPathSegment, AS_SEQUENCE, AS_SET,
                  Customer, Provider,
                  Unverifiable)

import pytest


class TestValidators(object):

    @pytest.mark.parametrize("neighbor_type", (Customer, Provider), ids=repr)
    def test_unverifible(self, afi, aspa_set, validator_cls, neighbor_type):
        validator = validator_cls(aspa_set=aspa_set, local_as=10)
        as_path = AsPath(AsPathSegment(segment_type=AS_SEQUENCE, values=(1,)),
                         AsPathSegment(segment_type=AS_SET, values=(2,)),
                         AsPathSegment(segment_type=AS_SEQUENCE, values=(3,)))
        state = validator.validate(as_path=as_path,
                                   neighbor_as=3,
                                   afi=afi,
                                   neighbor_type=neighbor_type)
        assert state is Unverifiable

    def test_validator(self, afi, aspa_set, validator_cls, case):
        validator = validator_cls(aspa_set, local_as=10)
        state = validator.validate(as_path=case.as_path,
                                   neighbor_as=case.neighbor_as,
                                   afi=afi,
                                   neighbor_type=case.neighbor_type)
        assert state is case.expected_state
