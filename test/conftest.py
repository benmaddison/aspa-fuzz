# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
"""aspa validation test fixtures."""

import os

from aspa import (IPV4, IPV6,
                  AsPath, AsPathSegment, AS_SEQUENCE,
                  Aspa, AspaSet,
                  Draft6Validator, HeitzValidator)
import aspa.neighbors
import aspa.state

import pytest
import yaml


class TestCase(object):
    def __init__(self, as_path, neighbor_as, neighbor_type,
                 expected_state, xfail={}, **kwargs):
        self.as_path = AsPath(AsPathSegment(segment_type=AS_SEQUENCE,
                                            values=as_path))
        self.neighbor_as = neighbor_as
        self.neighbor_type = getattr(aspa.neighbors, neighbor_type)
        self.expected_state = getattr(aspa.state, expected_state)
        self.xfail = xfail

    def __repr__(self):
        return f"<{self.expected_state} path: '{self.as_path}', " \
               f"from: {self.neighbor_type}>"


def read_test_cases():
    with open(os.path.join(os.path.dirname(__file__), "test_cases.yml")) as f:
        data = yaml.safe_load(f)
    return [TestCase(neighbor_type=t, **case)
            for case in data
            for t in case["neighbor_types"]]


@pytest.fixture(scope="session", params=read_test_cases(), ids=repr)
def case(request):
    return request.param


@pytest.fixture(scope="session", params=(IPV4, IPV6), ids=("IPv4", "IPv6"))
def afi(request):
    return request.param


@pytest.fixture(scope="session")
def aspa_set(afi):
    with open(os.path.join(os.path.dirname(__file__), "aspa_set.yml")) as f:
        data = yaml.safe_load(f)
    return AspaSet(*[Aspa(afi=afi, **aspa) for aspa in data])


@pytest.fixture(scope="session",
                params=(Draft6Validator, HeitzValidator),
                ids=repr)
def validator_cls(request):
    return request.param
