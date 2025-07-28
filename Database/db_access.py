"""
Database access module using asyncpg for asynchronous PostgreSQL operations.

This module provides a DbController class to manage database connections and execute queries.
"""
import os
import datetime
import logging
import asyncpg
from alembic.config import Config
from alembic import command

class DbController:
    """
        Controller for managing database connections and executing queries.
    """
    def __init__(self):
        """
        Initialize the DbController with a connection pool set to None.
        """
        self.pool = None
        self.logger = logging.getLogger('DbController')

    async def run_migrations(self):
        """
        Run database migrations using Alembic.
        Should be called before initializing the connection pool.
        """
        try:
            self.logger.info("Starting database migrations...")

            import asyncio
            import logging
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
            self.logger.error(f"Migration failed: {e}")
            raise

    async def init_pool(self):
        """
        Initialize the connection pool using asyncpg
        with parameters from environment variables.
        """
        try:
            self.logger.info("Initializing database connection pool...")
            self.pool = await asyncpg.create_pool(
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST'),
                port=int(os.getenv('DB_PORT', '5432')),
                database=os.getenv('DB_NAME'),
                min_size=1,
                max_size=10
            )
            self.logger.info("Database connection pool initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database pool: {e}")
            raise

    async def close_pool(self):
        """
        Close the connection pool.
        """
        if self.pool:
            await self.pool.close()
            self.logger.info("Database connection pool closed")

    async def execute_query(self, query, params=None):
        """
        Execute a SQL query with optional parameters.

        :param query: The SQL query to execute.
        :param params: Optional parameters for the SQL query.
        :return: The result of the query.
        """
        async with self.pool.acquire() as conn:
            if params:
                result = await conn.fetch(query, *params)
            else:
                result = await conn.fetch(query)
            return result

    async def get_users_with_money(self):
        """
        Retrieve all users ordered by their money in descending order.

        :return: The result of the query.
        """
        query = 'SELECT * FROM money ORDER BY money DESC'
        return await self.execute_query(query)

    async def create_new_user(self, userid):
        """
        Create a new user with the given user ID.

        :param userid: The ID of the user to create.
        :return: The result of the query.
        """
        query = 'INSERT INTO users VALUES ($1, $2)'
        return await self.execute_query(query, (userid, "user"))

    async def get_money_for_user(self, userid):
        """
        Retrieve the amount of money for a given user ID.
        If the user does not exist, create the user and set initial money.

        :param userid: The ID of the user.
        :return: The amount of money the user has.
        """
        if await self.user_exists_in_table('money', userid):
            query = "SELECT money FROM money WHERE identifier = $1"
            result = await self.execute_query(query, (userid,))
            if result:
                return result[0]['money']
        else:
            if not await self.user_exists_in_table("users", userid):
                await self.create_new_user(userid)
            query = "INSERT INTO money (identifier, money) VALUES ($1, $2)"
            await self.execute_query(query, (userid, 1000))
            return 1000

    async def set_money_for_user(self, userid, money):
        """
        Set the amount of money for a given user ID.

        :param userid: The ID of the user.
        :param money: The amount of money to set.
        """
        query = "UPDATE money SET money = $1 WHERE identifier = $2"
        await self.execute_query(query, (money, userid))

    async def get_daily(self, userid):
        """
        Check if the user can receive a daily reward.
        If the user does not exist, create the user and set initial daily data.

        :param userid: The ID of the user.
        :return: True if the user can receive a daily reward, False otherwise.
        """
        if await self.user_exists_in_table('daily', userid):
            query = """
                SELECT CASE WHEN EXISTS (
                    SELECT 1 FROM daily
                    WHERE identifier = $1
                    AND last_daily < CURRENT_DATE
                )
                THEN TRUE
                ELSE FALSE END AS can_daily;
            """
            result = await self.execute_query(query, (userid,))
            return bool(result[0]['can_daily']) if result else False
        if not await self.user_exists_in_table("users", userid):
            await self.create_new_user(userid)
        query = "INSERT INTO daily (identifier, last_daily, streak) VALUES ($1, CURRENT_DATE, 0)"
        await self.execute_query(query, (userid,))
        return True

    async def set_streak(self, userid, streak):
        """
        Set the streak for a given user ID.
        If the streak is less than or equal to 61, update the streak, otherwise reset it.

        :param userid: The ID of the user.
        :param streak: The streak value to set.
        """
        query = """
            SELECT CASE WHEN EXISTS (
                SELECT 1 FROM daily
                WHERE identifier = $1
                AND last_daily + INTERVAL '1 day' = CURRENT_DATE
            )
            THEN TRUE
            ELSE FALSE END AS update_streak;
        """
        result = await self.execute_query(query, (userid,))
        update = bool(result[0]['update_streak']) if result else False
        if update:
            if streak <= 61:
                query = "UPDATE daily SET streak = $1 WHERE identifier = $2"
                await self.execute_query(query, (streak, userid))
        else:
            query = "UPDATE daily SET streak = 0 WHERE identifier = $1"
            await self.execute_query(query, (userid,))

    async def get_streak_bonus(self, userid: int):
        """
        Retrieve the streak bonus for a given user ID. Update the streak accordingly.

        :param userid: The ID of the user.
        :return: The streak bonus.
        """
        query = """
            SELECT CASE WHEN EXISTS (
                SELECT 1 FROM daily
                WHERE identifier = $1
                AND last_daily + INTERVAL '1 day' = CURRENT_DATE
            )
            THEN (SELECT streak + 1 FROM daily WHERE identifier = $2)
            ELSE 0 END AS streak_value;
        """
        result = await self.execute_query(query, (userid, userid))
        streak = int(result[0]['streak_value']) if result else 0
        bonus = min(streak * 5, 300)
        await self.set_streak(userid, streak)
        return bonus

    async def set_daily(self, userid):
        """
        Set the last daily date to the current date for a given user ID.

        :param userid: The ID of the user.
        """
        query = "UPDATE daily SET last_daily = CURRENT_DATE WHERE identifier = $1"
        await self.execute_query(query, (userid,))

    async def user_exists_in_table(self, table, userid):
        """
        Check if a user exists in a given table.

        :param table: The table to check.
        :param userid: The ID of the user.
        :return: True if the user exists, False otherwise.
        """
        query = f"""
            SELECT EXISTS (
                SELECT 1 FROM {table}
                WHERE identifier = $1
            ) AS exists_user;
        """
        result = await self.execute_query(query, (userid,))
        return bool(result[0]['exists_user']) if result else False

    async def set_robbing_timeout(self, userid, auszeit):
        """
        Set the robbing timeout for a given user ID.

        :param userid: The ID of the user.
        :param auszeit: The timeout duration in days.
        """
        date = datetime.date.today()
        next_robbing = date + datetime.timedelta(days=auszeit)
        await self.update_robbing(userid, next_robbing)

    async def insert_robbing(self, userid):
        """
        Insert a new robbing record for a given user ID.

        :param userid: The ID of the user.
        """
        query = "INSERT INTO robbing (identifier, next_robbing) VALUES ($1, CURRENT_DATE)"
        await self.execute_query(query, (userid,))

    async def update_robbing(self, userid, next_robbing):
        """
        Update the robbing date for a given user ID.

        :param userid: The ID of the user.
        :param next_robbing: The next robbing date.
        """
        formatted_date = next_robbing.strftime('%Y-%m-%d') if next_robbing else None
        query = "UPDATE robbing SET next_robbing = $1 WHERE identifier = $2"
        await self.execute_query(query, (formatted_date, userid))

    async def can_rob(self, userid):
        """
        Check if a user can rob.
        If the user does not exist in the robbing table, insert a new record.

        :param userid: The ID of the user.
        :return: A tuple (can_rob, next_robbing_date).
        """
        if await self.user_exists_in_table('robbing', userid):
            query = "SELECT next_robbing FROM robbing WHERE identifier = $1"
            result = await self.execute_query(query, (userid,))
            if result:
                next_robbing_date = result[0]['next_robbing']
                can_rob = not (datetime.date.today() < next_robbing_date)
                return can_rob, next_robbing_date
            logging.error("The Check Rob made an Error")
            return False, None
        await self.insert_robbing(userid)
        return True, None