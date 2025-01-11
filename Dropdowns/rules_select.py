"""
Dieses Modul enthält die Klassen RuleSelect und RuleSelectView,
die für die Erstellung und Verwaltung von Dropdown-Menüs in einem Discord-Bot verwendet werden.
"""
import discord
from discord import Member
from Dropdowns.universal_select import UniversalSelect


class RuleSelect(UniversalSelect):
    """
        Eine Klasse, die ein Dropdown-Menü für Regeloptionen erstellt.

        Attribute:
            user (Member): Der Benutzer, der das Dropdown-Menü verwendet.
            view (discord.ui.View): Die Ansicht, die das Dropdown-Menü enthält.
        """
    def __init__(self, user: Member, view):
        """
        Initialisiert die RuleSelect-Klasse mit den gegebenen Optionen und Antworten.

        Args:
            user (Member): Der Benutzer, der das Dropdown-Menü verwendet.
            view (discord.ui.View): Die Ansicht, die das Dropdown-Menü enthält.
        """
        options = [
            discord.SelectOption(label="Blackjack",
                                 description="Regeln für Blackjack",
                                 emoji="🃏"),
            discord.SelectOption(label="Higher Lower",
                                 description="Regeln für Higher Lower Game",
                                 emoji="↕️"),
            discord.SelectOption(label="Roulette",
                                 description="Regeln für Roulette",
                                 emoji="🎡")
        ]
        response = {"Blackjack": [
            ["Ziel", "Durch ziehen der Karten so nah wie möglich an die Zahl 21 "
                     "rankommen aber nicht darüber hinnaus kommen", False],
            ["So wird gespielt", "Jeder erhält 2 Karten wobei "
                                   "beim Dealer nur eine gezeigt "
                                   "wird. Darauf hin können Karten "
                                   "gezogen (**DRAW**) werden "
                                   "oder die Runde beendet (**STAND**) "
                                   "werden.\nPro Draw wird "
                                   "eine Karte aufgedeckt, deren Wert "
                                   "zu den aktuellen Karten "
                                   "hinzugezählt wird. Hier ist dass "
                                   "ASS aber eine Ausnahme, "
                                   "da es den Wert 1 oder 11 annehmen "
                                   "kann (Wird bestimmt "
                                   "daran ob man über 21 kommt oder "
                                   "nicht).\nEntscheidet man "
                                   "sich für Stand ist nun der Dealer "
                                   "dran", False],
        ["Zug des Dealers", "Der Dealer spielt nach den gleichen Regeln wie man selbst, "
                              "doch mit einer Ausnahme. Er muss mit seinem Kartenwert "
                              "mindestens 17 Punkte haben oder er ist gezwungen zu ziehen",
         False],
        ["So gewinnst du", 'Habe am Ende des Spiels mehr Punkte als der Dealer, '
                             'aber sei nicht über 21. Falls du mit den Anfangskarten '
                             'direkt 21 erreichst, hast du ein "Natural Blackjack" falls '
                             'der Dealer keines hat gewinnst du automatisch und erhälts '
                             'den 2,5x einsatz anstelle des 2x', False],
        ],
        "Higher Lower": [["So wird gespielt", "Es wird eine Zahl zwischen 1 und 100 generiert "
                                             "und du musst schätzen ob die nächste Zahl höher oder "
                                             "niedriger ist", False],
            ["Wie gewinne ich?", "Du gewinnst wenn du mit deiner Schätzung richtig liegst", False],
            ["Was passiert bei 2 gleichen Zahlen", "Sollte dies vorkommen werden die Zahlen "
                                                   "neu generiert und du wirst darüber "
                                                   "informiert", False]],
        "Roulette": [["So wird gespielt",
                      "Du wählst eine Farbe (Rot, Schwarz, Grün) oder eine Zahl"
                        "(0-36)\nDanach wird der Rouletttisch gerollt und wenn dein "
                        "Wert zu dem Ergebnis passt gewinnst du", False],
                ["Warum muss ich nur einen Wert angeben?",
                 "Da deine Eingabe nur einem Teil des Ergebnis entsprechen "
                    "muss, siehe einen Rouletttisch", False],
                ["Wieviel kann ich gewinnen",
                 "* Wenn du auf schwarz oder rot wettest bekommst du den 1,5x "
                    "Einsatz zurück\n"
                    "* Wenn du auf eine Zahl oder auf Grün wettest bekommst du "
                    "den 20x Einsatz zurück", False],
                ["Warum bekomm ich so viel bei Grün oder einer Zahl",
                 "Da die Chance dieses bestimmte Feld zu treffen eine 1-36 "
                    "Chance ist (2,77%)", False],
                ["Wie sieht ein Rouletttisch aus?",
                 "Hier ein [Link](https://as2.ftcdn.net/v2/jpg/04/59/44/91"
                 "/1000_F_459449191_hTDFAeYXqBZKojowM3KupyCxe2F2Y0m1.jpg)", False]]
        }
        super().__init__(user, options, response, view)



class RuleSelectView(discord.ui.View):
    """
        Eine Klasse, die eine Ansicht für das RuleSelect-Dropdown-Menü erstellt.

        Attribute:
            user (Member): Der Benutzer, der die Ansicht verwendet.
            timeout (int): Die Zeit in Sekunden, nach der die Ansicht abläuft.
    """

    def __init__(self, user: Member, timeout=180):
        """
        Initialisiert die RuleSelectView-Klasse mit dem gegebenen Benutzer und Timeout.

        Args:
            user (Member): Der Benutzer, der die Ansicht verwendet.
            timeout (int, optional): Die Zeit in Sekunden,
            nach der die Ansicht abläuft. Standard ist 180 Sekunden.
        """
        super().__init__(timeout=timeout)
        self.add_item(RuleSelect(user, self))
