"""
Database access module using SQLAlchemy ORM for asynchronous PostgreSQL operations.

This module provides a DbController class to manage database connections and execute queries using db_tables definitions.
"""
import os
import datetime
import logging
import urllib.parse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from alembic.config import Config
from alembic import command

from .db_tables import User, Money, Daily, Robbing, Cogs

class DbController:
    """
        Controller for managing database connections and executing queries via SQLAlchemy ORM.
    """
    def __init__(self):
        self.engine = None
        self.async_session = None
        self.logger = logging.getLogger('DbController')

    async def run_migrations(self):
        """
        Run database migrations using Alembic.
        Should be called before initializing the connection pool.
        """
        try:
            self.logger.info("Starting database migrations...")

            import asyncio
            import sys
            from io import StringIO

            # Capture the current logging state more comprehensively
            root_logger = logging.getLogger()

            # Store all current loggers and their configurations
            logger_states = {}
            for name in logging.Logger.manager.loggerDict:
                logger = logging.getLogger(name)
                logger_states[name] = {
                    'level': logger.level,
                    'handlers': logger.handlers[:],
                    'propagate': logger.propagate,
                    'disabled': logger.disabled
                }

            # Store root logger state
            root_state = {
                'level': root_logger.level,
                'handlers': root_logger.handlers[:],
                'disabled': root_logger.disabled
            }

            def run_alembic_sync():
                # Create a minimal alembic config that doesn't interfere with logging
                alembic_cfg = Config("alembic.ini")

                # Completely disable alembic's logging configuration
                alembic_cfg.attributes['configure_logger'] = False

                # Temporarily redirect alembic's output to prevent it from affecting our loggers
                old_stdout = sys.stdout
                old_stderr = sys.stderr

                try:
                    # Capture alembic output instead of letting it interfere
                    capture_stdout = StringIO()
                    capture_stderr = StringIO()

                    # Only redirect if we want to suppress alembic output
                    # Comment out these lines if you want to see alembic output
                    sys.stdout = capture_stdout
                    sys.stderr = capture_stderr

                    # Run the migration
                    command.upgrade(alembic_cfg, "head")

                finally:
                    # Always restore stdout/stderr
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

            # Run alembic in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, run_alembic_sync)

            # Restore all logger configurations
            # First restore root logger
            root_logger.setLevel(root_state['level'])
            root_logger.handlers = root_state['handlers']
            root_logger.disabled = root_state['disabled']

            # Then restore all other loggers
            for name, state in logger_states.items():
                logger = logging.getLogger(name)
                logger.setLevel(state['level'])
                logger.handlers = state['handlers']
                logger.propagate = state['propagate']
                logger.disabled = state['disabled']

            # Clear any handlers that alembic might have added
            for handler in root_logger.handlers[:]:
                if hasattr(handler, 'stream') and hasattr(handler.stream, 'name'):
                    # Remove any file handlers that alembic might have added
                    if 'alembic' in str(handler.stream.name).lower():
                        root_logger.removeHandler(handler)

            self.logger.info("Database migrations completed successfully")

        except Exception as e:
            self.logger.error("Migration failed: %s", e)
            raise

    async def init_pool(self):
        """
        Initialize the async SQLAlchemy engine and sessionmaker.
        """
        try:
            self.logger.info("Initializing database connection engine...")
            user = urllib.parse.quote_plus(os.getenv('DB_USER', ''))
            password = urllib.parse.quote_plus(os.getenv('DB_PASSWORD', ''))
            host = os.getenv('DB_HOST', '')
            port = os.getenv('DB_PORT', '5432')
            dbname = os.getenv('DB_NAME', '')
            db_url = (
                f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"
            )
            self.engine = create_async_engine(db_url, echo=False, future=True)
            self.async_session = sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )
            self.logger.info("Database engine initialized successfully")
        except Exception as e:
            self.logger.error("Failed to initialize database engine: %s", e)
            raise

    async def load_cogs_state(self):
        """
        Lade alle Cogs und deren Status aus der Datenbank.
        """
        async with self.async_session() as session:
            stmt = select(Cogs)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def save_cog(self, cog: tuple[str, bool]):
        """
        Speichert den Status eines einzelnen Cogs als Tupel (Name, aktiviert) in der Datenbank.
        """
        async with self.async_session() as session:
            cog_name, enabled = cog
            existing_cog = await session.get(Cogs, cog_name)
            if existing_cog:
                existing_cog.state = enabled
            else:
                session.add(Cogs(name=cog_name, enabled=int(enabled)))
            await session.commit()
            self.logger.info("Cog '%s' state saved successfully", cog_name)

    async def close_pool(self):
        """
        Dispose the engine.
        """
        if self.engine:
            await self.engine.dispose()
            self.logger.info("Database engine disposed")

    async def get_users_with_money(self):
        """
        Retrieve all users ordered by their money in descending order.
        """
        async with self.async_session() as session:
            stmt = select(Money).order_by(Money.money.desc())
            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_money_for_user(self, userid):
        """
        Retrieve the amount of money for a given user ID.
        If the user does not exist, create the user and set initial money.
        """
        async with self.async_session() as session:
            money_obj = await session.get(Money, userid)
            if money_obj:
                return money_obj.money
            user_obj = await session.get(User, userid)
            if not user_obj:
                user_obj = User(identifier=userid, role="user")
                session.add(user_obj)
                await session.commit()
            money_obj = Money(identifier=userid, money=1000)
            session.add(money_obj)
            await session.commit()
            return 1000

    async def set_money_for_user(self, userid, money):
        """
        Set the amount of money for a given user ID.
        """
        async with self.async_session() as session:
            stmt = update(Money).where(Money.identifier == userid).values(money=money)
            await session.execute(stmt)
            await session.commit()

    async def get_daily(self, userid):
        """
        Check if the user can receive a daily reward.
        If the user does not exist, create the user and set initial daily data.
        """
        async with self.async_session() as session:
            daily_obj = await session.get(Daily, userid)
            if daily_obj:
                can_daily = daily_obj.last_daily < datetime.date.today()
                return can_daily
            user_obj = await session.get(User, userid)
            if not user_obj:
                user_obj = User(identifier=userid, role="user")
                session.add(user_obj)
                await session.commit()
            daily_obj = Daily(identifier=userid, last_daily=datetime.date.today(), streak=0)
            session.add(daily_obj)
            await session.commit()
            return True

    async def update_streak_and_get_bonus(self, userid: int):
        """
        Aktualisiert die Streak eines Users und berechnet den Bonus.
        Setzt die Streak zurück, falls der User nicht gestern aktiv war.
        """
        async with self.async_session() as session:
            daily_obj = await session.get(Daily, userid)
            streak = 0
            if daily_obj:
                if daily_obj.last_daily + datetime.timedelta(days=1) == datetime.date.today():
                    streak = min(daily_obj.streak + 1, 61)
                    daily_obj.streak = streak
                else:
                    daily_obj.streak = 0
                await session.commit()
            bonus = min(streak * 5, 300)
            return bonus

    async def set_daily(self, userid):
        """
        Set the last daily date to the current date for a given user ID.
        """
        async with self.async_session() as session:
            daily_obj = await session.get(Daily, userid)
            if daily_obj:
                daily_obj.last_daily = datetime.date.today()
                await session.commit()
            else:
                daily_obj = Daily(identifier=userid, last_daily=datetime.date.today(), streak=0)
                session.add(daily_obj)
                await session.commit()

    async def set_robbing_timeout(self, userid, auszeit):
        """
        Set the robbing timeout for a given user ID.
        """
        date = datetime.date.today()
        next_robbing = date + datetime.timedelta(days=auszeit)
        await self.update_robbing(userid, next_robbing)

    async def insert_robbing(self, userid):
        """
        Insert a new robbing record for a given user ID.
        """
        async with self.async_session() as session:
            robbing_obj = Robbing(identifier=userid, next_robbing=datetime.date.today())
            session.add(robbing_obj)
            await session.commit()

    async def update_robbing(self, userid, next_robbing):
        """
        Update the robbing date for a given user ID.
        """
        async with self.async_session() as session:
            robbing_obj = await session.get(Robbing, userid)
            if robbing_obj:
                robbing_obj.next_robbing = next_robbing if next_robbing else datetime.date.today()
            else:
                robbing_obj = Robbing(identifier=userid, next_robbing=next_robbing if next_robbing else datetime.date.today())
                session.add(robbing_obj)
            await session.commit()

    async def can_rob(self, userid):
        """
        Check if a user can rob.
        If the user does not exist in the robbing table, insert a new record.
        """
        async with self.async_session() as session:
            robbing_obj = await session.get(Robbing, userid)
            if robbing_obj:
                next_robbing_date = robbing_obj.next_robbing
                can_rob = not (datetime.date.today() < next_robbing_date)
                return can_rob, next_robbing_date
            await self.insert_robbing(userid)
            return True, None
