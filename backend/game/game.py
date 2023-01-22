from uuid import uuid4
import random

from flask import flash
from backend.db import get_db
from backend.game.hand import Hand
from backend.util import seed_random, generate_token
from typing import Self
from enum import Enum

from backend.game.direction import Direction
from backend.game.card import Card
from backend.game.bid import AdvancingBid, Bid, BidNumber, PassBid, Trump

FRESH_DECK_IDS = [
    'AH', '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', '0H', 'JH', 'QH', 'KH',
    'AS', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '0S', 'JS', 'QS', 'KS',
    'AD', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '0D', 'JD', 'QD', 'KD',
    'AC', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', '0C', 'JC', 'QC', 'KC'
]


class Stage(Enum):
    Auction = 0
    Tricks = 1


class Game:

    @classmethod
    def from_row(cls, row) -> Self:
        return Game(
            id=row['id'],
            seed=row['seed'],
            dealer=Direction(row['dealer']),
            direction_to_play=Direction(row['direction_to_play']),
            bids=Bid.decodeArray(row['bids'])
        )

    def __init__(self,
                 id: int,
                 seed: str,
                 dealer: Direction,
                 direction_to_play: Direction,
                 bids: list[Bid] | None = None,
                 contract: str | None = None,
                 declarer: Direction | None = None,
                 finished_tricks: str | None = None,
                 current_trick_partial: str | None = None):

        self.id = id
        self.seed = seed
        self.dealer = dealer
        self.direction_to_play = Direction(direction_to_play)

        self.bids = bids
        advancing_bids = [bid for bid in bids if isinstance(bid, AdvancingBid)]
        self.current_bid = max(advancing_bids) if len(
            advancing_bids) > 0 else None
        print(self.current_bid)

        self.possible_pass_bid = PassBid()
        self.possible_next_bids = [
            [AdvancingBid(number=BidNumber(number), trump=trump)
             for trump in Trump]
            for number in range(1, 8)
        ]

        with seed_random(seed):
            self.deck = [Card(card_id)
                         for card_id in random.sample(FRESH_DECK_IDS, 52)]

        self.hands = {
            Direction.N: Hand(self.deck[:13]),
            Direction.W: Hand(self.deck[13:26]),
            Direction.S: Hand(self.deck[26:39]),
            Direction.E: Hand(self.deck[39:])
        }

        self.stage = Stage.Auction if contract == None else Stage.Tricks


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


def update_bids(id, bids):
    db = get_db()

    try:
        db.execute(
            "UPDATE game SET bids=? WHERE id=?", (bids, id,)
        )
        db.commit()
    except db.IntegrityError:
        pass
