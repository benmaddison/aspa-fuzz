# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
# Derived from:
#   https://mailarchive.ietf.org/arch/msg/sidrops/JeEZnHWjrS3j9ldshEoyUMMOwus/
#   Credit: Jakob Heitz
#
"""aspa.heitz.algorithm Module."""

from ..as_path import AS_SEQUENCE, AsPath
from ..aspa import AspaSet, NoAspa
from ..state import Unverifiable, Unknown, Valid, Invalid


class Validator(object):
    """ASPA verification alternative triple-wise algorithm."""

    def __init__(self, aspa_set: AspaSet, local_as):
        self.aspa_set = aspa_set
        self.local_as = local_as

    def validate(self, as_path: AsPath, afi, **kwargs):
        # step 0 - return early if there are AS_SETs in the path
        if any((s.type != AS_SEQUENCE for s in as_path.segments)):
            return Unverifiable
        # step 1 - prepare de-duplicated AS sequence
        as_seq = list()
        for segment in as_path.segments:
            for asn in segment.values:
                if asn not in as_seq:
                    as_seq.append(asn)
        as_seq.append(self.local_as)
        # step 2 - iterate over transited ASNs
        path_state = Valid
        for transit in as_seq[1:-1]:
            # Get index of 'transit' in 'as_seq'
            i = as_seq.index(transit)
            # Create a tuple containing the neighbors of 'transit'
            neighbors = (as_seq[i-1], as_seq[i+1])
            # Get the pairwise assertions of each neighbor
            # with respect to 'transit'
            neighbor_assertions = [self.verify_pair(n, transit, afi)
                                   for n in neighbors]
            # step 2.1 - if both neighbors assert 'transit' is not an
            #            authorised provider, segment (and therefore also
            #            path) is Invalid
            if all(state is Invalid for state in neighbor_assertions):
                return Invalid
            # step 2.2 - if either neighbor asserts 'transit' is an
            #            authorised provider, segment is Valid
            if any(state is Valid for state in neighbor_assertions):
                continue
            # step 2.3 - otherwise, the segment is unknown.
            #            the path will be unkown unless some later segment
            #            is Invalid
            path_state = Unknown
        return path_state

    def verify_pair(self, as1, as2, afi):
        try:
            provider_as_set = self.aspa_set.get_providers(as1, afi)
        except NoAspa:
            return Unknown
        if as2 in provider_as_set:
            return Valid
        return Invalid
