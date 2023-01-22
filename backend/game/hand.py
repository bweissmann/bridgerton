from backend.game.card import Card


class Hand:

    def __init__(self, cards: list[Card]):
        self.cards = sorted(cards, key=lambda card: card.cmp())
        self.hcp = sum([card.hcp() for card in self.cards])
