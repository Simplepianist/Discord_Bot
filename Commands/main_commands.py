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
from Util.util_commands import send_message, return_author
from Util.variables import inviteLink, streamURL


async def help_command(ctx: Context | Interaction):
    """
    Sends a help message with a dropdown to select a category.

    Args:
        ctx (Context | Interaction): The context or interaction that triggered the command.
    """
    await send_message(ctx, "Wähle eine Category",
                       view=HelpSelectView(return_author(ctx)))


async def rules_command(ctx: Context | Interaction):
    """
    Sends a message with a dropdown to select the game rules.

    Args:
        ctx (Context | Interaction): The context or interaction that triggered the command.
    """
    await send_message(ctx, "Wähle das Spiel dessen Regeln du erfahren möchtest",
                       view=RuleSelectView(return_author(ctx)))


async def alias_command(ctx: Context | Interaction):
    """
    Sends a message with a dropdown to select an alias category.

    Args:
        ctx (Context | Interaction): The context or interaction that triggered the command.
    """
    await send_message(ctx, "Wähle eine Category",
                       view=AliasSelectView(return_author(ctx)))


async def ping_command(ctx: Context | Interaction):
    """
    Sends a pong message mentioning the author.

    Args:
        ctx (Context | Interaction): The context or interaction that triggered the command.
    """
    await send_message(ctx, "PONG!!! " + return_author(ctx).mention)


async def invite_command(ctx: Context | Interaction):
    """
    Sends an invite link.

    Args:
        ctx (Context | Interaction): The context or interaction that triggered the command.
    """
    await send_message(ctx, inviteLink)


async def stream_command(ctx: Context | Interaction):
    """
    Sends a stream URL.

    Args:
        ctx (Context | Interaction): The context or interaction that triggered the command.
    """
    await send_message(ctx, streamURL)
