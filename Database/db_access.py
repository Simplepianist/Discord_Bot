"""
Database access module using aiomysql for asynchronous MySQL operations.

This module provides a DbController class to manage database connections and execute queries.
"""
import os
import datetime
import logging
import aiomysql



class DbController:
    """
        Controller for managing database connections and executing queries.
    """
    def __init__(self):
        """
        Initialize the DbController with a connection pool set to None.
        """
        self.pool = None

    async def init_pool(self):
        """
        Initialize the connection pool using aiomysql
        with parameters from environment variables.
        """
        self.pool = await aiomysql.create_pool(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=3306,
            db=os.getenv('DB_NAME'),
            minsize=1,
            maxsize=10,
            autocommit=True
        )

    async def close_pool(self):
        """
        Close the connection pool.
        """
        if self.pool:
            self.pool.close()  # Close the pool
            await self.pool.wait_closed()  # Wait for all connections to close
            logging.info("Database connection pool closed")

    async def execute_query(self, query, params=None):
        """
        Execute a SQL query with optional parameters.

        :param query: The SQL query to execute.
        :param params: Optional parameters for the SQL query.
        :return: The result of the query.
        """
        async with self.pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(query, params)
            result = await cur.fetchall()
            return result

    async def get_users_with_money(self):
        """
        Retrieve all users ordered by their money in descending order.

        :return: The result of the query.
        """
        query = "SELECT * FROM `money` ORDER BY money DESC"
        return await self.execute_query(query)

    async def create_new_user(self, userid):
        """
        Create a new user with the given user ID.

        :param userid: The ID of the user to create.
        :return: The result of the query.
        """
        query = 'insert into users values (%s, "user")'
        return await self.execute_query(query, (userid,))

    async def get_money_for_user(self, userid):
        """
        Retrieve the amount of money for a given user ID.
        If the user does not exist, create the user and set initial money.

        :param userid: The ID of the user.
        :return: The amount of money the user has.
        """
        if await self.user_exists_in_table('money', userid):
            query = "SELECT money FROM money WHERE identifier = %s"
            result = await self.execute_query(query, (userid,))
            if result:
                return result[0][0]
        else:
            if not await self.user_exists_in_table("users", userid):
                await self.create_new_user(userid)
            query = "INSERT INTO money (identifier, money) VALUES (%s, %s)"
            await self.execute_query(query, (userid, 1000))
            return 1000

    async def set_money_for_user(self, userid, money):
        """
        Set the amount of money for a given user ID.

        :param userid: The ID of the user.
        :param money: The amount of money to set.
        """
        query = "UPDATE money SET money = %s WHERE identifier = %s"
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
                    SELECT * FROM daily
                    WHERE identifier = %s
                    AND last_daily < CURDATE()
                )
                THEN 1
                ELSE 0 END;
            """
            result = await self.execute_query(query, (userid,))
            return bool(result[0][0]) if result else False
        if not await self.user_exists_in_table("users", userid):
            await self.create_new_user(userid)
        query = "INSERT INTO daily (identifier, last_daily, streak) VALUES (%s, CURDATE(), 0)"
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
                SELECT * FROM daily
                WHERE identifier = %s
                AND last_daily + INTERVAL 1 DAY = CURDATE()
            )
            THEN 1
            ELSE 0 END;
        """
        result = await self.execute_query(query, (userid,))
        update = bool(result[0][0]) if result else False
        if update:
            if streak <= 61:
                query = "UPDATE daily SET streak = %s WHERE identifier = %s"
                await self.execute_query(query, (streak, userid))
        else:
            query = "UPDATE daily SET streak = 0 WHERE identifier = %s"
            await self.execute_query(query, (userid,))

    async def get_streak_bonus(self, userid: int):
        """
        Retrieve the streak bonus for a given user ID. Update the streak accordingly.

        :param userid: The ID of the user.
        :return: The streak bonus.
        """
        query = """
            SELECT CASE WHEN EXISTS (
                SELECT * FROM daily
                WHERE identifier = %s
                AND last_daily + INTERVAL 1 DAY = CURDATE()
            )
            THEN (SELECT streak + 1 FROM daily WHERE identifier = %s)
            ELSE 0 END;
        """
        result = await self.execute_query(query, (userid, userid))
        streak = int(result[0][0]) if result else 0
        bonus = min(streak * 5, 300)
        await self.set_streak(userid, streak)
        return bonus

    async def set_daily(self, userid):
        """
        Set the last daily date to the current date for a given user ID.

        :param userid: The ID of the user.
        """
        query = "UPDATE daily SET last_daily = CURDATE() WHERE identifier = %s"
        await self.execute_query(query, (userid,))

    async def user_exists_in_table(self, table, userid):
        """
        Check if a user exists in a given table.

        :param table: The table to check.
        :param userid: The ID of the user.
        :return: True if the user exists, False otherwise.
        """
        query = f"""
            SELECT CASE WHEN EXISTS (
                SELECT * FROM {table}
                WHERE identifier = %s
            )
            THEN 1
            ELSE 0 END;
        """
        result = await self.execute_query(query, (userid,))
        return bool(result[0][0]) if result else False

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
        query = "INSERT INTO robbing (identifier, next_robbing) VALUES (%s, CURDATE())"
        await self.execute_query(query, userid)

    async def update_robbing(self, userid, next_robbing):
        """
        Update the robbing date for a given user ID.

        :param userid: The ID of the user.
        :param next_robbing: The next robbing date.
        """
        formatted_date = next_robbing.strftime('%Y-%m-%d') if next_robbing else 'CURDATE()'
        query = "UPDATE robbing SET next_robbing = %s WHERE identifier = %s"
        await self.execute_query(query, (formatted_date, userid))

    async def can_rob(self, userid):
        """
        Check if a user can rob.
        If the user does not exist in the robbing table, insert a new record.

        :param userid: The ID of the user.
        :return: A tuple (can_rob, next_robbing_date).
        """
        if await self.user_exists_in_table('robbing', userid):
            query = "SELECT next_robbing FROM robbing WHERE identifier = %s"
            result = await self.execute_query(query, (userid,))
            if result:
                next_robbing_date = result[0][0]
                return not (datetime.date.today() < next_robbing_date), next_robbing_date
            logging.error("The Check Rob made an Error")
            return False, None
        await self.insert_robbing(userid)
        return True, None
