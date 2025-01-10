import datetime
import logging
import mariadb
import os


class DB_Controller:
    def __init__(self, test):
        try:
            self.conn = mariadb.connect(
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST'),
                port=3306,
                database=os.getenv('DB_NAME')
            )
        except mariadb.Error as e:
            logging.error(e)
        self.conn.auto_reconnect = True
        self.conn.autocommit = False
        self.conn.cursor().execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
        self.cur = self.conn.cursor()

    def close_connections(self):
        self.cur.close()
        self.conn.close()

    def get_all_users(self):
        self.cur.execute("Select identifier from users")
        return self.cur

    def get_users_with_money(self):
        self.cur.execute("SELECT * FROM `money` order by money DESC;")
        return self.cur

    def create_new_user(self, id):
        self.cur.execute(f'insert into users values ({id}, "user")')

    def get_money_for_user(self, id):
        if self.user_exists_in_table('money', id):
            self.cur.execute("SELECT money FROM money WHERE identifier = %s", (id,))
            money = self.cur.fetchone()
            if money:
                return money[0]
        else:
            if not self.user_exists_in_table("users", id):
                self.create_new_user(id)
            self.cur.execute("INSERT INTO money (identifier, money) VALUES (%s, %s)", (id, 1000))
            self.conn.commit()
            return 1000

    def set_money_for_user(self, id, money):
        self.cur.execute("UPDATE money SET money = %s WHERE identifier = %s", (money, id))
        self.conn.commit()

    def get_daily(self, id):
        if self.user_exists_in_table('daily', id):
            self.cur.execute(f"""SELECT CASE WHEN EXISTS (
                                    SELECT *
                                    from daily
                                    where identifier = {id}
                                    and last_daily < CURDATE()
                                )
                                THEN 1
                                ELSE 0 END;""")
        else:
            if not self.user_exists_in_table("users", id):
                self.create_new_user(id)
            self.cur.execute(f"insert into daily values ({id}, curdate(), 0)")
            self.conn.commit()
            return True
        for case in self.cur:
            return True if case[0] == 1 else False

    async def set_streak(self, id, streak):
        self.cur.execute(f"""SELECT CASE WHEN EXISTS (
                                        SELECT *
                                        from daily
                                        where identifier = {id}
                                        and last_daily + INTERVAL 1 DAY = curdate()
                                        )
                                        THEN 1
                                        ELSE 0 END;""")
        update = False
        for case in self.cur:
            update = True if case[0] == 1 else False
        if update:
            if streak <= 61:
                self.cur.execute(f"update daily set streak = {streak} where identifier = {id}")
                self.conn.commit()
        else:
            self.cur.execute(f"update daily set streak = 0 where identifier = {id}")
            self.conn.commit()

    async def get_streak_bonus(self, id: int):
        self.cur.execute(f"""SELECT CASE WHEN EXISTS (
                                SELECT *
                                from daily
                                where identifier = {id}
                                and last_daily + INTERVAL 1 DAY = curdate()
                                )
                                THEN (SELECT streak + 1 from daily where identifier = {id})
                                ELSE 0 END;""")
        bonus = 0
        streak = 0
        for case in self.cur:
            streak = int(case[0])
            bonus = streak * 5
            if bonus >= 300:
                bonus = 300
        await self.set_streak(id, streak)
        return bonus

    def set_daily(self, id):
        self.cur.execute(f"update daily set last_daily = current_date() where identifier = {id}")
        self.conn.commit()

    def user_exists_in_table(self, table, id):
        self.cur.execute(f"""SELECT CASE WHEN EXISTS (
                                Select * from {table}
                                where identifier = {id}
                            )
                            THEN 1
                            ELSE 0 END;""")
        for case in self.cur:
            return True if case[0] == 1 else False

    def set_robbing_timeout(self, id, auszeit):
        date = datetime.date.today()
        next_robbing = date + datetime.timedelta(days=auszeit)
        self.update_robbing(id, next_robbing)

    def insert_robbing(self, id):
        self.cur.execute(f"INSERT INTO robbing (identifier, next_robbing) VALUES ({id}, curdate())")
        self.conn.commit()

    def update_robbing(self, id, next_robbing):
        formatted_date = next_robbing.strftime('%Y-%m-%d') if next_robbing else 'curdate()'
        self.cur.execute(f"UPDATE robbing SET next_robbing = '{formatted_date}' WHERE identifier = {id}")
        self.conn.commit()

    def can_rob(self, id):
        if self.user_exists_in_table('robbing', id):
            query = f"SELECT next_robbing FROM robbing WHERE identifier = {id}"
            self.cur.execute(query)
            result = self.cur.fetchone()
            if result:
                next_robbing_date = result[0]
                return not (datetime.date.today() < next_robbing_date), next_robbing_date
            else:
                logging.error("The Check Rob made an Error")
                return False, None  # or raise an exception if the identifier does not exist
        else:
            self.insert_robbing(id)
            return True, None
