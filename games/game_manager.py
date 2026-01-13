from typing import Optional
from discord import Member
from discord.ext.commands import Context
from discord import Interaction


class GameManager:
    """Manages active game sessions."""

    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # {user_id: game_type}

    def is_user_busy(self, user_id: int) -> bool:
        """Check if user is currently in a game."""
        return user_id in self.active_games

    def start_game(self, user_id: int, game_type: str) -> bool:
        """
        Start a game session.
        Returns False if user is already in a game.
        """
        if self.is_user_busy(user_id):
            return False
        self.active_games[user_id] = game_type
        return True

    def end_game(self, user_id: int):
        """End a game session."""
        self.active_games.pop(user_id, None)

    async def validate_bet(self, ctx: Context | Interaction, bet: int) -> tuple[bool, str]:
        """
        Validate a bet amount.
        Returns: (is_valid, error_message)
        """
        author = ctx.user if isinstance(ctx, Interaction) else ctx.author

        if bet < 1:
            return False, "Bet must be at least 1 coin"

        user_balance = await self.bot.db.get_money_for_user(author.id)

        if bet > user_balance:
            return False, f"You only have {user_balance} coins"

        return True, ""

    async def execute_game(
            self,
            ctx: Context | Interaction,
            game_instance,
            author: Member
    ) -> Optional[int]:
        """
        Execute a game and handle the full lifecycle.
        Returns final balance or None if game couldn't start.
        """
        # Check if user is busy
        if self.is_user_busy(author.id):
            await ctx.send(f"{author.mention}, you're already in a game!", ephemeral=True)
            return None

        # Start game session
        game_type = game_instance.__class__.__name__
        self.start_game(author.id, game_type)

        try:
            # Play the game
            payout, message = await game_instance.play(ctx)

            # Update balance
            current_balance = await self.bot.db.get_money_for_user(author.id)
            new_balance = current_balance + payout
            await self.bot.db.set_money_for_user(author.id, new_balance)

            # Show result
            result_embed = game_instance.get_result_embed(ctx, new_balance)
            if message is not None:
                await message.edit(embed=result_embed, view=None)
            else:
                await ctx.send(embed=result_embed)
            return new_balance

        finally:
            # Always end the game session
            self.end_game(author.id)
            return None