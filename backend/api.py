from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from backend.game.bid import AdvancingBid, Bid
from backend.game.game import Stage, load_game

from backend.invite import load_invite_from_token

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/bid', methods=["POST"])
def bid():
    token = request.form['token']
    bid_encoded = request.form['bid']
    bid = Bid.decode(bid_encoded)

    invite = load_invite_from_token(token)
    if not invite:
        return "Invalid Token"

    game = load_game(invite.game_id)
    if not game:
        return "Could not find game from access token"

    if game.stage != Stage.Auction:
        return "invalid action: cannot bid after auction is over"

    if game.direction_to_play != invite.direction:
        return f"invalid action: it isn't your turn ({invite.direction.verbose()}), its { game.direction_to_play.verbose()}'s turn"

    if not bid.is_pass() and game.current_bid >= bid:
        return f"invalid action: attempting to bid {bid.display()}. must bid higher than the current bid ({game.current_bid.display()})"

    next_game = game.make_bid(bid)

    next_game.save()

    return redirect(url_for('play', token=token))
