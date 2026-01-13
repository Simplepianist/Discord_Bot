import random

import discord
from discord import ButtonStyle, Interaction, Embed, Colour
from discord.ui import View, Button
from discord.ext.commands import Context
from games.base_game import BaseGame


class HigherLowerGame(BaseGame):
    """Simple higher or lower number guessing game."""

    def __init__(self, player_id: int, bet: int):
        super().__init__(player_id, bet)
        self.shown_number: int = 0
        self.hidden_number: int = 0
        self.guess: str = ""
        self._draw_numbers()

    def _draw_numbers(self):
        """Draw two random numbers."""
        self.shown_number = random.randint(1, 100)
        self.hidden_number = random.randint(1, 100)

        # Ensure numbers are different
        while self.shown_number == self.hidden_number:
            self.hidden_number = random.randint(1, 100)

    def check_guess(self, guess: str) -> bool:
        """Check if the guess was correct."""
        if guess == "higher":
            return self.hidden_number > self.shown_number
        elif guess == "lower":
            return self.hidden_number < self.shown_number
        return False

    async def play(self, ctx: Context | Interaction) -> int:
        """Execute the higher/lower game."""
        view = HigherLowerView(self, ctx)
        embed = self._create_game_embed(ctx, show_result=False)
        message = await ctx.send(embed=embed, view=view)

        # Wait for player choice
        await view.wait()

        # Check if player made a guess (they might have timed out)
        if not self.guess:
            # Timeout - player loses
            self.result = 'lose'
            self.payout = -self.bet

            # Update message to show timeout
            embed = self._create_timeout_embed(ctx)
            await message.edit(embed=embed, view=None)
        else:
            # Player made a guess - show result
            won = self.check_guess(self.guess)
            self.result = 'win' if won else 'lose'
            self.payout = self.calculate_payout(won, 1.5)  # 1.5x multiplier

            # Update message to show result
            embed = self._create_game_embed(ctx, show_result=True)
            await message.edit(embed=embed, view=None)

        return self.payout

    def _create_game_embed(self, ctx: Context | Interaction, show_result: bool = False) -> Embed:
        """Create the game embed."""
        author = ctx.user if isinstance(ctx, Interaction) else ctx.author

        if show_result:
            # Determine color based on result
            color = 0x06660b if self.result == 'win' else 0xb50909
        else:
            # Blue/neutral during guessing
            color = 0x3498db

        embed = Embed(
            title="🎲 Higher or Lower",
            colour=Colour(color)
        )

        if show_result:
            # Show both numbers
            embed.add_field(
                name="The Numbers",
                value=f"Shown: **{self.shown_number}**\nHidden: **{self.hidden_number}**",
                inline=False
            )

            # Show what they guessed
            guess_emoji = "⬆️" if self.guess == "higher" else "⬇️"
            embed.add_field(
                name="Your Guess",
                value=f"{guess_emoji} **{self.guess.title()}**",
                inline=True
            )

            # Show if correct
            if self.hidden_number > self.shown_number:
                actual = "⬆️ Higher"
            else:
                actual = "⬇️ Lower"

            embed.add_field(
                name="Actual",
                value=actual,
                inline=True
            )
        else:
            # Just show the visible number
            embed.add_field(
                name="The shown number is:",
                value=f"# **{self.shown_number}**",
                inline=False
            )
            embed.add_field(
                name="Question",
                value="Is the hidden number **higher** or **lower**?",
                inline=False
            )

        # Always show bet info
        embed.add_field(name="Your Bet", value=f"{self.bet} coins", inline=False)

        if show_result:
            # Show win/loss amount
            if self.result == 'win':
                embed.add_field(name="Result", value=f"✅ +{abs(self.payout)} coins", inline=True)
            else:
                embed.add_field(name="Result", value=f"❌ -{abs(self.payout)} coins", inline=True)

        embed.set_footer(text=f"Played by {author.name}", icon_url=author.avatar)
        return embed

    def _create_timeout_embed(self, ctx: Context | Interaction) -> Embed:
        """Create embed for timeout scenario."""
        author = ctx.user if isinstance(ctx, Interaction) else ctx.author

        embed = Embed(
            title="🎲 Higher or Lower - Timeout",
            colour=Colour(0xb50909)
        )

        embed.add_field(
            name="⏰ Time's Up!",
            value=f"You didn't answer in time.\nThe hidden number was **{self.hidden_number}**",
            inline=False
        )

        embed.add_field(name="Lost", value=f"{self.bet} coins", inline=True)

        embed.set_footer(text=f"Played by {author.name}", icon_url=author.avatar)
        return embed

    def get_result_embed(self, ctx: Context | Interaction, final_balance: int) -> Embed:
        """Create final result embed with balance update."""
        author = ctx.user if isinstance(ctx, Interaction) else ctx.author

        color = 0x06660b if self.result == 'win' else 0xb50909

        embed = Embed(
            title="🎲 Higher or Lower - Final Result",
            colour=Colour(color)
        )

        # Show the numbers
        embed.add_field(
            name="The Numbers",
            value=f"Shown: **{self.shown_number}**\nHidden: **{self.hidden_number}**",
            inline=False
        )

        # Show guess and result
        if self.guess:
            guess_emoji = "⬆️" if self.guess == "higher" else "⬇️"
            if self.result == 'win':
                result_text = f"✅ Correct! You guessed {guess_emoji} **{self.guess.title()}**\n**Won {abs(self.payout)} coins**"
            else:
                result_text = f"❌ Wrong! You guessed {guess_emoji} **{self.guess.title()}**\n**Lost {abs(self.payout)} coins**"
        else:
            result_text = f"⏰ Timeout - Lost {abs(self.payout)} coins"

        embed.add_field(name="Result", value=result_text, inline=False)
        embed.add_field(name="💰 New Balance", value=f"**{final_balance}** coins", inline=False)

        embed.set_footer(text=f"Played by {author.name}", icon_url=author.avatar)
        return embed


class HigherLowerView(View):
    """View for Higher/Lower game controls."""

    def __init__(self, game: HigherLowerGame, ctx: Context | Interaction):
        super().__init__(timeout=60)
        self.game = game
        self.ctx = ctx
        self.author = ctx.user if isinstance(ctx, Interaction) else ctx.author

    async def on_timeout(self):
        """Called when the view times out."""
        # Game will handle this in the play() method by checking if guess is empty
        pass

    @discord.ui.button(label="Higher", style=ButtonStyle.green, emoji="⬆️")
    async def higher_button(self, interaction: Interaction, button: Button):
        """Player guesses higher."""
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Not your game!", ephemeral=True)
            return

        self.game.guess = "higher"
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label="Lower", style=ButtonStyle.red, emoji="⬇️")
    async def lower_button(self, interaction: Interaction, button: Button):
        """Player guesses lower."""
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Not your game!", ephemeral=True)
            return

        self.game.guess = "lower"
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()