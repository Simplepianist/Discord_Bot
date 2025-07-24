import os
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ext.commands import Context


def get_cog_choices():
    # Listet alle Python-Dateien im cogs-Ordner auf (ohne .py-Endung)
    return [
        app_commands.Choice(name=f[:-3], value=f[:-3])
        for f in os.listdir("cogs")
        if f.endswith(".py") and not f.startswith("__")
    ]

class CogSelector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="load_cogs", description="Wähle ein Cog")
    @app_commands.choices(cog=get_cog_choices())
    @commands.is_owner()
    async def select_cog(self, ctx: Context | Interaction, cog: str = None):
        if isinstance(ctx, Context):
            try:
                await self.bot.load_extension(f"cogs.{cog}")
                await ctx.send(f"Cog `{cog}` wurde geladen.", delete_after=10)
            except Exception as e:
                await ctx.send(f"Fehler beim Laden von `{cog}`: {e}", delete_after=10)
        else:
            try:
                await self.bot.load_extension(f"cogs.{cog}")
                await ctx.response.send_message(f"Cog `{cog}` wurde geladen.", ephemeral=True)
            except Exception as e:
                await ctx.response.send_message(f"Fehler beim Laden von `{cog}`: {e}", ephemeral=True)

    @commands.hybrid_command(name="unload_cogs", description="Entlade ein Cog")
    @app_commands.choices(cog=get_cog_choices())
    @commands.is_owner()
    async def unload_cog(self, ctx: Context | Interaction, cog: str = None):
        if isinstance(ctx, Context):
            try:
                await self.bot.unload_extension(f"cogs.{cog}")
                await ctx.send(f"Cog `{cog}` wurde entladen.", delete_after=10)
            except Exception as e:
                await ctx.send(f"Fehler beim Entladen von `{cog}`: {e}", delete_after=10)
        else:
            try:
                await self.bot.unload_extension(f"cogs.{cog}")
                await ctx.response.send_message(f"Cog `{cog}` wurde entladen.", ephemeral=True)
            except Exception as e:
                await ctx.response.send_message(f"Fehler beim Entladen von `{cog}`: {e}", ephemeral=True)


    @commands.hybrid_command(name="reload_cogs", description="Lade ein Cog neu")
    @app_commands.choices(cog=get_cog_choices())
    @commands.is_owner()
    async def reload_cog(self, ctx: Context | Interaction, cog: str = None):
        if isinstance(ctx, Context):
            try:
                await self.bot.reload_extension(f"cogs.{cog}")
                await ctx.send(f"Cog `{cog}` wurde neu geladen.", delete_after=10)
            except Exception as e:
                await ctx.send(f"Fehler beim Neuladen von `{cog}`: {e}", delete_after=10)
        else:
            try:
                await self.bot.reload_extension(f"cogs.{cog}")
                await ctx.response.send_message(f"Cog `{cog}` wurde neu geladen.", ephemeral=True)
            except Exception as e:
                await ctx.response.send_message(f"Fehler beim Neuladen von `{cog}`: {e}", ephemeral=True)