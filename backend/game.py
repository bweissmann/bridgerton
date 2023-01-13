from uuid import uuid4
import random

from flask import flash
from backend.db import get_db
from backend.util import seed_random, generate_token
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

FRESH_DECK_IDS = [
    'AH', '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', '0H', 'JH', 'QH', 'KH',
    'AS', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '0S', 'JS', 'QS', 'KS',
    'AD', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '0D', 'JD', 'QD', 'KD',
    'AC', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', '0C', 'JC', 'QC', 'KC'
]


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


class Card:

    def __init__(self, identifier: str):
        if len(identifier) != 2:
            raise Exception(f'Invalid card identifier: {identifier}')

        value_id = identifier[0]
        suit_id = identifier[1]

        self.value = value_id if value_id != '0' else '10'
        self.suit = Suit(suit_id)

    def hcp(self):
        hcp_values = {'J': 1, 'Q': 2, 'K': 3, 'A': 4}
        return hcp_values[self.value] if self.value in hcp_values else 0

    def cmp(self):
        facecard_values = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return (self.suit.value, facecard_values[self.value] if self.value in facecard_values else int(self.value))


class Game:

    @classmethod
    def from_row(cls, row):
        return Game(row['id'], row['seed'], Direction(row['dealer']), Direction(row['direction_to_play']))

    def __init__(self,
                 id: int,
                 seed: str,
                 dealer: Direction,
                 direction_to_play: Direction,
                 bids: str | None = None,
                 contract: str | None = None,
                 declarer: Direction | None = None,
                 finished_tricks: str | None = None,
                 current_trick_partial: str | None = None):
        self.id = id
        self.seed = seed
        self.dealer = dealer
        self.direction_to_play = Direction(direction_to_play)

        with seed_random(seed):
            self.deck = [Card(card_id)
                         for card_id in random.sample(FRESH_DECK_IDS, 52)]

        self.hands = {
            Direction.N: Hand(self.deck[:13]),
            Direction.W: Hand(self.deck[13:26]),
            Direction.S: Hand(self.deck[26:39]),
            Direction.E: Hand(self.deck[39:])
        }


class Hand:

    def __init__(self, cards: list[Card]):
        self.cards = sorted(cards, key=lambda card: card.cmp())
        self.hcp = sum([card.hcp() for card in self.cards])


def get_player_directions(you: Direction):
    return {'you': you, 'partner': you.partner(), 'left': you.left(), 'right': you.right()}


def create_game():
    seed = uuid4()
    dealer = random.choice([e.value for e in Direction])

    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO game (seed, dealer, direction_to_play) VALUES (?, ?, ?) RETURNING *",
            (str(seed), dealer, dealer)
        )
        row = cursor.fetchone()
        id = row['id']
        cursor.execute(
            "INSERT INTO game_token (game_id, direction, token) VALUES (?,?,?), (?,?,?), (?,?,?), (?,?,?)",
            (id, "N", generate_token(),
             id, "W", generate_token(),
             id, "S", generate_token(),
             id, "E", generate_token(),)
        )
        db.commit()

        return Game.from_row(row)
    except db.IntegrityError:
        flash("issue with the db")

    return None


def load_game(id):
    db = get_db()
    try:
        row = db.execute(
            "SELECT * FROM game WHERE id=?", (id,)
        ).fetchone()

        return Game.from_row(row) if row else None

    except db.IntegrityError:
        flash("issue with the db")

    return None
