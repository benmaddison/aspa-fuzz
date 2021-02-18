# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
"""aspa.as_path Module."""


AS_SEQUENCE = 0x0
AS_SET = 0x1


class AsPathSegment(object):
    def __init__(self, segment_type, values):
        if segment_type not in (AS_SEQUENCE, AS_SET):
            raise ValueError(int)
        self.type = segment_type
        self.values = values

    def __repr__(self):
        values = map(str, reversed(self.values))
        if self.type == AS_SEQUENCE:
            return f"{'_'.join(values)}"
        else:
            return f"[ {' '.join(values)} ]"


class AsPath(object):
    def __init__(self, *segments):
        for s in segments:
            if not isinstance(s, AsPathSegment):
                raise TypeError(f"expected AsPathSegment, got {s}")
        self.segments = segments

    def __repr__(self):
        return f"{'_'.join(map(repr, reversed(self.segments)))}"

    def flatten(self):
        return [AsPathElement(orig_segment_type=s.type, value=v)
                for s in self.segments
                for v in s.values]


class AsPathElement(object):
    def __init__(self, orig_segment_type, value):
        self.type = orig_segment_type
        self.value = value
