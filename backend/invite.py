from backend.db import get_db
from backend.game.game import Direction


class GameInvite:

    def __init__(self, game_id: str, token: str, direction: str):
        self.token = token
        self.game_id = game_id
        self.direction = Direction(direction)

    @classmethod
    def from_row(cls, row):
        return GameInvite(row['game_id'], row['token'], row['direction'])


def load_game_invites(game_id):
    db = get_db()

    try:
        rows = db.execute(
            "SELECT token, game_id, direction from game_token where game_id=?", (
                game_id,)
        ).fetchall()

        return [GameInvite.from_row(row) for row in rows]

    except db.IntegrityError:
        pass

    return None


def load_invite_from_token(token):
    db = get_db()

    try:
        row = db.execute(
            "SELECT token, game_id, direction from game_token where token=?", (
                token,)
        ).fetchone()

        if row:
            return GameInvite.from_row(row)
        else:
            return None

    except db.IntegrityError:
        pass

    return None
