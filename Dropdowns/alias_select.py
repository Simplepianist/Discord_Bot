import discord
from discord import Member
from Dropdowns.universal_select import UniversalSelect


class AliasSelect(UniversalSelect):
    def __init__(self, user: Member, view):
        options = [
            discord.SelectOption(label="Allgemein",
                                 description="Allgemeine Aliase für den Bot",
                                 emoji="📖"),
            discord.SelectOption(label="Games",
                                 description="Aliase für die Games",
                                 emoji="🎮"),
            discord.SelectOption(label="Quotes",
                                 description="Zitate aus verschiedenen Bereichen",
                                 emoji="📒")
        ]
        response = {"Allgemein": [
            [".h", "Zeigt die Hilfe an", True],
            [".i", "Sendet den Inivtelink", True],
            [".s", "Zeigt die Streaming-Url an", True],
            [".a", "Zeigt diese Aliasliste an", True]
        ],
            "Games": [
                [".sc", "Zeigt das Scoreboard an", True],
                [".bal (User)", "Zeigt dein Aktuelles Guthaben (oder eines Users)", True],
                [".give <user> <money>", "Sendet den Betrag an den Ausgewählten User", True],
                [".bj <einsatz>", "Startet ein Blackjack Spiel mit gegeben Einsatz", True],
                [".hl <einsatz>", "Startet ein Higher-Lower Game von 1 bis 100", True],
                [".rl <einsatz> <wettstein>",
                 "Startet ein Roulette Spiel mit gegeben Einsatz auf den gesetzten Wert", True],
                [".rob (player)", "Raube die Bank aus (oder einen User)", True]
            ],
            "Quotes": [
                [".quote", "Gibt ein Zufälliges Anime Zitat aus", True],
                [".qotd", "Gibt das Zitat des Tages aus", True]
            ]}
        super().__init__(user, options, response, view)


class AliasSelectView(discord.ui.View):
    def __init__(self, user: Member, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(AliasSelect(user, self))
