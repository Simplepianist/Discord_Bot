import discord
import Util.variables
from config_loader import Loader


class AliasSelect(discord.ui.Select):
    def __init__(self, user, owner):
        self.user_id = user
        self.owner = owner
        options = [
            discord.SelectOption(label="Allgemein", description="Allgemeine Aliase für den Bot", emoji="📖"),
            discord.SelectOption(label="Games", description="Aliase für die Games", emoji="🎮"),
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
            loaded_config = Loader(self.owner).load_config("embed")
            if self.values[0] == "Allgemein":
                embed = discord.Embed(title="Eine kleine Hilfe zu den alias Commands", colour=discord.Colour(0x0446b0),
                                      description="hier erfährst du mehr zu den einzelnen alias Commands")
                embed.set_thumbnail(url=loaded_config["embeds_thumbnail"])
                embed.set_footer(text=loaded_config["embeds_footertext"],
                                 icon_url=Util.variables.owner.avatar)
                embed.add_field(name=".h", value="Zeigt die Hilfe an", inline=True)
                embed.add_field(name=".i", value="Sendet den Inivtelink", inline=True)
                embed.add_field(name=".s", value="Zeigt die Streaming-Url an", inline=True)
                embed.add_field(name=".a", value="Zeigt diese Aliasliste an", inline=True)

            elif self.values[0] == 'Games':
                embed = discord.Embed(title="Game Aliase", colour=discord.Colour(0x0446b0),
                                      description="Aliasliste für die Games")

                embed.set_thumbnail(url=loaded_config["embeds_thumbnail"])
                embed.set_footer(text=loaded_config["embeds_footertext"],
                                 icon_url=Util.variables.owner.avatar)

                embed.add_field(name=".ga", value="Zeigt diese Liste hier an", inline=True)
                embed.add_field(name=".sc", value="Zeigt das Scoreboard an", inline=True)
                embed.add_field(name=".bal (User)", value="Zeigt dein Aktuelles Guthaben (oder eines Users)",
                                inline=True)
                embed.add_field(name=".give <user> <money>", value="Sendet den Betrag an den Ausgewählten User",
                                inline=True)
                embed.add_field(name=".bj <einsatz>", value="Startet ein Blackjack Spiel mit gegeben Einsatz",
                                inline=True)
                embed.add_field(name=".hl <einsatz>", value="Startet ein Higher-Lower Game von 1 bis 100", inline=True)
                embed.add_field(name=".rl <einsatz> <wettstein>", value="Startet ein Roulette Spiel mit gegeben Einsatz auf den gesetzten Wert", inline=True)
                embed.add_field(name=".rob (player)", value="Raube die Bank aus (oder einen User)", inline=True)
            elif self.values[0] == "Quotes":
                embed = discord.Embed(title="Quote Commands (Auch als /-Command verfügbar)", colour=discord.Colour(0x0446b0),
                                      description="Hier findest du alle Quote Commands")
                embed.add_field(name=".quote", value="Gives a random Anime Quote", inline=True)
                embed.add_field(name=".qotd", value="Gives a the Quote of the Day", inline=True)
            else:
                pass
            try:
                embed.set_footer(text="Asked by " + interaction.user.name,
                                 icon_url=interaction.user.avatar)
            except:
                pass
            await interaction.response.edit_message(embed=embed, view=AliasSelectView(self.user_id, self.owner))
        else:
            await interaction.response.send_message(content="Du hast nicht dieses Menü aufgerufen", ephemeral=True)


class AliasSelectView(discord.ui.View):
    def __init__(self, user, owner, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(AliasSelect(user, owner))
