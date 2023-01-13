# bridgerton

## .plan

### guiding directions

first milemarker is a unauthenticated, multiplayer bridge game with all rules correctly enforced.
mutliple concurrent games should be allowed, and games should last beyond a client session (accessable by stable identifiers in persistant storage)

as documentation of direction, future milemarkers include (1) auth and accounts (2) serverside analysis of possible plays (3) addictive ux

### first decisions

i'm going to start with vanilla flask app and jinja templating. no react. the theory is that i can just make this a functional state machine backed by persistant storage and when realtime becomes neccessary (e.g. live updates from other players) try implementing a simple websocket/liveview inspired solution.

the flask tutorial is suggesting sqlite as db. the main thing im conisdering is ease of deployment. im not especially worried about speed, or storage size or anything becuase (1) bridge isnt realtime so 50ms is plenty (2) there isn't that much data, just some representation of moves, board state, etc, so i shouldn't fill up storage.

if im trying to get this on the web as simply as possible, there are lots of free postgres dbs out there (railroad & render to pick a few). if i use sqlite then i'll need a real cpu to run this on, not just some serverless compute service, which i don't exactly know how to do. might force me to learn aws a bit more (not the worst thing in the world). on the other hand tailscale seems to think sqlite works pretty good, so seems worth a shot.

also pretty sure if i want to switch from sqlite to pg it shouldnt be very hard.

### game representation

each game wil have a fixed seed that can reconstruct the deal (given a fixed random function) as well as a cached representation of the deal
