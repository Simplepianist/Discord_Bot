import random
import discord
from discord.ext.commands import Context
from Util.variables import currentlyGaming
from Util.util_commands import send_message, return_author, get_money_for_user, db


class Rob:
    def __init__(self):
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
        # TODO UPDATE: implement Gun-Item from Shop
        user = return_author(ctx)
        user_money = await get_money_for_user(user)
        auszeit = 0
        worked = True
        currentlyGaming.append(str(user.id))
        if player is not None:
            canrob = True
            bot = False
            if player.bot:
                bot = True
            if str(player.id) in currentlyGaming:
                canrob = False
            if canrob and not bot:
                currentlyGaming.append(str(player.id))
                robbing_money = await db.get_money_for_user(player.id)
                if user_money < 250:
                    await send_message(msg="Du hast nichtmal Geld für die Mindeststrafe. "
                                           "Vergiss es lieber", ctx=ctx)
                    return
                if robbing_money < 500:
                    await send_message(msg="Du willst jemanden mit 500 :coin: oder weniger "
                                           "berauben.\nWas bist du für ein Monster", ctx=ctx)
                else:
                    if 250 > robbing_money * 0.05:
                        worth = int(robbing_money * 0.05)
                    else:
                        worth = 250
                    chance = random.randint(0,10)
                    if chance < 3:
                        await send_message(msg="Du hast " + player.mention + f" um {worth} :coin: "
                                   "beraubt. \n\nDu beschließt für ein paar Tage niemanden mehr zu"
                                   " berauben. Aber vielleicht ja in 2 Tagen wieder.", ctx=ctx)
                        new_money = user_money + worth
                        new_robbing_money = robbing_money - worth
                        await db.set_money_for_user(player.id, new_robbing_money)
                    else:
                        await send_message(msg="Du wurdest erwischt und musst nun 250 :coin: als "
                                               "Strafe zahlen. \n\nDu beschließt für ein paar Tage"
                                               " niemanden mehr zu berauben. Aber vielleicht ja "
                                               "in 2 Tagen wieder.", ctx=ctx)
                        new_money = user_money - 250
                    await db.set_money_for_user(user.id, new_money)
                    auszeit = 2
            else:
                worked = False
                if bot:
                    await send_message(ctx, msg="Please stop pinging the Bots!!",
                                       delete_after=10)
                else:
                    await send_message(ctx, "Der User ist beschäftigt, bitte warten.",
                                       delete_after=10)
            if worked:
                currentlyGaming.remove(str(player.id))
        elif player is None:
            if user_money < 300:
                await send_message(ctx, "Nopes. Du musst 300 :coin: oder mehr haben.",
                                   delete_after=5)
            else:
                chance = random.randint(0,10)
                if chance < 2:
                    await send_message(ctx, "Du hast die Bank erfolgreich ausgeraubt. Die "
                                            "hast 7000 :coin: erhalten. Musst aber für 5 Tage "
                                            "untertauchen\n(Darfst niemanden ausrauben)")
                    await db.set_money_for_user(user.id, user_money+7000)
                else:
                    if 300 < user_money * 0.075:
                        pay = int(user_money * 0.075)
                    else:
                        pay = 300
                    reason: str = random.choice(self.bank_caught)
                    new_money=user_money - pay
                    await db.set_money_for_user(user.id, new_money)
                    await send_message(ctx, reason.replace("{money}", str(pay)) + ""
                                           "\nDu musst für 5 Tage untertauchen "
                                            "(Darfst niemanden ausrauben)")
                auszeit = 5
        await self.set_robbing_stop(auszeit, user.id)

    async def set_robbing_stop(self, auszeit: int, userid):
        currentlyGaming.remove(str(userid))
        await db.set_robbing_timeout(userid, auszeit)
