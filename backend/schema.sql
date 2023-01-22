DROP TABLE IF EXISTS game_token;
DROP TABLE IF EXISTS game;

CREATE TABLE game (
    -- immutable
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seed TEXT,
    dealer TEXT, -- NSEW

    -- mutable
    direction_to_play TEXT, -- NSEW

    -- auction only
    bids TEXT, -- format TBD
    contract TEXT,
    declarer TEXT, -- NSEW

    -- gameplay only
    finished_tricks TEXT, -- format TBD
    current_trick_partial TEXT -- format TBD
);

CREATE TABLE game_token (
    game_id INTEGER,
    direction TEXT, -- NSEW
    token TEXT,

    FOREIGN KEY (game_id) REFERENCES game(id),
    PRIMARY KEY (game_id, direction)
);

