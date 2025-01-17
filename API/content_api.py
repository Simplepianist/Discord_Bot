from discord.ext.commands import Command
from fastapi import APIRouter

class API:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.router = APIRouter()
        self.router.add_api_route("/scoreboard", self.scoreboard, methods=["GET"])
        self.router.add_api_route("/commands", self.command_list, methods=["GET"])

    async def scoreboard(self):
        scorelist = sorted(await self.db.get_users_with_money(), key=lambda x: x[1], reverse=True)
        result = []
        for score in scorelist:
            user = self.bot.get_user(int(score[0])) or await self.bot.fetch_user(int(score[0]))
            result.append({"username": user.name, "money": score[1]})
        return result

    async def command_list(self):
        result = []
        for cog_name, cog in self.bot.cogs.items():
            commands = []
            for command in cog.get_commands():
                if isinstance(command, Command):
                    checks = [check.__qualname__.split(".")[0] for check in command.checks]
                    aliases = []
                    for alias in command.aliases:
                        aliases.append("." + alias)
                    commands.append([command.name, aliases, command.description, checks])
            result.append({cog_name: commands})
        return result