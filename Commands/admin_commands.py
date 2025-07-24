"""
Dieses Modul enthält administrative Befehle für den Discord-Bot.

Funktionen:
- shutdownCommand: Beendet den Bot und schließt die Datenbankverbindung.
- resetStatusCommand: Setzt den Status des Bots auf Streaming mit einer vordefinierten URL zurück.
- setStatusCommand: Setzt den Status des Bots basierend auf Benutzereingaben.
- setMoneyCommand: Setzt das Geld für einen angegebenen Benutzer.

Importierte Module:
- logging: Protokollierung von Ereignissen.
- discord: Discord-Bibliothek für die Bot-Interaktion.
- Util.util_commands: Hilfsfunktionen und Variablen für den Bot.
- Util.variables: Variablen für den Bot.
"""

import logging
from discord import Interaction, Streaming, Activity, ActivityType, Status, Member, Embed, Colour
from discord.ext.commands import Context

from Util.util_commands import Utility


class AdminCommands:
    """
    A class to handle administrative commands for the Discord bot.
    """

    def __init__(self, bot):
        self.bot = bot
        self.utils = Utility(bot)


    async def shutdown_command(self):
        """
        Shuts down the bot and closes the database connection.

        Returns:
        None
        """
        #await db.close_pool()
        logging.info("Closed Connection (DB)")
        await self.bot.close()
        logging.info("Bot stopped")


    async def reset_status_command(self, ctx: Context | Interaction):
        """
        Resets the bot's status to streaming with a predefined URL.

        Parameters:
        ctx (Context | Interaction): The context or interaction that triggered the command.

        Returns:
        None
        """
        if self.utils.check_admin(ctx):
            await self.bot.change_presence(
                activity=Streaming(name=".help", url=self.bot.config["streamURL"]))
        else:
            await ctx.send("Piss dich ", ephemeral=True, delete_after=5)


    async def set_status_command(self, ctx, name: str, status: str, art: str = None):
        """
        Sets the bot's status based on user input.

        Parameters:
        ctx (Context | Interaction): The context or interaction that triggered the command.

        Returns:
        None
        """
        if not self.utils.check_admin(ctx):
            await ctx.send("Keine Berechtigung", ephemeral=True, delete_after=5)
            return

        if status == "streaming":
            await self.bot.change_presence(activity=Streaming(name=name, url=self.bot.config["streamURL"]))
            await ctx.send("Status geändert zu Streaming")
            return

        if art not in ["listening", "playing"]:
            await ctx.send("Art muss angegeben werden (listening/playing)")
            return

        activity_type = ActivityType.listening if art == "listening" else ActivityType.playing
        act = Activity(type=activity_type, name=name)
        status_map = {
            "dnd": Status.dnd,
            "online": Status.online,
            "offline": Status.offline,
            "idle": Status.idle
        }
        await self.bot.change_presence(activity=act, status=status_map[status])
        await ctx.send(f"Status geändert zu {status} ({art})")

    async def set_money_command(self, ctx: Context | Interaction, member: Member, user_money=None):
        """
        Sets the money for a specified user.

        Parameters:
        ctx (Context | Interaction): The context or interaction that triggered the command.
        member (discord.Member): The member whose money is to be set.
        user_money (int, optional): The amount of money to set for the user. Defaults to None.

        Returns:
        None
        """
        user = member.name
        if int(member.discriminator) != 0:
            user = user + "#" + str(member.discriminator)
        try:
            user_money = int(user_money)
            if user_money is None:
                await ctx.send("Betrag muss angegeben sein", ephemeral=True, delete_after=5)
            elif user_money < 0:
                await ctx.send("Betrag muss positiv sein", ephemeral=True, delete_after=5)
            elif member is None:
                await ctx.send("Kein Spieler angegeben", ephemeral=True, delete_after=5)
            else:
                await self.bot.db.set_money_for_user(member.id, user_money)
                embed = Embed(
                    title="Bank", colour=Colour(0xc6c910))
                embed.add_field(
                    name=user,
                    value=f"Money: {await self.utils.get_money_for_user(self.utils.return_author(ctx))}", inline=False
                )
                await ctx.send(embed=embed)
        except ValueError:
            await ctx.send("Falsche Parameter übergeben")
