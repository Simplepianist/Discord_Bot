import os
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ext.commands import Context

def get_cog_choices():
    return [
        app_commands.Choice(name=f[:-3], value=f[:-3])
        for f in os.listdir("cogs")
        if f.endswith(".py") and not f.startswith("__") and not f.startswith("CogSelector")
    ]

def get_all_cog_names():
    return [
        f[:-3]
        for f in os.listdir("cogs")
        if f.endswith(".py") and not f.startswith("__") and not f.startswith("CogSelector")
    ]

class CogSelector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.logging.info(f"CogSelector loaded with {len(get_cog_choices())} cogs.")

    @commands.hybrid_command(name="load_cogs", description="Wähle ein Cog")
    @app_commands.choices(cog=get_cog_choices())
    @commands.is_owner()
    async def select_cog(self, ctx: Context | Interaction, cog: str = None):
        cogs_to_load = [cog] if cog else get_all_cog_names()
        results = []
        for c in cogs_to_load:
            try:
                await self.bot.load_extension(f"cogs.{c}")
                results.append(f"`{c}` geladen")
            except Exception as e:
                results.append(f"Fehler bei `{c}`: {e}")
        await self.bot.tree.sync()
        msg = "\n".join(results)
        if isinstance(ctx, Context):
            await ctx.send(msg, delete_after=10)
        else:
            await ctx.response.send_message(msg, ephemeral=True)

    @commands.hybrid_command(name="unload_cogs", description="Entlade ein Cog")
    @app_commands.choices(cog=get_cog_choices())
    @commands.is_owner()
    async def unload_cog(self, ctx: Context | Interaction, cog: str = None):
        cogs_to_unload = [cog] if cog else get_all_cog_names()
        results = []
        for c in cogs_to_unload:
            try:
                await self.bot.unload_extension(f"cogs.{c}")
                results.append(f"`{c}` entladen")
            except Exception as e:
                results.append(f"Fehler bei `{c}`: {e}")
        await self.bot.tree.sync()
        msg = "\n".join(results)
        if isinstance(ctx, Context):
            await ctx.send(msg, delete_after=10)
        else:
            await ctx.response.send_message(msg, ephemeral=True)

    @commands.hybrid_command(name="reload_cogs", description="Lade ein Cog neu")
    @app_commands.choices(cog=get_cog_choices())
    @commands.is_owner()
    async def reload_cog(self, ctx: Context | Interaction, cog: str = None):
        cogs_to_reload = [cog] if cog else get_all_cog_names()
        results = []
        for c in cogs_to_reload:
            try:
                await self.bot.reload_extension(f"cogs.{c}")
                results.append(f"`{c}` neu geladen")
            except Exception as e:
                results.append(f"Fehler bei `{c}`: {e}")
        await self.bot.tree.sync()
        msg = "\n".join(results)
        if isinstance(ctx, Context):
            await ctx.send(msg, delete_after=10)
        else:
            await ctx.response.send_message(msg, ephemeral=True)