"""
Dieses Modul enthält die Klasse `Rob`,
die Funktionen zum Ausrauben von Spielern und Banken in einem Discord-Bot implementiert.
"""
import random
import discord
from discord.ext.commands import Context
from Util.util_commands import Utility


class Rob:
    """
    Eine Klasse, die das Ausrauben von Spielern und Banken in einem Discord-Bot implementiert.
    """
    def __init__(self, bot):
        self.bot = bot
        self.utils = Utility(bot)
        self.bank_caught = [
            "Dir ist deine Pistole aus der Hand gefallen als du sie zücken wolltest.\n"
            "Man hat sie dir abgenommen und die Polizei gerufen.\n"
            "\nDu musst eine Strafe von {money} :coin: zahlen.",
            "Du hast nicht aufgepasst und der Bankangestelle konnte problemlos "
            "den Stillenalarm auslösen.\n\nDie "
            "Polizei hast dich Festgenommen und eine Strafe von {money} :coin: auferlegt.",
            "Du wolltest für den reibungslosen überfall eine Geisel nehmen, hast aber einen "
            "Polizisten erwischt, "
            "welcher dich sofot festnahm.\n\neine Strafe lautet {money} :coin:.",
            "Du warst so selbstüberzeugt, dass du den Banküberfall schaffts.\nDa deine "
            "Informationen jedoch "
            "unzureichend waren, bist du direkt in eine Alarmanlage gelaufen.\n"
            "\nDeine Strafe lautet {money} :coin:.",
            "Du konntest die Bank zwar ausrauben, wurdest aber mithilfe des Überwachungssystem "
            "identifiziert.\n"
            "\nDadurch konnte man dich finden und dir eine Strafe von {money} :coin: geben.",
            "Du hast die Angestellten mit deiner Waffe bedroht, doch diese merkten schnell, "
            "dass du nur mit einer "
            "Wasserspritzpistole bewaffnet warst.\n"
            "\nDeine Strafe lautet {money} :coin:.",
            "Du und dein Helfer wart bei der Geld übergabe so nervös, "
            "dass ihr euch gegenseitig ins Gesicht schlugt, "
            "wodurch die Polizei genügend Zeit hatte euch zu schnappen.\n"
            "\nDeine Strafe lautet {money} :coin:.",
            "Du bist voll mit zuversicht zu deinem Banküberfall, "
            "aber zu deinem Pech hast du gerade versucht die "
            "Polizei auszurauben.\n\nDeine Strafe lautet {money} :coin:.",
            "Du bist zuversichtlich nach einem gelungenen Raub "
            "auf dem Weg nach Hause und wurdest von einem anderen "
            "Räuber ausgeraubt.\n\nAls du dies der Polizei berichtest "
            "bekommst du eine Strafe von {money} :coin:" +
            "und Sie einen neuen Räuber zum verfolgen."
        ]

    async def rob(self, player: discord.Member, ctx: discord.Interaction | Context):
        """
        Initiates a robbing action. If a player is specified, attempts to rob the player.
        Otherwise, attempts to rob a bank.

        Args:
            player (discord.Member): The player to rob, if specified.
            ctx (discord.Interaction | Context): The context of the command.
        """
        # TODO UPDATE: implement Gun-Item from Shop
        author = self.utils.return_author(ctx)
        user_money = await self.utils.get_money_for_user(author)
        self.bot.currentlyGaming.append(str(author.id))
        if player is not None:
            auszeit = 2
            await self.rob_player(player, ctx, author, user_money)

        else:
            auszeit = 5
            await self.rob_bank(ctx, author, user_money)

        self.bot.currentlyGaming.remove(str(author.id))
        self.bot.currentlyGaming.remove(str(player.id))
        await self.set_robbing_stop(auszeit, author.id)

    async def rob_player(self, player: discord.Member, ctx: discord.Interaction | Context,
                     user, user_money):
        """
        Attempts to rob another player.

        Args:
            player (discord.Member): The player to rob.
            ctx (discord.Interaction | Context): The context of the command.
            user: The user initiating the robbing action.
            user_money: The amount of money the user has.

        Returns:
            None
        """
        if player.bot:
            await ctx.send("Please stop pinging the Bots!!", delete_after=10)
            return

        if str(player.id) in self.bot.currentlyGaming:
            await ctx.send("Der User ist beschäftigt, bitte warten.", delete_after=10)
            return

        self.bot.currentlyGaming.append(str(player.id))
        robbing_money = await self.bot.db.get_money_for_user(player.id)

        if user_money < 250:
            await ctx.send("Du hast nichtmal Geld für die Mindeststrafe. Vergiss es lieber")
            return

        if robbing_money < 500:
            await ctx.send("Du willst jemanden mit 500 :coin: oder weniger berauben.\nWas bist du für ein Monster")
            return

        worth = max(250, int(robbing_money * 0.05))
        worth = min(worth, 2500)  # Upper limit

        chance = random.randint(0, 10)
        if chance < 3:
            await ctx.send("Du hast " + player.mention + f" um {worth} :coin: beraubt. \n"
                                 f"\nDu beschließt für ein paar Tage niemanden mehr zu berauben. "
                                 f"Aber vielleicht ja in 2 Tagen wieder.")
            new_money = user_money + worth
            new_robbing_money = robbing_money - worth
            await self.bot.db.set_money_for_user(player.id, new_robbing_money)
        else:
            penalty = int(user_money * 0.1)
            penalty = min(penalty, 4000)
            await ctx.send("Du wurdest erwischt und musst nun " + str(penalty) + " :coin: "
                                 "als Strafe zahlen. \n\nDu beschließt für ein paar Tage "
                                 "niemanden mehr zu berauben. Aber vielleicht ja in 2 Tagen wieder.")
            new_money = user_money - penalty

        await self.bot.db.set_money_for_user(user.id, new_money)

    async def rob_bank(self, ctx: discord.Interaction | Context, user, user_money):
        """
        Attempts to rob a bank.

        Args:
            ctx (discord.Interaction | Context): The context of the command.
            user: The user initiating the robbing action.
            user_money: The amount of money the user has.

        Returns:
            None
        """
        if user_money < 300:
            await ctx.send("Nopes. Du musst 300 :coin: oder mehr haben.",
                               delete_after=5)
            return

        chance = random.randint(0, 10)
        if chance < 2:
            await ctx.send("Du hast die Bank erfolgreich ausgeraubt. "
                                    "Die hast 7000 :coin: erhalten. Musst aber für 5 Tage "
                                    "untertauchen\n(Darfst niemanden ausrauben)")
            await self.bot.db.set_money_for_user(user.id, user_money + 7000)
        else:
            penalty = max(300, int(user_money * 0.075))
            penalty = min(penalty, 5000)
            reason: str = random.choice(self.bank_caught)
            new_money = user_money - penalty
            await self.bot.db.set_money_for_user(user.id, new_money)
            await ctx.send(reason.replace("{money}", str(penalty)) +
                               "\nDu musst für 5 Tage untertauchen (Darfst niemanden ausrauben)")

    async def set_robbing_stop(self, auszeit: int, userid):
        await self.bot.db.set_robbing_timeout(userid, auszeit)
