from enum import Enum
from typing import Self


class Direction(Enum):
    N = 'N'
    S = 'S'
    E = 'E'
    W = 'W'

    def verbose(self) -> str:
        return _DIRECTIONS_VERBOSE[self]

    def partner(self) -> Self:
        return _DIRECTION_PARTNERS[self]

    def left(self) -> Self:
        return _DIRECTION_LEFT_OF[self]

    def right(self) -> Self:
        return _DIRECTION_RIGHT_OF[self]

    def clockwise_by(self, n: int) -> Self:
        n_modulo = n % 4

        if n_modulo == 0:
            return self
        elif n_modulo == 1:
            return self.left()
        elif n_modulo == 2:
            return self.partner()
        else:
            return self.right()

    def __repr__(self):
        return self.value

    def encode(self):
        return self.value

    @classmethod
    def decode_optional(cls, encoding: str | None) -> Self | None:
        return None if encoding == None else cls(encoding)


_DIRECTION_PARTNERS = {Direction.N: Direction.S, Direction.S: Direction.N,
                       Direction.E: Direction.W, Direction.W: Direction.E}
_DIRECTIONS_VERBOSE = {Direction.N: 'North',
                       Direction.S: 'South', Direction.E: 'East', Direction.W: 'West'}
_DIRECTION_LEFT_OF = {Direction.N: Direction.E, Direction.S: Direction.W,
                      Direction.E: Direction.S, Direction.W: Direction.N}
_DIRECTION_RIGHT_OF = {Direction.N: Direction.W, Direction.S: Direction.E,
                       Direction.E: Direction.N, Direction.W: Direction.S}
