import time

from discord.ui import Button
from Game.Blackjack import Blackjack
from Game.Higher_Lower import Higher_Lower
from Game.Rob import Rob
from Game import Roulette

import Util.variables
from Util.util_commands import *
from Util.variables import currentlyGaming


class Games():
    def __init__(self):
        self.gaming_enums = ["Blackjack", "Higherlower"]

    async def robCommand(self, ctx: Context | Interaction, player: discord.Member):
        author = return_author(ctx)
        can_rob, next_robbing = db.can_rob(author.id)
        if can_rob:
            if str(author.id) not in currentlyGaming:
                robbing = Rob()
                await robbing.rob(player, ctx)
            else:
                await send_message(ctx, f"{author.mention}. Du bist beschäftigt mit etwas anderem!!!", delete_after=5)
        else:
            if next_robbing:
                await send_message(ctx,
                                   "You cannot Rob cause you are still hiding.\nWait till: " + next_robbing.strftime(
                                       '%d.%m.%Y'), delete_after=10)
            else:
                await send_message(ctx, "There seems to be an Error, pls Contact Support for more Information",
                                   delete_after=10)

    async def scoreboardCommand(self, ctx: Context | Interaction):
        scorelist = db.get_users_with_money()
        loaded_config = load_config("embed")
        embed = discord.Embed(title="Scoreboard", colour=discord.Colour(0x6b0b04),
                              description="Hier ist das Scoreboard für die Games")

        embed.set_thumbnail(url=loaded_config["embeds_thumbnail"])
        embed.set_footer(text=loaded_config["embeds_footertext"],
                         icon_url=Util.variables.owner.avatar)

        for i, score in enumerate(scorelist):
            user = bot.get_user(int(score[0]))
            if user is None:
                user = await bot.fetch_user(int(score[0]))
            name = user.name
            if int(user.discriminator) != 0:
                name = name + "#" + str(user.discriminator)
            if i + 1 in [1, 2, 3]:
                emojis = ["first_place", "second_place", "third_place"]
                embed.add_field(name=f":{emojis[i]}: {name}", value=f"{score[1]} :coin:", inline=False)
            else:
                embed.add_field(name=f"{i + 1}. {name}", value=f"{score[1]} :coin:", inline=False)
            if i == 9:
                break
        await send_message(ctx, embed=embed)

    async def dailyCommand(self, ctx: Context | Interaction):
        author = return_author(ctx)
        if get_daily(author):
            money_user = int(get_money_for_user(author)) + 300
            bonus = await db.get_streak_bonus(author.id)
            money_user = money_user + bonus
            db.set_money_for_user(author.id, money_user)
            await send_message(ctx, f"Du hast {300 + bonus} Coins erhalten.\n**Total: {money_user} Coins**")
            db.set_daily(author.id)
        else:
            await send_message(ctx, "**Du hast dein Daily heute schon geclaimed**")

    async def sendCommand(self, ctx: Context | Interaction, member: discord.Member, set_money=None):
        if not member.bot:
            author = str(return_author(ctx))
            user = str(member)
            try:
                set_money = int(set_money)
                if author == user:
                    await send_message(ctx, "Du kannst dir selbst kein Geld senden", ephemeral=True, delete_after=5)
                elif set_money is None:
                    await send_message(ctx, "Betrag muss angegeben sein", ephemeral=True, delete_after=5)
                elif set_money <= 0:
                    await send_message(ctx, "Betrag muss positiv sein", ephemeral=True, delete_after=5)
                elif user is None:
                    await send_message(ctx, "Kein Spieler angegeben", ephemeral=True, delete_after=5)
                else:
                    money_user = get_money_for_user(return_author(ctx))
                    money_other = get_money_for_user(member)
                    if set_money > money_user:
                        await send_message(ctx, "Nicht genügend :coin: zum senden")
                    else:

                        money_user = money_user - set_money
                        money_other = money_other + set_money

                        db.set_money_for_user(return_author(ctx).id, money_user)
                        db.set_money_for_user(member.id, money_other)
                        embed = discord.Embed(title="Bank", colour=discord.Colour(0xc6c910))
                        embed.add_field(name=author, value=f"Money: {money_user} :coin:", inline=False)
                        embed.add_field(name=user, value=f"Money: {money_other} :coin:", inline=False)
                        await send_message(ctx, embed=embed)
            except Exception as e:
                await send_message(ctx, "Falsche Parameter übergeben", ephemeral=True)
        else:
            await send_message(ctx, "Bitte nicht die Bots pingen")

    async def moneyCommand(self, ctx: Context | Interaction, may_member: discord.Member = None):
        if may_member is not None:
            if not may_member.bot:
                user_money = get_money_for_user(may_member)
                await send_message(ctx, f"{may_member.name} hat aktuell {user_money} :coin:")
            else:
                await send_message(ctx, "Bitte nicht die Bots pingen", delete_after=20)
        else:
            user_money = get_money_for_user(return_author(ctx))
            await send_message(ctx, f"Du hast aktuell {user_money} :coin:")

    async def blackjackCommand(self, ctx: Context | Interaction, bet: int):
        playable = can_play(ctx, bet)
        msg = None
        if playable[0] and playable[1] :
            user = str(return_author(ctx).id)
            global user_money_dir
            if user not in currentlyGaming:
                money_user = get_money_for_user(return_author(ctx))
                currentlyGaming.append(user)
                draw_id = "draw_" + user
                hold_id = "hold_" + user
                draw_button = Button(label="Draw", style=discord.ButtonStyle.green, custom_id=draw_id)
                hold_button = Button(label="Stand", style=discord.ButtonStyle.red, custom_id=hold_id)

                embed = create_embed(ctx, 0xb59809, "Blackjack")
                # Logik Blackjack
                firstplayer = True
                has_interaction = True
                responded = False
                bj = Blackjack(bet)
                bj.firstdraw()
                dealerpoints = get_first_card(bj.dealerdrawn)
                dealershown = ""
                playerausgabe = ""
                while not bj.is_over():
                    if not bj.playerstand:
                        view = discord.ui.View(timeout=None)
                        view.add_item(draw_button)
                        view.add_item(hold_button)
                        if firstplayer:
                            dealercard = bj.dealerdrawn[0]
                            if dealercard[0] == "König":
                                dealershown = "K"
                            elif dealercard[0] == "Bube":
                                dealershown = "B"
                            elif dealercard[0] == "Dame":
                                dealershown = "D"
                            elif dealercard[0] == "Ass":
                                dealershown = "A"
                            else:
                                dealershown = str(dealercard[0])

                        else:
                            embed = create_embed(ctx, 0xb59809, "Blackjack")
                        cardshow = []
                        for card in bj.playerdrawn:
                            icon = card[0]
                            if icon == "König":
                                cardshow.append("K")
                            elif icon == "Bube":
                                cardshow.append("B")
                            elif icon == "Dame":
                                cardshow.append("D")
                            elif icon == "Ass":
                                cardshow.append("A")
                            else:
                                cardshow.append(str(card[0]))

                        playerausgabe = ", ".join(cardshow)

                        embed.add_field(name=str(return_author(ctx).name) + f" | ```{bj.player}```",
                                        value=f"{playerausgabe}",
                                        inline=True)
                        embed.add_field(name="Dealer" + f" | ```{dealerpoints}```", value=f"{dealershown}", inline=True)
                        if firstplayer:
                            msg = await send_message(ctx, embed=embed, view=view)
                            firstplayer = not firstplayer
                        else:
                            await res.response.edit_message(embed=embed, view=view)
                        checkin = False

                        if bj.natural_player:
                            bj.stand("player")
                            has_interaction = False
                        else:
                            #
                            while not checkin:
                                res: Interaction = await bot.wait_for('interaction',
                                                                      check=lambda
                                                                          interaction: interaction.user == return_author(
                                                                          ctx))

                                if "component_type" in res.data and "custom_id" in res.data:
                                    if user == str(res.user.id) and res.data[
                                        "component_type"] == 2 and "custom_id" in res.data.keys():
                                        checkin = True
                            action = res.data["custom_id"]
                            if action == draw_id:
                                bj.draw_another("player")
                                if bj.is_overbought("player"):
                                    bj.stand("player")
                            elif action == hold_id:
                                bj.stand("player")
                    else:
                        view.clear_items()
                        if not bj.is_overbought("player"):
                            embed = create_embed(ctx, 0xb59809, "Blackjack")
                            cardshow = []
                            for card in bj.dealerdrawn:
                                icon = card[0]
                                if icon == "König":
                                    cardshow.append("K")
                                elif icon == "Bube":
                                    cardshow.append("B")
                                elif icon == "Dame":
                                    cardshow.append("D")
                                elif icon == "Ass":
                                    cardshow.append("A")
                                else:
                                    cardshow.append(str(card[0]))

                            dealerausgabe = ", ".join(cardshow)
                            embed.add_field(name=str(return_author(ctx).name) + f" | ```{bj.player}```",
                                            value=f"{playerausgabe}",
                                            inline=True)
                            embed.add_field(name="Dealer" + f" | ```{bj.dealer}```", value=f"{dealerausgabe}",
                                            inline=True)
                            if not responded and has_interaction:
                                await res.response.edit_message(embed=embed, view=view)
                                responded = not responded
                            else:
                                await msg.edit(embed=embed, view=view)
                            if bj.dealer_draw() and not bj.dealerstand:
                                bj.draw_another("dealer")
                                if bj.is_overbought("dealer"):
                                    bj.stand("dealer")
                                time.sleep(2)
                            else:
                                bj.stand("dealer")
                        else:
                            bj.stand("dealer")
                            await res.response.edit_message(embed=embed, view=view)

                if bj.won() == "draw":
                    name = "Unentschieden"
                    value = f"Du hast {str(bj.get_money())} :coin: zurückerhalten"
                    color = 0xd6b22f
                elif bj.won() == "player":
                    name = "Gewonnen"
                    value = f"Du hast {str(bet)} :coin: erhalten"
                    money_user = int(money_user) + bet
                    color = 0x06660b
                elif bj.won() == "dealer":
                    name = "Verloren"
                    value = f"Du hast deinen Einsatz von {str(bet)} :coin: verloren"
                    money_user = int(money_user) - bet
                    color = 0xb50909
                elif bj.won() == "doppelt":
                    name = "Natural Blackjack"
                    value = f"Du hast {str(bj.get_money())} :coin: erhalten"
                    money_user = int(money_user) + bj.get_money()
                    color = 0x5f09b5

                cardshow = []
                for card in bj.playerdrawn:
                    icon = card[0]
                    if icon == "König":
                        cardshow.append("K")
                    elif icon == "Bube":
                        cardshow.append("B")
                    elif icon == "Dame":
                        cardshow.append("D")
                    elif icon == "Ass":
                        cardshow.append("A")
                    else:
                        cardshow.append(str(card[0]))

                playerausgabe = ", ".join(cardshow)

                dealercardshow = []
                for card in bj.dealerdrawn:
                    icon = card[0]
                    if icon == "König":
                        dealercardshow.append("K")
                    elif icon == "Bube":
                        dealercardshow.append("B")
                    elif icon == "Dame":
                        dealercardshow.append("D")
                    elif icon == "Ass":
                        dealercardshow.append("A")
                    else:
                        dealercardshow.append(str(card[0]))

                dealerausgabe = ", ".join(dealercardshow)
                embed = create_embed(ctx, color, "Blackjack")
                embed.add_field(name=str(return_author(ctx).name) + f" | ```{bj.player}```", value=f"{playerausgabe}",
                                inline=True)
                embed.add_field(name="Dealer" + f" | ```{bj.dealer}```", value=f"{dealerausgabe}", inline=True)
                embed.add_field(name=name, value=value, inline=False)
                embed.add_field(name="Aktueller Kontostand", value=f"{money_user} :coin:", inline=False)
                currentlyGaming.remove(user)
                db.set_money_for_user(return_author(ctx).id, money_user)
                await msg.edit(embed=embed)
            else:
                await send_message(ctx, f"{return_author(ctx).mention}. Du spielst schon!!!", ephemeral=True,
                                   delete_after=5)
        else:
            if not playable[0]:
                await send_message(ctx, "Wetteinsatz ungültig", ephemeral=True, delete_after=5)
            if not playable[1]:
                await send_message(ctx, f"Du hast nur {get_money_for_user(return_author(ctx))} :coin:")

    async def rouletteCommand(self, ctx: Context | Interaction, bet: int, entry: str):
        playable = can_play(ctx, bet)
        user = str(return_author(ctx).id)
        if playable[0] and playable[1] and user not in currentlyGaming:
            validator = Roulette.validate_entry(entry)
            if validator[0]:
                money_user = get_money_for_user(return_author(ctx))
                currentlyGaming.append(user)
                msg = await Roulette.spinning(ctx)
                if isinstance(validator[1], int):
                    multiplication = 20
                    result = await Roulette.play_roulette(entry, "number", msg)
                else:
                    if validator[1] == "green":
                        multiplication = 20
                    else:
                        multiplication = 0.5
                    result = await Roulette.play_roulette(entry, "color", msg)
                if result:
                    money_user = int(money_user) + int(bet * multiplication)
                    db.set_money_for_user(return_author(ctx).id, money_user)
                    await send_message(ctx, f"Du hast {str(int(bet * multiplication))} :coin: gewonnen.\nAktueller Kontostand: {money_user} :coin:")
                else:
                    money_user = int(money_user) - bet
                    db.set_money_for_user(return_author(ctx).id, money_user)
                    await send_message(ctx, f"Du hast {str(bet)} :coin: verloren.\nAktueller Kontostand: {money_user} :coin:")
                currentlyGaming.remove(str(return_author(ctx).id))
            else:
                await send_message(ctx, "Eingabe ungülltig. Gültig: 0-36, red, black, green", ephemeral=True, delete_after=5)
        else:
            if not playable[0]:
                await send_message(ctx, "Wetteinsatz ungültig", ephemeral=True, delete_after=5)
            if not playable[1]:
                await send_message(ctx, f"Du hast nur {get_money_for_user(return_author(ctx))} :coin:")

    async def higherLowerCommand(self, ctx: Context | Interaction, bet: int):
        playable = can_play(ctx, bet)
        money_user = get_money_for_user(return_author(ctx))
        if playable[0] and playable[1]:
            global user_money_dir
            if str(return_author(ctx).id) not in currentlyGaming:
                currentlyGaming.append(str(return_author(ctx).id))
                higher_button = Button(label="Higher", style=discord.ButtonStyle.green, custom_id="higher")
                lower_button = Button(label="Lower", style=discord.ButtonStyle.green, custom_id="lower")
                view = discord.ui.View(timeout=None)
                view.add_item(higher_button)
                view.add_item(lower_button)
                game = Higher_Lower(bet)
                embed = create_embed(ctx, 0xb59809, "Higher Lower")
                embed.add_field(name="Ist die Zahl kleiner oder größer?", value=f"Die gegebene Zahl ist: {game.shown}",
                                inline=False)
                msg = await send_message(ctx, embed=embed, view=view)
                res: Interaction = await bot.wait_for('interaction',
                                                      check=lambda interaction: interaction.user == return_author(ctx))
                if game.is_identical():
                    while game.is_identical():
                        await msg.delete()
                        msg = await send_message(ctx, "Beide Zahlen sind identisch. Probier es erneut", delete_after=5)
                        game.draw_numbers()
                        embed = create_embed(ctx, 0xb59809, "Higher Lower")
                        embed.add_field(name="Ist die Zahl kleiner oder größer?",
                                        value=f"Die gegebene Zahl ist: {game.shown}",
                                        inline=False)
                        await send_message(ctx, embed=embed, view=view)
                        res: Interaction = await bot.wait_for('interaction',
                                                              check=lambda
                                                                  interaction: interaction.user == return_author(
                                                                  ctx))
                if game.won(res.data["custom_id"]):
                    name = "Gewonnen"
                    bet = int(bet * 0.2)
                    value = f"Gegebener Wert: {game.shown}. Versteckter Wert: {game.hidden}.\n{bet} :coin: gewonnen"
                    money_user = int(money_user) + bet
                    color = 0x06660b
                else:
                    name = "Verloren"
                    value = f"Gegebener Wert: {game.shown}. Versteckter Wert: {game.hidden}.\n{bet} :coin: verloren"
                    money_user = int(money_user) - bet
                    color = 0xb50909
                view.clear_items()
                embed = create_embed(ctx, color, "Blackjack")
                embed.add_field(name=name, value=value, inline=False)
                embed.add_field(name="Aktueller Kontostand", value=f"{money_user} :coin:", inline=False)
                currentlyGaming.remove(str(return_author(ctx).id))
                db.set_money_for_user(return_author(ctx).id, money_user)
                await res.response.edit_message(embed=embed, view=view)
            else:
                await send_message(ctx, f"{return_author(ctx).mention}. Du spielst schon!!!", delete_after=5)
        else:
            if not playable[0]:
                await send_message(ctx, "Wetteinsatz ungültig")
            if not playable[1]:
                await send_message(ctx, f"Du hast nur {money_user} :coin:")
