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
from Util.util_commands import db, check_admin, send_message, get_money_for_user, return_author
from Util.variables import bot, streamURL


#region General

async def shutdown_command():
    """
    Shuts down the bot and closes the database connection.

    Returns:
    None
    """
    await db.close_pool()
    logging.info("Closed Connection (DB)")
    await bot.close()
    logging.info("Bot stopped")


async def reset_status_command(ctx: Context | Interaction):
    """
    Resets the bot's status to streaming with a predefined URL.

    Parameters:
    ctx (Context | Interaction): The context or interaction that triggered the command.

    Returns:
    None
    """
    if check_admin(ctx):
        await bot.change_presence(
            activity=Streaming(name=".help", url=streamURL))
    else:
        await send_message(ctx, "Piss dich ", ephemeral=True, delete_after=5)


async def set_status_command(ctx: Context | Interaction):
    """
    Sets the bot's status based on user input.

    Parameters:
    ctx (Context | Interaction): The context or interaction that triggered the command.

    Returns:
    None
    """
    if not check_admin(ctx):
        await send_message(ctx, "Piss dich ", ephemeral=True, delete_after=5)
        return

    await send_message(ctx, "Wie lautet der neue Status")
    content = (await bot.wait_for('message')).content
    if not content:
        await send_message(ctx, "Ändern abgebrochen")
        return

    await send_message(ctx, "Wie soll der Status sein (dnd,online,offline,idle,streaming)")
    status = (await bot.wait_for("message")).content.lower()
    if status not in ["dnd", "online", "offline", "idle", "streaming"]:
        await send_message(ctx, "Ändern abgebrochen")
        return

    if status == "streaming":
        await bot.change_presence(activity=Streaming(name=content, url=streamURL))
        return

    await send_message(ctx, "Art des Status (listening,playing)")
    art = (await bot.wait_for("message")).content.lower()
    if art not in ["listening", "playing"]:
        await send_message(ctx, "Ändern abgebrochen")
        return

    activity_type = ActivityType.listening if art == "listening" else ActivityType.playing
    act = Activity(type=activity_type, name=content)
    status_map = {
        "dnd": Status.dnd,
        "online": Status.online,
        "offline": Status.offline,
        "idle": Status.idle
    }
    await bot.change_presence(activity=act, status=status_map[status])

#endregion

#region Gaming
async def set_money_command(ctx: Context | Interaction, member: Member, user_money=None):
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
            await send_message(ctx, "Betrag muss angegeben sein", ephemeral=True, delete_after=5)
        elif user_money < 0:
            await send_message(ctx, "Betrag muss positiv sein", ephemeral=True, delete_after=5)
        elif member is None:
            await send_message(ctx, "Kein Spieler angegeben", ephemeral=True, delete_after=5)
        else:
            await db.set_money_for_user(member.id, user_money)
            embed = Embed(
                title="Bank", colour=Colour(0xc6c910))
            embed.add_field(
                name=user,
                value=f"Money: {await get_money_for_user(return_author(ctx))}", inline=False
            )
            await send_message(ctx, embed=embed)
    except ValueError:
        await send_message(ctx, "Falsche Parameter übergeben")
#endregion
