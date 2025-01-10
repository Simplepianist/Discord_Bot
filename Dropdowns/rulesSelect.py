import discord


class RuleSelect(discord.ui.Select):
    def __init__(self, user):
        self.user_id = user
        options = [
            discord.SelectOption(label="Blackjack", description="Regeln für Blackjack", emoji="🃏"),
            discord.SelectOption(label="Higher Lower", description="Regeln für Higher Lower Game", emoji="↕️"),
            discord.SelectOption(label="Roulette", description="Regeln für Roulette", emoji="🎡")
        ]
        super().__init__(placeholder="Wähle ein Spiel", max_values=1, min_values=1, options=options)

    def create_embed(self, author, colorcode, kind) -> discord.Embed:
        embed = discord.Embed(title=kind, colour=discord.Colour(colorcode))
        embed.set_footer(text="Asked by " + author.name,
                         icon_url=author.avatar)
        return embed

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.user_id:
            embed = None
            if self.values[0] == "Blackjack":
                embed = self.create_embed(interaction.user, 0x0446b0, "Blackjack")
                embed.add_field(name="Ziel", value="Durch ziehen der Karten so nah wie möglich an die Zahl 21 rankommen "
                                                   "aber nicht darüber hinnaus kommen", inline=False)
                embed.add_field(name="So wird gespielt", value="Jeder erhält 2 Karten wobei beim Dealer nur eine gezeigt "
                                                               "wird. Darauf hin können Karten gezogen (**DRAW**) werden "
                                                               "oder die Runde beendet (**STAND**) werden.\nPro Draw wird "
                                                               "eine Karte aufgedeckt, deren Wert zu den aktuellen Karten "
                                                               "hinzugezählt wird. Hier ist dass ASS aber eine Ausnahme, "
                                                               "da es den Wert 1 oder 11 annehmen kann (Wird bestimmt "
                                                               "daran ob man über 21 kommt oder nicht).\nEntscheidet man "
                                                               "sich für Stand ist nun der Dealer dran", inline=False)
                embed.add_field(name="Zug des Dealers", value="Der Dealer spielt nach den gleichen Regeln wie man selbst, "
                                                              "doch mit einer Ausnahme. Er muss mit seinem Kartenwert "
                                                              "mindestens 17 Punkte haben oder er ist gezwungen zu ziehen", inline=False)
                embed.add_field(name="So gewinnst du", value='Habe am Ende des Spiels mehr Punkte als der Dealer, '
                                                             'aber sei nicht über 21. Falls du mit den Anfangskarten '
                                                             'direkt 21 erreichst, hast du ein "Natural Blackjack" falls '
                                                             'der Dealer keines hat gewinnst du automatisch und erhälts '
                                                             'den 2,5x einsatz anstelle des 2x', inline=False)
            elif self.values[0] == 'Higher Lower':
                embed = self.create_embed(interaction.user, 0x0446b0, "Higher Lower")
                embed.add_field(name="So wird gespielt", value="Beim Start werden 2 Werte zwischen 1 und 100 generiert, "
                                                               "wovon dir der erste gezeigt wird.\n Deine Aufgabe ist es "
                                                               "nun zu schätzen ob die Zweite Zahl größer (**higher**) "
                                                               "oder kleiner (**lower**) ist", inline=False)
                embed.add_field(name="Wie gewinne ich?", value="Du gewinnst wenn du mit deiner Schätzung richtig liegst", inline=False)
                embed.add_field(name="Was passiert bei 2 gleichen Zahlen", value="Sollte dies vorkommen werden die Zahlen "
                                                                                 "neu generiert und du wirst darüber "
                                                                                 "informiert", inline=False)
            elif self.values[0] == 'Roulette':
                embed = self.create_embed(interaction.user, 0x0446b0, "Roulette")
                embed.add_field(name="So wird gespielt", value="Du wählst eine Farbe (Rot, Schwarz, Grün) oder eine Zahl (0-36)\nDanach wird der Rouletttisch gerollt und wenn dein Wert zu dem Ergebnis passt gewinnst du", inline=False)
                embed.add_field(name="Warum muss ich nur einen Wert angeben?", value="Da deine Eingabe nur einem Teil des Ergebnis entsprechen muss, siehe einen Rouletttisch", inline=False)
                embed.add_field(name="Wieviel kann ich gewinnen", value="* Wenn du auf schwarz oder rot wettest bekommst du den 1,5x Einsatz zurück\n"
                                                                        "* Wenn du auf eine Zahl oder auf Grün wettest bekommst du den 20x Einsatz zurück", inline=False)
                embed.add_field(name="Warum bekomm ich so viel bei Grün oder einer Zahl", value="Da die Chance dieses bestimmte Feld zu treffen eine 1-36 Chance ist (2,77%)", inline=False)
                embed.add_field(name="Wie sieht ein Rouletttisch aus?", value="Hier ein [Link](https://as2.ftcdn.net/v2/jpg/04/59/44/91/1000_F_459449191_hTDFAeYXqBZKojowM3KupyCxe2F2Y0m1.jpg)")

            else:
                pass
            await interaction.response.edit_message(embed=embed, view=RuleSelectView(self.user_id))
        else:
            await interaction.response.send_message(content="Du hast nicht dieses Menü aufgerufen", ephemeral=True)


class RuleSelectView(discord.ui.View):
    def __init__(self, user, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(RuleSelect(user))
