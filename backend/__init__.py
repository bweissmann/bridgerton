from flask import Flask, redirect, render_template, url_for
import os
from flask import request
from backend.game.bid import Bid

from backend.game.game import create_game, get_player_directions, load_all_game_ids, load_game
from backend.invite import load_game_invites, load_invite_from_token


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'bridgerton.sqlite'),
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def home():
        return render_template('home.html.jinja', id=id)

    @app.route("/join")
    def join():
        game_ids = load_all_game_ids()
        return render_template('join.html.jinja', game_ids=game_ids)

    @app.route("/lobby/<string:id>")
    def lobby(id):
        game_invites = load_game_invites(id)
        invites_by_direction = {
            invite.direction.value: invite for invite in game_invites}
        game = load_game(id)
        if not game:
            return "Invalid Lobby"

        return render_template('lobby.html.jinja', game=game, invites_by_direction=invites_by_direction)

    @app.route("/play/<string:token>")
    def play(token):
        invite = load_invite_from_token(token)
        if not invite:
            return "Invalid Token"

        all_invites = load_game_invites(invite.game_id)
        players = get_player_directions(invite.direction, all_invites)
        game = load_game(invite.game_id)

        new_game = game.make_bid(Bid.decode('X'))
        print(new_game.dealer, new_game.contract)
        return render_template('play.html.jinja', game=game, invite=invite, players=players)

    @app.route("/newgame", methods=["POST"])
    def new():
        game = create_game()
        return redirect(url_for('lobby', id=game.id))

    from . import db
    db.init_app(app)

    from . import api
    app.register_blueprint(api.bp)

    return app
