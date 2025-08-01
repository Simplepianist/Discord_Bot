import asyncio
import logging
import os
from discord.ext import commands
from discord import app_commands, Interaction, Embed
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
        self.logger = logging.getLogger('Cog-System')
        self.logger.info(f"CogSelector loaded with {len(get_cog_choices())} cogs.")
        # Initialisierung wird asynchron nach Bot-Start durchgeführt
        asyncio.create_task(self.initialize_cogs_from_db())

    async def initialize_cogs_from_db(self):
        """
        Lädt den Status der Cogs aus der Datenbank und aktiviert/deaktiviert sie entsprechend.
        """
        logger = logging.getLogger('InitializeCogs')
        try:
            cogs_state = await self.bot.db.load_cogs_state()
            for cog in cogs_state:
                if getattr(cog, 'enabled', False):
                    cog_name = cog.name if hasattr(cog, 'name') else str(cog)
                    ext_name = f"cogs.{cog_name}"
                    if ext_name not in self.bot.extensions:
                        try:
                            await self.bot.load_extension(ext_name)
                            logger.info(f"Cog '{cog_name}' automatisch geladen (Datenbank-Status).")
                        except Exception as e:
                            logger.error(f"Fehler beim automatischen Laden von Cog '{cog_name}': {e}")
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren der Cogs aus der Datenbank: {e}")

    def get_cog_status(self):
        """Returns dict with cog names and their status (loaded/unloaded)"""
        all_cogs = get_all_cog_names()
        loaded_cogs = [name.split('.')[-1] for name in self.bot.extensions.keys() if name.startswith('cogs.')]

        status = {}
        for cog in all_cogs:
            status[cog] = cog in loaded_cogs
        return status

    async def _update_cog_database(self, cog_name: str, enabled: bool):
        """Update cog state in database - runs in background"""
        try:
            await self.bot.db.save_cog((cog_name, enabled))  # Pass as tuple
            self.logger.info(f"Database updated for cog: {cog_name}")
        except Exception as e:
            self.logger.error(f"Failed to update database for cog {cog_name}: {e}")

    @commands.hybrid_command(name="coglist", description="Zeige den Status aller Cogs")
    @commands.is_owner()
    async def coglist(self, ctx: Context | Interaction):
        # Defer response for slash commands
        if isinstance(ctx, Interaction):
            await ctx.response.defer()

        status = self.get_cog_status()

        embed = Embed(title="Cog Status", color=0x00ff00)

        loaded = [name for name, is_loaded in status.items() if is_loaded]
        unloaded = [name for name, is_loaded in status.items() if not is_loaded]

        if loaded:
            embed.add_field(name="🟢 Geladen", value="\n".join(f"`{cog}`" for cog in loaded), inline=True)

        if unloaded:
            embed.add_field(name="🔴 Nicht geladen", value="\n".join(f"`{cog}`" for cog in unloaded), inline=True)

        embed.set_footer(text=f"Total: {len(loaded)} geladen, {len(unloaded)} nicht geladen")

        if isinstance(ctx, Interaction):
            await ctx.followup.send(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="load_cogs", description="Lade ein oder alle Cogs")
    @app_commands.choices(cog=get_cog_choices())
    @commands.is_owner()
    async def load_cog(self, ctx: Context | Interaction, cog: str = None):
        # Defer response for slash commands
        if isinstance(ctx, Interaction):
            await ctx.response.defer()

        status = self.get_cog_status()
        cogs_to_load = [cog] if cog else [name for name, is_loaded in status.items() if not is_loaded]

        if not cogs_to_load:
            msg = "Keine Cogs zum Laden gefunden."
            if isinstance(ctx, Interaction):
                await ctx.followup.send(msg)
            else:
                await ctx.send(msg)
            return

        results = []
        for c in cogs_to_load:
            if status.get(c, False):
                results.append(f"`{c}` ist bereits geladen")
                continue

            try:
                await self.bot.load_extension(f"cogs.{c}")
                asyncio.create_task(self._update_cog_database(c, True))
                results.append(f"✅ `{c}` geladen")
                msg = "\n".join(results)
                self.logger.info(
                    "Loaded cogs: " + ", ".join([c for c in cogs_to_load if not status.get(c, False)]))

            except commands.ExtensionAlreadyLoaded:
                results.append(f"⚠️ `{c}` ist bereits geladen")
            except Exception as e:
                results.append(f"❌ Fehler bei `{c}`: {e}")
        await self.start_sync_commands()



    async def start_sync_commands(self, ctx: Context | Interaction):
        """Sync commands in background and send follow-up message"""
        if isinstance(ctx, Interaction):
            await ctx.followup.send("🔄 Syncing commands...")
        else:
            await ctx.send("🔄 Syncing commands...")

        try:
            await self.bot.sync_commmands()
            follow_msg = "✅ Commands synced successfully!"
        except Exception as e:
            follow_msg = f"❌ Sync failed: {e}"

        if isinstance(ctx, Interaction):
            await ctx.followup.send(follow_msg)
        else:
            await ctx.send(follow_msg)



    @commands.hybrid_command(name="unload_cogs", description="Entlade ein oder alle Cogs")
    @app_commands.choices(cog=get_cog_choices())
    @commands.is_owner()
    async def unload_cog(self, ctx: Context | Interaction, cog: str = None):
        # Defer response for slash commands
        if isinstance(ctx, Interaction):
            await ctx.response.defer()

        status = self.get_cog_status()
        cogs_to_unload = [cog] if cog else [name for name, is_loaded in status.items() if is_loaded]

        if not cogs_to_unload:
            msg = "Keine Cogs zum Entladen gefunden."
            if isinstance(ctx, Interaction):
                await ctx.followup.send(msg)
            else:
                await ctx.send(msg)
            return

        results = []
        for c in cogs_to_unload:
            if not status.get(c, True):
                results.append(f"`{c}` ist bereits entladen")
                continue

            try:
                await self.bot.unload_extension(f"cogs.{c}")
                asyncio.create_task(self._update_cog_database(c, False))
                results.append(f"✅ `{c}` entladen")
                msg = "\n".join(results)
                self.logger.info(
                    "Unloaded cogs: " + ", ".join([c for c in cogs_to_unload if status.get(c, False)]))

            except commands.ExtensionNotLoaded:
                results.append(f"⚠️ `{c}` ist bereits entladen")
            except Exception as e:
                results.append(f"❌ Fehler bei `{c}`: {e}")
        await self.start_sync_commands()



    @commands.hybrid_command(name="reload_cogs", description="Lade ein oder alle geladene Cogs neu")
    @app_commands.choices(cog=get_cog_choices())
    @commands.is_owner()
    async def reload_cog(self, ctx: Context | Interaction, cog: str = None):
        # Defer response for slash commands
        if isinstance(ctx, Interaction):
            await ctx.response.defer()

        status = self.get_cog_status()
        cogs_to_reload = [cog] if cog else [name for name, is_loaded in status.items() if is_loaded]

        if not cogs_to_reload:
            msg = "Keine geladenen Cogs zum Neuladen gefunden."
            if isinstance(ctx, Interaction):
                await ctx.followup.send(msg)
            else:
                await ctx.send(msg)
            return

        results = []
        for c in cogs_to_reload:
            if not status.get(c, True):
                results.append(f"⚠️ `{c}` ist nicht geladen - kann nicht neu geladen werden")
                continue

            try:
                await self.bot.reload_extension(f"cogs.{c}")
                results.append(f"✅ `{c}` neu geladen")

                msg = "\n".join(results)
                self.logger.info(
                    "Reloaded cogs: " + ", ".join([c for c in cogs_to_reload if status.get(c, False)]))

                if isinstance(ctx, Interaction):
                    await ctx.followup.send(msg + "\n🔄 Syncing commands...")
                else:
                    await ctx.send(msg + "\n🔄 Syncing commands...")

            except commands.ExtensionNotLoaded:
                results.append(f"⚠️ `{c}` ist nicht geladen - kann nicht neu geladen werden")
            except Exception as e:
                results.append(f"❌ Fehler bei `{c}`: {e}")
        await self.start_sync_commands()


async def setup(bot):
    await bot.add_cog(CogSelector(bot))