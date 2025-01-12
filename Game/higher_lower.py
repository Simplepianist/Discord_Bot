"""
Dieses Modul enthält die Implementierung des HigherLower-Spiels.
"""

import random

class HigherLower:
    """
    Eine Klasse, die das HigherLower-Spiel repräsentiert.
    """

    def __init__(self, bet):
        """
        Initialisiert eine neue Instanz des HigherLower-Spiels.

        :param bet: Der Einsatz für das Spiel.
        """
        self.hidden = None
        self.shown = None
        self.draw_numbers()
        self.bet = bet

    def is_identical(self):
        """
        Überprüft, ob die versteckte und die gezeigte Zahl identisch sind.

        :return: True, wenn die Zahlen identisch sind, sonst False.
        """
        return self.hidden == self.shown

    def won(self, guess: str):
        """
        Überprüft, ob der Spieler gewonnen hat, basierend auf seiner Vermutung.

        :param guess: Die Vermutung des Spielers ('higher' oder 'lower').
        :return: True, wenn die Vermutung korrekt ist, sonst False.
        """
        if guess == "higher":
            return self.hidden > self.shown
        if guess == "lower":
            return self.hidden < self.shown
        return False

    def draw_numbers(self):
        """
        Zieht zwei zufällige Zahlen für das Spiel.
        """
        self.hidden = random.randint(0, 100)
        self.shown = random.randint(0, 100)
