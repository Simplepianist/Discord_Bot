import random


class Blackjack:
    def __init__(self, bet):
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
        for _ in range(2):
            self.draw_another("player")

        self.natural_player = self.is_blackjack("player")
        for _ in range(2):
            self.draw_another("dealer")

    def is_blackjack(self, who):
        if who == "player":
            if self.player == 21 and len(self.playerdrawn) == 2:
                return True
            return False
        if self.dealer == 21 and len(self.dealerdrawn) == 2:
            return True
        return False

    def draw_another(self, who):
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
        if kind == "player":
            self.playerstand = True
        elif kind == "dealer":
            self.dealerstand = True

    def dealer_draw(self):
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
        if kind == "player":
            if self.player > 21:
                return True
            return False
        if kind == "dealer":
            if self.dealer > 21:
                return True
        return False

    def is_over(self):
        if self.playerstand and self.dealerstand:
            return True
        return False

    def won(self):
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
        winner = self.won()
        if winner == "draw":
            return self.bet
        if winner == "player":
            return int(self.bet) * 2
        if winner == "dealer":
            return 0
        if winner == "doppelt":
            return int(int(self.bet) * 2.5 - self.bet)
