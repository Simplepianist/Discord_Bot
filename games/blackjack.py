import random
import asyncio
from typing import List, Tuple

import discord
from discord import ButtonStyle, Interaction, Embed, Colour
from discord.ui import View, Button
from discord.ext.commands import Context
from .base_game import BaseGame


class Card:
    RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    SUITS = ["♥️", "♠️", "♦️", "♣️"]

    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit

    @property
    def value(self) -> int:
        if self.rank in ["J", "Q", "K"]:
            return 10
        if self.rank == "A":
            return 11  # Initially treat Ace as 11
        return int(self.rank)

    def __str__(self) -> str:
        return f"{self.suit}{self.rank}"

class Hand:
    def __init__(self):
        self.cards: List[Card] = []

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    @property
    def value(self) -> int:
        total = sum(card.value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == "A")
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    @property
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.value == 21

    @property
    def is_bust(self) -> bool:
        return self.value > 21

    def __str__(self) -> str:
        return " | ".join(str(card) for card in self.cards)

class Deck:
    def __init__(self):
        self.cards = [
            Card(rank, suit)
            for rank in Card.RANKS
            for suit in Card.SUITS
        ]
        random.shuffle(self.cards)

    def draw(self) -> Card:
        """Draw a card from the deck."""
        if not self.cards:
            # Reshuffle if deck is empty
            self.__init__()
        return self.cards.pop()

class BlackjackGame(BaseGame):

    def __init__(self, player_id: int, bet: int):
        super().__init__(player_id, bet)
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.player_stood = False

    def deal_initial_cards(self) -> None:
        for _ in range(2):
            self.player_hand.add_card(self.deck.draw())
            self.dealer_hand.add_card(self.deck.draw())

    def player_hit(self):
        self.player_hand.add_card(self.deck.draw())

    def dealer_play(self):
        while self.dealer_hand.value < 17:
            self.dealer_hand.add_card(self.deck.draw())
            if self.dealer_hand.is_bust:
                break

    def determine_winner(self) -> Tuple[str, float]:
        """
        Determine the winner and payout multiplier.
        Returns: (result, multiplier) where result is 'win', 'lose', or 'draw'
        """
        player_val = self.player_hand.value
        dealer_val = self.dealer_hand.value

        # Player bust always loses
        if self.player_hand.is_bust:
            return 'lose', 0

        # Player blackjack
        if self.player_hand.is_blackjack and not self.dealer_hand.is_blackjack:
            return 'win', 2.5  # 3:2 payout

        # Dealer bust, player didn't
        if self.dealer_hand.is_bust:
            return 'win', 2.0

        # Compare values
        if player_val > dealer_val:
            return 'win', 2.0
        elif player_val < dealer_val:
            return 'lose', 0
        else:
            return 'draw', 1.0  # Push - get bet back

    async def play(self, ctx: Context | Interaction):
        self.deal_initial_cards()

        if self.player_hand.is_blackjack:
            self.player_stood = True
            self.dealer_play()
            self.result, multiplier = self.determine_winner()
            return self.calculate_payout(self.result == 'win', multiplier), None

        view = BlackjackView(self, ctx)
        embed = self._create_game_embed(ctx, show_dealer_card=False)
        message = await ctx.send(embed=embed, view=view)

        await view.wait()

        self.dealer_play()

        for _ in range(len(self.dealer_hand.cards) - 2):
            embed = self._create_game_embed(ctx, show_dealer_card=True)
            await message.edit(embed=embed, view=None)
            await asyncio.sleep(1)

        self.result, multiplier = self.determine_winner()
        self.payout = self.calculate_payout(self.result == 'win', multiplier)

        return self.payout, message

    def _create_game_embed(self, ctx: Context | Interaction, show_dealer_card: bool = True) -> Embed:
        author = ctx.user if isinstance(ctx, Interaction) else ctx.author

        color = 0x7B1FA2
        if self.player_stood:
            if self.result == "win":
                color = 0x06660b
            elif self.player_hand.is_bust or self.result == "lose":
                color = 0xb50909

        embed = Embed(title="♠️ Blackjack ♥️", color=Colour(color))

        # Player's hand
        additional_player_info = ""
        player_str = f"{self.player_hand}"
        if self.player_hand.is_blackjack:
            additional_player_info += "| BLACKJACK 💸"
        elif self.player_hand.is_bust:
            additional_player_info += "| BUST💥"
        embed.add_field(name=f"👤 {author.name} | ```{self.player_hand.value}``` {additional_player_info}", value=player_str, inline=True)

        additional_dealer_info = ""
        # Dealer's hand
        if show_dealer_card or self.player_stood:
            dealer_str = f"{self.dealer_hand}"
            additional_dealer_info = f"| ```{self.dealer_hand.value}```"
            if self.dealer_hand.is_bust:
                additional_dealer_info +=  " | BUST💥"
        else:
            additional_dealer_info = "| ```??```"
            dealer_str = f"{self.dealer_hand.cards[0]} | 🎴"
        embed.add_field(name=f"🃏 Dealer {additional_dealer_info}", value=dealer_str, inline=True)

        embed.set_footer(text=f"Bet: {self.bet} 🪙", icon_url=author.avatar)
        return embed

    def get_result_embed(self, ctx: Context | Interaction, final_balance: int) -> Embed:
        """Create the final result embed."""
        embed = self._create_game_embed(ctx, show_dealer_card=True)

        # Add result field
        if self.result == 'win':
            result_text = f"🎉 You won {abs(self.payout)} 🪙!"
            if self.player_hand.is_blackjack:
                result_text += "\n💸 Natural Blackjack!"
        elif self.result == 'lose':
            result_text = f"📉 You lost {abs(self.payout)} 🪙"
        else:
            result_text = "🤝 Draw! Bet returned"

        embed.add_field(
            name="Result",
            value=f"{result_text}\nCurrent Money: {final_balance} 🪙",
            inline=False
        )

        return embed


class BlackjackView(View):
    """View for Blackjack game controls."""

    def __init__(self, game: BlackjackGame, ctx: Context | Interaction):
        super().__init__(timeout=300)
        self.game = game
        self.ctx = ctx
        self.author = ctx.user if isinstance(ctx, Interaction) else ctx.author

    @discord.ui.button(label="Hit", style=ButtonStyle.green, emoji="▶️")
    async def hit_button(self, interaction: Interaction, button: Button):
        """Player hits (draws a card)."""
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Not your game!", ephemeral=True)
            return

        self.game.player_hit()

        if self.game.player_hand.is_bust:
            self.game.player_stood = True
            embed = self.game._create_game_embed(self.ctx, show_dealer_card=True)
            self.clear_items()
            await interaction.response.edit_message(embed=embed, view=self)
            self.stop()
        else:
            embed = self.game._create_game_embed(self.ctx, show_dealer_card=False)
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Stand", style=ButtonStyle.red, emoji="⏸️")
    async def stand_button(self, interaction: Interaction, button: Button):
        """Player stands (ends their turn)."""
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Not your game!", ephemeral=True)
            return

        self.game.player_stood = True
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()


