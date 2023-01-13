from flask import Flask, redirect, render_template, url_for
import os

from backend.game import create_game, get_player_directions, load_game
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

    @app.route("/newgame", methods=["POST"])
    def new():
        game = create_game()
        return redirect(url_for('lobby', id=game.id))

    @app.route("/lobby/<string:id>")
    def lobby(id):
        game_invites = load_game_invites(id)
        game = load_game(id)
        if not game:
            return "Invalid Lobby"

        return render_template('lobby.html.jinja', game=game, invites=game_invites)

    @app.route("/play/<string:token>")
    def play(token):
        invite = load_invite_from_token(token)
        if not invite:
            return "Invalid Token"

        players = get_player_directions(invite.direction)
        game = load_game(invite.game_id)
        return render_template('play.html.jinja', game=game, players=players)

    from . import db
    db.init_app(app)

    return app
