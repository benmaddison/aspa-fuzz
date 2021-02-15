# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
"""aspa.state Module."""


class _BaseState(object):
    pass


class _Unverifiable(_BaseState):
    pass


class _Unknown(_BaseState):
    pass


class _Valid(_BaseState):
    pass


class _Invalid(_BaseState):
    pass


Unverifiable = _Unverifiable()
Unknown = _Unknown()
Valid = _Valid()
Invalid = _Invalid()
