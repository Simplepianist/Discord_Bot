import logging
from discord.ext import commands
from fastapi import FastAPI
from uvicorn import Config, Server
from API.content_api import API
from Database.db_access import DbController


class SimpleBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = None
        self.db = DbController()

    async def run_fastapi(self, bot):
        logging.info("Starting FastAPI server")
        app = FastAPI()
        app.include_router(API(bot, self.db).router)
        config = Config(app, host="0.0.0.0", port=8000)
        self.server = Server(config)
        await self.server.serve()

    async def close(self) -> None:
        await super().close()
        await self.db.close_pool()
        await self.server.shutdown()