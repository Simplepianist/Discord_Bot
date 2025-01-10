import discord
import Util.variables
from Util.util_commands import load_config


class HelpSelect(discord.ui.Select):
    def __init__(self, user, owner):
        self.user_id = user
        self.owner = owner
        options = [
            discord.SelectOption(label="Allgemein", description="Allgemeine Commands für den Bot", emoji="📖"),
            discord.SelectOption(label="Games", description="Commands für die Games", emoji="🎮"),
            discord.SelectOption(label="Quotes", description="Zitate aus verschiedenen Bereichen", emoji="📒")
        ]
        super().__init__(placeholder="Wähle eine Category", max_values=1, min_values=1, options=options)

    def create_embed(self, author, colorcode, kind) -> discord.Embed:
        embed = discord.Embed(title=kind, colour=discord.Colour(colorcode))
        embed.set_footer(text="Asked by " + author.name,
                         icon_url=author.avatar)
        return embed

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.user_id:
            embed = None
            loaded_config = load_config("embed")
            if self.values[0] == "Allgemein":
                embed = discord.Embed(title="Eine kleine Hilfe zu den Commands (Auch als /-Command verfügbar)", colour=discord.Colour(0x0446b0),
                                      description="hier erfährst du mehr zu den einzelnen Commands")


                embed.add_field(name=".help", value="Zeigt diese Hilfe hier an", inline=True)
                embed.add_field(name=".invite", value="Gibt den Invitelink für diesen Server aus", inline=True)
                embed.add_field(name=".stream", value="Gibt den Streamlink aus", inline=True)
                embed.add_field(name=".alias", value="gibt die Aliasliste aus", inline=True)
                embed.add_field(name=".ping", value="Pong", inline=True)

            elif self.values[0] == 'Games':
                embed = discord.Embed(title="Game Commands (Auch als /-Command verfügbar)", colour=discord.Colour(0x0446b0),
                                      description="Hier findest du alle Game Commands")

                embed.add_field(name=".scoreboard", value="Zeigt das Scoreboard an", inline=True)
                embed.add_field(name=".daily", value=f"Claim der daily Coins", inline=True)
                embed.add_field(name=".money (user)", value="Zeigt dein Aktuelles Guthaben (oder eines Users)", inline=True)
                embed.add_field(name=".send <user> <money>", value="Sendet den Betrag an den Ausgewählten User",
                                inline=True)
                embed.add_field(name=".blackjack <einsatz>", value="Startet ein Blackjack Spiel mit gegeben Einsatz",
                                inline=True)
                embed.add_field(name=".higherlow <einsatz>", value="Startet ein Higher-Lower Game von 1 bis 100",
                                inline=True)
                embed.add_field(name=".roulette <einsatz> <wettstein>", value="Startet ein Roulette Spiel mit gegeben Einsatz auf den gesetzten Wert (red, black, green, 0-36)", inline=True)
                embed.add_field(name=".rob (player)", value="Raube die Bank aus (oder einen User)", inline=True)
            elif self.values[0] == "Quotes":
                embed = discord.Embed(title="Quote Commands (Auch als /-Command verfügbar)", colour=discord.Colour(0x0446b0),
                                      description="Hier findest du alle Quote Commands")
                embed.add_field(name=".quote", value="Gives a random Anime Quote", inline=True)
                embed.add_field(name=".qotd", value="Gives a the Quote of the Day", inline=True)
            else:
                pass
            embed.set_thumbnail(url=loaded_config["embeds_thumbnail"])
            embed.set_footer(text=loaded_config["embeds_footertext"],
                             icon_url=Util.variables.owner.avatar)
            try:
                embed.set_footer(text="Asked by " + interaction.user.name,
                                 icon_url=interaction.user.avatar)
            except:
                pass
            await interaction.response.edit_message(embed=embed, view=HelpSelectView(self.user_id, self.owner))
        else:
            await interaction.response.send_message(content="Du hast nicht dieses Menü aufgerufen", ephemeral=True)


class HelpSelectView(discord.ui.View):
    def __init__(self, user, owner, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(HelpSelect(user, owner))
