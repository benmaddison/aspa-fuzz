# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
# Derived from:
#   https://tools.ietf.org/id/draft-ietf-sidrops-aspa-verification-06.txt
#   Copyright (c) 2020 IETF Trust
#                      and the persons identified as the document authors.
#
"""aspa.draft-06.algorithm Module."""

from ..as_path import AS_SEQUENCE, AsPath
from ..aspa import AspaSet, NoAspa
from ..meta import MetaValidator
from ..neighbors import (Customer, IxpRouteServer, IxpRouteServerClient,
                         Peer, Provider)
from ..state import Unverifiable, Unknown, Valid, Invalid


class Validator(metaclass=MetaValidator):
    """ASPA verification as defined in draft-sidrops-aspa-verification-06."""

    name = "Draft6Validator"

    def __init__(self, aspa_set: AspaSet, **kwargs):
        self.aspa_set = aspa_set

    def validate(self, as_path: AsPath, neighbor_as, afi, neighbor_type):
        flattened_path = as_path.flatten()
        if neighbor_type in (Customer, Peer, IxpRouteServerClient):
            return self.check_upflow_path(flattened_path, neighbor_as, afi)
        elif neighbor_type is Provider:
            return self.check_downflow_path(flattened_path, neighbor_as,
                                            afi, from_ix=False)
        elif neighbor_type is IxpRouteServer:
            return self.check_downflow_path(flattened_path, neighbor_as,
                                            afi, from_ix=True)
        else:
            raise TypeError(f"Expected neighbor type, got '{neighbor_type}'")

    def verify_pair(self, as1, as2, afi):
        try:
            provider_as_set = self.aspa_set.get_providers(as1, afi)
        except NoAspa:
            return Unknown
        if as2 in provider_as_set:
            return Valid
        return Invalid

    def check_upflow_path(self, aspath, neighbor_as, afi):
        if len(aspath) == 0:
            return Invalid

        if aspath[-1].type == AS_SEQUENCE and aspath[-1].value != neighbor_as:
            return Invalid

        semi_state = Valid

        as1 = 0
        for segment in aspath:
            if segment.type != AS_SEQUENCE:
                as1 = 0
                semi_state = Unverifiable
            elif segment.type == AS_SEQUENCE:
                if not as1:
                    as1 = segment.value
                elif as1 == segment.value:
                    continue
                else:
                    pair_check = self.verify_pair(as1, segment.value, afi)
                    if pair_check == Invalid:
                        return Invalid
                    elif pair_check == Unknown and semi_state == Valid:
                        semi_state = pair_check
                    as1 = segment.value
        return semi_state

    def check_downflow_path(self, aspath, neighbor_as, afi, from_ix):  # noqa: E901
        if len(aspath) == 0:
            return Invalid

        if aspath[-1].type == AS_SEQUENCE and not from_ix and aspath[-1].value != neighbor_as:  # noqa: E501
            return Invalid
        else:
            semi_state = Valid

        as1 = 0
        upflow_fragment = True
        for segment in aspath:
            if segment.type != AS_SEQUENCE:
                as1 = 0
                semi_state = Unverifiable
            elif segment.type == AS_SEQUENCE:
                if not as1:
                    as1 = segment.value
                elif as1 == segment.value:
                    continue
                else:
                    if upflow_fragment:
                        pair_check = self.verify_pair(as1, segment.value, afi)
                        if pair_check == Invalid:
                            upflow_fragment = False
                        elif pair_check == Unknown and semi_state == Valid:
                            semi_state = Unknown
                    else:
                        pair_check = self.verify_pair(segment.value, as1, afi)
                        if pair_check == Invalid:
                            return Invalid
                        elif pair_check == Unknown and semi_state == Valid:
                            semi_state = pair_check
                    as1 = segment.value

        return semi_state
