from abc import ABC, abstractmethod
from typing import Optional
from discord import Embed
from discord.ext.commands import Context

class BaseGame(ABC):
    def __init__(self, player_id: int, bet: int):
        self.player_id = player_id
        self.bet = bet
        self.result: Optional[bool] = None  # True for win, False for loss, None for ongoing
        self.payout: int = 0

    @abstractmethod
    async def play(self, ctx: Context) -> None:
        """Start the game interaction with the player."""
        pass

    @abstractmethod
    def get_result_embed(self) -> Embed:
        """Generate an embed summarizing the game result."""
        pass

    def calculate_payout(self, won: bool, multiplier: float = 2.0) -> int:
        if won:
            return int(self.bet * multiplier) - self.bet
        return -self.bet