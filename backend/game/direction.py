from enum import Enum


class Direction(Enum):
    N = 'N'
    S = 'S'
    E = 'E'
    W = 'W'

    def verbose(self) -> str:
        return _DIRECTIONS_VERBOSE[self]

    def partner(self):
        return _DIRECTION_PARTNERS[self]

    def left(self):
        return _DIRECTION_LEFT_OF[self]

    def right(self):
        return _DIRECTION_RIGHT_OF[self]


_DIRECTION_PARTNERS = {Direction.N: Direction.S, Direction.S: Direction.N,
                       Direction.E: Direction.W, Direction.W: Direction.E}
_DIRECTIONS_VERBOSE = {Direction.N: 'North',
                       Direction.S: 'South', Direction.E: 'East', Direction.W: 'West'}
_DIRECTION_LEFT_OF = {Direction.N: Direction.E, Direction.S: Direction.W,
                      Direction.E: Direction.S, Direction.W: Direction.N}
_DIRECTION_RIGHT_OF = {Direction.N: Direction.W, Direction.S: Direction.E,
                       Direction.E: Direction.N, Direction.W: Direction.S}
