from enum import Enum
from typing import Self
from abc import ABC, abstractmethod
from functools import total_ordering

from backend.game.suit import Suit


class BidNumber(Enum):
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7


class Trump(Enum):
    C = 'C'
    D = 'D'
    H = 'H'
    S = 'S'
    NT = 'NT'

    def as_suit(self):
        if self == Trump.NT:
            return None

        return Suit(self.value)

    def ordinal(self):
        ords = {Trump.C: 0, Trump.D: 1, Trump.H: 2, Trump.S: 3, Trump.NT: 4}
        return ords[self]


@total_ordering
class Bid(ABC):

    @abstractmethod
    def color(self):
        pass

    @abstractmethod
    def encode(self) -> str:
        pass

    @abstractmethod
    def display(self):
        pass

    def __repr__(self) -> str:
        return self.encode()

    @abstractmethod
    def __eq__(self, other):
        return isinstance(other, PassBid)

    @abstractmethod
    def __gt__(self, other):
        return False

    @abstractmethod
    def is_pass(self) -> bool:
        pass

    @classmethod
    def decode(cls, encoding: str) -> Self:
        if encoding == 'X':
            return PassBid()

        return AdvancingBid(
            number=BidNumber(int(encoding[0])),
            trump=Trump(encoding[1:])
        )

    @classmethod
    def decode_optional(cls, encoding: str | None) -> Self | None:
        return None if encoding == None else cls.decode(encoding)

    @classmethod
    def decodeArray(cls, encoded_bids: str | None) -> list[Self]:
        if encoded_bids == None:
            return []

        return [Bid.decode(encoding) for encoding in encoded_bids.split(',')]

    @classmethod
    def encodeArray(cls, bids: list[Self]) -> str:
        return ','.join([bid.encode() for bid in bids])


class PassBid(Bid):

    def is_pass(self):
        return True

    def color(self):
        return 'text-black'

    def encode(self):
        return 'X'

    def display(self):
        return 'Pass'

    def __eq__(self, other):
        return isinstance(other, PassBid)

    def __gt__(self, other):
        return False


class AdvancingBid(Bid):

    def __init__(self, number: BidNumber, trump: Trump):
        self.number = number
        self.trump = trump

    def is_pass(self):
        return False

    def color(self):
        trump_suit = self.trump.as_suit()

        if trump_suit:
            return trump_suit.color()
        else:
            return 'text-black'

    def encode(self):
        return f'{self.number.value}{self.trump.value}'

    def display(self):
        trump_suit = self.trump.as_suit()
        return f'{self.number.value}{trump_suit.emoji() if trump_suit else "NT"}'

    def __eq__(self, other):
        return isinstance(other, AdvancingBid) and self.number == other.number and self.trump == other.trump

    def __gt__(self, other):
        if not isinstance(other, AdvancingBid):
            return True

        if self.number.value > other.number.value:
            return True

        return self.number.value == other.number.value and self.trump.ordinal() > other.trump.ordinal()


def last_n_passes(bids: list[Bid], n: int) -> bool:
    return len([bid for bid in bids[-n:] if bid.is_pass()]) == n


def highest_bid(bids: list[Bid]) -> AdvancingBid | None:
    advancing_bids = [bid for bid in bids if isinstance(bid, AdvancingBid)]
    return max(advancing_bids) if len(advancing_bids) > 0 else None
