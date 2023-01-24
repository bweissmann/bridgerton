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
from backend.game.bid import AdvancingBid, Bid, BidNumber, PassBid, Trump, highest_bid, last_n_passes

FRESH_DECK_IDS = [
    'AH', '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', '0H', 'JH', 'QH', 'KH',
    'AS', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '0S', 'JS', 'QS', 'KS',
    'AD', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '0D', 'JD', 'QD', 'KD',
    'AC', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', '0C', 'JC', 'QC', 'KC'
]


class Stage(Enum):
    Auction = 0
    Tricks = 1
    NoGame = 2  # Four passes to start auction = no game

    def is_auction(self):
        return self == Stage.Auction

    def is_tricks(self):
        return self == Stage.Tricks

    def is_no_game(self):
        return self == Stage.NoGame


class Game:

    @classmethod
    def from_row(cls, row) -> Self:
        return Game(
            id=row['id'],
            seed=row['seed'],
            dealer=Direction(row['dealer']),
            direction_to_play=Direction(row['direction_to_play']),
            bids=Bid.decodeArray(row['bids']),
            contract=Bid.decode_optional(row['contract']),
            declarer=Direction.decode_optional(row['declarer']),
            finished_tricks=row['finished_tricks'],
            current_trick_partial=row['current_trick_partial']
        )

    def __init__(self,
                 id: int,
                 seed: str,
                 dealer: Direction,
                 direction_to_play: Direction,
                 bids: list[Bid] | None = None,
                 contract: Bid | None = None,
                 declarer: Direction | None = None,
                 finished_tricks: str | None = None,
                 current_trick_partial: str | None = None):

        self.id = id
        self.seed = seed
        self.dealer = dealer
        self.direction_to_play = direction_to_play
        self.bids = bids
        self.contract = contract
        self.declarer = declarer
        self.finished_tricks = finished_tricks
        self.current_trick_partial = current_trick_partial

        self.bids_by = [
            {'direction': self.dealer, 'bids': bids[0::4]},
            {'direction': self.dealer.left(), 'bids': bids[1::4]},
            {'direction': self.dealer.partner(), 'bids': bids[2::4]},
            {'direction': self.dealer.right(), 'bids': bids[3::4]}
        ]
        self.current_bid = highest_bid(bids)

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

        if contract != None:
            self.stage = Stage.Tricks
        elif len(self.bids) == 4 and self.current_bid == None:
            self.stage = Stage.NoGame
        else:
            self.stage = Stage.Auction

    # Immutable, returns a new game object
    def make_bid(self, bid: Bid) -> Self:
        updated_bids = self.bids + [bid] if self.bids else [bid]
        # if some advancing bid exists and last three bids are passes => set contract
        if self.current_bid != None and last_n_passes(updated_bids, 3):
            contract = highest_bid(updated_bids)
            last_bidder_index = updated_bids.index(contract)
            bids_by_contract_team = updated_bids[last_bidder_index % 2::2]
            bids_by_contract_team_in_trump = [
                bid for bid in bids_by_contract_team if not bid.is_pass() and bid.trump == contract.trump]
            declarer_index = updated_bids.index(
                bids_by_contract_team_in_trump[0])
            declarer = self.dealer.clockwise_by(declarer_index)

            return Game(
                id=self.id,
                seed=self.seed,
                dealer=self.dealer,
                contract=highest_bid(updated_bids),
                declarer=declarer,
                direction_to_play=declarer.left(),
                bids=updated_bids
            )
        else:
            return Game(
                id=self.id,
                seed=self.seed,
                dealer=self.dealer,
                direction_to_play=self.direction_to_play.left(),
                bids=updated_bids
            )

    def encoded_bids(self):
        return Bid.encodeArray(self.bids)

    def save(self):
        db = get_db()

        try:
            db.execute(
                """
                UPDATE game 
                SET 
                    direction_to_play=?, 
                    bids=?, 
                    contract=?, 
                    declarer=?,
                    finished_tricks=?, 
                    current_trick_partial=? 
                WHERE id=?
                """,
                (
                    self.direction_to_play.encode(),
                    self.encoded_bids(),
                    self.contract.encode() if self.contract else None,
                    self.declarer.encode() if self.contract else None,
                    self.finished_tricks,
                    self.current_trick_partial,
                    self.id,
                )
            )
            db.commit()
        except db.IntegrityError:
            pass


def get_player_directions(you: Direction, invites):
    partner_invite = next(
        invite for invite in invites if invite.direction == you.partner())
    left_invite = next(
        invite for invite in invites if invite.direction == you.left())
    right_invite = next(
        invite for invite in invites if invite.direction == you.right())
    return {'you': you, 'partner': you.partner(), 'left': you.left(), 'right': you.right(), 'tokens': {'partner': partner_invite.token, 'left': left_invite.token, 'right': right_invite.token}}


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


def load_all_game_ids():
    db = get_db()
    try:
        rows = db.execute(
            "SELECT id FROM game"
        ).fetchall()

        return [row['id'] for row in rows]

    except db.IntegrityError:
        flash("issue with the db")

    return None
