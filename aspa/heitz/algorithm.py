# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
# Derived from:
#   https://mailarchive.ietf.org/arch/msg/sidrops/JeEZnHWjrS3j9ldshEoyUMMOwus/
#   Credit: Jakob Heitz
#
"""aspa.heitz.algorithm Module."""

from ..as_path import AS_SEQUENCE, AsPath
from ..aspa import AspaSet, NoAspa
from ..meta import MetaValidator
from ..state import Unverifiable, Unknown, Valid, Invalid


class Validator(metaclass=MetaValidator):
    """ASPA verification alternative triple-wise algorithm."""

    name = "HeitzValidator"

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
            #
            # step 2.1 - (incorporating step 3, since 2.1 is the special case
            #            n=1)
            #            if a sequence of transits T1..Tn (n >= 1) exists, such
            #            that:
            #            - the left neighor of T1 asserts that T1 is not an
            #              authorised provider; and
            #            - the right neighbor of Tn asserts that Tn is not an
            #              authorised provider
            #            then there is no possible set of ASPA objects for
            #            which the path can be Valid.
            #
            # check if the left neighbor of 'transit' has asserted that
            # 'transit' is not a provider
            if self.verify_left(as_seq, i, afi) is Invalid:
                # iterate over the remaining transits in the sequence
                # start at 'i', to account for case 'transit' == 'next_transit'
                for next_transit in as_seq[i:-1]:
                    # get index of 'next_transit' in 'as_seq'
                    j = as_seq.index(next_transit)
                    # check if the right neighbor of 'next_transit' has
                    # asserted that 'next_transit' is not a provider
                    if self.verify_right(as_seq, j, afi) is Invalid:
                        # the sequence 'transit..next_transit' is a valley
                        # there is a leak in there somewhere
                        return Invalid
            #
            # step 2.2 - if either neighbor asserts 'transit' is an
            #            authorised provider, segment is Valid.
            #
            if (self.verify_left(as_seq, i, afi) is Valid or
                    self.verify_right(as_seq, i, afi) is Valid):
                continue
            #
            # step 2.3 - otherwise, the segment is Unknown.
            #            the path will be Unkown unless some later segment
            #            is Invalid
            #
            path_state = Unknown
        return path_state

    def verify_left(self, as_seq, index, afi):
        return self.verify_pair(as_seq[index-1], as_seq[index], afi)

    def verify_right(self, as_seq, index, afi):
        return self.verify_pair(as_seq[index+1], as_seq[index], afi)

    def verify_pair(self, as1, as2, afi):
        try:
            provider_as_set = self.aspa_set.get_providers(as1, afi)
        except NoAspa:
            return Unknown
        if as2 in provider_as_set:
            return Valid
        return Invalid
