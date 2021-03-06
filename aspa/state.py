# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
"""aspa.state Module."""


class _BaseState(object):
    def __repr__(self):
        try:
            return self.name
        except AttributeError:
            return super().__repr__()


class _Unverifiable(_BaseState):
    name = "Unverifiable"


class _Unknown(_BaseState):
    name = "Unknown"


class _Valid(_BaseState):
    name = "Valid"


class _Invalid(_BaseState):
    name = "Invalid"


class _Authorised(_BaseState):
    name = "Authorised"


class _Unauthorised(_BaseState):
    name = "Unauthorised"


Unverifiable = _Unverifiable()
Unknown = _Unknown()
Valid = _Valid()
Invalid = _Invalid()
Authorised = _Authorised()
Unauthorised = _Unauthorised()
