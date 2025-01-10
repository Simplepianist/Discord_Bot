from Dropdowns.aliasSelect import AliasSelectView
from Dropdowns.helpSelect import HelpSelectView
from Dropdowns.rulesSelect import RuleSelectView
from Util.util_commands import *
from Util.variables import *

inviteLink = inviteLink
streamLink = streamURL


async def helpCommand(ctx: Context | Interaction):
    await send_message(ctx, "Wähle eine Category", view=HelpSelectView(return_author(ctx).id, owner))


async def rulesCommand(ctx: Context | Interaction):
    await send_message(ctx, "Wähle das Spiel dessen Regeln du erfahren möchtest", view=RuleSelectView(return_author(ctx).id))


async def aliasCommand(ctx: Context | Interaction):
    await send_message(ctx, "Wähle eine Category", view=AliasSelectView(return_author(ctx).id, owner))


async def pingCommand(ctx: Context | Interaction):
    await send_message(ctx, "PONG!!! " + return_author(ctx).mention)


async def inviteCommand(ctx: Context | Interaction):
    await send_message(ctx, inviteLink)


async def streamCommand(ctx: Context | Interaction):
    await send_message(ctx, streamLink)
