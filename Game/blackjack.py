"""
Blackjack game implementation in Python.

This module provides a class `Blackjack` to simulate a simple blackjack game.
"""

import random

class Blackjack:
    """
    A class to represent a Blackjack game.

    Attributes:
    cards (list): List of card values.
    kinds (list): List of card suits.
    bet (int): The bet amount.
    dealer (int): Dealer's current score.
    player (int): Player's current score.
    playerdrawn (list): List of cards drawn by the player.
    natural_player (bool): Indicates if the player has a natural blackjack.
    dealerdrawn (list): List of cards drawn by the dealer.
    playerstand (bool): Indicates if the player has chosen to stand.
    dealerstand (bool): Indicates if the dealer has chosen to stand.
    """

    def __init__(self, bet):
        """
        Initialize the Blackjack game with a bet amount.

        Parameters:
        bet (int): The bet amount.
        """
        self.cards = ["Ass", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Bube", "Dame", "König"]
        self.kinds = [["heart", "space", "diamonds", "clubs"],
                      ["heart", "space", "diamonds", "clubs"],
                      ["heart", "space", "diamonds", "clubs"],
                      ["heart", "space", "diamonds", "clubs"],
                      ["heart", "space", "diamonds", "clubs"],
                      ["heart", "space", "diamonds", "clubs"],
                      ["heart", "space", "diamonds", "clubs"],
                      ["heart", "space", "diamonds", "clubs"],
                      ["heart", "space", "diamonds", "clubs"],
                      ["heart", "space", "diamonds", "clubs"],
                      ["heart", "space", "diamonds", "clubs"],
                      ["heart", "space", "diamonds", "clubs"],
                      ["heart", "space", "diamonds", "clubs"]]
        self.bet = bet
        self.dealer = 0
        self.player = 0
        self.playerdrawn = []
        self.natural_player = False
        self.dealerdrawn = []
        self.playerstand = False
        self.dealerstand = False

    def firstdraw(self):
        """
        Perform the initial draw for both player and dealer.
        """
        for _ in range(2):
            self.draw_another("player")

        self.natural_player = self.is_blackjack("player")
        for _ in range(2):
            self.draw_another("dealer")

    def is_blackjack(self, who):
        """
        Check if the given player or dealer has a blackjack.

        Parameters:
        who (str): "player" or "dealer" to check for blackjack.

        Returns:
        bool: True if the specified player or dealer has a blackjack, False otherwise.
        """
        if who == "player":
            if self.player == 21 and len(self.playerdrawn) == 2:
                return True
            return False
        if self.dealer == 21 and len(self.dealerdrawn) == 2:
            return True
        return False

    def draw_another(self, who):
        """
        Draw another card for the specified player or dealer.

        Parameters:
        who (str): "player" or "dealer" to draw a card for.
        """
        try:
            drawnnum = random.randint(0, len(self.cards) - 1)
        except ValueError:
            drawnnum = 0
        drawn = self.cards[drawnnum]
        try:
            kindnum = random.randint(0, len(self.kinds[drawnnum]) - 1)
        except ValueError:
            kindnum = 0
        kind = self.kinds[drawnnum][kindnum]
        if len(self.kinds[drawnnum]) - 1 == 0:
            self.cards.pop(drawnnum)
        self.kinds[drawnnum].pop(kindnum)
        if who == "dealer":
            self.dealerdrawn.append([drawn, kind])
        elif who == "player":
            self.playerdrawn.append([drawn, kind])
        self.recalc(who)

    def recalc(self, who):
        """
        Recalculate the score for the specified player or dealer.

        Parameters:
        who (str): "player" or "dealer" to recalculate the score for.
        """
        if who == "player":
            self.player = 0
            assplayer = 0
            for card in self.playerdrawn:
                worth = card[0]
                if worth in ["Bube", "Dame", "König"]:
                    self.player += 10
                elif worth == "Ass":
                    assplayer += 1
                else:
                    self.player += int(worth)
            if assplayer != 0:
                noted = 0
                for i in range(assplayer):
                    noted += 11
                test = self.player + noted
                i = 0
                while test > 21 and i < assplayer:
                    test -= 10
                    i += 1
                self.player = test
        elif who == "dealer":
            assdealer = 0
            self.dealer = 0
            for card in self.dealerdrawn:
                worth = card[0]
                if worth in ["Bube", "Dame", "König"]:
                    self.dealer += 10
                elif worth == "Ass":
                    assdealer += 1
                else:
                    self.dealer += int(worth)
            if assdealer != 0:
                noted = 0
                for i in range(assdealer):
                    noted += 11
                test = self.dealer + noted
                i = 0
                while test > 21 and i < assdealer:
                    test -= 10
                    i += 1
                self.dealer = test

    def stand(self, kind):
        """
        Set the stand status for the specified player or dealer.

        Parameters:
        kind (str): "player" or "dealer" to set the stand status for.
        """
        if kind == "player":
            self.playerstand = True
        elif kind == "dealer":
            self.dealerstand = True

    def dealer_draw(self):
        """
        Determine if the dealer should draw another card.

        Returns:
        bool: True if the dealer should draw another card, False otherwise.
        """
        for card in self.dealerdrawn:
            if (card[0] == "Ass" and not (
                    self.dealer > 17 and self.is_overbought("player"))
                    and not self.dealer >= self.player):
                return True
        if self.dealer < 17:
            return True
        if self.dealer < self.player and not self.is_overbought("player"):
            return True
        return False

    def is_overbought(self, kind):
        """
        Check if the specified player or dealer is overbought (score > 21).

        Parameters:
        kind (str): "player" or "dealer" to check for overbought.

        Returns:
        bool: True if the specified player or dealer is overbought, False otherwise.
        """
        if kind == "player":
            if self.player > 21:
                return True
            return False
        if kind == "dealer" and self.dealer > 21:
            return True
        return False

    def is_over(self):
        """
        Check if the game is over (both player and dealer have stood).

        Returns:
        bool: True if the game is over, False otherwise.
        """
        if self.playerstand and self.dealerstand:
            return True
        return False

    def won(self):
        """
        Determine the winner of the game.

        Returns:
        str: "player", "dealer", "draw", or "doppelt" indicating the winner.
        """
        if (self.player == self.dealer and not self.is_overbought("player")
                and not self.is_overbought(
                "dealer") or self.is_overbought("player") and self.is_overbought("dealer")):
            if self.is_blackjack("player") and not self.is_blackjack("dealer"):
                return "doppelt"
            return "draw"
        if self.dealer > self.player and not self.is_overbought("dealer"):
            return "dealer"
        if self.player > self.dealer and not self.is_overbought("player"):
            if self.is_blackjack("player") and not self.is_blackjack("dealer"):
                return "doppelt"
            return "player"
        if self.is_overbought("player"):
            return "dealer"
        if self.is_overbought("dealer"):
            if self.is_blackjack("player") and not self.is_blackjack("dealer"):
                return "doppelt"
            return "player"
        return "draw"

    def get_money(self):
        """
        Calculate the money won or lost based on the game result.

        Returns:
        int: The amount of money won or lost.
        """
        winner = self.won()
        if winner == "player":
            return int(self.bet) * 2
        if winner == "dealer":
            return 0
        if winner == "doppelt":
            return int(int(self.bet) * 2.5 - self.bet)
        return self.bet
