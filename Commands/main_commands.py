"""
Dieses Modul enthält Befehle für einen Discord-Bot.

Funktionen:
- help_command: Sendet eine Hilfenachricht mit einem Dropdown zur Auswahl einer Kategorie.
- rules_command: Sendet eine Nachricht mit einem Dropdown zur Auswahl der Spielregeln.
- alias_command: Sendet eine Nachricht mit einem Dropdown zur Auswahl einer Alias-Kategorie.
- ping_command: Sendet eine Pong-Nachricht und erwähnt den Autor.
- invite_command: Sendet einen Einladungslink.
- stream_command: Sendet eine Stream-URL.
"""
from discord import Interaction
from discord.ext.commands import Context
from Dropdowns.alias_select import AliasSelectView
from Dropdowns.help_select import HelpSelectView
from Dropdowns.rules_select import RuleSelectView
from Util.util_commands import Utility


class MainCommands:
    """
    A class to handle main commands for the Discord bot.
    """

    def __init__(self, bot):
        self.bot = bot
        self.utils = Utility(bot)

    async def help_command(self, ctx: Context | Interaction):
        """
        Sends a help message with a dropdown to select a category.
    
        Args:
            ctx (Context | Interaction): The context or interaction that triggered the command.
        """
        await ctx.send("Wähle eine Category",
                           view=HelpSelectView(self.utils.return_author(ctx), self.bot))
    
    
    async def rules_command(self, ctx: Context | Interaction):
        """
        Sends a message with a dropdown to select the game rules.
    
        Args:
            ctx (Context | Interaction): The context or interaction that triggered the command.
        """
        await ctx.send("Wähle das Spiel dessen Regeln du erfahren möchtest",
                           view=RuleSelectView(self.utils.return_author(ctx), self.bot))
    
    
    async def alias_command(self, ctx: Context | Interaction):
        """
        Sends a message with a dropdown to select an alias category.
    
        Args:
            ctx (Context | Interaction): The context or interaction that triggered the command.
        """
        await ctx.send("Wähle eine Category",
                           view=AliasSelectView(self.utils.return_author(ctx), self.bot))
    
    
    async def ping_command(self, ctx: Context | Interaction):
        """
        Sends a pong message mentioning the author.
    
        Args:
            ctx (Context | Interaction): The context or interaction that triggered the command.
        """
        await ctx.send("PONG!!! " + self.utils.return_author(ctx).mention)
    
    
    async def invite_command(self, ctx: Context | Interaction):
        """
        Sends an invite link.
    
        Args:
            ctx (Context | Interaction): The context or interaction that triggered the command.
        """
        await ctx.send(self.bot.config["inviteLink"])
    
    
    async def stream_command(self, ctx: Context | Interaction):
        """
        Sends a stream URL.
    
        Args:
            ctx (Context | Interaction): The context or interaction that triggered the command.
        """
        await ctx.send(self.bot.config["streamURL"])
