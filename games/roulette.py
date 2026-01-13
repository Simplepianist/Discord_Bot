# games/roulette.py (Enhanced Version with Visual Wheel)
"""Enhanced Roulette game with animated spinning wheel visualization."""
import random
import asyncio
from typing import Tuple
from discord import Embed, Colour
from discord.ext.commands import Context
from discord import Interaction
from .base_game import BaseGame


class RouletteGame(BaseGame):
    """Roulette game with realistic wheel animation."""

    # Roulette wheel in actual European layout order
    WHEEL_ORDER = [
        0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10,
        5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
    ]

    # Color mapping
    RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

    COLOR_EMOJI = {
        "red": "🔴",
        "black": "⚫",
        "green": "🟢"
    }

    def __init__(self, player_id: int, bet: int, wager: str):
        super().__init__(player_id, bet)
        self.wager = wager.lower()
        self.bet_type = self._determine_bet_type()
        self.winning_number: int = 0
        self.winning_color: str = ""

    def _determine_bet_type(self) -> str:
        """Determine if bet is on color or number."""
        if self.wager in ["red", "black", "green"]:
            return "color"
        try:
            num = int(self.wager)
            if 0 <= num <= 36:
                return "number"
        except ValueError:
            pass
        return "invalid"

    def is_valid_bet(self) -> bool:
        """Check if the bet is valid."""
        return self.bet_type != "invalid"

    @staticmethod
    def _get_color(number: int) -> str:
        """Get the color of a number."""
        if number == 0:
            return "green"
        elif number in RouletteGame.RED_NUMBERS:
            return "red"
        else:
            return "black"

    def _create_wheel_display(self, current_number: int, highlight: bool = False) -> str:
        """Create a visual representation of the wheel showing nearby numbers."""
        # Find index of current number
        try:
            current_idx = self.WHEEL_ORDER.index(current_number)
        except ValueError:
            current_idx = 0

        # Get 5 numbers: 2 before, current, 2 after
        display_numbers = []
        for i in range(-2, 3):
            idx = (current_idx + i) % len(self.WHEEL_ORDER)
            num = self.WHEEL_ORDER[idx]
            color = self._get_color(num)
            emoji = self.COLOR_EMOJI[color]

            if i == 0 and highlight:
                # Current number - make it stand out
                display_numbers.append(f"**[{emoji} {num}]**")
            elif i == 0:
                display_numbers.append(f"**{emoji} {num}**")
            else:
                display_numbers.append(f"{emoji} {num}")

        return " <- ".join(display_numbers)

    def spin_wheel(self) -> Tuple[int, str]:
        """Spin the roulette wheel and return result."""
        self.winning_number = random.choice(self.WHEEL_ORDER)
        self.winning_color = self._get_color(self.winning_number)
        return self.winning_number, self.winning_color

    def check_win(self) -> Tuple[bool, float]:
        """
        Check if player won and return multiplier.
        Returns: (won, multiplier)
        """
        if self.bet_type == "number":
            won = int(self.wager) == self.winning_number
            return won, 36.0 if won else 0

        elif self.bet_type == "color":
            won = self.wager == self.winning_color
            if won and self.wager == "green":
                return True, 36.0
            elif won:
                return True, 2.0
            return False, 0

        return False, 0

    async def play(self, ctx: Context | Interaction) -> int:
        """Execute the roulette game with realistic spinning animation."""
        # Determine the winning number first
        self.spin_wheel()
        winning_idx = self.WHEEL_ORDER.index(self.winning_number)

        # Initial message
        embed = self._create_spin_embed(ctx, "🎰 Spinning the wheel...", None, "start")
        message = await ctx.send(embed=embed)
        await asyncio.sleep(0.5)

        # Calculate a path that ends on the winning number
        # We'll make multiple passes around the wheel, then land on winner
        total_positions = len(self.WHEEL_ORDER)

        # Start at a random position, make 2-3 full rotations, then land on winner
        start_pos = random.randint(0, total_positions - 1)
        full_rotations = random.randint(2, 3)
        positions_to_travel = (full_rotations * total_positions) + (winning_idx - start_pos) % total_positions

        current_pos = start_pos
        positions_shown = 0

        while positions_shown < positions_to_travel:
            current_pos = (current_pos + 1) % total_positions
            positions_shown += 1

            spin_num = self.WHEEL_ORDER[current_pos]

            # Are we at the final number?
            if current_pos == winning_idx:
                embed = self._create_spin_embed(ctx, "🎯 Ball landed on...", spin_num, "final")
            else:
                embed = self._create_spin_embed(ctx, "🎰 Spinning...", spin_num, "slowing")

            await message.edit(embed=embed)
            await asyncio.sleep(0.8)

        # Small pause on final number
        await asyncio.sleep(0.5)

        # Calculate payout
        won, multiplier = self.check_win()
        self.result = 'win' if won else 'lose'
        self.payout = self.calculate_payout(won, multiplier)

        return self.payout

    def _create_spin_embed(self, ctx: Context | Interaction, title: str,
                           number: int = None, phase: str = "start") -> Embed:
        """Create a simplified embed for the spinning animation."""
        author = ctx.user if isinstance(ctx, Interaction) else ctx.author

        # Color based on phase
        if phase == "final":
            won, _ = self.check_win()
            color = 0x06660b if won else 0xb50909
        else:
            color = 0xffd700  # Gold during spinning

        embed = Embed(title="🎰 Roulette", colour=Colour(color))

        # Show the wheel visualization
        if number is not None:
            wheel_display = self._create_wheel_display(number, phase == "final")

            # Show current number prominently
            color_name = self._get_color(number)
            emoji = self.COLOR_EMOJI[color_name]

            if phase == "final":
                embed.add_field(
                    name="🎯 Winner",
                    value=f"# {emoji} **{number}**",
                    inline=False
                )
            else:
                embed.add_field(
                    name=title,
                    value=wheel_display,
                    inline=False
                )
        else:
            # Initial state
            bet_display = self.wager.title() if self.bet_type == "color" else f"Number {self.wager}"
            embed.add_field(name=title, value=f"Betting on: **{bet_display}**", inline=False)

        # Always show bet info at the bottom
        bet_display = self.wager.title() if self.bet_type == "color" else f"Number {self.wager}"
        embed.add_field(name="Your Bet", value=bet_display, inline=True)
        embed.add_field(name="Amount", value=f"{self.bet} coins", inline=True)

        embed.set_footer(text=f"Played by {author.name}", icon_url=author.avatar)
        return embed

    def get_result_embed(self, ctx: Context | Interaction, final_balance: int) -> Embed:
        """Create final result embed with balance update."""
        author = ctx.user if isinstance(ctx, Interaction) else ctx.author

        won, multiplier = self.check_win()
        color = 0x06660b if won else 0xb50909

        embed = Embed(title="🎰 Roulette Result", colour=Colour(color))

        # Show result prominently
        emoji = self.COLOR_EMOJI[self.winning_color]
        embed.add_field(
            name="🎯 Landed on",
            value=f"# {emoji} **{self.winning_number}**",
            inline=False
        )

        # Show outcome
        bet_display = self.wager.title() if self.bet_type == "color" else f"Number {self.wager}"

        if won:
            if multiplier == 36:
                result_text = f"🎉 **JACKPOT!** Bet: {bet_display} → Won **{abs(self.payout)}** coins (36x)"
            else:
                result_text = f"✅ **Winner!** Bet: {bet_display} → Won **{abs(self.payout)}** coins (2x)"
        else:
            result_text = f"❌ Bet: {bet_display} → Lost {abs(self.payout)} coins"

        embed.add_field(name="Result", value=result_text, inline=False)
        embed.add_field(name="💰 New Balance", value=f"**{final_balance}** coins", inline=False)

        embed.set_footer(text=f"Played by {author.name}", icon_url=author.avatar)
        return embed


# Example usage in cog remains the same:
"""
@commands.hybrid_command(name="roulette", aliases=["rl"])
async def roulette(self, ctx: Context | Interaction, bet: int, wager: str):
    author = ctx.user if isinstance(ctx, Interaction) else ctx.author

    await self.game_manager.validate_bet(ctx, bet)

    game = RouletteGame(author.id, bet, wager)
    if not game.is_valid_bet():
        from utils.errors import InvalidBetError
        raise InvalidBetError("Valid options: 0-36, red, black, green")

    await self.game_manager.execute_game(ctx, game, author)
"""