import logging
from Util.util_commands import *
import Util.variables

"""
General
"""


async def shutdownCommand():
    db.close_connections()
    logging.info("Closed Connection (DB)")
    await bot.close()
    logging.info("Bot stopped")


async def resetStatusCommand(ctx: Context | Interaction):
    if checkAdmin(ctx):
        await bot.change_presence(activity=discord.Streaming(name=".help", url=Util.variables.streamURL))
    else:
        await send_message(ctx, "Piss dich ", ephemeral=True, delete_after=5)


async def setStatusCommand(ctx: Context | Interaction):
    global act
    if checkAdmin(ctx):
        await send_message(ctx, "Wie lautet der neue Status")
        content = await bot.wait_for('message')
        content = content.content
        if content != "":
            await send_message(ctx, "Wie soll der Status sein (dnd,online,offline,idle,streaming)")
            statuse = ["dnd", "online", "offline", "idle"]
            status = await bot.wait_for("message")
            status = status.content
            if str(status).lower() in statuse:
                await send_message(ctx, "Art des Status (listening,playing)")
                art = await bot.wait_for("message")
                art = art.content
                change = True
                if str(art).lower() == "listening":
                    act = discord.Activity(type=discord.ActivityType.listening, name=content)
                elif str(art).lower() == "playing":
                    act = discord.Activity(type=discord.ActivityType.playing, name=content)
                else:
                    change = False
                if change:
                    if str(status).lower() == "dnd":
                        await bot.change_presence(activity=act, status=discord.Status.dnd)
                    elif str(status).lower() == "online":
                        await bot.change_presence(activity=act, status=discord.Status.online)
                    elif str(status).lower() == "offline":
                        await bot.change_presence(activity=act, status=discord.Status.offline)
                    elif str(status).lower() == "idle":
                        await bot.change_presence(activity=act, status=discord.Status.idle)
                else:
                    await send_message(ctx, "Ändern abgebrochen")
            elif str(status).lower() == "streaming":
                await bot.change_presence(activity=discord.Streaming(name=content, url=Util.variables.streamURL))
            else:
                await send_message(ctx, "Ändern abgebrochen")
        else:
            await send_message(ctx, "Ändern abgebrochen")
    else:
        await send_message(ctx, "Piss dich ", ephemeral=True, delete_after=5)


"""
Gaming
"""


async def setMoneyCommand(ctx: Context | Interaction, member: discord.Member, user_money=None):
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
            db.set_money_for_user(member.id, user_money)
            embed = discord.Embed(title="Bank", colour=discord.Colour(0xc6c910))
            embed.add_field(name=user, value=f"Money: {get_money_for_user(return_author(ctx))}", inline=False)
            await send_message(ctx, embed=embed)
    except:
        await send_message(ctx, "Falsche Parameter übergeben")
