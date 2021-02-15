# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
"""aspa.aspa Module."""

from collections import defaultdict


class Aspa(object):
    """Representation of an ASPA object."""

    def __init__(self, customer_as, provider_as_set, afi):
        self.customer_as = customer_as
        self.provider_as_set = set(provider_as_set)
        self.afi = afi


class AspaSet(object):
    """Representation of a set of ASPA objects."""

    def __init__(self, *aspas: Aspa):
        self._aspas = defaultdict(lambda: defaultdict(set))
        for aspa in aspas:
            self._aspas[aspa.afi][aspa.customer_as] |= aspa.provider_as_set

    def get_providers(self, customer_as, afi):
        try:
            provider_as_set = self._aspas[afi][customer_as]
        except KeyError:
            raise NoAspa()
        if not provider_as_set:
            raise NoAspa()
        return provider_as_set


class NoAspa(Exception):
    """No ASPA found, or empty provider AS set."""

    pass
