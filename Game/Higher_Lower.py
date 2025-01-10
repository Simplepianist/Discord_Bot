import random


class Higher_Lower:
    def __init__(self, bet):
        self.hidden = None
        self.shown = None
        self.draw_numbers()
        self.bet = bet

    def is_identical(self):
        return self.hidden == self.shown

    def won(self, guess: str):
        if guess == "higher":
            return self.hidden > self.shown
        if guess == "lower":
            return self.hidden < self.shown

    def draw_numbers(self):
        self.hidden = random.randint(0, 100)
        self.shown = random.randint(0, 100)
