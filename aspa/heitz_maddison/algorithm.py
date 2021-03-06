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
        # Step 0 - return early if there are AS_SETs in the path
        #
        if any((s.type != AS_SEQUENCE for s in as_path.segments)):
            return Unverifiable
        #
        # Step 1 - prepare de-duplicated AS sequence
        #
        as_seq = list()
        for segment in as_path.segments:
            for asn in segment.values:
                try:
                    last = as_seq[-1]
                except IndexError:
                    last = None
                if asn != last:
                    as_seq.append(asn)
        as_seq.append(self.local_as)
        #
        # Step 2 - Initialise the path state to Valid
        #
        path_state = Valid
        #
        # Step 3 - iterate over transited ASNs
        #
        for transit in as_seq[1:-1]:
            #
            # Get index of 'transit' in 'as_seq'
            # Denote the ASN at as_seq[i] as Ti
            #
            i = as_seq.index(transit)
            #
            # Step 3.1 - determine whether Ti-1 asserts that Ti is an authorised
            #            provider
            #
            transit_for_left = self.verify_left(as_seq, i, afi)
            #
            # Step 3.2 - if Ti is an authorised provider of Ti-1 then Ti cannot
            #            have leaked the path.
            if transit_for_left is not Authorised:
                #        Alternatively, search for a sequence beginning at Ti in
                #        which a leak may have occurred.
                #
                # Step 3.3 - Check sequences of transits Ti..Tj for j>=i
                #
                for next_transit in as_seq[i:-1]:
                    j = as_seq.index(next_transit)
                    #
                    # Step 3.4 - For each sequence of transits Ti..Tj, determine
                    #            whether Tj is an authorised provider of Tj+1.
                    #
                    transit_for_right = self.verify_right(as_seq, j, afi)
                    #
                    # Step 3.5 - If both:
                    #              - Ti-1 asserts that Ti is not an authorised
                    #                provider; and
                    #              - Tj+1 asserts that Tj is not an authorised
                    #                provider
                    #            then a route has been sent to a non-provider by
                    #            Ti-1 and received from a non-provider by Tj+1.
                    #
                    #            Thus, there must be a leak somewhere in the
                    #            sequence Ti..Tj.
                    #
                    #            Note that if i=j, then Ti is the leaker.
                    #
                    if transit_for_left is Unauthorised and \
                       transit_for_right is Unauthorised:
                        return Invalid
                    #
                    # Step 3.6 - If Tj+1 has not authorised Tj as a provider
                    #            (either explicity, or by failing to create an
                    #            ASPA object), then we do not have enough
                    #            information to assert whether the path is
                    #            Valid or Invalid.
                    #
                    #            That is, there are exist ASPA objects that, if
                    #            they were created, could make the path either
                    #            Valid or Invalid depending on the authorisations
                    #            They provide.
                    #
                    #            Thus, Valid is no-longer a possible outcome of
                    #            this verification procedure.
                    #
                    if transit_for_right is not Authorised:
                        path_state = Unknown
        #
        # Step 4 - Having iterated over all transits in the path, return the
        #          current path state.
        return path_state

    def verify_left(self, as_seq, index, afi):
        return self.verify_authorisation(as_seq[index-1], as_seq[index], afi)

    def verify_right(self, as_seq, index, afi):
        return self.verify_authorisation(as_seq[index+1], as_seq[index], afi)

    def verify_authorisation(self, as1, as2, afi):
        try:
            provider_as_set = self.aspa_set.get_providers(as1, afi)
        except NoAspa:
            return Unknown
        if as2 in provider_as_set:
            return Authorised
        return Unauthorised
