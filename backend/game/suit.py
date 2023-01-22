from enum import Enum


class Suit(Enum):
    C = 'C'
    D = 'D'
    H = 'H'
    S = 'S'

    def emoji(self):
        return _SUIT_EMOJIS[self]

    def color(self):
        return _SUIT_COLORS[self]


_SUIT_EMOJIS = {Suit.H: '♥️', Suit.S: '♠️', Suit.C: '♣️', Suit.D: '♦️'}
_SUIT_COLORS = {Suit.H: 'text-red-500', Suit.S: 'text-blue-500',
                Suit.C: 'text-green-500', Suit.D: 'text-yellow-500'}
