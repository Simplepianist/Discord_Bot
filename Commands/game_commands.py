import asyncio
import time
from discord import Interaction, Member, Embed, Colour, ButtonStyle, ui
from discord.ext.commands import Context
from discord.ui import Button
from Game.blackjack import Blackjack
from Game.higher_lower import HigherLower
from Game.rob import Rob

from Game.roulette import validate_entry, spinning, play_roulette
from Util.util_commands import Utility

embed_view, message = None, None


def create_blackjack_view(draw_button, hold_button):
    """Erstellt die Blackjack-Ansicht."""
    view = ui.View(timeout=None)
    view.add_item(draw_button)
    view.add_item(hold_button)
    return view


def get_card_icon(card):
    """Gibt das Symbol für eine Karte zurück."""
    icons = {"König": "K", "Bube": "B", "Dame": "D", "Ass": "A"}
    return icons.get(card, str(card))


class GamingCommands:
    """Class containing gaming commands."""

    def __init__(self, bot):
        self.currentlyGaming = []
        self.bot = bot
        self.utils = Utility(bot)

    async def handle_invalid_bet(self, ctx, playable):
        """Handles invalid bet scenarios."""
        if not playable[0]:
            await ctx.send("Wetteinsatz ungültig",
                           ephemeral=True, delete_after=5)
        if not playable[1]:
            await ctx.send(
                f"Du hast nur {await self.utils.get_money_for_user(self.utils.return_author(ctx))} :coin:")

    async def execute_gaming_with_timeout(self, ctx: Context | Interaction, befehl,
                                          param_one, param_two=None):
        try:
            if param_two is None:
                await asyncio.wait_for(befehl(ctx, param_one), timeout=300)
            else:
                await asyncio.wait_for(befehl(ctx, param_one, param_two), timeout=300)
        except asyncio.TimeoutError:
            self.currentlyGaming.remove(str(self.utils.return_author(ctx).id))
            await ctx.send("Du hast zu lange gebraucht. Deine Runde endet.")

    async def rob_command(self, ctx: Context | Interaction, player: Member):
        """Handles the rob command."""
        author = self.utils.return_author(ctx)
        can_rob, next_robbing = await self.bot.db.can_rob(author.id)
        if can_rob:
            if str(author.id) not in self.currentlyGaming:
                robbing = Rob(self.bot)
                await robbing.rob(player, ctx)
            else:
                await ctx.send(f"{author.mention}. Du bist beschäftigt mit etwas anderem!!!",
                    delete_after=5
                )
        else:
            if next_robbing:
                await ctx.send("You cannot Rob cause you are still hiding.\nWait till: "
                         + next_robbing.strftime('%d.%m.%Y'),
                    delete_after=10
                )
            else:
                await ctx.send("There seems to be an Error, pls Contact Support for more Information",
                    delete_after=10)

    async def scoreboard_command(self, ctx: Context | Interaction):
        """Displays the scoreboard."""
        scorelist = await self.bot.db.get_users_with_money()
        loaded_config = self.bot.config["embed"]
        embed = Embed(title="Scoreboard",
                              colour=Colour(0x6b0b04),
                              description="Hier ist das Scoreboard für die Games")
        embed.set_thumbnail(url=loaded_config["embeds_thumbnail"])
        embed.set_footer(text="Asked by " + self.utils.return_author(ctx).name,
                         icon_url=self.utils.return_author(ctx).avatar)
        for i, score in enumerate(scorelist):
            user = (self.bot.get_user(int(score.identifier))
                    or await self.bot.fetch_user(int(score.identifier)))
            username = user.name if int(user.discriminator) == 0 \
                else f"{user.name}#{user.discriminator}"
            if i + 1 in [1, 2, 3]:
                emojis = ["first_place", "second_place", "third_place"]
                embed.add_field(name=f":{emojis[i]}: {username}",
                                value=f"{score.money} :coin:", inline=False)
            else:
                embed.add_field(name=f"{i + 1}. {username}",
                                value=f"{score.money} :coin:", inline=False)
            if i == 9:
                break
        await ctx.send(embed=embed)

    async def daily_command(self, ctx: Context | Interaction):
        """Verarbeitet den täglichen Befehl."""
        author = self.utils.return_author(ctx)
        if await self.utils.get_daily(author):
            money_user = int(await self.utils.get_money_for_user(author)) + 300
            bonus = await self.bot.db.update_streak_and_get_bonus(author.id)
            money_user += bonus
            await self.bot.db.set_money_for_user(author.id, money_user)
            await ctx.send(
                               f"Du hast {300 + bonus} Coins erhalten.\n" +
                               f"**Total: {money_user} Coins**")
            await self.bot.db.set_daily(author.id)
        else:
            await ctx.send(
                               "**Du hast dein Daily heute schon geclaimed**")

    async def send_command(self, ctx: Context | Interaction, member: Member, set_money=None):
        """Verarbeitet den Sende-Befehl."""
        if not member.bot:
            author = str(self.utils.return_author(ctx))
            user = str(member)
            try:
                set_money = int(set_money)
                if author == user:
                    await ctx.send(
                                       "Du kannst dir selbst kein Geld senden",
                                       ephemeral=True, delete_after=5)
                elif set_money is None:
                    await ctx.send(
                                       "Betrag muss angegeben sein",
                                       ephemeral=True, delete_after=5)
                elif set_money <= 0:
                    await ctx.send(
                                       "Betrag muss positiv sein",
                                       ephemeral=True, delete_after=5)
                elif user is None:
                    await ctx.send(
                                       "Kein Spieler angegeben",
                                       ephemeral=True, delete_after=5)
                elif str(member.id) in self.currentlyGaming:
                    await ctx.send(
                                       "Dieser Spiel ist gerade beschäftigt",
                                       ephemeral=True, delete_after=5)
                else:
                    money_user = await self.utils.get_money_for_user(self.utils.return_author(ctx))
                    money_other = await self.utils.get_money_for_user(member)
                    if set_money > money_user:
                        await ctx.send("Nicht genügend :coin: zum senden")
                    else:
                        money_user -= set_money
                        money_other += set_money
                        await self.bot.db.set_money_for_user(self.utils.return_author(ctx).id, money_user)
                        await self.bot.db.set_money_for_user(member.id, money_other)
                        embed = Embed(title="Bank", colour=Colour(0xc6c910))
                        embed.add_field(name=author,
                                        value=f"Money: {money_user} :coin:",
                                        inline=False)
                        embed.add_field(name=user,
                                        value=f"Money: {money_other} :coin:",
                                        inline=False)
                        await ctx.send(embed=embed)
            except ValueError:
                await ctx.send(
                                   "Falsche Parameter übergeben",
                                   ephemeral=True)
        else:
            await ctx.send(
                               "Bitte nicht die Bots pingen")

    async def money_command(self, ctx: Context | Interaction, may_member: Member = None):
        """Zeigt das Geld eines Benutzers an."""
        if may_member is not None:
            if not may_member.bot:
                user_money = await self.utils.get_money_for_user(may_member)
                await ctx.send(f"{may_member.name} hat aktuell {user_money} :coin:")
            else:
                await ctx.send("Bitte nicht die Bots pingen", delete_after=20)
        else:
            user_money = await self.utils.get_money_for_user(self.utils.return_author(ctx))
            await ctx.send(f"Du hast aktuell {user_money} :coin:")

    async def blackjack_command(self, ctx: Context | Interaction, bet: int):
        """Verarbeitet den Blackjack-Befehl."""
        playable = await self.utils.can_play(ctx, bet)
        if playable[0] and playable[1]:
            user = str(self.utils.return_author(ctx).id)
            if user not in self.currentlyGaming:
                money_user = await self.utils.get_money_for_user(self.utils.return_author(ctx))
                self.currentlyGaming.append(user)
                draw_id = "draw_" + user
                hold_id = "hold_" + user
                draw_button = Button(label="Draw",
                                     style=ButtonStyle.green,
                                     custom_id=draw_id)
                hold_button = Button(label="Stand",
                                     style=ButtonStyle.red,
                                     custom_id=hold_id)
                embed = self.utils.create_embed(ctx, 0xb59809, "Blackjack")
                firstplayer = True
                has_interaction = True
                responded = False
                bj = Blackjack(bet)
                bj.firstdraw()
                dealerpoints = self.utils.get_first_card(bj.dealerdrawn)
                dealershown = ""
                playerausgabe = ""
                while not bj.is_over():
                    if not bj.playerstand:
                        blackjack_view = ui.View(timeout=None)
                        blackjack_view.add_item(draw_button)
                        blackjack_view.add_item(hold_button)
                        if firstplayer:
                            dealercard = bj.dealerdrawn[0]
                            dealershown = get_card_icon(dealercard[0])
                        else:
                            embed = self.utils.create_embed(ctx, 0xb59809, "Blackjack")
                        cardshow = [get_card_icon(card[0]) for card in bj.playerdrawn]
                        playerausgabe = ", ".join(cardshow)
                        embed.add_field(name=str(self.utils.return_author(ctx).name) + f" | ```{bj.player}```",
                                        value=f"{playerausgabe}", inline=True)
                        embed.add_field(name="Dealer" + f" | ```{dealerpoints}```",
                                        value=f"{dealershown}", inline=True)
                        if firstplayer:
                            blackjack_msg = await ctx.send(embed=embed, view=blackjack_view)
                            firstplayer = not firstplayer
                        else:
                            await response.response.edit_message(embed=embed, view=blackjack_view)
                        checkin = False
                        if bj.natural_player:
                            bj.stand("player")
                            has_interaction = False
                        else:
                            while not checkin:
                                response: Interaction = await self.bot.wait_for('interaction',
                                                                           check=lambda
                                      interaction: interaction.user == self.utils.return_author(ctx))
                                if (
                                    ("component_type" in response.data
                                    and "custom_id" in response.data)
                                    and (user == str(response.user.id)
                                        and response.data["component_type"] == 2
                                    and "custom_id" in response.data.keys())
                                ):
                                    checkin = True
                            action = response.data["custom_id"]
                            if action == draw_id:
                                bj.draw_another("player")
                                if bj.is_overbought("player"):
                                    bj.stand("player")
                            elif action == hold_id:
                                bj.stand("player")
                    else:
                        blackjack_view.clear_items()
                        if not bj.is_overbought("player"):
                            embed = self.utils.create_embed(ctx, 0xb59809, "Blackjack")
                            cardshow = [get_card_icon(card[0]) for card in bj.dealerdrawn]
                            dealerausgabe = ", ".join(cardshow)
                            embed.add_field(name=str(self.utils.return_author(ctx).name) +
                                                 f" | ```{bj.player}```",
                                            value=f"{playerausgabe}", inline=True)
                            embed.add_field(name="Dealer" + f" | ```{bj.dealer}```",
                                            value=f"{dealerausgabe}", inline=True)
                            if not responded and has_interaction:
                                await response.response.edit_message(embed=embed, view=blackjack_view)
                                responded = not responded
                            else:
                                await blackjack_msg.edit(embed=embed, view=blackjack_view)
                            if bj.dealer_draw() and not bj.dealerstand:
                                bj.draw_another("dealer")
                                if bj.is_overbought("dealer"):
                                    bj.stand("dealer")
                                time.sleep(2)
                            else:
                                bj.stand("dealer")
                        else:
                            bj.stand("dealer")
                            await response.response.edit_message(embed=embed, view=blackjack_view)
                await self.finalize_blackjack(ctx, bj, bet, money_user, user, blackjack_msg, embed)
            else:
                await ctx.send(
                                    f"{self.utils.return_author(ctx).mention}. Du spielst schon!!!",
                                   ephemeral=True,
                                   delete_after=5)
        else:
            await self.handle_invalid_bet(ctx, playable)

    async def roulette_command(self, ctx: Context | Interaction, bet: int, entry: str):
        """Verarbeitet den Roulette-Befehl."""
        playable = await self.utils.can_play(ctx, bet)
        user = str(self.utils.return_author(ctx).id)
        if playable[0] and playable[1]:
            if user not in self.currentlyGaming:
                validator = validate_entry(entry)
                if validator[0]:
                    money_user = await self.utils.get_money_for_user(self.utils.return_author(ctx))
                    self.currentlyGaming.append(user)
                    roulette_message = await spinning(ctx)
                    if isinstance(validator[1], int):
                        multiplication = 20
                        result = await play_roulette(entry, "number", roulette_message)
                    else:
                        if validator[1] == "green":
                            multiplication = 20
                        else:
                            multiplication = 0.5
                        result = await play_roulette(entry, "color", roulette_message)
                    if result:
                        money_user += int(bet * multiplication)
                        await self.bot.db.set_money_for_user(self.utils.return_author(ctx).id, money_user)
                        await ctx.send(
                                           f"Du hast {str(int(bet * multiplication))} "
                                           f":coin: gewonnen.\n"
                                           f"Aktueller Kontostand: {money_user} :coin:")
                    else:
                        money_user -= bet
                        await self.bot.db.set_money_for_user(self.utils.return_author(ctx).id, money_user)
                        await ctx.send(
                                           f"Du hast {str(bet)} :coin: verloren.\n"
                                            f"Aktueller Kontostand: {money_user} :coin:")
                    self.currentlyGaming.remove(str(self.utils.return_author(ctx).id))
                else:
                    await ctx.send(
                                       "Eingabe ungülltig. Gültig: 0-36, red, black, green",
                                       ephemeral=True, delete_after=5)
            else:
                await ctx.send(
                                   f"{self.utils.return_author(ctx).mention}. Du spielst schon!!!",
                                   ephemeral=True, delete_after=5)
        else:
            await self.handle_invalid_bet(ctx, playable)

    async def higher_lower_command(self, ctx: Context | Interaction, bet: int):
        """Verarbeitet den Higher-Lower-Befehl."""
        playable = await self.utils.can_play(ctx, bet)
        money_user = await self.utils.get_money_for_user(self.utils.return_author(ctx))
        if playable[0] and playable[1]:
            if str(self.utils.return_author(ctx).id) not in self.currentlyGaming:
                self.currentlyGaming.append(str(self.utils.return_author(ctx).id))
                higher_button = Button(label="Higher",
                                       style=ButtonStyle.green,
                                       custom_id="higher")
                lower_button = Button(label="Lower",
                                      style=ButtonStyle.green,
                                      custom_id="lower")
                higher_lower_view = ui.View(timeout=None)
                higher_lower_view.add_item(higher_button)
                higher_lower_view.add_item(lower_button)
                game = HigherLower(bet)
                embed = self.utils.create_embed(ctx, 0xb59809, "Higher Lower")
                embed.add_field(name="Ist die Zahl kleiner oder größer?",
                                value=f"Die gegebene Zahl ist: {game.shown}",
                                inline=False)
                higher_lower_message = await ctx.send(embed=embed, view=higher_lower_view)
                response_object: Interaction = await self.bot.wait_for('interaction',
                      check=lambda
                          interaction: interaction.user == self.utils.return_author(ctx))
                if game.is_identical():
                    await self.handle_identical_numbers(ctx, game, embed,
                                                   higher_lower_view, higher_lower_message)
                if game.won(str(response_object.data["custom_id"])):
                    game_response = "Gewonnen"
                    bet = int(bet * 0.2)
                    description = (f"Gegebener Wert: {game.shown}. "
                                   f"Versteckter Wert: {game.hidden}.\n{bet} :coin: gewonnen")
                    money_user += bet
                    embed_color = 0x06660b
                else:
                    game_response = "Verloren"
                    description = (f"Gegebener Wert: {game.shown}. "
                                   f"Versteckter Wert: {game.hidden}.\n{bet} :coin: verloren")
                    money_user -= bet
                    embed_color = 0xb50909
                higher_lower_view.clear_items()
                embed = self.utils.create_embed(ctx, embed_color, "Blackjack")
                embed.add_field(name=game_response,
                                value=description,
                                inline=False)
                embed.add_field(name="Aktueller Kontostand",
                                value=f"{money_user} :coin:",
                                inline=False)
                self.currentlyGaming.remove(str(self.utils.return_author(ctx).id))
                await self.bot.db.set_money_for_user(self.utils.return_author(ctx).id, money_user)
                await response_object.response.edit_message(embed=embed, view=higher_lower_view)
            else:
                await ctx.send(
                                   f"{self.utils.return_author(ctx).mention}. Du spielst schon!!!",
                                   delete_after=5)
        else:
            await self.handle_invalid_bet(ctx, playable)

    async def finalize_blackjack(self, ctx, bj, bet, money_user, user, sending_message, embed):
        """Beendet das Blackjack-Spiel."""
        name = ""
        value = ""
        color = None
        if bj.won() == "draw":
            name = "Unentschieden"
            value = f"Du hast {str(bj.get_money())} :coin: zurückerhalten"
            color = 0xd6b22f
        elif bj.won() == "player":
            name = "Gewonnen"
            value = f"Du hast {str(bet)} :coin: erhalten"
            money_user += bet
            color = 0x06660b
        elif bj.won() == "dealer":
            name = "Verloren"
            value = f"Du hast deinen Einsatz von {str(bet)} :coin: verloren"
            money_user -= bet
            color = 0xb50909
        elif bj.won() == "doppelt":
            name = "Natural Blackjack"
            value = f"Du hast {str(bj.get_money())} :coin: erhalten"
            money_user += bj.get_money()
            color = 0x5f09b5
        embed.color = color
        cardshow = [get_card_icon(card[0]) for card in bj.playerdrawn]
        playerausgabe = ", ".join(cardshow)
        dealercardshow = [get_card_icon(card[0]) for card in bj.dealerdrawn]
        dealerausgabe = ", ".join(dealercardshow)
        embed.clear_fields()
        embed.add_field(name=str(self.utils.return_author(ctx).name) + f" | ```{bj.player}```",
                        value=f"{playerausgabe}",
                        inline=True)
        embed.add_field(name="Dealer" + f" | ```{bj.dealer}```",
                        value=f"{dealerausgabe}",
                        inline=True)
        embed.add_field(name=name,
                        value=value,
                        inline=False)
        embed.add_field(name="Aktueller Kontostand",
                        value=f"{money_user} :coin:",
                        inline=False)
        self.currentlyGaming.remove(user)
        await self.bot.db.set_money_for_user(self.utils.return_author(ctx).id, money_user)
        await sending_message.edit(embed=embed)


    async def play_blackjack(self, ctx, bj, user, draw_id, hold_id, embed, msg,
                             money_user, bet, playerausgabe):
        """Spielt das Blackjack-Spiel."""
        draw_button = Button(label="Draw",
                             style=ButtonStyle.green,
                             custom_id=draw_id)
        hold_button = Button(label="Stand",
                             style=ButtonStyle.red,
                             custom_id=hold_id)
        firstplayer = True
        while not bj.is_over():
            if not bj.playerstand:
                if firstplayer:
                    firstplayer = False
                else:
                    await res.response.edit_message(embed=embed,
                                                      view=create_blackjack_view(draw_button,
                                                                                 hold_button))
                res = await self.bot.wait_for('interaction', check=
                                         lambda interaction: interaction.user == self.utils.return_author(ctx))
                action = res.data["custom_id"]
                if action == draw_id:
                    bj.draw_another("player")
                    if bj.is_overbought("player"):
                        bj.stand("player")
                elif action == hold_id:
                    bj.stand("player")
            else:
                await self.handle_dealer_turn(ctx, bj, embed, msg, money_user, bet, user, playerausgabe)
                break

    async def handle_dealer_turn(self, ctx, bj, embed, msg, money_user, bet, user, playerausgabe):
        """Verarbeitet den Zug des Dealers."""
        while not bj.is_over():
            if not bj.is_overbought("player"):
                embed = self.utils.create_embed(ctx, 0xb59809, "Blackjack")
                cardshow = [get_card_icon(card[0]) for card in bj.dealerdrawn]
                dealerausgabe = ", ".join(cardshow)
                embed.add_field(name=str(self.utils.return_author(ctx).name) + f" | ```{bj.player}```",
                                value=f"{playerausgabe}", inline=True)
                embed.add_field(name="Dealer" + f" | ```{bj.dealer}```", value=f"{dealerausgabe}",
                                inline=True)
                await msg.edit(embed=embed, view=None)
                if bj.dealer_draw() and not bj.dealerstand:
                    bj.draw_another("dealer")
                    if bj.is_overbought("dealer"):
                        bj.stand("dealer")
                    time.sleep(2)
                else:
                    bj.stand("dealer")
            else:
                bj.stand("dealer")
                await msg.edit(embed=embed, view=None)
        await self.finalize_blackjack(ctx, bj, bet, money_user, user, msg, embed)

    async def handle_identical_numbers(self, ctx, game, embed, view, msg):
        """Handles identical numbers in higher lower game."""
        while game.is_identical():
            await msg.delete()
            msg = await ctx.send(
                                         "Beide Zahlen sind identisch. Probier es erneut",
                                     delete_after=5)
            game.draw_numbers()
            embed.add_field(name="Ist die Zahl kleiner oder größer?",
                            value=f"Die gegebene Zahl ist: {game.shown}",
                            inline=False)
            await ctx.send(embed=embed, view=view)
            await self.bot.wait_for('interaction',
                               check=lambda interaction: interaction.user == self.utils.return_author(ctx))
