# Copyright (c) 2021 Ben Maddison. All rights reserved.
#
"""aspa.meta Module."""


class MetaValidator(type):
    def __repr__(cls):
        try:
            return cls.name
        except AttributeError:
            super().__repr__()
