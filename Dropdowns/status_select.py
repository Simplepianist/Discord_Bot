import discord
import Util.variables


def check_author(author_id):
    def inner_check(msg):
        return msg.author.id == author_id
    return inner_check


class StatusSelect(discord.ui.Select):
    def __init__(self, user, owner):
        self.user_id = user
        self.owner = owner
        self.bot = Util.variables.bot
        self.options = [
            discord.SelectOption(label="Online",
                                 description="Setzt den Status Online",
                                 emoji="🟢"),
            discord.SelectOption(label="DND",
                                 description="Setzt den Status Do not Disturb",
                                 emoji="⛔"),
            discord.SelectOption(label="Offline",
                                 description="Setzt den Status Offline"),
            discord.SelectOption(label="Abwesend",
                                 description="Setzt den Status Abwesend")
        ]
        super().__init__(placeholder="Wähle einen Status",
                         max_values=1,
                         min_values=1,
                         options=self.options)

    def create_embed(self, author, colorcode, kind) -> discord.Embed:
        embed = discord.Embed(title=kind, colour=discord.Colour(colorcode))
        embed.set_footer(text="Asked by " + author.name,
                         icon_url=author.avatar)
        return embed

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.user_id:
            if self.values[0] == "Status":
                self.options = [
                    discord.SelectOption(label="Online",
                                         description="Setzt den Status Online",
                                         emoji="🟢"),
                    discord.SelectOption(label="DND",
                                         description="Setzt den Status Do not Disturb",
                                         emoji="⛔"),
                    discord.SelectOption(label="Offline",
                                         description="Setzt den Status Offline"),
                    discord.SelectOption(label="Abwesend",
                                         description="Setzt den Status Abwesend")
                ]
            elif self.values[0] == "Message":
                await self.bot.wait_for('message', check=check_author(self.user_id))
            elif self.values[0] == "Type":
                pass

        else:
            await interaction.response.send_message(content="Du hast nicht dieses "
                                                              "Menü aufgerufen",
                                                      ephemeral=True)


class StatusSelectView(discord.ui.View):
    def __init__(self, user, owner, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(StatusSelect(user, owner))
