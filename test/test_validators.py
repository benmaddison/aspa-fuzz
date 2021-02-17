# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
"""aspa validation tests."""

from aspa import (AsPath, AsPathSegment, AS_SEQUENCE, AS_SET,
                  Customer, Provider,
                  Unverifiable)

import pytest

LOCAL_AS = 1


class TestValidators(object):

    @pytest.mark.parametrize("neighbor_type", (Customer, Provider), ids=repr)
    def test_unverifible(self, afi, aspa_set, validator_cls, neighbor_type):
        validator = validator_cls(aspa_set=aspa_set, local_as=LOCAL_AS)
        as_path = AsPath(AsPathSegment(segment_type=AS_SEQUENCE, values=(10,)),
                         AsPathSegment(segment_type=AS_SET, values=(20,)),
                         AsPathSegment(segment_type=AS_SEQUENCE, values=(30,)))
        state = validator.validate(as_path=as_path,
                                   neighbor_as=30,
                                   afi=afi,
                                   neighbor_type=neighbor_type)
        assert state is Unverifiable

    def test_validator(self, afi, aspa_set, validator_cls, case):
        if case.xfail.get("validator") == validator_cls.name:
            pytest.xfail(case.xfail["msg"])
        validator = validator_cls(aspa_set, local_as=LOCAL_AS)
        state = validator.validate(as_path=case.as_path,
                                   neighbor_as=case.neighbor_as,
                                   afi=afi,
                                   neighbor_type=case.neighbor_type)
        assert state is case.expected_state
