from backend.game.suit import Suit


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
