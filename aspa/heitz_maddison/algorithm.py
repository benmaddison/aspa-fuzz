# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
# Derived from:
#   https://mailarchive.ietf.org/arch/msg/sidrops/JeEZnHWjrS3j9ldshEoyUMMOwus/
#   Credit: Jakob Heitz
# With additional improvements:
#   - detection of Unknowns in the presence of siblings (issue #7)
#   - use of "Authorised" and "Unauthorised" to describe the relationships
#     ASes to avoid confusion with Valid and Invalid.
#   - Only de-duplicate consecutive ASNs in the AS_PATH
#
# """aspa.heitz_maddison.algorithm Module."""

from ..as_path import AS_SEQUENCE, AsPath
from ..aspa import AspaSet, NoAspa
from ..meta import MetaValidator
from ..state import (Unverifiable, Unknown,
                     Valid, Invalid,
                     Authorised, Unauthorised)


class Validator(metaclass=MetaValidator):
    """ASPA verification alternative triple-wise algorithm."""

    name = "HeitzMaddisonValidator"

    def __init__(self, aspa_set: AspaSet, local_as):
        self.aspa_set = aspa_set
        self.local_as = local_as

    def validate(self, as_path: AsPath, afi, **kwargs):
        #
        # Step 1 - prepare `propagation_path`
        #
        # 1.1 Initialise `propagation_path`
        propagation_path = list()
        # 1.2 Interate over as_path segments
        for segment in as_path.segments:
            # 1.2.1 Return early if non AS_SEQUENCE segments are found
            if segment.type != AS_SEQUENCE:
                return Unverifiable
            # 1.2.2 Append ASNs in AS_PATH to `propagation_path`
            for asn in segment.values:
                try:
                    last = propagation_path[-1]
                except IndexError:
                    last = None
                if asn != last:
                    propagation_path.append(asn)
        # 1.3 Append `local_as` to `propagation_path`
        propagation_path.append(self.local_as)
        #
        # Step 2 - Initialise the path state to Valid
        #
        partial_status = Valid
        #
        # Step 3 - iterate over transited ASNs
        #
        # Denote the ASN at propagation_path[k] as Tk
        #
        # TODO: fix nasty offset hack
        for offset_i, left_transit in enumerate(propagation_path[1:-1]):
            i = 1 + offset_i
            for offset_j, right_transit in enumerate(propagation_path[i:-1]):
                j = i + offset_j
                #
                # 3.1 - determine whether Ti-1 asserts that Ti is an authorised
                #       provider
                #
                transit_for_left = self.verify_left(propagation_path, i, afi)
                #
                # 3.2 - For each sequence of transits Ti..Tj, determine
                #       whether Tj is an authorised provider of Tj+1.
                #
                transit_for_right = self.verify_right(propagation_path, j, afi)
                #
                # 3.3 - If both:
                #         - Ti-1 asserts that Ti is not an authorised
                #           provider; and
                #         - Tj+1 asserts that Tj is not an authorised
                #           provider
                #       then a route has been sent to a non-provider by
                #       Ti-1 and received from a non-provider by Tj+1.
                #
                #       Thus, there must be a leak somewhere in the
                #       sequence Ti..Tj.
                #
                #       Note that if i=j, then Ti is the leaker.
                #
                if transit_for_left is Unauthorised and \
                   transit_for_right is Unauthorised:
                    return Invalid
                #
                # 3.4 - If either:
                #         - Ti-1 asserts that Ti is an authorised
                #           provider; or
                #         - Tj+1 asserts that Tj is an authorised
                #           provider,
                #       then no leak has occured in the sequence Ti..Tj.
                #
                #       Continue to the next sequence of transits.
                #
                if transit_for_left is Authorised or \
                   transit_for_right is Authorised:
                    continue
                #
                # 3.5 - We do not have enough information about this sequence
                #       to assert that no leak as occured.
                #
                #       The path can no longer be Valid.
                #
                partial_status = Unknown
        #
        # Step 4 - Having iterated over all sub-sequences of transits in the
        #          path, return the current path state.
        #
        return partial_status

    def verify_left(self, propagation_path, index, afi):
        return self.verify_authorisation(propagation_path[index-1],
                                         propagation_path[index],
                                         afi)

    def verify_right(self, propagation_path, index, afi):
        return self.verify_authorisation(propagation_path[index+1],
                                         propagation_path[index],
                                         afi)

    def verify_authorisation(self, as1, as2, afi):
        try:
            provider_as_set = self.aspa_set.get_providers(as1, afi)
        except NoAspa:
            return Unknown
        if as2 in provider_as_set:
            return Authorised
        return Unauthorised
